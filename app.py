import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de página e Identidade Visual (Cores baseadas na logo)
st.set_page_config(page_title="SofiHub - Gestão Inteligente", layout="wide", page_icon="🚀")

# URL da logo (pode ser um link do GitHub ou Imgur onde você hospedou a imagem)
LOGO_URL = "INSIRA_AQUI_O_LINK_DIRETO_DA_SUA_LOGO_HOSPEDADA" # Ex: https://raw.githubusercontent.com/.../logo.png

# Estilização CSS personalizada para fixar as cores da logo SofiHub
st.markdown(f"""
    <style>
    /* Cor principal do texto (Azul Petróleo SofiHub) */
    .stApp, .css-10trblm, p, h1, h2, h3, .stMetric label {{
        color: #0A2540 !important;
    }}
    /* Cor de destaque (Laranja SofiHub) para botões e links */
    .stButton>button {{
        background-color: #F05A28 !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #D64C20 !important; /* Laranja mais escuro no hover */
        transform: scale(1.02);
    }}
    /* Estilo dos Cards de Métrica */
    div[data-testid="metric-container"] {{
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }}
    /* Alertas customizados */
    .stAlert {{
        border-left: 5px solid #F05A28 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Link da planilha formatado (GID=0 é a primeira aba "Produtos")
SHEET_ID = "1STMwOAe88ZdRrN749aYNLepkeWpv9jiwHZpODRONubw"
URL_PRODUTOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- BARRA LATERAL (IDENTIDADE) ---
with st.sidebar:
    st.image(LOGO_URL, use_column_width=True)
    st.markdown("---")
    st.markdown("### Menu de Gestão")
    menu = st.radio("", ["📊 Dashboard", "🆕 Registrar Item", "🔄 Movimentar Estoque", "📋 Relatórios"])
    st.markdown("---")
    st.caption("SofiHub v1.0 - Hub de Soluções Tecnológicas")

# Função para carregar dados (Robustez contra erro 400 em planilha vazia)
def carregar_dados():
    try:
        produtos = pd.read_csv(URL_PRODUTOS)
        # Se a planilha tiver apenas o cabeçalho, garante que o Pandas entenda as colunas
        if produtos.empty:
            cols = ["ID", "SKU", "Nome", "Categoria", "Qtd_Atual", "Estoque_Minimo", "Preco_Custo", "Preco_Venda", "Localizacao"]
            produtos = pd.DataFrame(columns=cols)
        return produtos
    except Exception as e:
        # Se der erro 400 ou outro, cria uma estrutura vazia padrão
        cols = ["ID", "SKU", "Nome", "Categoria", "Qtd_Atual", "Estoque_Minimo", "Preco_Custo", "Preco_Venda", "Localizacao"]
        return pd.DataFrame(columns=cols)

df_p = carregar_dados()

# --- LÓGICA DO DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Painel SofiHub")
    
    # Métricas formatadas em Cards brancos com texto Azul SofiHub
    c1, c2, c3 = st.columns(3)
    c1.metric("Total SKUs", len(df_p))
    
    # Tratamento de dados numéricos para evitar erros
    if not df_p.empty:
        df_p['Qtd_Atual'] = pd.to_numeric(df_p['Qtd_Atual'], errors='coerce').fillna(0)
        df_p['Preco_Custo'] = pd.to_numeric(df_p['Preco_Custo'], errors='coerce').fillna(0)
        df_p['Estoque_Minimo'] = pd.to_numeric(df_p['Estoque_Minimo'], errors='coerce').fillna(0)
        
        capital = (df_p['Qtd_Atual'] * df_p['Preco_Custo']).sum()
        c2.metric("Capital Parado (Custo)", f"R$ {capital:,.2f}")
        
        criticos = len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']])
        c3.metric("Itens Críticos", criticos)
        
        st.divider()
        st.subheader("Lista de Inventário")
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        if criticos > 0:
            st.warning(f"⚠️ Atenção: {criticos} itens precisam de reposição imediata!")
    else:
        c2.metric("Capital Parado", "R$ 0.00")
        c3.metric("Itens Críticos", "0")
        st.info("🚀 SofiHub pronto! Use o menu 'Registrar Item' para começar.")
