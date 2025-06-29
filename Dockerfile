FROM python:3.10-slim

# Instalar dependências para o Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome estável
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
