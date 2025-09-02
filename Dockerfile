FROM python:3.10-slim

USER root

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates unzip \
    firefox-esr \
    libglib2.0-0 libnss3 libfontconfig1 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libxss1 libxtst6 libxext6 libxrender1 libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Instalar GeckoDriver (Firefox)
RUN GECKODRIVER_VERSION="v0.34.0" && \
    wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux-aarch64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Instalar pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
WORKDIR /app
COPY . .

# Comando padrão
CMD ["python", "main.py"]
