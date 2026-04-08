import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import time

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão Pro", layout="wide", page_icon="🚀")

# CSS PERSONALIZADO (CORES DA LOGO)
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    h1, h2, h3 { color: #0A2540 !important; font-weight: 800 !important; }
    
    /* Cards de Métrica */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #F05A28;
    }
    
    /* Botões SofiHub */
    .stButton>button {
        background-color: #F05A28 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0A2540 !important;
        transform: scale(1.02);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #0A2540 !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO E CARREGAMENTO
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
            m['Valor_Unitario'] = pd.to_numeric(m['Valor_Unitario'], errors='coerce').fillna(0)
            
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. BARRA LATERAL
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.title("🚀 SofiHub")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Inventário", "🆕 Cadastrar Item", "🔄 Compras e Saídas", "🏷️ Categorias", "📋 Histórico"])
    st.markdown("---")
    if st.button("🔄 Sincronizar Agora"):
        st.cache_data.clear()
        st.rerun()

# --- FUNÇÃO DE ESTILO ---
def style_stock(row):
    styles = [''] * len(row)
    val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
    bg = '#F05A28' if val <= min_v else ('#FF4B4B' if val <= 0 else '#28A745')
    styles[df_p.columns.get_loc('Qtd_Atual')] = f'background-color: {bg}; color: white; font-weight: bold; border-radius: 4px'
    return styles

# --- ABA: INVENTÁRIO (COM AÇÕES RÁPIDAS) ---
if menu == "📊 Inventário":
    st.title("📊 Painel de Inventário")
    
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total em Stock", int(df_p['Qtd_Atual'].sum()))
        c2.metric("Alertas Críticos", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        c3.metric("Categorias", len(df_c))

        with st.expander("⚡ Ações Rápidas - Entrada/Saída Instantânea", expanded=False):
            col_p, col_q, col_b = st.columns([2, 1, 1])
            prod_fast = col_p.selectbox("Produto", df_p['Nome'].tolist(), key="fast_p")
            qtd_fast = col_q.number_input("Quantidade", min_value=1, step=1, key="fast_q")
            sub_c1, sub_c2 = col_b.columns(2)
            
            if sub_c1.button("➕"):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                df_p.at[idx, 'Qtd_Atual'] += qtd_fast
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Entrada (Rápida)", "Qtd": qtd_fast, "Usuario": "Murilo"}])
                conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log]))
                st.cache_data.clear()
                st.toast(f"+{qtd_fast} {prod_fast}", icon="🚀")
                st.rerun()

            if sub_c2.button("➖"):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                if df_p.at[idx, 'Qtd_Atual'] >= qtd_fast:
                    df_p.at[idx, 'Qtd_Atual'] -= qtd_fast
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Saída (Rápida)", "Qtd": qtd_fast, "Usuario": "Murilo"}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log]))
                    st.cache_data.clear()
                    st.toast(f"-{qtd_fast} {prod_fast}", icon="📉")
                    st.rerun()
                else: st.error("Sem estoque!")

        st.divider()
        busca = st.text_input("🔍 Buscar no SofiHub...", placeholder="Nome, SKU ou Categoria")
        df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p
        st.dataframe(df_view.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
    else: st.info("Sistema vazio.")

# --- ABA: CADASTRAR ITEM (COM SEGURANÇA) ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    with st.form("cad_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        n_nome = col1.text_input("Nome do Produto")
        n_sku = col2.text_input("SKU / Código").strip().upper()
        n_cat = st.selectbox("Categoria", df_c['Nome'].tolist() if not df_c.empty else ["Geral"])
        n_loc = st.text_input("Localização Física")
        c3, c4 = st.columns(2)
        n_min = c3.number_input("Estoque Mínimo", min_value=0, value=5)
        n_ini = c4.number_input("Quantidade Inicial", min_value=0, value=0)
        
        if st.form_submit_button("FINALIZAR CADASTRO"):
            if not n_nome or not n_sku: st.error("Nome e SKU são obrigatórios.")
            elif not df_p.empty and n_sku in df_p['SKU'].astype(str).str.upper().values:
                st.warning(f"O SKU '{n_sku}' já existe!")
            else:
                with st.status("Salvando...", expanded=False):
                    novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": n_sku, "Nome": n_nome, "Categoria": n_cat, "Qtd_Atual": n_ini, "Estoque_Minimo": n_min, "Localizacao": n_loc}])
                    conn.update(worksheet="Produtos", data=pd.concat([df_p, novo], ignore_index=True))
                    st.cache_data.clear()
                st.toast(f"{n_nome} Cadastrado!", icon="✅")
                time.sleep(1)
                st.rerun()

# --- ABA: MOVIMENTAÇÃO ---
elif menu == "🔄 Compras e Saídas":
    st.title("🔄 Movimentação")
    if not df_p.empty:
        with st.form("mov_full"):
            p_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            t_op = st.radio("Tipo", ["Entrada (Compra)", "Saída (Uso)"])
            qtd = st.number_input("Quantidade", min_value=1)
            v_un = st.number_input("Valor Unitário (R$)", min_value=0.0)
            if st.form_submit_button("REGISTRAR"):
                with st.status("Atualizando..."):
                    idx = df_p.index[df_p['Nome'] == p_sel][0]
                    df_p.at[idx, 'Qtd_Atual'] += qtd if "Entrada" in t_op else -qtd
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": p_sel, 
                        "Tipo": t_op, "Qtd": qtd, "Valor_Unitario": v_un, 
                        "Total_Gasto": v_un * qtd if "Entrada" in t_op else 0, "Usuario": "Murilo"
                    }])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear()
                st.toast("Sucesso!", icon="🔄")
                st.rerun()

# --- ABA: CATEGORIAS ---
elif menu == "🏷️ Categorias":
    st.title("🏷️ Gerenciar Categorias")
    c1, c2 = st.columns(2)
    with c1:
        nova = st.text_input("Nova Categoria")
        if st.button("Adicionar"):
            if nova:
                conn.update(worksheet="Categorias", data=pd.concat([df_c, pd.DataFrame([{"Nome": nova}])]))
                st.cache_data.clear()
                st.rerun()
    with c2:
        if not df_c.empty:
            rem = st.selectbox("Remover", df_c['Nome'].tolist())
            if st.button("Excluir"):
                conn.update(worksheet="Categorias", data=df_c[df_c['Nome'] != rem])
                st.cache_data.clear()
                st.rerun()

# --- ABA: HISTÓRICO ---
elif menu == "📋 Histórico":
    st.title("📋 Histórico")
    if not df_m.empty:
        st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
        st.info(f"💰 Investimento Total: R$ {df_m['Total_Gasto'].sum():,.2f}")
