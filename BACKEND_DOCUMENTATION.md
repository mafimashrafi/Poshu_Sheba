# Poshu Sheba AI — Backend Documentation

## Purpose

This FastAPI service accepts animal-health questions as text, images, or audio and returns an AI-generated Bengali response. It also provides account, login, and saved-response features.

## Run locally

1. Create a `.env` file in the repository root with `MONGODB_URI` and `MONGODB_DB`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the API from the `Backend` directory: `uvicorn main:app --reload`.
4. Open `http://127.0.0.1:8000/docs` for FastAPI's interactive API documentation.

The service verifies MongoDB connectivity on startup and requires the configured Ollama model (`gemma4:e4b-it-q4_K_M`) for `/generate`.

## Routes

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| GET | `/` | No | API status response |
| POST | `/register` | No | Create an account |
| POST | `/login` | No | Create a 30-day bearer-token session |
| POST | `/generate` | No | Generate veterinary guidance from text, images, or audio |
| POST | `/save-response` | Bearer token | Save a generated response for the logged-in user |
| GET | `/saved-responses` | Bearer token | Read the logged-in user's saved responses |

## Data and security behavior

- Passwords are stored as hashes, not plaintext.
- Phone numbers are normalized to the `+8801XXXXXXXXX` format. Accepted input formats include `01...`, `8801...`, and `+8801...`.
- Session tokens are returned once by `/login`; only their hashes are stored in MongoDB.
- A session expires after 30 days. Expired sessions cause protected routes to return `401`.
- `/generate` accepts `multipart/form-data`, not JSON, because it supports file uploads.

## Main error responses

| Status | Meaning |
| --- | --- |
| 400 | `/generate` was called without text, images, or audio |
| 401 | Missing, invalid, or expired bearer token; or invalid login credentials |
| 409 | Phone number already registered |
| 422 | Request validation failed, such as an invalid phone number or short password |
| 502 / 503 | The AI service could not generate a response or could not be reached |

## Development notes

- The current API does not configure CORS. Add `CORSMiddleware` before deploying a frontend hosted on a different origin.
- Keep secret values in `.env`; do not commit them.
