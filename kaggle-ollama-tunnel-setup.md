# Hosting Gemma via Ollama on Kaggle + Tunnel + Proxy — Setup Documentation

> **Note on model name:** Throughout this setup, the model used is
> `gemma3n:e4b-it-q4_K_M` (Gemma 3n, "E4B" effective-parameter variant,
> instruction-tuned, Q4_K_M quantization). There is no publicly released
> "Gemma 4" as of this writing — if you intended a different model, swap
> the tag accordingly.

> **Important caveat:** Kaggle notebooks are interactive dev environments,
> not always-on hosts. Sessions can disconnect from idle timeouts, browser
> tab throttling, or GPU quota limits — wiping all installed software,
> the downloaded model, and running processes. This setup is suitable for
> development/testing, not production. For a stable, always-on deployment,
> use a persistent VM (e.g. Oracle Cloud Always Free tier) or a GPU host
> (RunPod, Modal, etc.) instead.

---

## 1. Loading Ollama

Kaggle's base image doesn't include Ollama or `zstd` (a dependency of the
install script), so both need to be installed each fresh session.

```bash
# Install system dependency required by the Ollama installer
!apt-get update -qq && apt-get install -y zstd

# Install Ollama itself
!curl -fsSL https://ollama.com/install.sh | sh
```

Start the Ollama server as a background process and wait until it's
actually accepting connections (a fixed `sleep` is unreliable — poll
instead):

```python
import subprocess, time, requests

ollama_log = open("/kaggle/working/ollama.log", "w")
ollama_proc = subprocess.Popen(["ollama", "serve"], stdout=ollama_log, stderr=ollama_log)

for i in range(30):
    try:
        requests.get("http://localhost:11434")
        print(f"Ollama is up after {i+1}s")
        break
    except requests.exceptions.ConnectionError:
        time.sleep(1)
else:
    print("Ollama did not start in time — check ollama.log")
```

Verify:
```bash
!ollama list
```

---

## 2. Loading `gemma3n:e4b-it-q4_K_M`

Once the server is running, pull the model:

```bash
!ollama pull gemma3n:e4b-it-q4_K_M
```

Confirm it downloaded:
```bash
!ollama list
```

Quick local test (before exposing it externally):
```python
import requests

resp = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma3n:e4b-it-q4_K_M",
        "prompt": "Hello, who are you?",
        "stream": False
    }
)
print(resp.json())
```

---

## 3. Making the tunnel

We used Cloudflare's free "quick tunnel" (`cloudflared`) — no signup
required, but the URL is temporary and changes every time the tunnel
restarts.

Download the binary (also wiped on session reset, so re-download as needed):
```bash
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
!chmod +x cloudflared-linux-amd64
```

Start a tunnel pointed at the **proxy** (port `8000`), not directly at
Ollama (port `11434`) — see Section 4 for why:

```python
import subprocess, time, re

tunnel_log_path = "/kaggle/working/tunnel_proxy.log"
tunnel_log = open(tunnel_log_path, "w")
tunnel_proc = subprocess.Popen(
    ["./cloudflared-linux-amd64", "tunnel", "--url", "http://localhost:8000"],
    stdout=tunnel_log, stderr=tunnel_log, text=True
)

url = None
for i in range(30):
    time.sleep(1)
    with open(tunnel_log_path) as f:
        content = f.read()
    match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", content)
    if match:
        url = match.group(0)
        print("Tunnel URL:", url)
        break
if not url:
    print("Tunnel URL not found yet — check tunnel_proxy.log manually")
```

The printed URL (e.g. `https://cadillac-induction-developer-urw.trycloudflare.com`)
is your public endpoint. **It changes every time the tunnel process is
restarted** — update your app's config each time.

---

## 4. Setting the proxy

Ollama has no built-in authentication — anyone with the tunnel URL could
use your GPU. A small FastAPI proxy sits in front of Ollama and requires
an API key (a secret string you invent yourself, not issued by Ollama or
any service) before forwarding requests.

**Generate a secret key:**
```python
import secrets
key = secrets.token_urlsafe(32)
print(key)
```

**Install dependencies:**
```bash
!pip install fastapi uvicorn httpx -q
```

**Write the proxy** (paste your generated key into `API_KEY`):
```python
%%writefile /kaggle/working/proxy.py
from fastapi import FastAPI, Request, HTTPException
import httpx

API_KEY = "<your-generated-api-key>"
OLLAMA_URL = "http://localhost:11434"

app = FastAPI()

@app.post("/{path:path}")
async def proxy(path: str, request: Request):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    body = await request.body()
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(f"{OLLAMA_URL}/{path}", content=body)
    return resp.json()
```

**Start the proxy:**
```python
import subprocess, time, requests

proxy_log = open("/kaggle/working/proxy.log", "w")
proxy_proc = subprocess.Popen(
    ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/kaggle/working", stdout=proxy_log, stderr=proxy_log
)

for i in range(20):
    try:
        requests.get("http://localhost:8000")
        print(f"Proxy is up after {i+1}s")
        break
    except requests.exceptions.ConnectionError:
        time.sleep(1)
else:
    print("Proxy did not start — check proxy.log")
```

