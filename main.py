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

def coletar_preco_kabum(produto: str) -> dict:
    driver = configurar_driver()
    driver.get(f"https://www.kabum.com.br/busca/{produto.replace(' ', '%20')}")
    sleep(2)  # Aguarda o carregamento

    try:
        nome = driver.find_element(By.CSS_SELECTOR, ".sc-d79c9c3f-0").text
        preco = driver.find_element(By.CSS_SELECTOR, ".sc-3b515ca1-2").text
        preco = float(preco.replace('R$', '').replace('.', '').replace(',', '.').strip())
    except Exception as e:
        nome = "Produto não encontrado"
        preco = 0.0
        print(f"Erro ao coletar dados do Kabum: {e}")

    driver.quit()
    return {
        "produto": produto,
        "nome": nome,
        "preco": preco,
        "site": "Kabum",
        "data": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def salvar_dados_xlsx(dados: list[dict], caminho: str = "data/historico_precos.xlsx"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df_novo = pd.DataFrame(dados)

    if os.path.exists(caminho):
        df_existente = pd.read_excel(caminho)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    df_final.to_excel(caminho, index=False)

def analisar_precos(caminho: str = "data/historico_precos.xlsx"):
    if not os.path.exists(caminho):
        print("Nenhum dado para analisar.")
        return

    df = pd.read_excel(caminho)
    print("\n📊 Análise de preços:")
    print(df.groupby("produto")["preco"].describe())

def main():
    produtos = ["monitor", "notebook"]
    resultados = [coletar_preco_kabum(produto) for produto in produtos]
    salvar_dados_xlsx(resultados)
    analisar_precos()

if __name__ == "__main__":
    main()
    sleep(3)
    enviar_planilha_telegram("data/historico_precos.xlsx")
