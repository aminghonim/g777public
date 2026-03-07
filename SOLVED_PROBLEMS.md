# Solved Problems Log

## 1. Empty Response for Audio Messages (N8N Workflow)

**Date:** 2026-02-11
**Status:** ✅ Solved

### Issue

When a user sends an audio message, the AI bot in N8N responds with a generic fallback message ("عايز تعرف عن إيه بالظبط؟") instead of transcribing the audio and answering based on its content.

### Root Cause

1. **Payload Mismatch:** The Python backend was forwarding data inside a `body` object, while the N8N AI Agent prompt was looking for `$json.message` (which was undefined).
2. **Data Structure Mismatch:** The Google Gemini node (used for transcription) outputs data in a nested structure: `content.parts[0].text`. The AI Agent prompt was attempting to read from `json.text`, which did not exist on that node's output.

### Solution (Surgical Fix)

Updated the AI Agent node's prompt to use the correct data paths:

- **Audio path:** Changed `$("Transcribe a recording2").first().json.text` to `$("Transcribe a recording2").first().json.content.parts[0].text`.
- **Text path:** Changed `$json.message` to `$json.body.message` to align with the backend's forwarding structure.

---

## 2. Double Bot Replies (Python vs N8N)

**Date:** 2026-02-11
**Status:** ✅ Solved

### Issue

The bot was sending two replies: one long/robotic message from the Python backend and one from N8N.

### Root Cause

Both the Python backend and N8N were configured to process the same webhook and generate AI responses independently.

### Solution

Implemented a "**One Brain**" architecture:

1. Disabled AI response generation in the Python backend (`webhook_handler.py`).
2. Enabled active forwarding to N8N as the primary brain.
3. Updated `deploy.ps1` to ensure `trips_db.json` and `docker-compose.yaml` are correctly synced to the server with proper volumes.

---

## 3. Gemini API Connection Failure (Proxy & API Key)

**Date:** 2026-02-12
**Status:** ✅ Solved

### Issue

The system failed to connect to Gemini AI through the Antigravity Proxy, returning "API key not valid" errors and "Handshake failed" SSL errors when using the old SDK.

### Root Cause

1. **Invalid API Key:** The key in `الـ Secrets الكاملة.txt` starting with `AIzaSyA9Tu...` was no longer valid.
2. **SDK Deprecation:** The `google.generativeai` package is deprecated. Switching to the new `google-genai` SDK required a different approach for proxy configuration.
3. **Configuration Endpoint Mismatch:** The initial attempt to set the proxy endpoint via `client_options` failed in the new SDK because it expects either a direct `api_endpoint` parameter in the client or a specific environment variable.

### Solution (Surgical Fix)

1. **Key Replacement:** Identified and verified a working API key: `AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g`.
2. **Environment Configuration:** Set `os.environ["GOOGLE_GENAI_API_ENDPOINT"] = "http://127.0.0.1:8045"` to route all SDK traffic through the local proxy.
3. **Client Optimization:** Initialized the client using:
   ```python
   client = genai.Client(api_key="...", vertex=False)
   ```
   ```

   ```
4. **Verification:** Success confirmed via `test_gemini_via_proxy_stable.py` with a 200 OK response from the proxy and a valid AI response.

---

## 4. Guest Trial Authentication Loop (SAAS-017)

**Date:** 2026-02-22
**Status:** ✅ Solved

### Issue

Users clicking "Continue As Guest" were granted local UI access, but subsequent API calls failed with `401 Unauthorized` because they lacked a valid JWT. The `Dio` interceptor interpreted this as an expired session, forcing a logout loop back to the activation screen.

### Root Cause & Pipeline Analysis

The frontend (`auth_provider.dart`) was faking the session locally without informing the backend. The backend APIs inherently expect a `user_id` and `instance_name` for isolated queries (as per Rule 11).

### Solution (Surgical Fix)

1. **Backend (`routers/license.py`):** Created a `/guest` endpoint that generates a real JWT token with a `guest` role and a null-equivalent UUID (`00000000-0000-0000-0000-000000000000`) for the `user_id` to bypass PostgreSQL type casting errors while maintaining query isolation.
2. **Frontend State (`auth_provider.dart`):** Updated `AuthGuest` to hold the `token`. The `continueAsGuest` method now makes a real HTTP request to fetch and save this token.
3. **Network Interceptor (`dio_provider.dart`):** Updated to explicitly inject the `AuthGuest` token into the `Authorization` header, and resolved a race condition by `await`ing the Future of `authProvider`.
