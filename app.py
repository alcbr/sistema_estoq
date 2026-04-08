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
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. BARRA LATERAL
with st.sidebar:
    caminho_logo = "logo.jpg"
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.title("🚀 SofiHub")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard", "🆕 Cadastrar Item", "🔄 Movimentar Estoque", "🔧 Editar / Excluir", "🏷️ Gerenciar Categorias", "📋 Relatórios"])

# --- FUNÇÃO DE CATEGORIAS ---
if menu == "🏷️ Gerenciar Categorias":
    st.title("🏷️ Configurações de Categorias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nova Categoria")
        nova_cat = st.text_input("Nome da Categoria (Ex: Ferramentas)")
        if st.button("Adicionar"):
            if nova_cat and nova_cat not in df_c['Nome'].values:
                nova_linha = pd.DataFrame([{"Nome": nova_cat}])
                df_c = pd.concat([df_c, nova_linha], ignore_index=True)
                conn.update(worksheet="Categorias", data=df_c)
                st.success(f"Categoria '{nova_cat}' criada!")
                st.rerun()
            else:
                st.error("Nome inválido ou já existente.")

    with col2:
        st.subheader("Excluir Existente")
        if not df_c.empty:
            cat_excluir = st.selectbox("Selecione para apagar", df_c['Nome'].tolist())
            if st.button("Confirmar Exclusão"):
                df_c = df_c[df_c['Nome'] != cat_excluir]
                conn.update(worksheet="Categorias", data=df_c)
                st.warning(f"Categoria '{cat_excluir}' removida.")
                st.rerun()

# --- CADASTRO (COM CATEGORIAS DINÂMICAS) ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    lista_categorias = df_c['Nome'].tolist() if not df_c.empty else ["Geral"]
    
    with st.form("cadastro"):
        c1, c2 = st.columns(2)
        sku = c1.text_input("SKU")
        nome = c2.text_input("Nome")
        cat = c1.selectbox("Categoria", lista_categorias)
        loc = c2.text_input("Localização")
        
        c3, c4 = st.columns(2)
        qtd = c3.number_input("Qtd Inicial", min_value=0)
        est_min = c4.number_input("Mínimo para Alerta", min_value=1)
        
        if st.form_submit_button("SALVAR"):
            novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": sku, "Nome": nome, "Categoria": cat, "Qtd_Atual": qtd, "Estoque_Minimo": est_min, "Localizacao": loc}])
            df_p = pd.concat([df_p, novo], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_p)
            st.success("Produto cadastrado!")
            st.rerun()

# --- DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("📊 Painel de Controle")
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Produtos", len(df_p))
        c2.metric("Categorias", len(df_c))
        c3.metric("Alertas", len(df_p[pd.to_numeric(df_p['Qtd_Atual']) <= pd.to_numeric(df_p['Estoque_Minimo'])]))
        st.divider()
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("Sistema vazio. Crie categorias e cadastre itens.")

# --- MOVIMENTAR ---
elif menu == "🔄 Movimentar Estoque":
    st.title("🔄 Movimentação")
    if not df_p.empty:
        with st.form("mov"):
            prod = st.selectbox("Item", df_p['Nome'].tolist())
            tipo = st.radio("Tipo", ["Entrada (+)", "Saída (-)"])
            valor = st.number_input("Quantidade", min_value=1)
            if st.form_submit_button("EXECUTAR"):
                idx = df_p.index[df_p['Nome'] == prod][0]
                estoque_atual = pd.to_numeric(df_p.at[idx, 'Qtd_Atual'])
                novo_saldo = estoque_atual + valor if "Entrada" in tipo else estoque_atual - valor
                df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                conn.update(worksheet="Produtos", data=df_p)
                
                log = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "SKU": df_p.at[idx, 'SKU'], "Produto": prod, "Tipo": tipo, "Qtd": valor, "Usuario": "Murilo"}])
                df_m = pd.concat([df_m, log], ignore_index=True)
                conn.update(worksheet="Movimentacoes", data=df_m)
                st.success("Estoque atualizado!")
                st.rerun()

# --- EDITAR / EXCLUIR ---
elif menu == "🔧 Editar / Excluir":
    st.title("🔧 Manutenção")
    if not df_p.empty:
        item_sel = st.selectbox("Produto", df_p['Nome'].tolist())
        idx = df_p.index[df_p['Nome'] == item_sel][0]
        
        with st.expander("Editar"):
            novo_n = st.text_input("Nome", value=df_p.at[idx, 'Nome'])
            nova_cat = st.selectbox("Categoria", df_c['Nome'].tolist(), index=df_c['Nome'].tolist().index(df_p.at[idx, 'Categoria']) if df_p.at[idx, 'Categoria'] in df_c['Nome'].values else 0)
            if st.button("Salvar Alterações"):
                df_p.at[idx, 'Nome'] = novo_n
                df_p.at[idx, 'Categoria'] = nova_cat
                conn.update(worksheet="Produtos", data=df_p)
                st.success("Atualizado!")
                st.rerun()
        
        if st.button("EXCLUIR ITEM"):
            df_p = df_p.drop(idx)
            conn.update(worksheet="Produtos", data=df_p)
            st.rerun()

# --- RELATÓRIOS ---
elif menu == "📋 Relatórios":
    st.title("📋 Histórico")
    st.dataframe(df_m.sort_index(ascending=False), use_container_width=True)
