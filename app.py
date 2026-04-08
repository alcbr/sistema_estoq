import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão Pro", layout="wide", page_icon="📦")

# CSS PROFISSIONAL
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #F4F7F9 0%, #E8F0FE 100%); }
    h1 { color: #0A2540; font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 2rem; }
    h2, h3 { color: #0A2540; font-weight: 700; }
    .metric-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(240,90,40,0.1); transition: transform 0.3s; }
    .metric-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.15); }
    .stButton > button { background: linear-gradient(135deg, #F05A28, #E55A2B); color: white; border-radius: 12px; padding: 0.8rem 2.5rem; font-weight: 600; border: none; box-shadow: 0 4px 16px rgba(240,90,40,0.3); transition: all 0.3s; }
    .stButton > button:hover { background: linear-gradient(135deg, #0A2540, #1A3A5E); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(10,37,64,0.4); }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A2540 0%, #1A3A5E 100%); border-right: 1px solid rgba(240,90,40,0.2); }
    section[data-testid="stSidebar"] .stRadio > div > label { color: white; font-weight: 500; }
    .dataframe { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    .stDataFrame { border-radius: 12px; }
    .stForm { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO E CARREGAMENTO
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')

        if not p.empty:
            p.columns = p.columns.str.strip()
            p['Qtd_Atual'] = pd.to_numeric(p['Qtd_Atual'], errors='coerce').fillna(0)
            p['Estoque_Minimo'] = pd.to_numeric(p['Estoque_Minimo'], errors='coerce').fillna(0)
        if not m.empty:
            m.columns = m.columns.str.strip()
            if 'Total_Gasto' in m.columns:
                m['Total_Gasto'] = pd.to_numeric(m['Total_Gasto'], errors='coerce').fillna(0)
            if 'Valor_Unitario' in m.columns:
                m['Valor_Unitario'] = pd.to_numeric(m['Valor_Unitario'], errors='coerce').fillna(0)
        if not c.empty:
            c.columns = c.columns.str.strip()

        return p, m, c
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. HEADER COM LOGO
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
with header_col2:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)
    else:
        st.markdown("<h1>📦 SofiHub Pro</h1>", unsafe_allow_html=True)

# 4. BARRA LATERAL
with st.sidebar:
    st.markdown("### 🚀 Navegação")
    menu = st.radio("", ["📊 Dashboard", "➕ Cadastrar", "🔄 Movimentações", "🏷️ Categorias", "📈 Relatórios"])
    st.markdown("---")
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption("© SofiHub 2026")

# FUNÇÃO DE ESTILO TABELA
def style_stock(row):
    styles = [''] * len(row)
    if 'Qtd_Atual' not in row.index or 'Estoque_Minimo' not in row.index:
        return styles
    val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
    if val <= 0:
        bg = '#FF4B4B'
    elif val <= min_v:
        bg = '#F05A28'
    else:
        bg = '#28A745'
    col_idx = df_p.columns.get_loc('Qtd_Atual')
    styles[col_idx] = f'background: {bg}; color: white; font-weight: bold; border-radius: 6px; padding: 0.3rem 0.5rem;'
    return styles

# =====================
# 5. DASHBOARD
# =====================
if menu == "📊 Dashboard":
    st.markdown("## 📊 Visão Geral")

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

    tab1, tab2 = st.tabs(["⚡ Ações Rápidas", "🔍 Buscar & Filtrar"])
    with tab1:
        if not df_p.empty and 'Nome' in df_p.columns:
            col_p, col_q, col_ent, col_sai = st.columns([2, 1, 2, 2])
            prod_fast = col_p.selectbox("Produto", df_p['Nome'].tolist())
            qtd_fast = col_q.number_input("Qtd", min_value=1, step=1)
            if col_ent.button("➕ Entrada", use_container_width=True):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                df_p.at[idx, 'Qtd_Atual'] += qtd_fast
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Entrada (Rápida)", "Qtd": qtd_fast, "Usuario": "Admin"}])
                df_m_novo = pd.concat([df_m, log], ignore_index=True)
                conn.update(worksheet="Movimentacoes", data=df_m_novo)
                st.cache_data.clear()
                st.success(f"✅ +{qtd_fast} unidades de {prod_fast}")
                st.rerun()
            if col_sai.button("➖ Saída", use_container_width=True):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                if df_p.at[idx, 'Qtd_Atual'] >= qtd_fast:
                    df_p.at[idx, 'Qtd_Atual'] -= qtd_fast
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Saída (Rápida)", "Qtd": qtd_fast, "Usuario": "Admin"}])
                    df_m_novo = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_novo)
                    st.cache_data.clear()
                    st.success(f"✅ -{qtd_fast} unidades de {prod_fast}")
                    st.rerun()
                else:
                    st.error("❌ Estoque insuficiente!")
        else:
            st.info("Nenhum produto cadastrado ainda.")

    with tab2:
        busca = st.text_input("🔍 Buscar produto...")
        if not df_p.empty:
            df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p
            if 'Qtd_Atual' in df_view.columns and 'Estoque_Minimo' in df_view.columns:
                st.dataframe(df_view.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_view, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum produto encontrado.")

# =====================
# 6. CADASTRAR PRODUTO
# =====================
elif menu == "➕ Cadastrar":
    st.markdown("## ➕ Cadastrar Novo Produto")

    categorias_lista = df_c['Nome'].tolist() if not df_c.empty and 'Nome' in df_c.columns else ["Geral"]

    with st.form("cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Produto *")
        sku = col2.text_input("SKU (código)").upper()
        col3, col4 = st.columns(2)
        categoria = col3.selectbox("Categoria", categorias_lista)
        localizacao = col4.text_input("Localização (ex: Prateleira A)")
        col5, col6, col7 = st.columns(3)
        qtd_inicial = col5.number_input("Quantidade Inicial", min_value=0, step=1)
        estoque_min = col6.number_input("Estoque Mínimo", min_value=0, step=1)
        preco_custo = col7.number_input("Preço de Custo (R$)", min_value=0.0, step=0.01, format="%.2f")
        preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")

        submitted = st.form_submit_button("✅ Cadastrar Produto", use_container_width=True)
        if submitted:
            if not nome:
                st.error("❌ O nome do produto é obrigatório!")
            else:
                novo = pd.DataFrame([{
                    "ID": len(df_p) + 1,
                    "SKU": sku,
                    "Nome": nome,
                    "Categoria": categoria,
                    "Qtd_Atual": qtd_inicial,
                    "Estoque_Minimo": estoque_min,
                    "Preco_Custo": preco_custo,
                    "Preco_Venda": preco_venda,
                    "Localizacao": localizacao
                }])
                df_atualizado = pd.concat([df_p, novo], ignore_index=True)
                conn.update(worksheet="Produtos", data=df_atualizado)
                st.cache_data.clear()
                st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")
                st.rerun()

# =====================
# 7. MOVIMENTAÇÕES
# =====================
elif menu == "🔄 Movimentações":
    st.markdown("## 🔄 Movimentações de Estoque")

    tab_reg, tab_hist = st.tabs(["📝 Registrar", "📋 Histórico"])

    with tab_reg:
        if not df_p.empty and 'Nome' in df_p.columns:
            with st.form("movimentacao", clear_on_submit=True):
                col1, col2 = st.columns(2)
                produto_mov = col1.selectbox("Produto", df_p['Nome'].tolist())
                tipo_mov = col2.selectbox("Tipo", ["Entrada", "Saída", "Ajuste"])
                col3, col4 = st.columns(2)
                qtd_mov = col3.number_input("Quantidade", min_value=1, step=1)
                valor_unit = col4.number_input("Valor Unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
                observacao = st.text_input("Observação (opcional)")

                if st.form_submit_button("✅ Registrar", use_container_width=True):
                    idx = df_p.index[df_p['Nome'] == produto_mov][0]
                    qtd_atual = df_p.at[idx, 'Qtd_Atual']

                    if tipo_mov == "Entrada":
                        df_p.at[idx, 'Qtd_Atual'] = qtd_atual + qtd_mov
                    elif tipo_mov == "Saída":
                        if qtd_atual < qtd_mov:
                            st.error("❌ Estoque insuficiente!")
                            st.stop()
                        df_p.at[idx, 'Qtd_Atual'] = qtd_atual - qtd_mov
                    else:
                        df_p.at[idx, 'Qtd_Atual'] = qtd_mov

                    conn.update(worksheet="Produtos", data=df_p)

                    log = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Produto": produto_mov,
                        "Tipo": tipo_mov,
                        "Qtd": qtd_mov,
                        "Valor_Unitario": valor_unit,
                        "Total_Gasto": qtd_mov * valor_unit,
                        "Observacao": observacao,
                        "Usuario": "Admin"
                    }])
                    df_m_novo = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_novo)
                    st.cache_data.clear()
                    st.success(f"✅ {tipo_mov} de {qtd_mov}x {produto_mov} registrada!")
                    st.rerun()
        else:
            st.info("Cadastre produtos primeiro.")

    with tab_hist:
        if not df_m.empty:
            st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação registrada ainda.")

# =====================
# 8. CATEGORIAS
# =====================
elif menu == "🏷️ Categorias":
    st.markdown("## 🏷️ Gerenciar Categorias")

    col_cat1, col_cat2 = st.columns(2)

    with col_cat1:
        st.markdown("### ➕ Nova Categoria")
        with st.form("nova_categoria", clear_on_submit=True):
            nova_cat = st.text_input("Nome da Categoria *")
            descricao_cat = st.text_input("Descrição (opcional)")
            if st.form_submit_button("✅ Adicionar", use_container_width=True):
                if not nova_cat:
                    st.error("❌ Nome obrigatório!")
                else:
                    nova_linha = pd.DataFrame([{"Nome": nova_cat, "Descricao": descricao_cat}])
                    df_c_novo = pd.concat([df_c, nova_linha], ignore_index=True)
                    conn.update(worksheet="Categorias", data=df_c_novo)
                    st.cache_data.clear()
                    st.success(f"✅ Categoria '{nova_cat}' adicionada!")
                    st.rerun()

    with col_cat2:
        st.markdown("### 📋 Categorias Cadastradas")
        if not df_c.empty:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma categoria cadastrada.")

# =====================
# 9. RELATÓRIOS
# =====================
elif menu == "📈 Relatórios":
    st.markdown("## 📈 Relatórios")

    tab_r1, tab_r2, tab_r3 = st.tabs(["⚠️ Estoque Baixo", "📦 Todos Produtos", "💰 Movimentações"])

    with tab_r1:
        st.markdown("### ⚠️ Produtos com Estoque Baixo ou Zerado")
        if not df_p.empty and 'Qtd_Atual' in df_p.columns:
            df_alerta = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]
            if not df_alerta.empty:
                st.warning(f"⚠️ {len(df_alerta)} produto(s) precisam de atenção!")
                st.dataframe(df_alerta, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Todos os produtos estão com estoque adequado!")
        else:
            st.info("Nenhum dado disponível.")

    with tab_r2:
        st.markdown("### 📦 Todos os Produtos")
        if not df_p.empty:
            if 'Qtd_Atual' in df_p.columns and 'Estoque_Minimo' in df_p.columns:
                st.dataframe(df_p.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_p, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_r3:
        st.markdown("### 💰 Histórico de Movimentações")
        if not df_m.empty:
            if 'Total_Gasto' in df_m.columns:
                total = df_m['Total_Gasto'].sum()
                st.metric("💵 Total Movimentado", f"R$ {total:,.2f}")
            st.dataframe(df_m, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação registrada.")
