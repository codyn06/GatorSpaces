# Use official Python image
FROM python:3.13-slim

# Avoid prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive

# Install necessary OS dependencies for Playwright
RUN apt-get update -q && \
    apt-get install -y --no-install-recommends \
    curl \
    wget \
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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy app source code
COPY . .

# Set DISPLAY for headless/virtual framebuffer
ENV DISPLAY=:99

# Expose port (for Flask)
EXPOSE 5000

# Start Flask app with virtual framebuffer
CMD Xvfb :99 -screen 0 1024x768x16 & python tester.py