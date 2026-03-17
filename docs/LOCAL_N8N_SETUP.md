# 🧠 Local n8n Setup Guide (G777)

This guide explains how to set up and run n8n locally for the G777 project, replacing the cloud-based instance.

## 📋 Prerequisites

- **Node.js**: Version 18+ installed.
- **n8n**: Installed globally via npm (`npm install -g n8n`) or available via `npx`.
- **PowerShell**: For running setup scripts.

## ⚙️ Configuration

The `.env` file has been automatically updated to point to the local instance:

```ini
N8N_WEBHOOK_URL=http://localhost:5678/webhook/dental-clinic-waha-prod
```

## 🚀 Setup Steps

### 1. Import Workflow (One-Time Setup)

We have prepared a script to import the **Production Workflow** and configure it for local use (patching cloud IPs to localhost).

Run the following command in PowerShell:

```powershell
./scripts/import_local_n8n.ps1
```

- **What this does**:
  - Patches `Al-Madar Al-Zahabi - Noura AI [PRODUCTION].json` to use local `Evolution API`.
  - Imports the workflow into your local n8n database.
  - Activates the workflow.

> **Note**: If n8n is running, you might see a warning to restart it.

### 2. Start n8n

To run n8n, simply run the batch file:

```cmd
start_n8n.bat
```

This will launch n8n at `http://localhost:5678`.

> **⚠️ IMPORTANT**: If you just ran the import script while n8n was running, you **MUST RESTART n8n** for the workflow activation to take effect.
> Close the n8n terminal window and run `start_n8n.bat` again.

### 3. Verify Connection

Once n8n is running and the workflow is active (check the dashboard), run the test script:

```cmd
python scripts/test_local_n8n_connection.py
```

- **Success**: `✅ Connection Successful! n8n received the payload.`
- **Failure**: `❌ Error 404...` -> Means workflow is not active or Webhook ID mismatch.

## 🐛 Troubleshooting

### "Webhook not found (404)"

1.  Go to n8n dashboard (`http://localhost:5678`).
2.  Find **"Al-Madar Al-Zahabi - Noura AI [PRODUCTION]"**.
3.  Ensure the toggle switch is **Green (Active)**.
    - id: `N21CHPDQBgNFbUIK`
4.  Open the workflow and check the **Webhook Node**.
    - Path should be: `dental-clinic-waha-prod`
    - Method: `POST`

### Evolution API Connection

The workflow now points to:
`http://localhost:8080/message/sendText/G777`
Ensure your Evolution API/WAHA service is running on port **8080**.
