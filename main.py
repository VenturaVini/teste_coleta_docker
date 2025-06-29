import os
from time import sleep
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from enviar_arquivo_telegram import enviar_planilha_telegram

def configurar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path="/usr/local/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)

def coletar_tabela_investing():
    driver = configurar_driver()
    url = "https://br.investing.com/currencies/exchange-rates-table"
    driver.get(url)
    sleep(5)  # Aguarda carregamento

    try:
        tabela = driver.find_element(By.ID, "exchange_rates_1")
        linhas_elementos = tabela.find_elements(By.TAG_NAME, "tr")

        dados = []
        for i, linha in enumerate(linhas_elementos):
            colunas = linha.find_elements(By.TAG_NAME, "th" if i == 0 else "td")
            dados.append([col.text.strip() for col in colunas])

    except Exception as e:
        print(f"❌ Erro ao coletar tabela: {e}")
        dados = []

    driver.quit()

    if len(dados) < 2:
        print("⚠️ Tabela não encontrada ou vazia.")
        return pd.DataFrame()

    # Primeira linha são os headers
    headers = dados[0]
    linhas = dados[1:]

    df = pd.DataFrame(linhas, columns=headers)
    df["data_coleta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    caminho = "data/historico_precos.xlsx"
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_excel(caminho, index=False)

    print(f"📄 Dados salvos em {caminho}")
    return df

def analisar_precos(caminho: str = "data/historico_precos.xlsx"):
    if not os.path.exists(caminho):
        print("Nenhum dado para analisar.")
        return
    df = pd.read_excel(caminho)
    print("\n📊 Análise de dados coletados:")
    print(df.describe(include='all'))

def main():
    df = coletar_tabela_investing()
    if not df.empty:
        analisar_precos()

if __name__ == "__main__":
    main()
    sleep(3)
    enviar_planilha_telegram("data/historico_precos.xlsx")
