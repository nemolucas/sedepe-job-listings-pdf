import os
import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def ler_csv(arquivo_csv):
    data_columns = ["Posto", "Ocupação", "Qtd. Vagas Disponíveis", "Município Local de Trabalho", "Forma de Contratação", "Salário", "Frequência de Pagamento", "Escolaridade", "Tempo de Experiência", "Aceita Deficientes"]
    csv_files = [file for file in os.listdir() if file.endswith(".csv")]
    dfs = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, sep=';', usecols=data_columns, encoding='latin1')
        df = df.iloc[:-1] 
        dfs.append(df)

    return dfs


def limitar_texto(texto, limite):
    return texto[:35]


def formatar_posto(posto):
    posto = posto.replace('Sine', '').strip()
    if posto.endswith('/Pe'):
        posto = posto[:-3].strip()
    return posto

def abreviar_posto(posto):
    abreviacoes = {
        "Cabo de Santo Agostinho" : "Cabo de Santo A.",
        "Nazare da Mata" : "Nazaré da Mata",
        "Igarassu" : "Igarassu",
        "Vitoria de Santo Antao" : "Vitória de S. Antão",
        "Santa Cruz do Capibaribe" : "Santa Cruz do C.",
        "Sao Lourenco da Mata" : "São L. da Mata"
    }
    return abreviacoes.get(posto, posto).replace('Sine', '').strip()


def formatar_municipio(municipio):
    return limitar_texto(municipio.replace("PE-", ""), 30)


def formatar_escolaridade(valor):
    valor = valor.replace(" Completo", "").replace(" Incompleto", " Não C.")
    return valor


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
    

def criar_pdf(dados, nome_pdf):
    global total_vagas
    doc = SimpleDocTemplate(nome_pdf, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=20, bottomMargin=10)
    table_data = (dados.values.tolist())

    table = Table(table_data)

    col_widths = [90, 40, 190, 135, 75, 80, 100, 65, 0]  
    row_height = 25

    for index, row in enumerate(table_data):
        row[0] = formatar_posto(row[0])
        row[0] = abreviar_posto(row[0])
        row[2] = limitar_texto(str(row[2]), 35)
        row[3] = formatar_municipio(row[3])
        salario = row[5]
        frequencia = row[6]

        salario = salario.replace(".", "").replace(",", ".") 
        salario_float = float(salario)
        salario_redondo = round(salario_float)

        if salario_float == 0.0:
            salario_frequencia = "Não informado"
        elif salario_float >= 100.0:
            salario_frequencia = f"R$ {salario_redondo} / {frequencia}"
        else:
            salario_frequencia = f"R$ {salario_float} / {frequencia}"

        row[5] = salario_frequencia
        row[6] = formatar_escolaridade(row[7])
        row[7] = formatar_experiencia(row[8])
        row[8] = None

        if "Exclusivamente deficiente" in row[9] :
            if row[4] != "Aceita deficiente":
                forma_contratacao_aceita_deficientes = "Exclusivo PCD"
                row[4] = forma_contratacao_aceita_deficientes
        row[8] = None
        row[9] = None

    table = Table(table_data, colWidths=col_widths, rowHeights=row_height, repeatRows=1)

    obs_style = getSampleStyleSheet()["Heading1"]
    obs_style.fontName = 'Helvetica-Bold'
    obs_style.fontSize = 12
    obs_style.textColor = colors.red
    obs_style.alignment = 1
    obs_style.spaceAfter = 12

    vazio_style = getSampleStyleSheet()["Heading1"]
    vazio_style.fontSize = 1
    vazio_style.textColor = colors.white

    legenda_style = getSampleStyleSheet()["Italic"]
    legenda_style.fontName = 'Helvetica-Bold'
    legenda_style.textColor = colors.red

    title_style = getSampleStyleSheet()["Normal"]  
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 10
    title_style.alignment = 1

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), title_style.fontName),
        ('FONTSIZE', (0, 0), (-1, 0), title_style.fontSize),
    ]))

    table_parts = []
    max_rows_per_page = 18
    
    table_data.sort(key=lambda x: (x[0][0].upper(), x[0], x[4])) 
    
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

        for row in grupo_data:

            if len(current_page_rows) >= max_rows_per_page:
                    adicionar_quebra_pagina = True  
                    if len(current_page_rows) < max_rows_per_page and grupo_data.index(row) == len(grupo_data) - 1:
                        adicionar_quebra_pagina = False  
                    if adicionar_quebra_pagina:

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
            
            if not current_page_rows:  
                table_parts.append(img)
                nomes_colunas = ["Agência", "Vagas", "Descrição", "Local de Trabalho", "Contrato", "Salário", "Escolaridade", "Experiência"]
                current_page_rows.append(nomes_colunas)
            current_page_rows.append(row)
        
        total_vagas_posto = sum(int(row[1]) for row in grupo_data)
        posto_vagas_row = [f"Vagas", total_vagas_posto] + [None] * 6
        current_page_rows.append(posto_vagas_row)

        if current_page_rows: 
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

        vagas_por_contratacao = {}
        vagas_exclusivas_pcd = []

        for row in grupo_data:
            forma_contratacao = row[4]
            if forma_contratacao != "Exclusivo PCD":
                if forma_contratacao not in vagas_por_contratacao:
                    vagas_por_contratacao[forma_contratacao] = []
                vagas_por_contratacao[forma_contratacao].append(row)
            else:
                vagas_exclusivas_pcd.append(row)

    current_page_rows_grouped = []
    
    for forma_contratacao, vagas in vagas_por_contratacao.items():
        current_page_rows_grouped.extend(vagas)
    current_page_rows_grouped.extend(vagas_exclusivas_pcd)
    current_page_rows.extend(current_page_rows_grouped)


    total_vagas = 0
    for row in table_data:
        try:
            total_vagas += int(row[1])
        except ValueError:
            pass

    paragrafo_vazio = Paragraph ("-", vazio_style)
    paragrafo_total_vagas = Paragraph(f"Total de Vagas: {total_vagas}", obs_style)
    table_parts.append(paragrafo_vazio)
    table_parts.append(paragrafo_total_vagas)

    paragrafo_legenda0 = Paragraph("Legenda:", legenda_style)
    paragrafo_legenda1 = Paragraph("Exclusivo PCD = Exclusivo para Pessoa com Deficiência")
    paragrafo_legenda2 = Paragraph("Não C. = Não Completo")
    table_parts.append(paragrafo_legenda0)
    table_parts.append(paragrafo_legenda1)
    table_parts.append(paragrafo_legenda2)

    doc.build(table_parts)


if __name__ == "__main__":
    pasta_output = "output"

    if not os.path.exists(pasta_output):
        os.makedirs(pasta_output)

    csv_files = [file for file in os.listdir() if file.endswith(".csv")]

    for csv_file in csv_files:
        lista_de_dataframes = ler_csv(csv_file)

        for df in lista_de_dataframes:

            df.sort_values(by='Posto', inplace=True)

            filtered_df = df[~df['Posto'].str.startswith('-')]
            
            if not filtered_df.empty:  
                nome_pdf = os.path.join(pasta_output, os.path.splitext(csv_file)[0] + "_relatorio.pdf")
            
            nome_pdf = os.path.join(pasta_output, os.path.splitext(csv_file)[0] + "_relatorio.pdf")

            try:
                criar_pdf(df, nome_pdf)
                print(f"Relatório gerado com sucesso: {nome_pdf}")

            except Exception as e:
                print(f"Erro ao gerar o relatório para {nome_pdf}: {e}")

                print("Dados que causaram o erro:")
                print(df)

