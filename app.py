import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Inteligência em Estoque", layout="wide", page_icon="🚀")

# Estilização CSS Avançada
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #F05A28 !important; }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO E DADOS
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        # Garantir que colunas financeiras sejam números
        for col in ['Qtd_Atual', 'Estoque_Minimo', 'Preco_Custo', 'Preco_Venda']:
            if col in p.columns:
                p[col] = pd.to_numeric(p[col], errors='coerce').fillna(0)
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. BARRA LATERAL (LOGO BLINDADA)
with st.sidebar:
    caminho_logo = "logo.jpg"
    try:
        if os.path.exists(caminho_logo):
            st.image(caminho_logo, use_container_width=True)
        else:
            st.title("🚀 SofiHub")
    except:
        st.title("🚀 SofiHub")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard Profissional", "🆕 Cadastrar Item", "🔄 Movimentar Estoque", "🔧 Editar / Excluir", "🏷️ Gerenciar Categorias", "📋 Relatórios"])
    st.markdown("---")
    st.caption("SofiHub v1.2 | Inteligência de Dados")

# --- DASHBOARD PROFISSIONAL (Sugestões 1 e 2) ---
if menu == "📊 Dashboard Profissional":
    st.title("📊 Gestão Estratégica SofiHub")
    
    if not df_p.empty:
        # Cálculos Financeiros
        capital_investido = (df_p['Qtd_Atual'] * df_p['Preco_Custo']).sum()
        faturamento_estimado = (df_p['Qtd_Atual'] * df_p['Preco_Venda']).sum()
        lucro_potencial = faturamento_estimado - capital_investido
        itens_criticos = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]

        # Linha 1: Métricas Financeiras
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Capital Parado", f"R$ {capital_investido:,.2f}")
        c2.metric("Lucro em Gôndola", f"R$ {lucro_potencial:,.2f}")
        c3.metric("Total de Itens", int(df_p['Qtd_Atual'].sum()))
        c4.metric("Alertas Críticos", len(itens_criticos), delta_color="inverse")

        st.divider()

        # Sugestão 4: Filtro de Pesquisa Avançado
        st.subheader("🔍 Busca Rápida no Inventário")
        busca = st.text_input("Pesquise por Nome, SKU, Categoria ou Localização...")
        
        # Lógica do Filtro
        if busca:
            df_filtrado = df_p[
                df_p['Nome'].str.contains(busca, case=False, na=False) |
                df_p['SKU'].str.contains(busca, case=False, na=False) |
                df_p['Categoria'].str.contains(busca, case=False, na=False) |
                df_p['Localizacao'].str.contains(busca, case=False, na=False)
            ]
        else:
            df_filtrado = df_p

        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

        # Sugestão 1: Visão por Categoria
        if not df_c.empty:
            st.subheader("📦 Distribuição por Categoria")
            estoque_por_cat = df_p.groupby('Categoria')['Qtd_Atual'].sum().reset_index()
            st.bar_chart(estoque_por_cat.set_index('Categoria'))
            
    else:
        st.info("O Dashboard será preenchido após o cadastro dos itens.")

# --- ABA: CADASTRAR ITEM (Com campos financeiros) ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Cadastro de Produto")
    lista_cats = df_c['Nome'].tolist() if not df_c.empty else ["Geral"]
    
    with st.form("cadastro"):
        c1, c2 = st.columns(2)
        sku = c1.text_input("SKU")
        nome = c2.text_input("Nome")
        cat = c1.selectbox("Categoria", lista_cats)
        loc = c2.text_input("Localização Física")
        
        c3, c4 = st.columns(2)
        qtd = c3.number_input("Quantidade Atual", min_value=0, step=1)
        est_min = c4.number_input("Estoque Mínimo", min_value=0, step=1)
        
        c5, c6 = st.columns(2)
        p_custo = c5.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
        p_venda = c6.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("SALVAR NO SOFIHUB"):
            novo = pd.DataFrame([{
                "ID": len(df_p)+1, "SKU": sku, "Nome": nome, "Categoria": cat, 
                "Qtd_Atual": qtd, "Estoque_Minimo": est_min, 
                "Preco_Custo": p_custo, "Preco_Venda": p_venda, "Localizacao": loc
            }])
            df_p_new = pd.concat([df_p, novo], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_p_new)
            st.cache_data.clear()
            st.success("✅ Produto registrado!")
            st.rerun()

# --- ABA: GERENCIAR CATEGORIAS ---
elif menu == "🏷️ Gerenciar Categorias":
    st.title("🏷️ Categorias")
    col1, col2 = st.columns(2)
    with col1:
        nova_cat = st.text_input("Nova Categoria")
        if st.button("Adicionar"):
            if nova_cat:
                nova_l = pd.DataFrame([{"Nome": nova_cat}])
                df_c_new = pd.concat([df_c, nova_l], ignore_index=True)
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.rerun()
    with col2:
        if not df_c.empty:
            excluir = st.selectbox("Excluir", df_c['Nome'].tolist())
            if st.button("Apagar"):
                df_c_new = df_c[df_c['Nome'] != excluir]
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.rerun()

# --- ABA: MOVIMENTAR ---
elif menu == "🔄 Movimentar Estoque":
    st.title("🔄 Movimentação")
    if not df_p.empty:
        with st.form("mov"):
            p_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            t_op = st.radio("Operação", ["Entrada (+)", "Saída (-)"])
            v_qtd = st.number_input("Quantidade", min_value=1, step=1)
            if st.form_submit_button("EXECUTAR"):
                idx = df_p.index[df_p['Nome'] == p_sel][0]
                estoque_atual = df_p.at[idx, 'Qtd_Atual']
                novo_saldo = estoque_atual + v_qtd if "Entrada" in t_op else estoque_atual - v_qtd
                df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "SKU": df_p.at[idx, 'SKU'], "Produto": p_sel, "Tipo": t_op, "Qtd": v_qtd, "Usuario": "Murilo"}])
                df_m_new = pd.concat([df_m, log], ignore_index=True)
                conn.update(worksheet="Movimentacoes", data=df_m_new)
                st.cache_data.clear()
                st.rerun()

# --- ABA: RELATÓRIOS ---
elif menu == "📋 Relatórios":
    st.title("📋 Histórico Completo")
    st.dataframe(df_m.sort_index(ascending=False), use_container_width=True)
    csv = df_p.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha CSV", csv, "SofiHub_Estoque.csv", "text/csv")
