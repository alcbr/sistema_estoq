import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# =====================
# CONFIGURAÇÕES
# =====================
st.set_page_config(page_title="SofiHub - Gestão de Estoque", layout="wide", page_icon="📦")

# =====================
# USUÁRIOS E LOGIN
# =====================
USUARIOS = {
    "leiapollone":  {"senha": "1234321", "nome": "Leia Pollone"},
    "murilobraga":  {"senha": "1234321", "nome": "Murilo Braga"},
    "visitante":    {"senha": "43211234", "nome": "Visitante"},
}

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None

def tela_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #F7F8FA; }
    .login-box {
        max-width: 400px;
        margin: 4rem auto;
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        border: 1px solid #E5E7EB;
    }
    .login-title { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem; }
    .login-sub   { font-size: 0.85rem; color: #6B7280; margin-bottom: 2rem; }
    .stButton > button {
        background: #F05A28 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.65rem !important;
    }
    .stButton > button:hover { background: #D94E20 !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <div class="login-title">📦 SofiHub</div>
            <div class="login-sub">Faça login para continuar</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("👤 Usuário").strip().lower()
            senha   = st.text_input("🔒 Senha", type="password")
            entrar  = st.form_submit_button("Entrar", use_container_width=True)

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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

/* ── Fundo geral ── */
.stApp { background: #F7F8FA; }
.block-container { padding-top: 2rem !important; }

/* ══════════════════════════════
   SIDEBAR — clean dark
══════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1F2937;
}
section[data-testid="stSidebar"] * { color: #D1D5DB !important; }

/* Esconde radio completamente */
section[data-testid="stSidebar"] .stRadio { display: none !important; }

/* Botões de menu */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #9CA3AF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1F2937 !important;
    color: #F9FAFB !important;
    transform: none !important;
    box-shadow: none !important;
}
.menu-btn-active > button {
    background: #1F2937 !important;
    color: #F9FAFB !important;
    font-weight: 600 !important;
    border-left: 3px solid #F05A28 !important;
}
/* Sidebar brand */
.sidebar-brand {
    padding: 1.5rem 1rem 1rem 1rem;
    border-bottom: 1px solid #1F2937;
    margin-bottom: 0.5rem;
}
.sidebar-brand-name {
    color: #F9FAFB !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    display: block;
}
.sidebar-brand-sub {
    color: #6B7280 !important;
    font-size: 0.73rem !important;
    display: block;
    margin-top: 2px;
}
.sidebar-divider {
    border-top: 1px solid #1F2937;
    margin: 0.5rem 0;
}
/* Botão atualizar */
.btn-atualizar > button {
    background: #1F2937 !important;
    color: #9CA3AF !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    margin-top: 0.5rem !important;
}

/* ══════════════════════════════
   BOTÕES principais
══════════════════════════════ */
.stButton > button {
    background: #F05A28 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #D94E20 !important;
    transform: none !important;
    box-shadow: 0 4px 12px rgba(240,90,40,0.25) !important;
}

/* ══════════════════════════════
   CARDS métricas
══════════════════════════════ */
.card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #E5E7EB;
    margin-bottom: 0.5rem;
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.5rem;
}
.card-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.card-hint { font-size: 0.7rem; color: #9CA3AF; margin-top: 0.4rem; }
.card-green  { border-top: 3px solid #22C55E; }
.card-orange { border-top: 3px solid #F05A28; }
.card-red    { border-top: 3px solid #EF4444; }
.card-blue   { border-top: 3px solid #3B82F6; }

/* ══════════════════════════════
   FORMULÁRIOS
══════════════════════════════ */
.stForm {
    background: white !important;
    border-radius: 12px !important;
    padding: 1.5rem 2rem !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: none !important;
}
.form-section {
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1rem 1.25rem 0.25rem 1.25rem;
    margin-bottom: 1.25rem;
    background: #FAFAFA;
}
.form-section-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #E5E7EB;
}

/* ══════════════════════════════
   TÍTULO DE SEÇÃO
══════════════════════════════ */
.section-header {
    font-size: 1.35rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #E5E7EB;
}

/* ══════════════════════════════
   TABS
══════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 10px;
    padding: 3px;
    border: 1px solid #E5E7EB;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    color: #6B7280 !important;
    padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: #F05A28 !important;
    color: white !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════
   TABELA
══════════════════════════════ */
.stDataFrame, [data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
    overflow: hidden;
}

/* ══════════════════════════════
   MISC
══════════════════════════════ */
hr { border-color: #E5E7EB !important; margin: 1.25rem 0 !important; }
h2, h3, h4 { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)

# =====================
# CONEXÃO
# =====================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')

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

# =====================
# SESSION STATE
# =====================
if 'menu' not in st.session_state:
    st.session_state.menu = "📊 Dashboard"
if 'relatorio_tab' not in st.session_state:
    st.session_state.relatorio_tab = 0

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-brand-name">📦 SofiHub</span>
        <span class="sidebar-brand-sub">Gestão de Estoque</span>
    </div>
    """, unsafe_allow_html=True)

    # Usuário logado
    st.markdown(f"<div style='padding:0.5rem 1rem;margin-bottom:0.5rem;'><span style='font-size:0.75rem;color:#6B7280;'>👤 Olá, <b style=\"color:#9CA3AF\">{usuario_nome}</b></span></div>", unsafe_allow_html=True)

    opcoes = {
        "📊 Dashboard": "📊 Dashboard",
        "➕ Cadastrar Produto": "➕ Cadastrar Produto",
        "🔄 Movimentações": "🔄 Movimentações",
        "🏷️ Categorias": "🏷️ Categorias",
        "📈 Relatórios": "📈 Relatórios",
    }

    for label in opcoes:
        ativo = st.session_state.menu == label
        css_class = "menu-btn-active" if ativo else ""
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.menu = label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-atualizar">', unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_refresh"):
        st.cache_data.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()
    st.markdown("<p style='color:#4B5563;font-size:0.72rem;text-align:center;padding:0.5rem 0'>© SofiHub 2026</p>", unsafe_allow_html=True)

menu = st.session_state.menu

# =====================
# HEADER
# =====================
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)

# ── Cor da tabela ──
def style_stock(row):
    styles = [''] * len(row)
    if 'Qtd_Atual' not in row.index or 'Estoque_Minimo' not in row.index:
        return styles
    val, min_v = row['Qtd_Atual'], row['Estoque_Minimo']
    bg = '#EF4444' if val <= 0 else ('#F97316' if val <= min_v else '#22C55E')
    idx = df_p.columns.get_loc('Qtd_Atual')
    styles[idx] = f'background:{bg};color:white;font-weight:700;border-radius:6px;padding:2px 8px;text-align:center;'
    return styles

# =====================
# DASHBOARD
# =====================
if menu == "📊 Dashboard":
    st.markdown('<div class="section-header">📊 Visão Geral</div>', unsafe_allow_html=True)

    total_prod  = len(df_p)
    total_estq  = int(df_p['Qtd_Atual'].sum()) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_alert = len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_cat   = len(df_c)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="card card-green"><div class="card-title">Total Produtos</div><div class="card-value" style="color:#22C55E">{total_prod}</div><div class="card-hint">👆 Ver todos os produtos</div></div>', unsafe_allow_html=True)
        if st.button("Ver Produtos", key="btn_prod", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"
            st.session_state.relatorio_tab = 1
            st.rerun()
    with c2:
        st.markdown(f'<div class="card card-orange"><div class="card-title">Estoque Total</div><div class="card-value" style="color:#F05A28">{total_estq}</div><div class="card-hint">👆 Ver estoque</div></div>', unsafe_allow_html=True)
        if st.button("Ver Estoque", key="btn_estq", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"
            st.session_state.relatorio_tab = 1
            st.rerun()
    with c3:
        st.markdown(f'<div class="card card-red"><div class="card-title">Alertas</div><div class="card-value" style="color:#EF4444">{total_alert}</div><div class="card-hint">👆 Ver alertas</div></div>', unsafe_allow_html=True)
        if st.button("Ver Alertas", key="btn_alert", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"
            st.session_state.relatorio_tab = 0
            st.rerun()
    with c4:
        st.markdown(f'<div class="card card-blue"><div class="card-title">Categorias</div><div class="card-value" style="color:#3B82F6">{total_cat}</div><div class="card-hint">👆 Gerenciar categorias</div></div>', unsafe_allow_html=True)
        if st.button("Ver Categorias", key="btn_cat", use_container_width=True):
            st.session_state.menu = "🏷️ Categorias"
            st.rerun()

    st.divider()

    tab1, tab2 = st.tabs(["⚡ Ações Rápidas", "🔍 Buscar & Filtrar"])

    with tab1:
        if not df_p.empty and 'Nome' in df_p.columns:
            col_p, col_q, col_ent, col_sai = st.columns([3, 1, 2, 2])
            prod_fast = col_p.selectbox("Produto", df_p['Nome'].tolist(), label_visibility="collapsed")
            qtd_fast  = col_q.number_input("Qtd", min_value=1, step=1, label_visibility="collapsed")
            if col_ent.button("➕ Entrada", use_container_width=True):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                df_p.at[idx, 'Qtd_Atual'] += qtd_fast
                conn.update(worksheet="Produtos", data=df_p)
                log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Entrada Rápida", "Qtd": qtd_fast, "Valor_Unitario": 0, "Total_Gasto": 0, "Observacao": "", "Usuario": usuario_nome}])
                conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                st.cache_data.clear()
                st.success(f"✅ +{qtd_fast} {prod_fast}")
                st.rerun()
            if col_sai.button("➖ Saída", use_container_width=True):
                idx = df_p.index[df_p['Nome'] == prod_fast][0]
                if df_p.at[idx, 'Qtd_Atual'] >= qtd_fast:
                    df_p.at[idx, 'Qtd_Atual'] -= qtd_fast
                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": prod_fast, "Tipo": "Saída Rápida", "Qtd": qtd_fast, "Valor_Unitario": 0, "Total_Gasto": 0, "Observacao": "", "Usuario": usuario_nome}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ -{qtd_fast} {prod_fast}")
                    st.rerun()
                else:
                    st.error("❌ Estoque insuficiente!")
        else:
            st.info("Nenhum produto cadastrado ainda.")

    with tab2:
        busca = st.text_input("🔍 Buscar produto por nome, categoria...")
        if not df_p.empty:
            df_view = df_p[df_p.apply(lambda r: busca.lower() in str(r).lower(), axis=1)] if busca else df_p
            if 'Qtd_Atual' in df_view.columns and not df_view.empty:
                st.dataframe(df_view.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_view, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum produto cadastrado.")

# =====================
# CADASTRAR
# =====================
elif menu == "➕ Cadastrar Produto":
    st.markdown('<div class="section-header">➕ Cadastrar Novo Produto</div>', unsafe_allow_html=True)

    categorias_lista = df_c['Nome'].tolist() if not df_c.empty and 'Nome' in df_c.columns else ["Geral"]
    unidades_lista   = ["un", "kg", "g", "L", "ml", "cx", "pç", "m", "m²"]

    with st.form("cadastro", clear_on_submit=True):

        st.markdown('<div class="form-section"><div class="form-section-title">📋 Identificação do Produto</div>', unsafe_allow_html=True)
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
        estoque_min = col7.number_input("Estoque Mínimo", min_value=0, step=1)
        col8, col9 = st.columns(2)
        preco_custo = col8.number_input("Preço de Custo (R$)", min_value=0.0, step=0.01, format="%.2f")
        preco_venda = col9.number_input("Preço de Venda (R$)", min_value=0.0, step=0.01, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.form_submit_button("✅ Cadastrar Produto", use_container_width=True):
            if not nome:
                st.error("❌ O nome do produto é obrigatório!")
            else:
                novo_id = int(df_p['ID'].max()) + 1 if not df_p.empty and 'ID' in df_p.columns else 1
                novo = pd.DataFrame([{
                    "ID": novo_id, "SKU": sku, "Nome": nome,
                    "Categoria": categoria, "Unidade": unidade,
                    "Qtd_Atual": qtd_inicial, "Estoque_Minimo": estoque_min,
                    "Preco_Custo": preco_custo, "Preco_Venda": preco_venda,
                    "Localizacao": localizacao
                }])
                conn.update(worksheet="Produtos", data=pd.concat([df_p, novo], ignore_index=True))
                st.cache_data.clear()
                st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")
                st.rerun()

# =====================
# MOVIMENTAÇÕES
# =====================
elif menu == "🔄 Movimentações":
    st.markdown('<div class="section-header">🔄 Movimentações de Estoque</div>', unsafe_allow_html=True)

    tab_reg, tab_hist = st.tabs(["📝 Registrar Movimentação", "📋 Histórico"])

    with tab_reg:
        if not df_p.empty and 'Nome' in df_p.columns:
            with st.form("movimentacao", clear_on_submit=True):

                st.markdown('<div class="form-section"><div class="form-section-title">📦 Produto e Tipo</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                produto_mov = col1.selectbox("Produto", df_p['Nome'].tolist())
                tipo_mov    = col2.selectbox("Tipo de Movimentação", ["Entrada", "Saída", "Ajuste de Estoque"])
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
                            st.error("❌ Estoque insuficiente!")
                            st.stop()
                        df_p.at[idx, 'Qtd_Atual'] = qtd_atual - qtd_mov
                    else:
                        df_p.at[idx, 'Qtd_Atual'] = qtd_mov

                    conn.update(worksheet="Produtos", data=df_p)
                    log = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Produto": produto_mov, "Tipo": tipo_mov,
                        "Qtd": qtd_mov, "Valor_Unitario": valor_unit,
                        "Total_Gasto": qtd_mov * valor_unit,
                        "Observacao": observacao, "Usuario": usuario_nome
                    }])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ {tipo_mov} de {qtd_mov}x {produto_mov} registrada!")
                    st.rerun()
        else:
            st.info("Cadastre produtos primeiro.")

    with tab_hist:
        if not df_m.empty:
            st.dataframe(df_m.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação registrada ainda.")

# =====================
# CATEGORIAS
# =====================
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
                if cc2.button("🗑️", key=f"del_cat_{i}", help="Excluir categoria"):
                    st.session_state[f"confirmar_del_{i}"] = True

                if st.session_state.get(f"confirmar_del_{i}"):
                    st.warning(f"⚠️ Tem certeza que quer excluir **{row['Nome']}**?")
                    c_sim, c_nao = st.columns(2)
                    if c_sim.button("✅ Sim, excluir", key=f"sim_{i}"):
                        df_c_novo = df_c.drop(index=i).reset_index(drop=True)
                        conn.update(worksheet="Categorias", data=df_c_novo)
                        st.cache_data.clear()
                        st.session_state.pop(f"confirmar_del_{i}", None)
                        st.success("🗑️ Categoria removida!")
                        st.rerun()
                    if c_nao.button("❌ Cancelar", key=f"nao_{i}"):
                        st.session_state.pop(f"confirmar_del_{i}", None)
                        st.rerun()
        else:
            st.info("Nenhuma categoria cadastrada.")

# =====================
# RELATÓRIOS
# =====================
elif menu == "📈 Relatórios":
    st.markdown('<div class="section-header">📈 Relatórios</div>', unsafe_allow_html=True)

    tab_idx = st.session_state.get('relatorio_tab', 0)
    tab_r1, tab_r2, tab_r3 = st.tabs(["⚠️ Estoque Baixo", "📦 Todos os Produtos", "💰 Movimentações"])

    # Força abertura na aba correta via JS
    if tab_idx == 1:
        st.session_state.relatorio_tab = 0  # reseta para não ficar em loop

    with tab_r1:
        st.markdown("#### ⚠️ Produtos com Estoque Baixo ou Zerado")
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
        st.markdown("#### 📦 Todos os Produtos")
        if not df_p.empty:
            cats_disp = ["Todas"] + (df_p['Categoria'].dropna().unique().tolist() if 'Categoria' in df_p.columns else [])
            filtro_cat = st.selectbox("Filtrar por Categoria", cats_disp)
            df_rel = df_p if filtro_cat == "Todas" else df_p[df_p['Categoria'] == filtro_cat]
            if 'Qtd_Atual' in df_rel.columns and not df_rel.empty:
                st.dataframe(df_rel.style.apply(style_stock, axis=1), use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_rel, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_r3:
        st.markdown("#### 💰 Histórico de Movimentações")
        if not df_m.empty:
            if 'Total_Gasto' in df_m.columns:
                total_mov = df_m['Total_Gasto'].sum()
                st.metric("💵 Total Movimentado", f"R$ {total_mov:,.2f}")
            st.dataframe(df_m.iloc[::-1].reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação registrada.")
