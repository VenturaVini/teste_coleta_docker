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

def coletar_tabela_bc():
    driver = configurar_driver()
    url = "https://www.bcb.gov.br/controleinflacao/historicocotacao"
    driver.get(url)
    sleep(3)  # espera a página carregar

    try:
        tabela = driver.find_element(By.CSS_SELECTOR, "table")  # primeira tabela da página
        linhas = tabela.find_elements(By.TAG_NAME, "tr")
        dados = []
        for linha in linhas:
            cols = linha.find_elements(By.TAG_NAME, "td")
            if cols:
                dados.append([col.text for col in cols])
    except Exception as e:
        print(f"Erro ao coletar tabela: {e}")
        dados = []
    driver.quit()

    df = pd.DataFrame(dados)
    df['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    caminho = "data/historico_precos.xlsx"
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_excel(caminho, index=False)  # **sobrescreve o arquivo toda vez**

    print(f"Dados salvos em {caminho}")
    return df

def analisar_precos(caminho: str = "data/historico_precos.xlsx"):
    if not os.path.exists(caminho):
        print("Nenhum dado para analisar.")
        return
    df = pd.read_excel(caminho)
    print("\n📊 Análise de dados coletados:")
    print(df.describe())

def main():
    df = coletar_tabela_bc()
    analisar_precos()

if __name__ == "__main__":
    main()
    sleep(3)
    enviar_planilha_telegram("data/historico_precos.xlsx")
