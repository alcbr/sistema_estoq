import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão Inteligente", layout="wide", page_icon="🚀")

# Estilização CSS SofiHub
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, p, label { color: #0A2540 !important; }
    .stButton>button {
        background-color: #F05A28 !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #D64C20 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM O GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        return p, m, c
    except:
        # Fallback caso a planilha esteja vazia ou abas não existam
        cols_p = ["ID", "SKU", "Nome", "Categoria", "Qtd_Atual", "Estoque_Minimo", "Preco_Custo", "Preco_Venda", "Localizacao"]
        cols_m = ["Data_Hora", "SKU", "Produto", "Tipo", "Qtd", "Motivo", "Usuario"]
        cols_c = ["Nome"]
        return pd.DataFrame(columns=cols_p), pd.DataFrame(columns=cols_m), pd.DataFrame(columns=cols_c)

df_p, df_m, df_c = carregar_dados()

# 3. BARRA LATERAL
with st.sidebar:
    caminho_logo = "logo.jpg"
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.title("🚀 SofiHub")
    
    st.markdown("---")
    menu = st.sidebar.radio("NAVEGAÇÃO", ["📊 Dashboard", "🆕 Cadastrar Item", "🔄 Movimentar Estoque", "🔧 Editar / Excluir", "🏷️ Gerenciar Categorias", "📋 Relatórios"])
    st.markdown("---")
    st.caption("SofiHub v1.1 | Hub de Soluções Tecnológicas")

# --- ABA: GERENCIAR CATEGORIAS ---
if menu == "🏷️ Gerenciar Categorias":
    st.title("🏷️ Configurações de Categorias")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nova Categoria")
        nova_cat = st.text_input("Nome da Categoria")
        if st.button("Adicionar"):
            if nova_cat and nova_cat not in df_c['Nome'].values:
                nova_linha = pd.DataFrame([{"Nome": nova_cat}])
                df_c_new = pd.concat([df_c, nova_linha], ignore_index=True)
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.success(f"Categoria '{nova_cat}' criada!")
                st.rerun()

    with col2:
        st.subheader("Excluir Categoria")
        if not df_c.empty:
            cat_excluir = st.selectbox("Selecione para remover", df_c['Nome'].tolist())
            if st.button("Confirmar Exclusão"):
                df_c_new = df_c[df_c['Nome'] != cat_excluir]
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.warning(f"Categoria '{cat_excluir}' removida.")
                st.rerun()

# --- ABA: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    lista_cats = df_c['Nome'].tolist() if not df_c.empty else ["Geral"]
    
    with st.form("cadastro"):
        c1, c2 = st.columns(2)
        sku = c1.text_input("SKU")
        nome = c2.text_input("Nome")
        cat = c1.selectbox("Categoria", lista_cats)
        loc = c2.text_input("Localização Física")
        
        c3, c4 = st.columns(2)
        qtd = c3.number_input("Qtd Inicial", min_value=0, step=1)
        est_min = c4.number_input("Estoque Mínimo (Alerta)", min_value=1, step=1)
        
        if st.form_submit_button("SALVAR NO SOFIHUB"):
            novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": sku, "Nome": nome, "Categoria": cat, "Qtd_Atual": qtd, "Estoque_Minimo": est_min, "Localizacao": loc}])
            df_p_new = pd.concat([df_p, novo], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_p_new)
            st.cache_data.clear()
            st.success("✅ Produto cadastrado!")
            st.rerun()

# --- ABA: DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("📊 Painel de Controle SofiHub")
    if not df_p.empty:
        df_p['Qtd_Atual'] = pd.to_numeric(df_p['Qtd_Atual'], errors='coerce').fillna(0)
        df_p['Estoque_Minimo'] = pd.to_numeric(df_p['Estoque_Minimo'], errors='coerce').fillna(0)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Produtos", len(df_p))
        m2.metric("Categorias", len(df_c))
        m3.metric("Alertas Críticos", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        
        st.divider()
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("O sistema está vazio. Comece criando categorias e cadastrando produtos.")

# --- ABA: MOVIMENTAR ---
elif menu == "🔄 Movimentar Estoque":
    st.title("🔄 Entrada e Saída")
    if not df_p.empty:
        with st.form("mov"):
            p_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            t_op = st.radio("Operação", ["Entrada (+)", "Saída (-)"])
            v_qtd = st.number_input("Quantidade", min_value=1, step=1)
            m_obs = st.text_input("Motivo")
            
            if st.form_submit_button("CONFIRMAR"):
                idx = df_p.index[df_p['Nome'] == p_sel][0]
                estoque_atual = pd.to_numeric(df_p.at[idx, 'Qtd_Atual'])
                
                if "Saída" in t_op and estoque_atual < v_qtd:
                    st.error("❌ Estoque insuficiente!")
                else:
                    novo_saldo = estoque_atual + v_qtd if "Entrada" in t_op else estoque_atual - v_qtd
                    df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                    conn.update(worksheet="Produtos", data=df_p)
                    
                    log = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "SKU": df_p.at[idx, 'SKU'], "Produto": p_sel, "Tipo": t_op, "Qtd": v_qtd, "Motivo": m_obs, "Usuario": "Murilo"}])
                    df_m_new = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_new)
                    st.cache_data.clear()
                    st.success(f"✅ Estoque atualizado: {novo_saldo}")
                    st.rerun()

# --- ABA: EDITAR/EXCLUIR ---
elif menu == "🔧 Editar / Excluir":
    st.title("🔧 Manutenção")
    if not df_p.empty:
        i_sel = st.selectbox("Escolha o Produto", df_p['Nome'].tolist())
        idx_e = df_p.index[df_p['Nome'] == i_sel][0]
        
        t_edit, t_del = st.tabs(["📝 Editar", "🗑️ Excluir"])
        
        with t_edit:
            n_nome = st.text_input("Nome", value=df_p.at[idx_e, 'Nome'])
            if st.button("Salvar"):
                df_p.at[idx_e, 'Nome'] = n_nome
                conn.update(worksheet="Produtos", data=df_p)
                st.cache_data.clear()
                st.success("Atualizado!")
                st.rerun()
        
        with t_del:
            if st.button("EXCLUIR PERMANENTEMENTE"):
                df_p_new = df_p.drop(idx_e)
                conn.update(worksheet="Produtos", data=df_p_new)
                st.cache_data.clear()
                st.warning("Removido.")
                st.rerun()

# --- ABA: RELATÓRIOS ---
elif menu == "📋 Relatórios":
    st.title("📋 Histórico")
    st.dataframe(df_m.sort_index(ascending=False), use_container_width=True)
