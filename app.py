import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import io

# =====================
# CONFIGURAÇÕES
# =====================
st.set_page_config(page_title="SofiHub - Gestão de Estoque", layout="wide", page_icon="📦")

# =====================
# USUÁRIOS E LOGIN
# =====================
USUARIOS = {
    "leiapollone": {"senha": "1234321", "nome": "Leia Pollone"},
    "murilobraga": {"senha": "1234321", "nome": "Murilo Braga"},
    "visitante":   {"senha": "43211234", "nome": "Visitante"},
}

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None
if "menu" not in st.session_state:
    st.session_state.menu = "📊 Dashboard"
if "relatorio_tab" not in st.session_state:
    st.session_state.relatorio_tab = 0

# ── CSS GLOBAL ──
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #F7F8FA; }
.block-container { padding-top: 1.5rem !important; }

/* SIDEBAR */
section[data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid #1F2937; }
section[data-testid="stSidebar"] * { color: #D1D5DB !important; }
section[data-testid="stSidebar"] .stRadio { display: none !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #9CA3AF !important;
    border: none !important; border-radius: 8px !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    padding: 0.55rem 1rem !important; box-shadow: none !important;
    width: 100% !important; text-align: left !important;
    justify-content: flex-start !important; transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1F2937 !important; color: #F9FAFB !important;
    transform: none !important; box-shadow: none !important;
}
.menu-btn-active > div > button {
    background: #1F2937 !important; color: #F9FAFB !important;
    font-weight: 600 !important; border-left: 3px solid #F05A28 !important;
}
.sidebar-brand { padding: 1.25rem 1rem 0.75rem 1rem; border-bottom: 1px solid #1F2937; margin-bottom: 0.25rem; }
.sidebar-brand-name { color: #F9FAFB !important; font-size: 1rem !important; font-weight: 700 !important; display: block; }
.sidebar-brand-sub { color: #6B7280 !important; font-size: 0.72rem !important; display: block; margin-top: 2px; }
.sidebar-divider { border-top: 1px solid #1F2937; margin: 0.4rem 0; }
.btn-atualizar > div > button { background: #1F2937 !important; color: #9CA3AF !important; border: 1px solid #374151 !important; font-size: 0.82rem !important; }
.btn-sair > div > button { background: transparent !important; color: #6B7280 !important; font-size: 0.82rem !important; border: none !important; }
.btn-sair > div > button:hover { color: #EF4444 !important; background: rgba(239,68,68,0.1) !important; }

/* BOTÕES PRINCIPAIS */
.stButton > button {
    background: #F05A28 !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.87rem !important;
    padding: 0.5rem 1.2rem !important; transition: all 0.15s !important; box-shadow: none !important;
}
.stButton > button:hover { background: #D94E20 !important; transform: none !important; }

/* CARDS */
.card { background: white; border-radius: 12px; padding: 1.2rem 1.4rem; border: 1px solid #E5E7EB; margin-bottom: 0.5rem; }
.card-title { font-size: 0.72rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4rem; }
.card-value { font-size: 1.9rem; font-weight: 700; line-height: 1; }
.card-hint { font-size: 0.68rem; color: #9CA3AF; margin-top: 0.35rem; }
.card-green  { border-top: 3px solid #22C55E; }
.card-orange { border-top: 3px solid #F05A28; }
.card-red    { border-top: 3px solid #EF4444; }
.card-blue   { border-top: 3px solid #3B82F6; }

/* FORMULÁRIOS */
.stForm { background: white !important; border-radius: 12px !important; padding: 1.5rem 1.75rem !important; border: 1px solid #E5E7EB !important; box-shadow: none !important; }
.form-section { border: 1px solid #E5E7EB; border-radius: 10px; padding: 1rem 1.2rem 0.5rem 1.2rem; margin-bottom: 1rem; background: #FAFAFA; }
.form-section-title { font-size: 0.7rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 0.75rem; padding-bottom: 0.4rem; border-bottom: 1px solid #E5E7EB; }

/* TÍTULOS */
.section-header { font-size: 1.3rem; font-weight: 700; color: #111827; margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid #E5E7EB; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { background: white; border-radius: 10px; padding: 3px; border: 1px solid #E5E7EB; gap: 2px; }
.stTabs [data-baseweb="tab"] { border-radius: 7px !important; font-weight: 500 !important; font-size: 0.85rem !important; color: #6B7280 !important; padding: 0.38rem 0.9rem !important; }
.stTabs [aria-selected="true"] { background: #F05A28 !important; color: white !important; font-weight: 600 !important; }

/* TABELA */
.stDataFrame, [data-testid="stDataFrame"] { border-radius: 10px !important; border: 1px solid #E5E7EB !important; overflow: hidden; }

hr { border-color: #E5E7EB !important; margin: 1rem 0 !important; }
h2, h3, h4 { color: #111827 !important; }
</style>
"""

# ── TELA DE LOGIN ──
def tela_login():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .login-wrap { max-width: 420px; margin: 0 auto; padding-top: 2rem; }
    .login-logo { text-align: center; margin-bottom: 1.5rem; }
    .login-card { background: white; border-radius: 16px; padding: 2.5rem; border: 1px solid #E5E7EB; }
    .login-title { font-size: 1.3rem; font-weight: 700; color: #111827; margin-bottom: 0.2rem; }
    .login-sub { font-size: 0.83rem; color: #6B7280; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        # Logo
        if os.path.exists("logo.jpg.png"):
            st.image("logo.jpg.png", use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;font-size:2rem;font-weight:800;color:#111827;margin-bottom:1rem;">📦 SofiHub</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-card"><div class="login-title">Bem-vindo de volta!</div><div class="login-sub">Faça login para acessar o sistema</div></div>', unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("Usuário").strip().lower()
            senha   = st.text_input("Senha", type="password")
            entrar  = st.form_submit_button("Entrar →", use_container_width=True)
            if entrar:
                if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
                    st.session_state.logado = True
                    st.session_state.usuario_atual = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

if not st.session_state.logado:
    tela_login()
    st.stop()

usuario_nome = USUARIOS[st.session_state.usuario_atual]["nome"]

# ── CSS PRINCIPAL ──
st.markdown(CSS, unsafe_allow_html=True)

# ── CONEXÃO ──
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos",      ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias",    ttl=0).dropna(how='all')
        if not p.empty:
            p.columns = p.columns.str.strip()
            p['Qtd_Atual']      = pd.to_numeric(p['Qtd_Atual'],      errors='coerce').fillna(0).astype(int)
            p['Estoque_Minimo'] = pd.to_numeric(p['Estoque_Minimo'], errors='coerce').fillna(0).astype(int)
            p['ID']             = pd.to_numeric(p['ID'],             errors='coerce').fillna(0).astype(int)
            for col in ['Preco_Custo', 'Preco_Venda']:
                if col in p.columns:
                    p[col] = pd.to_numeric(p[col], errors='coerce').fillna(0.0)
        if not m.empty:
            m.columns = m.columns.str.strip()
            for col in ['Total_Gasto', 'Valor_Unitario']:
                if col in m.columns:
                    m[col] = pd.to_numeric(m[col], errors='coerce').fillna(0.0)
        if not c.empty:
            c.columns = c.columns.str.strip()
        return p, m, c
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# ── SIDEBAR ──
with st.sidebar:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)
    else:
        st.markdown('<div class="sidebar-brand"><span class="sidebar-brand-name">📦 SofiHub</span><span class="sidebar-brand-sub">Gestão de Estoque</span></div>', unsafe_allow_html=True)

    st.markdown(f"<div style='padding:0.4rem 1rem 0.6rem;'><span style='font-size:0.73rem;color:#6B7280;'>👤 <b style=\"color:#9CA3AF\">{usuario_nome}</b></span></div>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    opcoes = ["📊 Dashboard", "➕ Cadastrar Produto", "🔄 Movimentações", "🏷️ Categorias", "📈 Relatórios"]
    for label in opcoes:
        ativo = st.session_state.menu == label
        if ativo:
            st.markdown('<div class="menu-btn-active">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.menu = label
            st.rerun()
        if ativo:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-atualizar">', unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_refresh"):
        st.cache_data.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-sair">', unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#374151;font-size:0.7rem;text-align:center;padding:0.5rem 0'>© SofiHub 2026</p>", unsafe_allow_html=True)

menu = st.session_state.menu

# ── COR DA TABELA ──
def style_stock(row):
    styles = [''] * len(row)
    if 'Qtd_Atual' not in row.index or 'Estoque_Minimo' not in row.index:
        return styles
    val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
    bg = '#EF4444' if val <= 0 else ('#F97316' if val <= min_v else '#22C55E')
    idx = df_p.columns.get_loc('Qtd_Atual')
    styles[idx] = f'background:{bg};color:white;font-weight:700;border-radius:4px;padding:2px 8px;text-align:center;'
    return styles

# ── EXPORTAR EXCEL ──
def exportar_excel(df, nome_aba):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    return buf.getvalue()

# ════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════
if menu == "📊 Dashboard":
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)

    total_prod  = len(df_p)
    total_estq  = int(df_p['Qtd_Atual'].sum()) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_alert = len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_cat   = len(df_c)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="card card-green"><div class="card-title">Total Produtos</div><div class="card-value" style="color:#22C55E">{total_prod}</div><div class="card-hint">👆 Ver todos</div></div>', unsafe_allow_html=True)
        if st.button("Ver Produtos", key="btn_prod", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.session_state.relatorio_tab = 1; st.rerun()
    with c2:
        st.markdown(f'<div class="card card-orange"><div class="card-title">Estoque Total</div><div class="card-value" style="color:#F05A28">{total_estq}</div><div class="card-hint">👆 Ver estoque</div></div>', unsafe_allow_html=True)
        if st.button("Ver Estoque", key="btn_estq", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.session_state.relatorio_tab = 1; st.rerun()
    with c3:
        st.markdown(f'<div class="card card-red"><div class="card-title">Alertas</div><div class="card-value" style="color:#EF4444">{total_alert}</div><div class="card-hint">👆 Ver alertas</div></div>', unsafe_allow_html=True)
        if st.button("Ver Alertas", key="btn_alert", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.session_state.relatorio_tab = 0; st.rerun()
    with c4:
        st.markdown(f'<div class="card card-blue"><div class="card-title">Categorias</div><div class="card-value" style="color:#3B82F6">{total_cat}</div><div class="card-hint">👆 Gerenciar</div></div>', unsafe_allow_html=True)
        if st.button("Ver Categorias", key="btn_cat", use_container_width=True):
            st.session_state.menu = "🏷️ Categorias"; st.rerun()

    st.divider()

    # Gráfico de barras — produtos com menor estoque
    if not df_p.empty and 'Qtd_Atual' in df_p.columns and 'Nome' in df_p.columns:
        col_g, col_t = st.columns([1, 1])
        with col_g:
            st.markdown("#### 📊 Estoque por Produto")
            df_graf = df_p[['Nome', 'Qtd_Atual', 'Estoque_Minimo']].sort_values('Qtd_Atual')
            st.bar_chart(df_graf.set_index('Nome')['Qtd_Atual'])

        with col_t:
            st.markdown("#### ⚡ Ações Rápidas")
            prod_fast = st.selectbox("Produto", df_p['Nome'].tolist(), key="prod_fast")
            qtd_fast  = st.number_input("Quantidade", min_value=1, step=1, key="qtd_fast")
            ce, cs = st.columns(2)
            if ce.button("➕ Entrada", use_container_width=True, key="ent_fast"):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                df_p.at[idx, 'Qtd_Atual'] += qtd_fast
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Entrada Rápida", "Qtd": qtd_fast, "Valor_Unitario": 0, "Total_Gasto": 0, "Observacao": "", "Usuario": usuario_nome}])
                conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                st.cache_data.clear(); st.success(f"✅ +{qtd_fast} {prod_fast}"); st.rerun()
            if cs.button("➖ Saída", use_container_width=True, key="sai_fast"):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                if df_p.at[idx, 'Qtd_Atual'] >= qtd_fast:
                    df_p.at[idx, 'Qtd_Atual'] -= qtd_fast
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Saída Rápida", "Qtd": qtd_fast, "Valor_Unitario": 0, "Total_Gasto": 0, "Observacao": "", "Usuario": usuario_nome}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear(); st.success(f"✅ -{qtd_fast} {prod_fast}"); st.rerun()
                else:
                    st.error("❌ Estoque insuficiente!")
    else:
        st.info("Nenhum produto cadastrado ainda.")

# ════════════════════════════════════════
# CADASTRAR
# ════════════════════════════════════════
elif menu == "➕ Cadastrar Produto":
    st.markdown('<div class="section-header">➕ Cadastrar Novo Produto</div>', unsafe_allow_html=True)

    categorias_lista = df_c['Nome'].tolist() if not df_c.empty and 'Nome' in df_c.columns else ["Geral"]
    unidades_lista   = ["un", "kg", "g", "L", "ml", "cx", "pç", "m", "m²"]

    with st.form("cadastro", clear_on_submit=True):
        st.markdown('<div class="form-section"><div class="form-section-title">📋 Identificação</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        nome    = col1.text_input("Nome do Produto *")
        sku     = col2.text_input("SKU (código)").upper()
        unidade = col3.selectbox("Unidade de Medida", unidades_lista)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section"><div class="form-section-title">🏷️ Classificação</div>', unsafe_allow_html=True)
        col4, col5 = st.columns(2)
        categoria   = col4.selectbox("Categoria", categorias_lista)
        localizacao = col5.text_input("Localização (ex: Prateleira A)")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section"><div class="form-section-title">📦 Estoque e Preços</div>', unsafe_allow_html=True)
        col6, col7 = st.columns(2)
        qtd_inicial = col6.number_input("Quantidade Inicial", min_value=0, step=1)
        estoque_min = col7.number_input("Estoque Mínimo",     min_value=0, step=1)
        col8, col9 = st.columns(2)
        preco_custo = col8.number_input("Preço de Custo (R$)", min_value=0.0, step=0.01, format="%.2f")
        preco_venda = col9.number_input("Preço de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("✅ Cadastrar Produto", use_container_width=True):
            if not nome:
                st.error("❌ O nome do produto é obrigatório!")
            else:
                novo_id = int(df_p['ID'].max()) + 1 if not df_p.empty and 'ID' in df_p.columns else 1
                novo = pd.DataFrame([{"ID": novo_id, "SKU": sku, "Nome": nome, "Categoria": categoria,
                                       "Unidade": unidade, "Qtd_Atual": qtd_inicial, "Estoque_Minimo": estoque_min,
                                       "Preco_Custo": preco_custo, "Preco_Venda": preco_venda, "Localizacao": localizacao}])
                conn.update(worksheet="Produtos", data=pd.concat([df_p, novo], ignore_index=True))
                st.cache_data.clear()
                st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")
                st.rerun()

# ════════════════════════════════════════
# MOVIMENTAÇÕES
# ════════════════════════════════════════
elif menu == "🔄 Movimentações":
    st.markdown('<div class="section-header">🔄 Movimentações de Estoque</div>', unsafe_allow_html=True)

    tab_reg, tab_hist = st.tabs(["📝 Registrar", "📋 Histórico"])

    with tab_reg:
        if not df_p.empty and 'Nome' in df_p.columns:
            with st.form("movimentacao", clear_on_submit=True):
                st.markdown('<div class="form-section"><div class="form-section-title">📦 Produto e Tipo</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                produto_mov = col1.selectbox("Produto", df_p['Nome'].tolist())
                tipo_mov    = col2.selectbox("Tipo", ["Entrada", "Saída", "Ajuste de Estoque"])
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="form-section"><div class="form-section-title">🔢 Quantidade e Valor</div>', unsafe_allow_html=True)
                col3, col4 = st.columns(2)
                qtd_mov    = col3.number_input("Quantidade", min_value=1, step=1)
                valor_unit = col4.number_input("Valor Unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
                st.markdown('</div>', unsafe_allow_html=True)

                observacao = st.text_input("💬 Observação (opcional)")

                if st.form_submit_button("✅ Registrar", use_container_width=True):
                    idx = df_p.index[df_p['Nome'] == produto_mov][0]
                    qtd_atual = df_p.at[idx, 'Qtd_Atual']
                    if tipo_mov == "Entrada":
                        df_p.at[idx, 'Qtd_Atual'] = qtd_atual + qtd_mov
                    elif tipo_mov == "Saída":
                        if qtd_atual < qtd_mov:
                            st.error("❌ Estoque insuficiente!"); st.stop()
                        df_p.at[idx, 'Qtd_Atual'] = qtd_atual - qtd_mov
                    else:
                        df_p.at[idx, 'Qtd_Atual'] = qtd_mov
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": produto_mov,
                                          "Tipo": tipo_mov, "Qtd": qtd_mov, "Valor_Unitario": valor_unit,
                                          "Total_Gasto": qtd_mov * valor_unit, "Observacao": observacao, "Usuario": usuario_nome}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ {tipo_mov} de {qtd_mov}x {produto_mov} registrada!")
                    st.rerun()
        else:
            st.info("Cadastre produtos primeiro.")

    with tab_hist:
        if not df_m.empty:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            prods_hist = ["Todos"] + df_m['Produto'].dropna().unique().tolist() if 'Produto' in df_m.columns else ["Todos"]
            tipos_hist = ["Todos"] + df_m['Tipo'].dropna().unique().tolist() if 'Tipo' in df_m.columns else ["Todos"]
            filtro_prod = col_f1.selectbox("Filtrar por Produto", prods_hist, key="filt_prod")
            filtro_tipo = col_f2.selectbox("Filtrar por Tipo", tipos_hist, key="filt_tipo")

            df_hist = df_m.copy()
            if filtro_prod != "Todos":
                df_hist = df_hist[df_hist['Produto'] == filtro_prod]
            if filtro_tipo != "Todos":
                df_hist = df_hist[df_hist['Tipo'] == filtro_tipo]

            st.dataframe(df_hist.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)

            # Exportar
            excel_data = exportar_excel(df_hist, "Movimentacoes")
            st.download_button("📥 Exportar Excel", data=excel_data,
                               file_name=f"movimentacoes_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhuma movimentação registrada ainda.")

# ════════════════════════════════════════
# CATEGORIAS
# ════════════════════════════════════════
elif menu == "🏷️ Categorias":
    st.markdown('<div class="section-header">🏷️ Gerenciar Categorias</div>', unsafe_allow_html=True)

    col_f, col_l = st.columns([1, 1])

    with col_f:
        st.markdown("#### ➕ Nova Categoria")
        with st.form("nova_categoria", clear_on_submit=True):
            nova_cat      = st.text_input("Nome da Categoria *")
            descricao_cat = st.text_input("Descrição (opcional)")
            if st.form_submit_button("✅ Adicionar", use_container_width=True):
                if not nova_cat:
                    st.error("❌ Nome obrigatório!")
                else:
                    nova_linha = pd.DataFrame([{"Nome": nova_cat, "Descricao": descricao_cat}])
                    conn.update(worksheet="Categorias", data=pd.concat([df_c, nova_linha], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ Categoria '{nova_cat}' adicionada!")
                    st.rerun()

    with col_l:
        st.markdown("#### 📋 Categorias Cadastradas")
        if not df_c.empty and 'Nome' in df_c.columns:
            for i, row in df_c.iterrows():
                cc1, cc2 = st.columns([4, 1])
                desc = row.get('Descricao', '')
                desc_txt = f" — {desc}" if pd.notna(desc) and str(desc).strip() else ""
                cc1.markdown(f"**{row['Nome']}**{desc_txt}")
                if cc2.button("🗑️", key=f"del_cat_{i}"):
                    st.session_state[f"confirmar_del_{i}"] = True
                if st.session_state.get(f"confirmar_del_{i}"):
                    st.warning(f"⚠️ Tem certeza que quer excluir **{row['Nome']}**?")
                    cs, cn = st.columns(2)
                    if cs.button("✅ Sim", key=f"sim_{i}"):
                        df_c_novo = df_c.drop(index=i).reset_index(drop=True)
                        conn.update(worksheet="Categorias", data=df_c_novo)
                        st.cache_data.clear()
                        st.session_state.pop(f"confirmar_del_{i}", None)
                        st.success("🗑️ Removida!"); st.rerun()
                    if cn.button("❌ Não", key=f"nao_{i}"):
                        st.session_state.pop(f"confirmar_del_{i}", None); st.rerun()
        else:
            st.info("Nenhuma categoria cadastrada.")

# ════════════════════════════════════════
# RELATÓRIOS
# ════════════════════════════════════════
elif menu == "📈 Relatórios":
    st.markdown('<div class="section-header">📈 Relatórios</div>', unsafe_allow_html=True)

    tab_r1, tab_r2, tab_r3 = st.tabs(["⚠️ Estoque Baixo", "📦 Todos os Produtos", "💰 Movimentações"])

    with tab_r1:
        if not df_p.empty and 'Qtd_Atual' in df_p.columns:
            df_alerta = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]
            if not df_alerta.empty:
                st.warning(f"⚠️ {len(df_alerta)} produto(s) precisam de atenção!")
                st.dataframe(df_alerta, use_container_width=True, hide_index=True)
                excel_data = exportar_excel(df_alerta, "Estoque_Baixo")
                st.download_button("📥 Exportar Excel", data=excel_data,
                                   file_name=f"estoque_baixo_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.success("✅ Todos os produtos estão com estoque adequado!")
        else:
            st.info("Nenhum dado disponível.")

    with tab_r2:
        if not df_p.empty:
            col_f1, col_f2 = st.columns(2)
            cats_disp  = ["Todas"] + (df_p['Categoria'].dropna().unique().tolist() if 'Categoria' in df_p.columns else [])
            filtro_cat = col_f1.selectbox("Filtrar por Categoria", cats_disp)
            busca_rel  = col_f2.text_input("🔍 Buscar produto")

            df_rel = df_p if filtro_cat == "Todas" else df_p[df_p['Categoria'] == filtro_cat]
            if busca_rel:
                df_rel = df_rel[df_rel.apply(lambda r: busca_rel.lower() in str(r).lower(), axis=1)]

            if not df_rel.empty:
                if 'Qtd_Atual' in df_rel.columns:
                    st.dataframe(df_rel.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_rel, use_container_width=True, hide_index=True)

                # Editar / Excluir produto
                st.markdown("---")
                st.markdown("#### ✏️ Editar ou Excluir Produto")
                prod_sel = st.selectbox("Selecione o produto", df_rel['Nome'].tolist(), key="prod_editar")

                if prod_sel:
                    idx = df_p.index[df_p['Nome'] == prod_sel][0]
                    row = df_p.loc[idx]

                    tab_ed, tab_ex = st.tabs(["✏️ Editar", "🗑️ Excluir"])

                    with tab_ed:
                        with st.form("editar_produto"):
                            cats_e = df_c['Nome'].tolist() if not df_c.empty and 'Nome' in df_c.columns else ["Geral"]
                            unds_e = ["un","kg","g","L","ml","cx","pç","m","m²"]
                            col_e1, col_e2, col_e3 = st.columns(3)
                            e_nome    = col_e1.text_input("Nome",     value=str(row.get('Nome','')))
                            e_sku     = col_e2.text_input("SKU",      value=str(row.get('SKU','')))
                            e_und_idx = unds_e.index(row.get('Unidade','un')) if row.get('Unidade','un') in unds_e else 0
                            e_unidade = col_e3.selectbox("Unidade", unds_e, index=e_und_idx)
                            col_e4, col_e5 = st.columns(2)
                            e_cat_idx = cats_e.index(row.get('Categoria','')) if row.get('Categoria','') in cats_e else 0
                            e_cat  = col_e4.selectbox("Categoria", cats_e, index=e_cat_idx)
                            e_loc  = col_e5.text_input("Localização", value=str(row.get('Localizacao','')))
                            col_e6, col_e7, col_e8, col_e9 = st.columns(4)
                            e_qtd  = col_e6.number_input("Qtd Atual",      min_value=0, step=1,   value=int(row.get('Qtd_Atual',0)))
                            e_min  = col_e7.number_input("Estoque Mín",    min_value=0, step=1,   value=int(row.get('Estoque_Minimo',0)))
                            e_cst  = col_e8.number_input("Preço Custo",    min_value=0.0, step=0.01, format="%.2f", value=float(row.get('Preco_Custo',0)))
                            e_vnd  = col_e9.number_input("Preço Venda",    min_value=0.0, step=0.01, format="%.2f", value=float(row.get('Preco_Venda',0)))

                            if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                                df_p.at[idx, 'Nome']          = e_nome
                                df_p.at[idx, 'SKU']           = e_sku
                                df_p.at[idx, 'Unidade']       = e_unidade
                                df_p.at[idx, 'Categoria']     = e_cat
                                df_p.at[idx, 'Localizacao']   = e_loc
                                df_p.at[idx, 'Qtd_Atual']     = e_qtd
                                df_p.at[idx, 'Estoque_Minimo']= e_min
                                df_p.at[idx, 'Preco_Custo']   = e_cst
                                df_p.at[idx, 'Preco_Venda']   = e_vnd
                                conn.update(worksheet="Produtos", data=df_p)
                                st.cache_data.clear()
                                st.success(f"✅ Produto '{e_nome}' atualizado!")
                                st.rerun()

                    with tab_ex:
                        st.warning(f"⚠️ Isso vai excluir permanentemente o produto **{prod_sel}**.")
                        if st.button("🗑️ Confirmar Exclusão", key="excluir_prod"):
                            df_p_novo = df_p.drop(index=idx).reset_index(drop=True)
                            conn.update(worksheet="Produtos", data=df_p_novo)
                            st.cache_data.clear()
                            st.success(f"🗑️ Produto '{prod_sel}' excluído!")
                            st.rerun()

            excel_data = exportar_excel(df_rel, "Produtos")
            st.download_button("📥 Exportar Excel", data=excel_data,
                               file_name=f"produtos_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="exp_prod")
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_r3:
        if not df_m.empty:
            if 'Total_Gasto' in df_m.columns:
                st.metric("💵 Total Movimentado", f"R$ {df_m['Total_Gasto'].sum():,.2f}")
            st.dataframe(df_m.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
            excel_data = exportar_excel(df_m, "Movimentacoes")
            st.download_button("📥 Exportar Excel", data=excel_data,
                               file_name=f"movimentacoes_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="exp_mov2")
        else:
            st.info("Nenhuma movimentação registrada.")
