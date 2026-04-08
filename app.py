import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA E DESIGN (CORES DA LOGO)
st.set_page_config(page_title="SofiHub - Gestão", layout="wide", page_icon="🚀")

# CSS Personalizado com a Identidade Visual SofiHub
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #F4F7F9; }
    
    /* Títulos em Azul Petróleo */
    h1, h2, h3 { color: #0A2540 !important; font-weight: 800 !important; }
    
    /* Cards de Métrica Customizados */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #F05A28; /* Laranja da Logo */
    }
    
    /* Botões em Laranja com Hover em Azul */
    .stButton>button {
        background-color: #F05A28 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #0A2540 !important;
        transform: scale(1.02);
    }

    /* Ajuste na barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #0A2540 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO E DADOS
conn = st.connection("gsheets", type=GSheetsConnection)

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
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. SIDEBAR COM LOGO
with st.sidebar:
    # Atenção: Verifique se o nome do arquivo no seu GitHub é "logo.jpg"
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)
    else:
        st.markdown("## 🚀 SofiHub")
    
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["📊 Inventário", "🆕 Cadastrar Item", "🔄 Compras e Saídas", "🏷️ Categorias", "📋 Histórico"])

# --- FUNÇÃO DE ESTILO DA TABELA ---
def style_inventory(row):
    styles = [''] * len(row)
    val = row['Qtd_Atual']
    min_v = row['Estoque_Minimo']
    
    if val <= 0: bg = '#FF4B4B' # Vermelho Crítico
    elif val <= min_v: bg = '#F05A28' # Laranja Alerta (Cor da Logo)
    else: bg = '#28A745' # Verde OK
    
    styles[df_p.columns.get_loc('Qtd_Atual')] = f'background-color: {bg}; color: white; font-weight: bold; border-radius: 4px'
    return styles

# --- ABA: INVENTÁRIO ---
if menu == "📊 Inventário":
    st.title("📊 Painel de Inventário")
    
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Itens em Estoque", int(df_p['Qtd_Atual'].sum()))
        c2.metric("Alertas de Reposição", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        c3.metric("Total de Categorias", len(df_c))

        st.markdown("---")
        busca = st.text_input("🔍 Buscar no SofiHub...", placeholder="Nome, SKU ou Categoria")
        df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p

        st.dataframe(df_view.style.apply(style_inventory, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("O sistema está vazio. Comece cadastrando seus itens.")

# --- ABA: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    with st.form("cad"):
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome")
        n_sku = c2.text_input("SKU")
        n_cat = st.selectbox("Categoria", df_c['Nome'].tolist() if not df_c.empty else ["Geral"])
        
        c3, c4 = st.columns(2)
        n_min = c3.number_input("Estoque Mínimo", min_value=0)
        n_ini = c4.number_input("Qtd Inicial", min_value=0)
        
        if st.form_submit_button("CADASTRAR NO SISTEMA"):
            novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": n_sku, "Nome": n_nome, "Categoria": n_cat, "Qtd_Atual": n_ini, "Estoque_Minimo": n_min}])
            df_p_new = pd.concat([df_p, novo], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_p_new)
            st.cache_data.clear()
            st.success("Produto adicionado com sucesso!")
            st.rerun()

# --- ABA: COMPRAS E SAÍDAS ---
elif menu == "🔄 Compras e Saídas":
    st.title("🔄 Movimentação")
    if not df_p.empty:
        with st.form("mov"):
            p_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            t_op = st.radio("Tipo", ["Entrada (Compra)", "Saída (Uso)"])
            qtd = st.number_input("Quantidade", min_value=1)
            v_unit = st.number_input("Valor Unitário (R$)", min_value=0.0)
            if st.form_submit_button("REGISTRAR"):
                idx = df_p.index[df_p['Nome'] == p_sel][0]
                novo_saldo = df_p.at[idx, 'Qtd_Atual'] + qtd if "Entrada" in t_op else df_p.at[idx, 'Qtd_Atual'] - qtd
                df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                conn.update(worksheet="Produtos", data=df_p)
                
                log = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": p_sel, 
                    "Tipo": t_op, "Qtd": qtd, "Valor_Unitario": v_unit, 
                    "Total_Gasto": v_unit * qtd if "Entrada" in t_op else 0, "Usuario": "Murilo"
                }])
                df_m_new = pd.concat([df_m, log], ignore_index=True)
                conn.update(worksheet="Movimentacoes", data=df_m_new)
                st.cache_data.clear()
                st.rerun()

# --- ABA: CATEGORIAS ---
elif menu == "🏷️ Categorias":
    st.title("🏷️ Gerenciar Categorias")
    c1, c2 = st.columns(2)
    with c1:
        nova = st.text_input("Nova")
        if st.button("Adicionar"):
            if nova:
                df_c_new = pd.concat([df_c, pd.DataFrame([{"Nome": nova}])], ignore_index=True)
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.rerun()
    with c2:
        if not df_c.empty:
            apagar = st.selectbox("Remover", df_c['Nome'].tolist())
            if st.button("Excluir"):
                df_c_new = df_c[df_c['Nome'] != apagar]
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.rerun()

# --- ABA: HISTÓRICO ---
elif menu == "📋 Histórico":
    st.title("📋 Fluxo de Caixa e Itens")
    if not df_m.empty:
        st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
        st.info(f"💰 Investimento total em estoque: R$ {df_m['Total_Gasto'].sum():,.2f}")
