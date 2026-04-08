import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import time

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão", layout="wide", page_icon="🚀")

# CSS - Identidade Visual SofiHub (Cores da Logo)
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    h1, h2, h3 { color: #0A2540 !important; font-weight: 800 !important; }
    
    /* Estilo dos Cards de Métrica */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #F05A28;
    }
    
    /* Estilo dos Botões */
    .stButton>button {
        background-color: #F05A28 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* Barra Lateral Azul SofiHub */
    section[data-testid="stSidebar"] {
        background-color: #0A2540 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO E CACHE
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        
        # Ajustes numéricos
        if not p.empty:
            p['Qtd_Atual'] = pd.to_numeric(p['Qtd_Atual'], errors='coerce').fillna(0)
            p['Estoque_Minimo'] = pd.to_numeric(p['Estoque_Minimo'], errors='coerce').fillna(0)
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.title("🚀 SofiHub")
    
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["📊 Inventário", "🆕 Cadastrar Item", "🔄 Compras e Saídas", "🏷️ Categorias", "📋 Histórico"])
    st.markdown("---")
    if st.button("🔄 Atualizar Base de Dados"):
        st.cache_data.clear()
        st.toast("Dados sincronizados!", icon="🔄")
        st.rerun()

# --- ABA: INVENTÁRIO ---
if menu == "📊 Inventário":
    st.title("📊 Painel de Inventário")
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total em Stock", int(df_p['Qtd_Atual'].sum()))
        c2.metric("Alertas Críticos", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        c3.metric("Categorias", len(df_c))

        st.divider()
        busca = st.text_input("🔍 Pesquisar no SofiHub...", placeholder="Procurar por nome, SKU ou categoria...")
        df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p

        # Estilo de Alerta na Tabela
        def style_stock(row):
            styles = [''] * len(row)
            val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
            bg = '#F05A28' if val <= min_v else ('#FF4B4B' if val <= 0 else '#28A745')
            styles[df_view.columns.get_loc('Qtd_Atual')] = f'background-color: {bg}; color: white; font-weight: bold; border-radius: 4px'
            return styles

        st.dataframe(df_view.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item encontrado.")

# --- ABA: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    with st.form("cad_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        n_nome = col1.text_input("Nome do Produto")
        n_sku = col2.text_input("SKU / Código")
        n_cat = st.selectbox("Categoria", df_c['Nome'].tolist() if not df_c.empty else ["Geral"])
        
        c3, c4 = st.columns(2)
        n_min = c3.number_input("Estoque Mínimo", min_value=0)
        n_ini = c4.number_input("Qtd Inicial", min_value=0)
        
        enviar = st.form_submit_button("CADASTRAR")
        
        if enviar:
            if n_nome:
                with st.status("A gravar no Google Sheets...", expanded=True) as status:
                    novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": n_sku, "Nome": n_nome, "Categoria": n_cat, "Qtd_Atual": n_ini, "Estoque_Minimo": n_min}])
                    df_p_new = pd.concat([df_p, novo], ignore_index=True)
                    conn.update(worksheet="Produtos", data=df_p_new)
                    st.cache_data.clear()
                    status.update(label="Cadastro Concluído!", state="complete", expanded=False)
                st.toast(f"Sucesso! {n_nome} adicionado.", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Por favor, preencha o nome do produto.")

# --- ABA: MOVIMENTAÇÃO ---
elif menu == "🔄 Compras e Saídas":
    st.title("🔄 Movimentação")
    if not df_p.empty:
        with st.form("mov_form"):
            p_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            t_op = st.radio("Operação", ["Entrada (Compra)", "Saída (Uso)"])
            qtd = st.number_input("Quantidade", min_value=1)
            v_un = st.number_input("Valor Unitário (R$)", min_value=0.0)
            
            if st.form_submit_button("CONFIRMAR"):
                with st.status("A atualizar stock...", expanded=True) as s:
                    idx = df_p.index[df_p['Nome'] == p_sel][0]
                    df_p.at[idx, 'Qtd_Atual'] += qtd if "Entrada" in t_op else -qtd
                    conn.update(worksheet="Produtos", data=df_p)
                    
                    log = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": p_sel, 
                        "Tipo": t_op, "Qtd": qtd, "Valor_Unitario": v_un, 
                        "Total_Gasto": v_un * qtd if "Entrada" in t_op else 0, "Usuario": "Murilo"
                    }])
                    df_m_new = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_new)
                    st.cache_data.clear()
                    s.update(label="Stock Atualizado!", state="complete")
                st.toast(f"Movimentação de {p_sel} registada!", icon="🔄")
                time.sleep(1)
                st.rerun()

# --- ABA: CATEGORIAS ---
elif menu == "🏷️ Categorias":
    st.title("🏷️ Categorias")
    c1, c2 = st.columns(2)
    with c1:
        nova = st.text_input("Nova Categoria")
        if st.button("Adicionar"):
            if nova:
                with st.spinner("A guardar..."):
                    df_c_new = pd.concat([df_c, pd.DataFrame([{"Nome": nova}])], ignore_index=True)
                    conn.update(worksheet="Categorias", data=df_c_new)
                    st.cache_data.clear()
                st.toast(f"Categoria {nova} criada!", icon="🏷️")
                st.rerun()
    with c2:
        if not df_c.empty:
            rem = st.selectbox("Remover Categoria", df_c['Nome'].tolist())
            if st.button("Excluir"):
                with st.spinner("A apagar..."):
                    df_c_new = df_c[df_c['Nome'] != rem]
                    conn.update(worksheet="Categorias", data=df_c_new)
                    st.cache_data.clear()
                st.toast("Categoria removida.", icon="🗑️")
                st.rerun()

# --- ABA: HISTÓRICO ---
elif menu == "📋 Histórico":
    st.title("📋 Relatório de Fluxo")
    if not df_m.empty:
        st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
        st.info(f"💰 Investimento Total: R$ {df_m['Total_Gasto'].astype(float).sum():,.2f}")
