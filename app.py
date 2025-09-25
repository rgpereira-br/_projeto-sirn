# ----------------------
# IMPORTANDO BIBLIOTECAS
# ----------------------

import pandas as pd
import streamlit as st
import re

# -----------------------------------
# CONFIGURAÇÕES INICIAIS DO STREAMLIT
# -----------------------------------

st.set_page_config(
    page_title="Análise de Despesas", 
    layout="wide"
)

# -------------------------
# LENDO ARQUIVO DE DESPESAS
# -------------------------

file_path = r"C:\Users\rgper\OneDrive\Documents\Tech\_projeto-sirn\2025090512571673344arquivo.txt"
#df = pd.read_csv(file_path)

# ----------------
# PREPARANDO DADOS
# ----------------

# Lê todas as linhas não vazias
with open(file_path, 'r', encoding='utf-8') as f:
    linhas = [l.rstrip('\n') for l in f.readlines() if l.strip()]

data = []
codigo_pai_atual = ""
descricao_pai_atual = ""

for l in linhas:
    l_strip = l.lstrip()  # remove espaços à esquerda

    # Detecta Código Pai: 13 dígitos separados por pontos
    match_pai = re.match(r'^(\d{2}\.\d{3}\.\d{4}\.\d\.\d{3})\s+(.+)', l_strip)
    if match_pai:
        codigo_pai_atual = match_pai.group(1)
        descricao_pai_atual = match_pai.group(2).strip()
        continue

    # Detecta Código Filho: 14 dígitos separados por pontos
    match_filho = re.match(r'^(\d+\.\d+\.\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s+(.*)$', l_strip)
    if match_filho and codigo_pai_atual:
        codigo_filho = match_filho.group(1)
        restante = match_filho.group(2)

        # Extrai Fonte de Rec (4 dígitos)
        fonte_match = re.search(r'\s(\d{4})\s', restante)
        if fonte_match:
            fonte_rec = fonte_match.group(1)
            partes = restante.split(fonte_rec, 1)
            especificacao = partes[0].strip()
            valores_raw = partes[1].strip().split()
            # Limpa os valores monetários: remove pontos e troca ',' por '.'
            valores = [v.replace('.', '').replace(',', '.') for v in valores_raw]
            valores += [None]*(8 - len(valores))  # garante 8 colunas
        else:
            fonte_rec = None
            especificacao = restante.strip()
            valores = [None]*8

        data.append([codigo_pai_atual, descricao_pai_atual, codigo_filho, especificacao, fonte_rec] + valores)

# Cria DataFrame
colunas = [
    "Código Pai", "Descrição Pai", "Códigos", "Especificação do Elemento", "Fonte de Rec",
    "Autorizada-Pelo Orçamento", "Autorizada-Créd. Suplem.", "Autorizada-Créd. Especial",
    "Autorizada-Anulações", "Autorizada-Total", "Realizada-Até Mês Anterior",
    "Realizada-Neste Mês", "Realizada-Total"
]

df = pd.DataFrame(data, columns=colunas)

# Converte colunas monetárias para numérico
for col in colunas[5:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# -------------------
# CONSTRUINDO VISUAIS
# -------------------

df.set_index("Especificação do Elemento", inplace=True)

elemento = df["Descrição Pai"].value_counts().index
elemento_filtro = st.sidebar.selectbox("Selecione o Elemento Pai:", elemento)
df_filtred = df[df["Descrição Pai"] == elemento_filtro]

fonte_rec = df["Fonte de Rec"].value_counts().index
fonte_rec_filtro = st.sidebar.selectbox("Selecione a Fonte de Rec:", fonte_rec)
df_filtred2 = df_filtred[df_filtred["Fonte de Rec"] == fonte_rec_filtro]

st.write(elemento_filtro)
#st.bar_chart(df_filtred["Realizada-Total"])
st.bar_chart(df_filtred2[df_filtred2["Realizada-Total"] > 0]["Realizada-Total"])

df
