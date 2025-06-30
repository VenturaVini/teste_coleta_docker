import os
import pandas as pd
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from enviar_arquivo_telegram import enviar_planilha_telegram  # certifique-se que essa função está implementada

# === CONFIGURAR DRIVER ===
def configurar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path="/usr/local/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)

# === PARTE 1: Criar planilhas de Janeiro, Fevereiro e Março ===
def criar_planilhas_mensais():
    os.makedirs("data", exist_ok=True)
    cidades = ["Recife", "Manaus", "Rio de Janeiro", "Salvador"]

    meses = {
        "Janeiro": [[100, 200, 300, 250], [150, 180, 320, 270], [140, 190, 310, 260], [130, 185, 305, 255]],
        "Fevereiro": [[90, 210, 310, 240], [160, 175, 330, 280], [135, 200, 315, 265], [120, 195, 300, 250]],
        "Março": [[110, 220, 290, 260], [170, 185, 340, 290], [145, 205, 320, 270], [125, 200, 310, 260]]
    }

    for mes, valores in meses.items():
        df = pd.DataFrame(valores, columns=["Semana1", "Semana2", "Semana3", "Semana4"])
        df.insert(0, "Cidade", cidades)
        df.to_excel(f"data/{mes}.xlsx", index=False)

# === PARTE 2: Somar dados dos 3 meses ===
def gerar_resumo_trimestre():
    cidades = ["Recife", "Manaus", "Rio de Janeiro", "Salvador"]
    total_por_cidade = {cidade: 0 for cidade in cidades}

    for mes in ["Janeiro", "Fevereiro", "Março"]:
        caminho = f"data/{mes}.xlsx"
        df = pd.read_excel(caminho)
        for _, linha in df.iterrows():
            total = linha[1:].sum()
            total_por_cidade[linha["Cidade"]] += total

    df_final = pd.DataFrame([
        {"Cidade": cidade, "Total_Trimestre": total}
        for cidade, total in total_por_cidade.items()
    ])

    caminho_final = "data/planilha_final_trimestre.xlsx"
    df_final.to_excel(caminho_final, index=False)
    print(f"✅ Planilha consolidada criada: {caminho_final}")
    return caminho_final, df_final

# === PARTE 3: Obter taxa de câmbio e converter valores ===
def coletar_taxa_moeda_para_brl(moeda_destino: str) -> float:
    driver = configurar_driver()
    url = "https://br.investing.com/currencies/exchange-rates-table"
    driver.get(url)
    sleep(5)

    taxa = None
    try:
        tabela = driver.find_element(By.ID, "exchange_rates_1")
        linhas = tabela.find_elements(By.TAG_NAME, "tr")

        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, "td")
            if colunas and colunas[0].text.strip() == moeda_destino.upper():
                taxa = float(colunas[1].text.strip().replace(',', '.'))
                break
    except Exception as e:
        print(f"Erro ao buscar taxa: {e}")
    finally:
        driver.quit()

    if taxa is None:
        raise ValueError(f"Moeda '{moeda_destino}' não encontrada.")
    
    return taxa

# === PARTE FINAL: Converter e salvar nova planilha ===
def gerar_planilha_convertida(moeda_destino: str, df_original: pd.DataFrame):
    taxa = coletar_taxa_moeda_para_brl(moeda_destino)
    df_convertido = df_original.copy()
    df_convertido["Total_Convertido"] = df_convertido["Total_Trimestre"] * taxa

    # Arredonda a taxa para 2 casas e substitui ponto por "_" para não dar erro em nome de arquivo
    taxa_str = str(round(taxa, 4)).replace('.', '_')
    nome_arquivo = f"data/planilha_final_trimestre_{moeda_destino.upper()}_{taxa_str}.xlsx"

    df_convertido.to_excel(nome_arquivo, index=False)
    print(f"📁 Planilha convertida salva: {nome_arquivo}")
    return nome_arquivo

# === EXECUÇÃO ===
def main():
    criar_planilhas_mensais()
    caminho_final, df_final = gerar_resumo_trimestre()
    enviar_planilha_telegram(caminho_final)

    # Se quiser gerar em USD, por exemplo
    moeda_destino = "USD"
    caminho_convertido = gerar_planilha_convertida(moeda_destino, df_final)
    enviar_planilha_telegram(caminho_convertido)

if __name__ == "__main__":
    main()
