FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Baixa e instala o GeckoDriver
RUN GECKO_VERSION=v0.33.0 && \
    wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz && \
    tar -xzf geckodriver-$GECKO_VERSION-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-$GECKO_VERSION-linux64.tar.gz && \
    chmod +x /usr/local/bin/geckodriver

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "main.py"]
