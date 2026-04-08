import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import time

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão Pro", layout="wide", page_icon="📦")

# CSS PROFISSIONAL (MELHORADO)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #F4F7F9 0%, #E8F0FE 100%); }
    h1 { color: #0A2540; font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 2rem; }
    h2, h3 { color: #0A2540; font-weight: 700; }
    
    /* Cards Premium */
    .metric-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(240,90,40,0.1); transition: transform 0.3s; }
    .metric-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.15); }
    
    /* Botões Enterprise */
    .stButton > button { background: linear-gradient(135deg, #F05A28, #E55A2B); color: white; border-radius: 12px; padding: 0.8rem 2.5rem; font-weight: 600; border: none; box-shadow: 0 4px 16px rgba(240,90,40,0.3); transition: all 0.3s; }
    .stButton > button:hover { background: linear-gradient(135deg, #0A2540, #1A3A5E); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(10,37,64,0.4); }
    
    /* Sidebar Moderna */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A2540 0%, #1A3A5E 100%); border-right: 1px solid rgba(240,90,40,0.2); }
    section[data-testid="stSidebar"] .stRadio > div > label { color: white; font-weight: 500; }
    
    /* Tabela Profissional */
    .dataframe { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    .stDataFrame { border-radius: 12px; }
    
    /* Forms */
    .stForm { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO E CARREGAMENTO (IGUAL)
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        
        if not p.empty:
            p['Qtd_Atual'] = pd.to_numeric(p['Qtd_Atual'], errors='coerce').fillna(0)
            p['Estoque_Minimo'] = pd.to_numeric(p['Estoque_Minimo'], errors='coerce').fillna(0)
        if not m.empty:
            m['Total_Gasto'] = pd.to_numeric(m['Total_Gasto'], errors='coerce').fillna(0)
            m['Valor_Unitario'] = pd.to_numeric(m['Valor_Unitario'], errors='coerce').fillna(0)
            
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. HEADER COM LOGO
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
with header_col2:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)
    else:
        st.markdown("<h1>📦 SofiHub Pro</h1>", unsafe_allow_html=True)

# 4. BARRA LATERAL (MELHORADA)
with st.sidebar:
    st.markdown("### 🚀 Navegação")
    menu = st.radio("", ["📊 Dashboard", "➕ Cadastrar", "🔄 Movimentações", "🏷️ Categorias", "📈 Relatórios"])
    st.markdown("---")
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption("© SofiHub 2026")

# --- FUNÇÃO DE ESTILO TABELA (MELHORADA) ---
def style_stock(row):
    styles = [''] * len(row)
    val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
    if val <= 0:
        bg = '#FF4B4B'
    elif val <= min_v:
        bg = '#F05A28'
    else:
        bg = '#28A745'
    styles[df_p.columns.get_loc('Qtd_Atual')] = f'background: linear-gradient(90deg, {bg}, {bg}CC); color: white; font-weight: bold; border-radius: 6px; padding: 0.5rem;'
    return styles

# 5. DASHBOARD PRINCIPAL (NOVO LAYOUT COM CARDS)
if menu == "📊 Dashboard":
    st.markdown("## 📊 Visão Geral")
    
    # Cards de Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Produtos</h3>
            <h1 style="color: #28A745; font-size: 2.5rem;">{}</h1>
        </div>""".format(len(df_p)), unsafe_allow_html=True)
    with col2:
        total_estoque = int(df_p['Qtd_Atual'].sum()) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
        st.markdown("""
        <div class="metric-card">
            <h3>Estoque Total</h3>
            <h1 style="color: #F05A28; font-size: 2.5rem;">{}</h1>
        </div>""".format(total_estoque), unsafe_allow_html=True)
    with col3:
        total_alertas = len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
        st.markdown("""
        <div class="metric-card">
            <h3>Alertas</h3>
            <h1 style="color: #FF4B4B; font-size: 2.5rem;">{}</h1>
        </div>""".format(total_alertas), unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Categorias</h3>
            <h1 style="color: #0A2540; font-size: 2.5rem;">{}</h1>
        </div>""".format(len(df_c)), unsafe_allow_html=True)
    
    st.divider()
    
    # Ações Rápidas em Tabs
    tab1, tab2 = st.tabs(["⚡ Ações Rápidas", "🔍 Buscar & Filtrar"])
    with tab1:
        col_p, col_q, col_ent, col_sai = st.columns([2,1,2,2])
        if not df_p.empty:
            prod_fast = col_p.selectbox("Produto", df_p['Nome'].tolist())
            qtd_fast = col_q.number_input("Qtd", min_value=1, step=1)
            if col_ent.button("➕ Entrada", use_container_width=True):
                # [LÓGICA IGUAL À ORIGINAL - COPIE DAQUI]
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                df_p.at[idx, 'Qtd_Atual'] += qtd_fast
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Entrada (Rápida)", "Qtd": qtd_fast, "Usuario": "Murilo"}])
                conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log]))
                st.cache_data.clear()
                st.success(f"+{qtd_fast} {prod_fast}")
                st.rerun()
            if col_sai.button("➖ Saída", use_container_width=True):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                if df_p.at[idx, 'Qtd_Atual'] >= qtd_fast:
                    df_p.at[idx, 'Qtd_Atual'] -= qtd_fast
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Saída (Rápida)", "Qtd": qtd_fast, "Usuario": "Murilo"}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log]))
                    st.cache_data.clear()
                    st.success(f"-{qtd_fast} {prod_fast}")
                    st.rerun()
                else: st.error("Sem estoque!")
    
    with tab2:
        busca = st.text_input("Buscar...")
        df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p
        st.dataframe(df_view.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)

# [AS DEMAIS ABAS - MESMA LÓGICA, SÓ ADICIONE CARDS E CSS]
elif menu == "➕ Cadastrar":
    st.markdown("## ➕ Novo Produto")
    with st.form("cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome")
        sku = col2.text_input("SKU").upper()
        # ... (resto igual, mas dentro de .stForm)
        if st.form_submit_button("Cadastrar", use_container_width=True):
            # lógica original
            pass

# Demais seções seguem o mesmo padrão...
