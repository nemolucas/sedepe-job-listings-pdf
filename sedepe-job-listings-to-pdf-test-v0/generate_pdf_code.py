import os
import csv
import pandas as pd
import chardet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def detectar_codificacao(arquivo_csv):
    with open(arquivo_csv, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def ler_csv(arquivo_csv, codificacao):
    linhas = []
    with open(arquivo_csv, 'r', encoding=codificacao) as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if len(linha) == 5: 
                linhas.append(linha)

    colunas = ["C", "E", "H", "K", "P"]
    dataframe = pd.DataFrame(linhas, columns=colunas)
    return dataframe

def extrair_dados(dataframe, colunas):
    return dataframe[colunas]

def criar_pdf(dados, nome_pdf):
    doc = SimpleDocTemplate(nome_pdf, pagesize=letter)
    table_data = [dados.columns.to_list()] + dados.values.tolist()
    table = Table(table_data)

    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    doc.build([table])

if __name__ == "__main__":
    pasta_output = "output"

    if not os.path.exists(pasta_output):
        os.makedirs(pasta_output)

    arquivos_csv = [arquivo for arquivo in os.listdir() if arquivo.endswith(".csv")]

    for arquivo_csv in arquivos_csv:
        colunas = ["C", "E", "H", "K", "P"]  
        nomes_colunas = ["Vagas", "Ocupação", "Município", "Salário", "Escolaridade"]  
        nome_pdf = os.path.join(pasta_output, os.path.splitext(arquivo_csv)[0] + "_relatorio.pdf")

        try:
            codificacao = detectar_codificacao(arquivo_csv)
            dataframe = ler_csv(arquivo_csv, codificacao)
            dados = extrair_dados(dataframe, colunas)
            dados.columns = nomes_colunas  
            criar_pdf(dados, nome_pdf)
            print(f"Relatório gerado com sucesso: {nome_pdf}")
        except Exception as e:
            print(f"Erro ao gerar o relatório para {arquivo_csv}: {e}")
