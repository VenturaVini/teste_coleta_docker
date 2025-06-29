FROM python:3.10-slim

# Instalar dependências para o Firefox
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libdbus-glib-1-2 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxt6 \
    libxrender1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxdamage1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatspi2.0-0 \
    libnss3 \
    libxrandr2 \
    libxss1 \
    libgconf-2-4 \
    libgbm1 \
    libxfixes3 \
    libxshmfence1 \
    libdrm2 \
    && rm -rf /var/lib/apt/lists/*

# Baixar e instalar geckodriver
RUN GECKO_VERSION=v0.33.0 && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz" -O /tmp/geckodriver.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
