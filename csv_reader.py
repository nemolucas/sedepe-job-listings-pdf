import os
import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Frame, PageTemplate, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# Ler o .csv
def ler_csv(arquivo_csv):
    data_columns = ["Posto", "Ocupação", "Qtd. Vagas Disponíveis", "Município Local de Trabalho", "Forma de Contratação", "Salário", "Frequência de Pagamento", "Escolaridade", "Tempo de Experiência", "Aceita Deficientes"]
    csv_files = [file for file in os.listdir() if file.endswith(".csv")]
    dfs = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, sep=';', usecols=data_columns, encoding='latin1')
        dfs.append(df)

    return dfs


# Limitar a quantidade de caracteres
def limitar_texto(texto, limite):
    return texto[:35]


def formatar_posto(posto):
    posto = posto.replace('Sine', '').strip()
    if posto.endswith('/Pe'):
        posto = posto[:-3].strip()
    return posto

def abreviar_posto(posto):
    abreviacoes = {
        "Cabo de Santo Agostinho": "Cabo de Santo A.",
        "Nazare da Mata": "Nazaré da Mata",
        "Igarassu": "Igarassu",
        "Vitoria de Santo Antao": "Vitória de S. Antão",
        "Santa Cruz do Capibaribe": "Santa Cruz do C."
    }
    return abreviacoes.get(posto, posto).replace('Sine', '').strip()


# Formatar a coluna 'Município'
def formatar_municipio(municipio):
    return limitar_texto(municipio.replace("PE-", ""), 30)

def abreviar_municipio(municipio):
    abreviacoes = {
        "Cabo de Santo Agostinho": "Cabo de Santo A.",
        "Nazare da Mata": "Nazaré da Mata",
        "Igarassu": "Igarassu",
        "Vitoria de Santo Antao": "Vitória de S. Antão",
        "Santa Cruz do Capibaribe": "Santa Cruz do C.",
        "Jaboatão dos Guararapes": "Jaboatão dos G."
    }
    return abreviacoes.get(municipio, municipio)


def formatar_escolaridade(valor):
    valor = valor.replace(" Completo", "").replace(" Incompleto", " n/C")
    return valor


# Formatar a coluna 'Tempo de Experiência'
def formatar_experiencia(valor):
    try:
        valor_inteiro = int(float(valor)) 
        if valor_inteiro == 0:
            return "Não Exigida"
        else:
            return f"{valor_inteiro} Meses"
    except ValueError:
        return "Não Exigida"
    

def formatar_pcds(valor):
    if valor == "Aceita deficiente":
        return None
    elif valor == "Exclusivamente deficiente":
        return "Exclusivo para PCDs"
    
    else:
        return valor
    
total_vagas = 0 

