# Use official Python slim image
FROM python:3.13-slim

# Avoid interactive prompts during installation
ARG DEBIAN_FRONTEND=noninteractive

# Install OS dependencies for Playwright
RUN apt-get update -q && \
    apt-get install -y -qq --no-install-recommends \
    xvfb \
    libxcomposite1 \
    libxdamage1 \
    libatk1.0-0 \
    libasound2 \
    libdbus-1-3 \
    libnspr4 \
    libgbm1 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libnss3 \
    libxfixes3 \
    libcairo2 \
    libpango-1.0-0 \
    curl \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy app source code
COPY . .

# Set DISPLAY for virtual framebuffer
ENV DISPLAY=:99

# Expose Flask port
EXPOSE 5000

# Start Flask app with virtual framebuffer
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & python tester.py"]
