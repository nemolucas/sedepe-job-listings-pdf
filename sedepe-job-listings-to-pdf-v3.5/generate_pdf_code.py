import os
import pandas as pd
import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, PageBreak, Spacer
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
    
    
def traduzir_mes(mes_numero):
    meses = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }

    return meses.get(mes_numero, 'Mês inválido')

def obter_data_em_portugues():
    data_atual = datetime.datetime.now()
    ano = data_atual.year
    mes_numero = data_atual.month
    dia = data_atual.day

    mes_em_portugues = traduzir_mes(mes_numero)

    data_texto = f'{dia} de {mes_em_portugues} de {ano}'

    return data_texto


def criar_pdf(dados, nome_pdf):
    global total_vagas
    global data_texto
    doc = SimpleDocTemplate(nome_pdf, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=5, bottomMargin=20)
    table_data = (dados.values.tolist())
    Table(table_data)

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

    table_part = Table(table_data, colWidths=col_widths, rowHeights=row_height, repeatRows=1)

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

    style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), title_style.fontName),
                ('FONTSIZE', (0, 0), (-1, 0), title_style.fontSize),
            ])

    table_parts = []
    max_rows_per_page = 15

    table_data.sort(key=lambda x: (x[0][0].upper(), x[0], x[4])) 

    grupos = {}
    for row in table_data:
        posto = row[0]
        if posto not in grupos:
            grupos[posto] = []
        grupos[posto].append(row)

    img_path = "governo-copia.png"
    img = Image(img_path, width=400, height=80)
    data_line = Paragraph("Vagas a serem publicadas para o dia: " + data_texto, obs_style)
    obs_line = Paragraph("Obs: Vagas sujeitas a alterações no decorrer do dia.", obs_style)
    
    table_parts.append(img)
    table_parts.append(data_line)
    table_parts.append(obs_line)

    
    table_todas_as_vagas = Table([["Agência", "Vagas", "Descrição", "Local de Trabalho", "Contrato", "Salário", "Escolaridade", "Experiência"]] +
                                    [[str(item) for item in row] for row in table_data],
            colWidths=col_widths, rowHeights=row_height, repeatRows=0)
    table_todas_as_vagas.setStyle(style)
        
    table_parts.append(table_todas_as_vagas)

    for posto, grupo_data in grupos.items():
        add_row = []

        vagas_por_contratacao = {}
        vagas_exclusivas_pcd = []
        
        for row in grupo_data: 
            forma_contratacao = row[4]

            if forma_contratacao != "Exclusivo PCD":
                if forma_contratacao not in vagas_por_contratacao:
                    vagas_por_contratacao[forma_contratacao] = []

                vagas_por_contratacao[forma_contratacao].append(row)

        grouped_rows = []

        for forma_contratacao, vagas in vagas_por_contratacao.items():
            if forma_contratacao != "Exclusivo PCD":
                grouped_rows.extend(vagas)
        
        add_row.extend(grouped_rows)

        vagas_exclusivas_pcd = [row for row in table_data if row[4] == "Exclusivo PCD"]

    if vagas_exclusivas_pcd:
        if table_parts:
            table_parts.append(PageBreak())

        table_exclusivo_pcd = Table([["Agência", "Vagas", "Descrição", "Local de Trabalho", "Contrato", "Salário", "Escolaridade", "Experiência"]] +
                                    [[str(item) for item in row] for row in vagas_exclusivas_pcd],
                                    colWidths=col_widths, rowHeights=row_height, repeatRows=0)
        table_exclusivo_pcd.setStyle(style)

        table_parts.append(img)
        table_parts.append(Paragraph("Vagas Exclusivas para PCD:", obs_style))
        table_parts.append(obs_line)
        table_parts.append(Spacer(1, 6))
        table_parts.append(table_exclusivo_pcd)

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

    data_texto = obter_data_em_portugues()    
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
