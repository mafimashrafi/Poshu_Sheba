# Poshu Sheba AI — Frontend Integration Guide

## API base URL

During local development, use `http://127.0.0.1:8000`. The root URL returns:

```json
{"message": "Poshu Sheba AI API is running"}
```

Use `POST` for `/generate`; visiting it in the browser uses `GET` and correctly returns `405 Method Not Allowed`.

## Endpoint reference

### `POST /register`

Creates an account. Send JSON:

```json
{
  "name": "Optional name",
  "phone_number": "01712345678",
  "password": "at-least-8-characters"
}
```

Success (`201`):

```json
{"message": "User registered successfully", "user_id": "..."}
```

Show the API's error `detail` for invalid input (`422`) or an already-registered phone number (`409`).

### `POST /login`

Send JSON:

```json
{"phone_number": "01712345678", "password": "at-least-8-characters"}
```

Success (`200`):

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_at": "2026-..."
}
```

Keep the token for the current signed-in user and send it on every protected request:

```http
Authorization: Bearer <access_token>
```

Invalid credentials return `401` with `{"detail": "Invalid phone number or password"}`.

### `POST /generate`

This is the chat/generation endpoint. It accepts `multipart/form-data` with any one or more of these fields:

| Field | Type | Required | Use |
| --- | --- | --- | --- |
| `text` | text | No* | User's typed question |
| `images` | file, repeatable | No* | One or more animal/problem images |
| `audio` | file | No* | One audio recording in Bengali |

\*At least one field must be supplied. The request returns `400` otherwise.

Example:

```js
const form = new FormData();
form.append("text", userMessage);
selectedImages.forEach((image) => form.append("images", image));
if (audioFile) form.append("audio", audioFile);

const result = await fetch(`${API_URL}/generate`, {
  method: "POST",
  body: form,
});
const data = await result.json();
```

Do not manually set `Content-Type` for `FormData`; the browser adds the required boundary.

Success (`200`):

```json
{"response": "AI-generated Bengali veterinary guidance"}
```

Display `data.response` as the assistant's chat message. This endpoint does not require login.

### `POST /save-response`

Saves a generated response for the logged-in user. Send JSON and the bearer token:

```js
await fetch(`${API_URL}/save-response`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  },
  body: JSON.stringify({ response: generatedResponse }),
});
```

Success (`201`):

```json
{"message": "Response saved successfully", "response_id": "..."}
```

The `response` cannot be empty and has a maximum of 50,000 characters. If no token is available, show a login prompt instead of calling this endpoint.

### `GET /saved-responses`

Fetches only the logged-in user's saved responses. Send the bearer token:

```js
const result = await fetch(`${API_URL}/saved-responses`, {
  headers: { "Authorization": `Bearer ${token}` },
});
const data = await result.json();
```

Success (`200`):

```json
{
  "phone_number": "+8801712345678",
  "responses": [
    {
      "response_id": "...",
      "response": "Saved AI guidance",
      "created_at": "2026-..."
    }
  ]
}
```

Render the items in `data.responses`, most recent first. Each item has `response_id`, `response`, and `created_at`.

If the request returns `401`, clear the local login state and show a **Log in to view saved responses** button. Clicking it should open the login screen.

## Recommended user flow

```text
Ask question (+ optional image/audio) → POST /generate → show data.response
                                                     ↓
                              Signed in? ── no → show “Log in to save”
                                   ↓ yes
                     POST /save-response with bearer token

Saved responses page → token present? ── no → show “Log in to view saved responses”
                         ↓ yes
              GET /saved-responses with bearer token → render data.responses
```

## Handling errors

- Always parse the response body and show `data.detail` when a request fails.
- For `401` from protected routes, remove the stored token and redirect or offer login.
- For `/generate` errors (`502` or `503`), show a retry message; the AI service may be unavailable.
- If the frontend is hosted on a different domain or port, ask the backend developer to enable CORS before browser integration.
