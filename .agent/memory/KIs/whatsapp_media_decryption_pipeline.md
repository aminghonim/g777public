# Knowledge Item (KI): WhatsApp Media Decryption Pipeline

> **Purpose:** Document the stable architecture for downloading and analyzing WhatsApp media (images/videos) via n8n and Gemini.

## Metadata

- **KI-ID:** `KI-WHATSAPP-MEDIA-001`
- **Component:** `WhatsApp Pipeline (n8n + Baileys Bridge + Gemini)`
- **Date Added:** `2026-03-14`
- **Associated Skill:** `N/A`

---

## 💥 The Problem / Symptom

1. **401 Unauthorized**: n8n nodes failed to download media because the request passed through the `g777_backend` middleware, which required a valid Clerk/Auth Token.
2. **404 Not Found**: The Baileys Bridge container did not have a `/download` endpoint to handle decryption requests.
3. **AI Logic Error (Veo)**: Gemini nodes in n8n were attempting to use the "Veo" model (video generation) instead of analyzing the incoming video file.

## 🔍 Root Cause Analysis (The "Why")

- **Architectural Overhead**: Using the main backend as a proxy for internal service-to-service media traffic introduced authentication complexity that wasn't needed inside the Docker network.
- **Bridge Limitation**: The original `baileys-service` was designed only for sending messages, not for intercepting and decrypting encrypted media attachments from WhatsApp.
- **n8n Operation Mismatch**: The Gemini node was configured with the "Generate Video" operation, which triggers specialized generative models (Veo) rather than the Multimodal capabilities of Gemini 2.5 Flash for comprehension.

## ✅ The Solution / Workaround

1. **Internal Bypassing**: Configured n8n to call the Baileys Bridge directly (`http://baileys_bridge:3000/download`) instead of going through `g777_backend`.
2. **Surgical Route Injection**: Added a `/download` POST route to `baileys-service/server.js`. This route uses `downloadMediaMessage` from `@whiskeysockets/baileys` to decrypt the media and return it to n8n.
3. **Task Redefinition**: Changed the Gemini node "Operation" in n8n to **Multimodal Chat** (or **Analyze**). Set **Input Type** to **Binary File** to pass the decrypted media buffer directly to the model.
4. **Quoted Media Support**: Added logic to handle media sent as a reply (Quoted Messages). Updated `baileys-service` to automatically extract media from the `quotedMessage` context.

## 🚫 What NOT to Do (Anti-Patterns)

1. **Internal Auth Walls**: Do NOT route internal media downloads through the public-facing backend middleware. It adds latency and auth failures.
2. **Generative vs. Analytical**: Do NOT use "Generate" operations in n8n when the goal is to "See" or "Read" content. This leads to model mismatch errors.
3. **Decryption Responsibility**: Do NOT try to decrypt WhatsApp media inside n8n nodes. The Baileys session (keys/tokens) resides in the bridge; let the bridge handle the decryption.

---

## Associated Skill Recommendation
Consider creating an n8n template or a custom node specifically for "Baileys Decrypted Download" to standardize this across all workflows.

---

## 🔮 Future-Proofing (التأمين للمستقبل)

1. **Config Separation Rule (فصل التكوين)**: 
   - **Current State:** API keys and handshake tokens (like `G777_HANDSHAKE_TOKEN`) might be hardcoded in scripts or n8n parameters.
   - **Future Requirement:** Move all secrets completely into `.env` files. Both n8n and `baileys-service` must read these from environment variables. This enables seamless key rotation without modifying the source code or workflow UI.
2. **Resource Management (إدارة الموارد)**: 
   - **Current State:** The system is now analyzing large video blobs.
   - **Future Requirement:** Because video processing heavily taxes RAM and fast storage (in `baileys_bridge` and `n8n`), we must set up monitoring for Docker Container Health. Additionally, we need to implement an automated **Cleanup Script** to periodically wipe temporary media files so the host disk does not run out of space.