Then point the tunnel from **Section 3** at port `8000` (already shown
above) — this means all public traffic now goes: `tunnel → proxy (checks
API key) → Ollama`.

**Test end-to-end with the key:**
```python
import requests

resp = requests.post(
    f"{url}/api/generate",
    headers={"Authorization": "Bearer <your-generated-api-key>"},
    json={"model": "gemma3n:e4b-it-q4_K_M", "prompt": "Hello", "stream": False}
)
print(resp.status_code)
print(resp.json())
```

---

## 5. Connecting the tunnel + model to the application script

The application uses the `ollama` Python library's `chat()` function,
which by default only talks to `localhost:11434` with no auth support.
To point it at the remote tunnel + proxy instead, swap the top-level
`ollama.chat()` call for a configured `ollama.Client` instance that
carries the host URL and the `Authorization` header.

### `.env` file

Create a `.env` file (keep it out of version control):
```
OLLAMA_HOST=https://cadillac-induction-developer-urw.trycloudflare.com
OLLAMA_API_KEY=<your-generated-api-key>
```

> ⚠️ **These values are session-specific.** The tunnel URL above was only
> valid while that particular Kaggle session and `cloudflared` process
> were running — it will go dead (502/DNS error) the moment the tunnel
> restarts or the session resets, which happens frequently (see
> "Known limitations" below). The API key stays valid as long as
> `proxy.py` on Kaggle isn't rewritten with a different `API_KEY` value.
> Treat both as values you'll need to refresh in this `.env` file each
> time you restart the Kaggle notebook, not as permanent config.

### `core/config.py` — load from `.env`

```python
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_MODEL = "gemma3n:e4b-it-q4_K_M"
```

(Requires `pip install python-dotenv` if not already installed.)

### Modified script (changes marked)

```python
from typing import Optional
import ollama
from ollama import Client          # <-- ADDED
from fastapi import HTTPException
from core import config

client = Client(                   # <-- ADDED: configured client instead of
    host=config.OLLAMA_HOST,       #     the bare `ollama` module, so we can
    headers={"Authorization": f"Bearer {config.OLLAMA_API_KEY}"},  # pass host + auth
)


def generate_guidance(
    text: Optional[str],
    images_b64: list[str],
    audio_transcript: Optional[str],
) -> str:

    content_parts = ["তুমি একজন অভিজ্ঞ ও দক্ষ পশু চিকিৎসক (ভেটেরিনারিয়ান), ..."]
    # (unchanged prompt content omitted here for brevity)

    if text:
        content_parts.append(text)
    if audio_transcript:
        content_parts.append(
            "[Audio transcript — note: this was transcribed from Bengali "
            "(Bangla) speech using automatic speech recognition, which "
            "sometimes mistakenly renders Bangla in Hindi wording/script "
            "due to phonetic similarity. Interpret the following as "
            f"Bengali speech and reply entirely in Bengali]: {audio_transcript}")
    content = "\n\n".join(content_parts)

    message = {"role": "user", "content": content}
    if images_b64:
        message["images"] = images_b64

    try:
        response = client.chat(model=config.OLLAMA_MODEL, messages=[message])  # <-- CHANGED: client.chat(...) instead of ollama.chat(...)
    except ollama.ResponseError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=f"এই মুহূর্তে AI সাহায্য করতে পারছে না। বিকল্প উপায় দেখুন বা আবার চেষ্টা করুন।\n{str(e)}")
    except ollama.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI পর্যন্ত কল যায়নি। বিকল্প উপায় দেখুন।\n{str(e)}")
    return response["message"]["content"]
```

**Summary of changes:**
1. Added `from ollama import Client` and instantiated it once at module
   level with `host=` (the tunnel URL) and `headers=` (the API key).
2. Replaced `ollama.chat(...)` with `client.chat(...)`.
3. `config.py` now loads `OLLAMA_HOST` and `OLLAMA_API_KEY` from a `.env`
   file via `python-dotenv`, instead of hardcoding them.
4. `import ollama` is kept alongside `from ollama import Client` because
   `ollama.ResponseError` / `ollama.RequestError` are still referenced in
   the exception handlers.

**Remember:** every time the Kaggle session or tunnel restarts, the
tunnel URL changes — update `OLLAMA_HOST` in `.env` accordingly. The API
key only needs to change if you regenerate/rewrite `proxy.py`.

---

## Known limitations of this setup

- **Session fragility:** Kaggle notebooks can disconnect from idle
  timeouts, background-tab throttling, laptop sleep, or weekly GPU quota
  limits — wiping Ollama, the model, and the tunnel each time.
- **Ephemeral URL:** the free Cloudflare quick tunnel issues a new random
  URL on every restart; there's no fixed address without a paid/named
  tunnel setup.
- **Single point of concurrency:** Ollama defaults to `OLLAMA_NUM_PARALLEL=1`,
  so concurrent requests from multiple users will queue rather than run
  in parallel.
- **Recommended next step for production:** move off Kaggle to a
  persistent host (e.g. an always-on VM or a managed GPU inference
  service) to eliminate session resets and get a stable URL.
