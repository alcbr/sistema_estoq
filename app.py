import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
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

if "logado"        not in st.session_state: st.session_state.logado        = False
if "usuario_atual" not in st.session_state: st.session_state.usuario_atual = None
if "menu"          not in st.session_state: st.session_state.menu          = "📊 Dashboard"
if "relatorio_tab" not in st.session_state: st.session_state.relatorio_tab = 0

def tela_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #F7F8FA; }
    .stButton > button {
        background: #F05A28 !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; padding: 0.65rem !important;
    }
    .stButton > button:hover { background: #D94E20 !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if os.path.exists("logo.jpg.png"):
            st.image("logo.jpg.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align:center;color:#111827;font-family:Inter,sans-serif'>📦 SofiHub</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#6B7280;font-size:0.85rem;margin-bottom:1.5rem;font-family:Inter,sans-serif'>Faça login para continuar</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario = st.text_input("Usuário").strip().lower()
            senha   = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
                    st.session_state.logado        = True
                    st.session_state.usuario_atual = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

if not st.session_state.logado:
    tela_login()
    st.stop()

usuario_nome = USUARIOS[st.session_state.usuario_atual]["nome"]

# =====================
# CSS GLOBAL
# =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #F7F8FA; }
.block-container { padding-top: 1.5rem !important; }

section[data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid #1F2937; }
section[data-testid="stSidebar"] * { color: #D1D5DB !important; }
section[data-testid="stSidebar"] .stRadio { display: none !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: #9CA3AF !important;
    border: none !important; border-radius: 8px !important;
    font-size: 0.9rem !important; font-weight: 500 !important;
    padding: 0.6rem 1rem !important; box-shadow: none !important;
    width: 100% !important; text-align: left !important;
    justify-content: flex-start !important; transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1F2937 !important; color: #F9FAFB !important;
    transform: none !important; box-shadow: none !important;
}
.menu-btn-active > button {
    background: #1F2937 !important; color: #F9FAFB !important;
    font-weight: 600 !important; border-left: 3px solid #F05A28 !important;
}
.sidebar-brand { padding: 1.25rem 1rem 0.75rem 1rem; border-bottom: 1px solid #1F2937; margin-bottom: 0.5rem; }
.sidebar-brand-name { color: #F9FAFB !important; font-size: 1rem !important; font-weight: 700 !important; display: block; }
.sidebar-brand-sub  { color: #6B7280 !important; font-size: 0.72rem !important; display: block; margin-top: 2px; }
.sidebar-divider { border-top: 1px solid #1F2937; margin: 0.5rem 0; }
.btn-atualizar > button, .btn-sair > button {
    background: #1F2937 !important; color: #9CA3AF !important;
    border: 1px solid #374151 !important; border-radius: 8px !important; font-size: 0.82rem !important;
}

.stButton > button {
    background: #F05A28 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    padding: 0.55rem 1.4rem !important; transition: all 0.15s !important; box-shadow: none !important;
}
.stButton > button:hover { background: #D94E20 !important; box-shadow: 0 4px 12px rgba(240,90,40,0.25) !important; }

.card { background: white; border-radius: 12px; padding: 1.25rem 1.5rem; border: 1px solid #E5E7EB; margin-bottom: 0.5rem; }
.card-title { font-size: 0.75rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.5rem; }
.card-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.card-hint  { font-size: 0.7rem; color: #9CA3AF; margin-top: 0.4rem; }
.card-green  { border-top: 3px solid #22C55E; }
.card-orange { border-top: 3px solid #F05A28; }
.card-red    { border-top: 3px solid #EF4444; }
.card-blue   { border-top: 3px solid #3B82F6; }
.card-purple { border-top: 3px solid #8B5CF6; }

.stForm { background: white !important; border-radius: 12px !important; padding: 1.5rem 2rem !important; border: 1px solid #E5E7EB !important; box-shadow: none !important; }
.form-section { border: 1px solid #E5E7EB; border-radius: 10px; padding: 1rem 1.25rem 0.25rem 1.25rem; margin-bottom: 1.25rem; background: #FAFAFA; }
.form-section-title { font-size: 0.72rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #E5E7EB; }

.section-header { font-size: 1.35rem; font-weight: 700; color: #111827; margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid #E5E7EB; }

.stTabs [data-baseweb="tab-list"] { background: white; border-radius: 10px; padding: 3px; border: 1px solid #E5E7EB; gap: 2px; }
.stTabs [data-baseweb="tab"] { border-radius: 7px !important; font-weight: 500 !important; font-size: 0.87rem !important; color: #6B7280 !important; padding: 0.4rem 1rem !important; }
.stTabs [aria-selected="true"] { background: #F05A28 !important; color: white !important; font-weight: 600 !important; }

.stDataFrame, [data-testid="stDataFrame"] { border-radius: 10px !important; border: 1px solid #E5E7EB !important; overflow: hidden; }
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
            if 'Data' in m.columns:
                m['Data_dt'] = pd.to_datetime(m['Data'], dayfirst=True, errors='coerce')
        if not c.empty:
            c.columns = c.columns.str.strip()
        return p, m, c
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)
    else:
        st.markdown('<div class="sidebar-brand"><span class="sidebar-brand-name">📦 SofiHub</span><span class="sidebar-brand-sub">Gestão de Estoque</span></div>', unsafe_allow_html=True)

    st.markdown(f"<div style='padding:0.4rem 1rem 0.6rem;'><span style='font-size:0.75rem;color:#6B7280;'>👤 <b style=\"color:#9CA3AF\">{usuario_nome}</b></span></div>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    for label in ["📊 Dashboard", "➕ Cadastrar Produto", "🔄 Movimentações", "🏷️ Categorias", "📈 Relatórios"]:
        ativo = st.session_state.menu == label
        st.markdown(f'<div class="{"menu-btn-active" if ativo else ""}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.menu = label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-atualizar">', unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_refresh"):
        st.cache_data.clear(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-sair">', unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        st.session_state.logado = False; st.session_state.usuario_atual = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#4B5563;font-size:0.72rem;text-align:center;padding:0.5rem 0'>© SofiHub 2026</p>", unsafe_allow_html=True)

menu = st.session_state.menu

# ── Header logo ──
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)

# ── Status tabela ──
def adicionar_status(df):
    df = df.copy()
    if 'Qtd_Atual' in df.columns and 'Estoque_Minimo' in df.columns:
        def status(row):
            if row['Qtd_Atual'] <= 0: return '🔴 Zerado'
            elif row['Qtd_Atual'] <= row['Estoque_Minimo']: return '🟠 Baixo'
            else: return '🟢 OK'
        df.insert(df.columns.get_loc('Qtd_Atual') + 1, 'Status', df.apply(status, axis=1))
    return df

# ── Excel export ──
def exportar_excel(df, nome_aba="Dados"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    return output.getvalue()

# ── Filtrar movimentações por data ──
def filtrar_por_data(df, col_data='Data_dt', data_ini=None, data_fim=None):
    if df.empty or col_data not in df.columns: return df
    df = df.copy()
    if data_ini:
        df = df[df[col_data] >= pd.Timestamp(data_ini)]
    if data_fim:
        df = df[df[col_data] <= pd.Timestamp(data_fim) + pd.Timedelta(days=1)]
    return df

# =====================
# DASHBOARD
# =====================
if menu == "📊 Dashboard":
    st.markdown('<div class="section-header">📊 Visão Geral</div>', unsafe_allow_html=True)

    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    total_prod  = len(df_p)
    total_estq  = int(df_p['Qtd_Atual'].sum()) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_alert = len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]) if not df_p.empty and 'Qtd_Atual' in df_p.columns else 0
    total_cat   = len(df_c)

    # Resumo do mês atual
    entradas_mes = saidas_mes = valor_mes = 0
    if not df_m.empty and 'Data_dt' in df_m.columns:
        df_mes = df_m[(df_m['Data_dt'].dt.month == mes_atual) & (df_m['Data_dt'].dt.year == ano_atual)]
        entradas_mes = int(df_mes[df_mes['Tipo'].str.contains('Entrada', na=False)]['Qtd'].sum()) if 'Qtd' in df_mes.columns else 0
        saidas_mes   = int(df_mes[df_mes['Tipo'].str.contains('Saída', na=False)]['Qtd'].sum()) if 'Qtd' in df_mes.columns else 0
        valor_mes    = df_mes[df_mes['Tipo'].str.contains('Entrada', na=False)]['Total_Gasto'].sum() if 'Total_Gasto' in df_mes.columns else 0

    # Cards principais
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

    # Resumo do mês
    st.markdown(f"#### 📅 Resumo de {hoje.strftime('%B/%Y')}")
    r1, r2, r3 = st.columns(3)
    r1.markdown(f'<div class="card card-green"><div class="card-title">Entradas no Mês</div><div class="card-value" style="color:#22C55E">{entradas_mes}</div><div class="card-hint">unidades</div></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="card card-red"><div class="card-title">Saídas no Mês</div><div class="card-value" style="color:#EF4444">{saidas_mes}</div><div class="card-hint">unidades</div></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="card card-purple"><div class="card-title">Valor Entradas Mês</div><div class="card-value" style="color:#8B5CF6">R$ {valor_mes:,.2f}</div><div class="card-hint">total gasto</div></div>', unsafe_allow_html=True)

    st.divider()

    # Gráfico de estoque
    if not df_p.empty and 'Qtd_Atual' in df_p.columns:
        st.markdown("#### 📊 Estoque por Produto")
        df_graf = df_p[['Nome', 'Qtd_Atual', 'Estoque_Minimo']].copy().sort_values('Qtd_Atual')
        st.bar_chart(df_graf.set_index('Nome')[['Qtd_Atual', 'Estoque_Minimo']])

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
                st.cache_data.clear(); st.success(f"✅ +{qtd_fast} {prod_fast}"); st.rerun()
            if col_sai.button("➖ Saída", use_container_width=True):
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

    with tab2:
        busca = st.text_input("🔍 Buscar produto por nome, categoria...")
        if not df_p.empty:
            df_view = df_p[df_p.apply(lambda r: busca.lower() in str(r).lower(), axis=1)] if busca else df_p
            st.dataframe(adicionar_status(df_view) if not df_view.empty else df_view, use_container_width=True, hide_index=True)
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
                st.success(f"✅ Produto '{nome}' cadastrado!")
                st.rerun()

# =====================
# MOVIMENTAÇÕES
# =====================
elif menu == "🔄 Movimentações":
    st.markdown('<div class="section-header">🔄 Movimentações de Estoque</div>', unsafe_allow_html=True)

    tab_reg, tab_hist, tab_media = st.tabs(["📝 Registrar", "📋 Histórico", "📊 Médias de Entrada"])

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
            st.markdown("##### 🔍 Filtros")
            fc1, fc2, fc3, fc4 = st.columns(4)

            prods_hist = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            tipos_hist = ["Todos"] + sorted(df_m['Tipo'].dropna().unique().tolist()) if 'Tipo' in df_m.columns else ["Todos"]

            filtro_prod = fc1.selectbox("Produto", prods_hist, key="hist_prod")
            filtro_tipo = fc2.selectbox("Tipo", tipos_hist, key="hist_tipo")
            data_ini    = fc3.date_input("De", value=None, key="hist_de")
            data_fim    = fc4.date_input("Até", value=None, key="hist_ate")

            df_hist = df_m.copy()
            if filtro_prod != "Todos": df_hist = df_hist[df_hist['Produto'] == filtro_prod]
            if filtro_tipo != "Todos": df_hist = df_hist[df_hist['Tipo']    == filtro_tipo]
            df_hist = filtrar_por_data(df_hist, data_ini=data_ini, data_fim=data_fim)

            df_show = df_hist.drop(columns=['Data_dt'], errors='ignore').iloc[::-1].reset_index(drop=True)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            excel_hist = exportar_excel(df_show, "Histórico")
            st.download_button("📥 Exportar Excel", data=excel_hist,
                               file_name=f"historico_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhuma movimentação registrada ainda.")

    with tab_media:
        st.markdown("##### 📊 Média de Entradas por Produto")
        if not df_m.empty and 'Data_dt' in df_m.columns:
            # Filtros da média
            mc1, mc2, mc3 = st.columns(3)
            prods_med = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            filtro_prod_med = mc1.selectbox("Produto", prods_med, key="med_prod")
            data_ini_med    = mc2.date_input("De", value=None, key="med_de")
            data_fim_med    = mc3.date_input("Até", value=None, key="med_ate")

            df_ent = df_m[df_m['Tipo'].str.contains('Entrada', na=False)].copy()
            if filtro_prod_med != "Todos":
                df_ent = df_ent[df_ent['Produto'] == filtro_prod_med]
            df_ent = filtrar_por_data(df_ent, data_ini=data_ini_med, data_fim=data_fim_med)

            if not df_ent.empty:
                df_ent['Mes'] = df_ent['Data_dt'].dt.to_period('M').astype(str)
                n_meses = df_ent['Mes'].nunique()
                n_meses = max(n_meses, 1)

                resumo = df_ent.groupby('Produto').agg(
                    Total_Unidades=('Qtd', 'sum'),
                    Total_Valor=('Total_Gasto', 'sum'),
                    Num_Entradas=('Qtd', 'count')
                ).reset_index()

                resumo['Média Unid/Mês'] = (resumo['Total_Unidades'] / n_meses).round(1)
                resumo['Média R$/Mês']   = (resumo['Total_Valor']    / n_meses).round(2)
                resumo['Média R$/Mês']   = resumo['Média R$/Mês'].apply(lambda x: f"R$ {x:,.2f}")

                st.info(f"📅 Calculado sobre **{n_meses} mês(es)** no período selecionado.")
                st.dataframe(resumo[['Produto', 'Total_Unidades', 'Total_Valor', 'Num_Entradas', 'Média Unid/Mês', 'Média R$/Mês']],
                             use_container_width=True, hide_index=True)

                # Gráfico de entradas ao longo do tempo
                st.markdown("##### 📈 Entradas ao Longo do Tempo")
                df_graf = df_ent.groupby('Mes')['Qtd'].sum().reset_index()
                df_graf.columns = ['Mês', 'Unidades Entrada']
                st.bar_chart(df_graf.set_index('Mês'))

                excel_med = exportar_excel(resumo, "Médias")
                st.download_button("📥 Exportar Excel", data=excel_med,
                                   file_name=f"medias_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Nenhuma entrada encontrada para os filtros selecionados.")
        else:
            st.info("Sem dados de movimentação para calcular médias.")

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
                    st.success(f"✅ '{nova_cat}' adicionada!")
                    st.rerun()

    with col_l:
        st.markdown("#### 📋 Categorias Cadastradas")
        if not df_c.empty and 'Nome' in df_c.columns:
            for i, row in df_c.iterrows():
                cc1, cc2 = st.columns([4, 1])
                desc     = row.get('Descricao', '')
                desc_txt = f" — {desc}" if pd.notna(desc) and str(desc).strip() else ""
                cc1.markdown(f"**{row['Nome']}**{desc_txt}")
                if cc2.button("🗑️", key=f"del_cat_{i}"):
                    st.session_state[f"confirmar_del_{i}"] = True
                if st.session_state.get(f"confirmar_del_{i}"):
                    st.warning(f"⚠️ Excluir **{row['Nome']}**?")
                    cs, cn = st.columns(2)
                    if cs.button("✅ Sim", key=f"sim_{i}"):
                        conn.update(worksheet="Categorias", data=df_c.drop(index=i).reset_index(drop=True))
                        st.cache_data.clear(); st.session_state.pop(f"confirmar_del_{i}", None)
                        st.success("🗑️ Removida!"); st.rerun()
                    if cn.button("❌ Cancelar", key=f"nao_{i}"):
                        st.session_state.pop(f"confirmar_del_{i}", None); st.rerun()
        else:
            st.info("Nenhuma categoria cadastrada.")

# =====================
# RELATÓRIOS
# =====================
elif menu == "📈 Relatórios":
    st.markdown('<div class="section-header">📈 Relatórios</div>', unsafe_allow_html=True)

    tab_r1, tab_r2, tab_r3 = st.tabs(["⚠️ Estoque Baixo", "📦 Todos os Produtos", "💰 Movimentações"])

    with tab_r1:
        st.markdown("#### ⚠️ Estoque Baixo ou Zerado")
        if not df_p.empty and 'Qtd_Atual' in df_p.columns:
            df_alerta = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]
            if not df_alerta.empty:
                st.warning(f"⚠️ {len(df_alerta)} produto(s) precisam de atenção!")
                st.dataframe(adicionar_status(df_alerta), use_container_width=True, hide_index=True)
                excel_alerta = exportar_excel(df_alerta, "Estoque Baixo")
                st.download_button("📥 Exportar Excel", data=excel_alerta,
                                   file_name=f"estoque_baixo_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.success("✅ Todos os produtos estão com estoque adequado!")
        else:
            st.info("Nenhum dado disponível.")

    with tab_r2:
        st.markdown("#### 📦 Todos os Produtos")
        if not df_p.empty:
            cats_disp  = ["Todas"] + (df_p['Categoria'].dropna().unique().tolist() if 'Categoria' in df_p.columns else [])
            filtro_cat = st.selectbox("Filtrar por Categoria", cats_disp)
            df_rel     = df_p if filtro_cat == "Todas" else df_p[df_p['Categoria'] == filtro_cat]
            st.dataframe(adicionar_status(df_rel) if not df_rel.empty else df_rel, use_container_width=True, hide_index=True)
            excel_prod = exportar_excel(df_rel, "Produtos")
            st.download_button("📥 Exportar Excel", data=excel_prod,
                               file_name=f"produtos_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_r3:
        st.markdown("#### 💰 Histórico de Movimentações")
        if not df_m.empty:
            # Filtros
            rc1, rc2, rc3, rc4 = st.columns(4)
            prods_r = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            tipos_r = ["Todos"] + sorted(df_m['Tipo'].dropna().unique().tolist()) if 'Tipo' in df_m.columns else ["Todos"]
            filtro_prod_r = rc1.selectbox("Produto", prods_r, key="rel_prod")
            filtro_tipo_r = rc2.selectbox("Tipo",    tipos_r, key="rel_tipo")
            data_ini_r    = rc3.date_input("De",  value=None, key="rel_de")
            data_fim_r    = rc4.date_input("Até", value=None, key="rel_ate")

            df_mov = df_m.copy()
            if filtro_prod_r != "Todos": df_mov = df_mov[df_mov['Produto'] == filtro_prod_r]
            if filtro_tipo_r != "Todos": df_mov = df_mov[df_mov['Tipo']    == filtro_tipo_r]
            df_mov = filtrar_por_data(df_mov, data_ini=data_ini_r, data_fim=data_fim_r)

            if 'Total_Gasto' in df_mov.columns:
                st.metric("💵 Total no período", f"R$ {df_mov['Total_Gasto'].sum():,.2f}")

            df_mov_show = df_mov.drop(columns=['Data_dt'], errors='ignore').iloc[::-1].reset_index(drop=True)
            st.dataframe(df_mov_show, use_container_width=True, hide_index=True)

            excel_mov = exportar_excel(df_mov_show, "Movimentações")
            st.download_button("📥 Exportar Excel", data=excel_mov,
                               file_name=f"movimentacoes_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhuma movimentação registrada.")
