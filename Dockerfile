# =============================================================================
# G777 SAAF Backend - Production Dockerfile
# Base: python:3.12-slim | Includes: Chrome (headless), RTK, Python deps
# =============================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# =============================================================================
# RTK Integration - Token Optimization (must precede app install)
# WHY: RTK is a shell-level proxy; must be in PATH before any RUN commands
#      that invoke shell tools in later build stages.
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"
ENV RTK_TELEMETRY_DISABLED=1

# Verify RTK binary is available
RUN rtk --version

# =============================================================================
# Google Chrome + System Dependencies Layer
# WHY: Required by:
#   1. undetected-chromedriver (WhatsApp Web automation)
#   2. Scrapling's StealthyFetcher/DynamicFetcher (Playwright backend)
#   3. browser-use AI Agent (Playwright-based AI browser automation)
#      Without this layer, all Grabber, Social Extractor, and AI
#      Self-Healing tools will crash at runtime.
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    libmagic1 \
    gnupg \
    ca-certificates \
    # Core Chrome runtime dependencies (shared by Chrome, Playwright, browser-use)
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libasound2 \
    libxshmfence1 \
    # Required for undetected-chromedriver subprocess management
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome official repository and install stable version
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && google-chrome --version

# Set Chrome binary path for undetected-chromedriver auto-detection
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# =============================================================================
# Python Dependencies
# =============================================================================
COPY requirements.txt .
# Install Python dependencies (includes browser-use + langchain-google-genai)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "scrapling[all]"

# WHY: || true is forbidden here (SAAF Clean Code Oath).
# If playwright install fails, the build MUST fail — a container with a
# broken browser is worse than no container (it crashes silently at runtime).
# NOTE: This also satisfies browser-use's Playwright requirement.
RUN python -m playwright install chromium --with-deps

# =============================================================================
# Application Code
# =============================================================================
COPY . .

# Persistent storage directories (mapped to Docker volumes in compose)
RUN mkdir -p /app/data /app/chrome_profile /app/auth_info

# Expose FastAPI default port
EXPOSE 8000

# Health check: ensures the API is responsive before routing traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

# WHY: main.py in dev mode binds to settings.network.host which may be
# 127.0.0.1 (loopback only). Inside Docker, other containers CANNOT
# reach 127.0.0.1 — they need 0.0.0.0 (all interfaces).
# Using uvicorn directly gives us explicit control over host binding.
# The app import path is confirmed from main.py: app = FastAPI(...) at module level.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
