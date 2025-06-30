import os
import pandas as pd
from time import sleep
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

def coletar_taxa_moeda_para_brl(moeda_destino: str) -> float:
    driver = configurar_driver()
    url = "https://br.investing.com/currencies/exchange-rates-table"
    driver.get(url)
    sleep(5)
    taxa = None
    try:
        tabela = driver.find_element(By.ID, "exchange_rates_1")
        linhas = tabela.find_elements(By.TAG_NAME, "tr")
        for i, linha in enumerate(linhas[1:]):
            colunas = linha.find_elements(By.TAG_NAME, "td")
            if not colunas:
                continue
            codigo = colunas[0].text.strip()
            if codigo == moeda_destino.upper():
                taxa_str = colunas[1].text.strip().replace(",", ".")
                taxa = float(taxa_str)
                break
    except Exception as e:
        print(f"Erro ao coletar taxa: {e}")
    driver.quit()
    if taxa is None:
        raise ValueError(f"Moeda '{moeda_destino}' não encontrada.")
    print(f"✅ Cotação {moeda_destino.upper()} para BRL: {taxa}")
    return taxa

def ler_todos_os_meses():
    arquivos = ['Janeiro.xlsx', 'Fevereiro.xlsx', 'Marco.xlsx']
    pasta = 'data'
    dfs = []
    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        if os.path.exists(caminho):
            df = pd.read_excel(caminho)
            df['mes'] = arquivo.replace('.xlsx', '')
            dfs.append(df)
        else:
            print(f"⚠️ Arquivo {caminho} não encontrado.")
    if not dfs:
        raise FileNotFoundError("Nenhum arquivo encontrado.")
    return pd.concat(dfs, ignore_index=True)

def gerar_planilha_final(df_consolidado: pd.DataFrame):
    colunas_valores = ['Valor1', 'Valor2', 'Valor3', 'Valor4']
    df_consolidado['Total_Mes'] = df_consolidado[colunas_valores].sum(axis=1)

    df_trimestre = df_consolidado.groupby('Cidade')['Total_Mes'].sum().reset_index()
    df_trimestre.rename(columns={'Total_Mes': 'Total_Trimestre'}, inplace=True)

    os.makedirs("data", exist_ok=True)
    caminho = "data/planilha_final_trimestre.xlsx"
    df_trimestre.to_excel(caminho, index=False)
    print(f"✅ Planilha consolidada: {caminho}")
    return df_trimestre

def gerar_planilha_convertida(moeda_destino: str, df_original: pd.DataFrame):
    taxa = coletar_taxa_moeda_para_brl(moeda_destino)
    df_convertido = df_original.copy()
    df_convertido["Total_Convertido"] = df_convertido["Total_Trimestre"] * taxa

    taxa_str = str(round(taxa, 4)).replace('.', '_')
    nome_arquivo = f"data/planilha_final_trimestre_{moeda_destino.upper()}_{taxa_str}.xlsx"
    df_convertido.to_excel(nome_arquivo, index=False)

    print(f"📁 Planilha convertida salva: {nome_arquivo}")
    return nome_arquivo

def main():
    df_mes = ler_todos_os_meses()
    df_trimestre = gerar_planilha_final(df_mes)

    enviar_planilha_telegram("data/planilha_final_trimestre.xlsx")

    # exemplo com moeda USD
    moeda = "EUR"
    caminho_convertido = gerar_planilha_convertida(moeda, df_trimestre)
    enviar_planilha_telegram(caminho_convertido)

if __name__ == "__main__":
    main()