# Criar o PDF 
def criar_pdf(dados, nome_pdf):
    global total_vagas
    doc = SimpleDocTemplate(nome_pdf, pagesize=landscape(letter), rightMargin=30, leftMargin=30)
    table_data = (dados.values.tolist())

    table = Table(table_data)

    # Ajustar as dimensões das células
    col_widths = [90, 40, 190, 135, 75, 80, 100, 65, 0]  
    row_height = 25

    # Formatações na tabela
    for row in table_data:
        row[0] = formatar_posto(row[0])
        row[0] = abreviar_posto(row[0])
        row[2] = limitar_texto(str(row[2]), 35)
        row[3] = formatar_municipio(row[3])
        row[3] = abreviar_municipio(row[3])

        salario = row[5]
        frequencia = row[6]

        if salario == "0" or salario == "0.0":
            salario_frequencia = "Não informado"
        else:
            if frequencia != "Não informado":
                salario_frequencia = f"{salario} - {frequencia}"
            else:
                salario_frequencia = salario

        row[5] = salario_frequencia
        row[6] = formatar_escolaridade(row[7])
        row[7] = formatar_experiencia(row[8])
        row[8] = None
        row[9] = None

    table = Table(table_data, colWidths=col_widths, rowHeights=row_height, repeatRows=1)

    # Definição de estilos para títulos e conteúdo
    obs_style = getSampleStyleSheet()["Heading1"]
    obs_style.fontName = 'Helvetica-Bold'
    obs_style.fontSize = 12
    obs_style.textColor = colors.red
    obs_style.alignment = 1
    obs_style.spaceAfter = 12

    title_style = getSampleStyleSheet()["Normal"]  
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 10
    title_style.alignment = 1

    table.setStyle(TableStyle([
        # Estilo para a primeira linha (títulos das colunas)
        ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), title_style.fontName),
        ('FONTSIZE', (0, 0), (-1, 0), title_style.fontSize),
    ]))

    table_parts = []
    max_rows_per_page = 12
    
    # Ordenar os dados pelo valor da coluna "Posto"
    table_data.sort(key=lambda x: (x[0][0].upper(), x[0]))  
    
    # Agrupar os dados pelo valor da coluna "Posto"
    grupos = {}
    for row in table_data:
        posto = row[0]
        if posto not in grupos:
            grupos[posto] = []
        grupos[posto].append(row)

    for posto, grupo_data in grupos.items():
        current_page_rows = []

        # Adicionar a imagem no início da página
        img_path = "governo-copia.png"
        img = Image(img_path, width=400, height=80)

        for row in grupo_data:

            if len(current_page_rows) >= max_rows_per_page:
                    # Criar uma nova página com as vagas do posto anterior
                    adicionar_quebra_pagina = True  # Adicionar quebra de página por padrão
                    if len(current_page_rows) < max_rows_per_page and grupo_data.index(row) == len(grupo_data) - 1:
                        adicionar_quebra_pagina = False  # Não adicionar quebra de página se for a última vaga e não completou a página
                    if adicionar_quebra_pagina:
                        # Adicionar linha de observação no topo da nova página
                        obs_line = Paragraph("Obs: Vagas sujeitas a alterações no decorrer do dia.", obs_style)
                        table_parts.append(obs_line)
                        table_part = current_page_rows
                        style = TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('FONTNAME', (0, 0), (-1, 0), title_style.fontName),
                                    ('FONTSIZE', (0, 0), (-1, 0), title_style.fontSize),
                                ])
                        table_part_obj = Table(table_part, colWidths=col_widths, rowHeights=row_height)
                        table_part_obj.setStyle(style)
                        table_parts.append(table_part_obj)
                        table_parts.append(PageBreak())
                        current_page_rows = []
            
            if not current_page_rows:  # Adicionar cabeçalho na primeira linha da página
                table_parts.append(img)
                nomes_colunas = ["Agência", "Vagas", "Descrição", "Local de Trabalho", "Contrato", "Salário", "Escolaridade", "Experiência"]
                current_page_rows.append(nomes_colunas)
            current_page_rows.append(row)
        
        if current_page_rows:  # Adicionar linha de observação no topo da nova página
            obs_line = Paragraph("Obs: Vagas sujeitas a alterações no decorrer do dia.", obs_style)
            table_parts.append(obs_line)

            table_part = current_page_rows
            style = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, 0), title_style.fontName),
                                ('FONTSIZE', (0, 0), (-1, 0), title_style.fontSize),
                            ])
            table_part_obj = Table(table_part, colWidths=col_widths, rowHeights=row_height)
            table_part_obj.setStyle(style)
            table_parts.append(table_part_obj)
            if posto != list(grupos.keys())[-1]:
                table_parts.append(PageBreak())

    paragrafo_total_vagas = Paragraph(f"Total de Vagas: {total_vagas}", obs_style)
    table_parts.append(paragrafo_total_vagas)

    
    doc.build(table_parts)


# Criação da pasta de saída e leitura do .csv
if __name__ == "__main__":
    pasta_output = "output"

    if not os.path.exists(pasta_output):
        os.makedirs(pasta_output)

    # Obtém a lista de arquivos .csv na pasta do programa
    csv_files = [file for file in os.listdir() if file.endswith(".csv")]

    for csv_file in csv_files:
        lista_de_dataframes = ler_csv(csv_file)

        for df in lista_de_dataframes:
            df.sort_values(by='Posto', inplace=True)
            
            nome_pdf = os.path.join(pasta_output, os.path.splitext(csv_file)[0] + "_relatorio.pdf")

            try:
                criar_pdf(df, nome_pdf)
                print(f"Relatório gerado com sucesso: {nome_pdf}")
            except Exception as e:
                print(f"Erro ao gerar o relatório para {nome_pdf}: {e}")
                #Debug
                #print("Dados que causaram o erro:")
                #print(df)