# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# ---------------------------------------------------------------------------
# RTK Integration - Token Optimization (must precede app install)
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"
ENV RTK_TELEMETRY_DISABLED=1

# Verify RTK binary is available
RUN rtk --version

# ---------------------------------------------------------------------------
# Python Dependencies
# ---------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the main application
CMD ["python", "main.py"]
