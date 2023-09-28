import os
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph, Spacer, Image

def ler_csv(arquivo_csv):
    colunas_desejadas = ["Posto", "Qtd. Vagas Disponíveis", "Ocupação", "Município Local de Trabalho", "Salário", "Escolaridade", "Tempo de Experiência"]
    return pd.read_csv(arquivo_csv, sep=';', usecols=colunas_desejadas, encoding='latin1')

def formatar_experiencia(valor):
    valor_inteiro = int(float(valor)) 
    if valor_inteiro == 0:
        return "Não Exigida"
    else:
        return f"{valor_inteiro} Meses"

def formatar_salario(valor):
    if valor == "0":
        return "Não informado"
    else:
        return valor

def limitar_texto(texto, limite):
    return texto[:32]


def remover_sine_pe(posto):
    postos_a_manter = ["Sine Santa Cruz do Capibaribe/Pe", "Sine Cabo de Santo Agostinho/Pe", "Sine Nazare da Mata/Pe"]
    
    if posto not in postos_a_manter:
        posto = posto.replace("Sine", "").replace("/Pe", "").strip()
    return posto


def formatar_municipio(municipio):
    return limitar_texto(municipio.replace("PE-", ""), 30)

def criar_pdf(dados, nome_pdf):
    doc = SimpleDocTemplate(nome_pdf, pagesize=landscape(letter), rightMargin=30, leftMargin=30)
    table_data = dados.values.tolist()
    
    col_widths = [130, 40, 175, 150, 80, 120, 75]  
    row_height = 25 
    
    for row in table_data:
        row[0] = remover_sine_pe(row[0])
        row[1] = limitar_texto(str(row[1]), 100)  
        row[2] = limitar_texto(str(row[2]), 45)  
        row[3] = formatar_municipio(row[3])
        row[4] = formatar_salario(row[4])
        row[5] = limitar_texto(str(row[5]), 120)  
        row[6] = formatar_experiencia(row[6])
    
    table_parts = []
    max_rows_per_page = 14  
    num_rows = len(table_data)
    
    table_data.sort(key=lambda x: (x[0][0].upper(), x[0]))  
    
    grupos = {}
    for row in table_data:
        posto = row[0]
        if posto not in grupos:
            grupos[posto] = []
        grupos[posto].append(row)
    
    
    for posto, grupo_data in grupos.items():
        current_page_rows = []
        img_path = "governo-copia.png"  
        img = Image(img_path, width=400, height=80)

        has_content = False

        for row in grupo_data:
            if row[0] == "-":
                continue 

            has_content = True

            if len(current_page_rows) >= max_rows_per_page:
                    adicionar_quebra_pagina = True  
                    if len(current_page_rows) < max_rows_per_page and grupo_data.index(row) == len(grupo_data) - 1:
                        adicionar_quebra_pagina = False  
                    if adicionar_quebra_pagina:
                        obs_line = ['Obs: Vagas sujeitas a alterações no decorrer do dia.', '', '', '', '', '', '']
                        styles = getSampleStyleSheet()
                        bold_style = styles['Normal']
                        bold_style.fontName = 'Helvetica-Bold'
                        table_parts.append(Table([obs_line], colWidths=col_widths, rowHeights=row_height, hAlign='CENTER'))

                        table_part = current_page_rows
                        style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),  
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        table_part_obj = Table(table_part, colWidths=col_widths, rowHeights=row_height)
                        table_part_obj.setStyle(style)
                        table_parts.append(table_part_obj)
                        table_parts.append(PageBreak())
                        current_page_rows = []
            
            if not current_page_rows:  
                table_parts.append(img)
                nomes_colunas = ["Agência", "Vagas", "Ocupação", "Local de Trabalho", "Salário", "Escolaridade", "Experiência"]
                current_page_rows.append(nomes_colunas)
            current_page_rows.append(row)
        
        if current_page_rows:
            obs_line = ['Obs: Vagas sujeitas a alterações no decorrer do dia.', '', '', '', '', '', '']
            table_parts.append(Table([obs_line], colWidths=col_widths, rowHeights=row_height, hAlign='CENTER'))

            
            table_part = current_page_rows
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),  
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table_part_obj = Table(table_part, colWidths=col_widths, rowHeights=row_height)
            table_part_obj.setStyle(style)
            table_parts.append(table_part_obj)
            if posto != list(grupos.keys())[-1]:
                table_parts.append(PageBreak())
    
    doc.build(table_parts)

if __name__ == "__main__":
    pasta_output = "output"

    if not os.path.exists(pasta_output):
        os.makedirs(pasta_output)

    arquivos_csv = [arquivo for arquivo in os.listdir() if arquivo.endswith(".csv")]

    for arquivo_csv in arquivos_csv:
        nome_pdf = os.path.join(pasta_output, os.path.splitext(arquivo_csv)[0] + "_relatorio.pdf")

        try:
            dataframe = ler_csv(arquivo_csv)
            
            dataframe = dataframe.sort_values(by=["Posto"], key=lambda x: x.str.casefold())
            
            criar_pdf(dataframe, nome_pdf)
            print(f"Relatório gerado com sucesso: {nome_pdf}")
        except Exception as e:
            print(f"Erro ao gerar o relatório para {arquivo_csv}: {e}")
