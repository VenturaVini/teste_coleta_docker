FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgtk-3-0 \
    libasound2 libgbm1 libxshmfence1 libu2f-udev libvulkan1 \
    xdg-utils --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
