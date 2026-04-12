import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date, timedelta
import os
import io

st.set_page_config(page_title="SofiHub - Gestão de Estoque", layout="wide", page_icon="📦")

# =====================
# USUÁRIOS E LOGIN
# =====================
USUARIOS = {
    "leiapollone": {"senha": "1234321", "nome": "Leia Pollone"},
    "murilobraga": {"senha": "1234321", "nome": "Murilo Braga"},
    "visitante":   {"senha": "43211234", "nome": "Visitante"},
}

for k, v in {"logado": False, "usuario_atual": None, "menu": "📊 Dashboard", "relatorio_tab": 0}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================
# LOGIN
# =====================
def tela_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #F7F8FA; }
    .stButton > button { background: #F05A28 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 0.65rem !important; }
    .stButton > button:hover { background: #D94E20 !important; }
    </style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if os.path.exists("logo.jpg.png"):
            st.image("logo.jpg.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align:center;color:#111827'>📦 SofiHub</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#6B7280;font-size:0.85rem;margin-bottom:1rem'>Faça login para continuar</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario = st.text_input("Usuário").strip().lower()
            senha   = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
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

# =====================
# CSS
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
    background: transparent !important; color: #9CA3AF !important; border: none !important;
    border-radius: 8px !important; font-size: 0.9rem !important; font-weight: 500 !important;
    padding: 0.6rem 1rem !important; box-shadow: none !important; width: 100% !important;
    text-align: left !important; justify-content: flex-start !important; transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #1F2937 !important; color: #F9FAFB !important; transform: none !important; box-shadow: none !important; }
.menu-btn-active > button { background: #1F2937 !important; color: #F9FAFB !important; font-weight: 600 !important; border-left: 3px solid #F05A28 !important; }
.sidebar-brand { padding: 1.25rem 1rem 0.75rem 1rem; border-bottom: 1px solid #1F2937; margin-bottom: 0.5rem; }
.sidebar-brand-name { color: #F9FAFB !important; font-size: 1rem !important; font-weight: 700 !important; display: block; }
.sidebar-brand-sub { color: #6B7280 !important; font-size: 0.72rem !important; display: block; margin-top: 2px; }
.sidebar-divider { border-top: 1px solid #1F2937; margin: 0.5rem 0; }
.btn-util > button { background: #1F2937 !important; color: #9CA3AF !important; border: 1px solid #374151 !important; border-radius: 8px !important; font-size: 0.82rem !important; }
.stButton > button { background: #F05A28 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.88rem !important; padding: 0.55rem 1.4rem !important; transition: all 0.15s !important; box-shadow: none !important; }
.stButton > button:hover { background: #D94E20 !important; box-shadow: 0 4px 12px rgba(240,90,40,0.25) !important; }
.card { background: white; border-radius: 12px; padding: 1.25rem 1.5rem; border: 1px solid #E5E7EB; margin-bottom: 0.5rem; }
.card-title { font-size: 0.75rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.5rem; }
.card-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.card-hint { font-size: 0.7rem; color: #9CA3AF; margin-top: 0.4rem; }
.card-green { border-top: 3px solid #22C55E; }
.card-orange { border-top: 3px solid #F05A28; }
.card-red { border-top: 3px solid #EF4444; }
.card-blue { border-top: 3px solid #3B82F6; }
.card-purple { border-top: 3px solid #8B5CF6; }
.card-yellow { border-top: 3px solid #F59E0B; }
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
.info-box { background: white; border-radius: 12px; padding: 1rem 1.5rem; border: 1px solid #E5E7EB; margin-bottom: 1rem; }
</style>""", unsafe_allow_html=True)

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
            for col in ['Qtd_Atual', 'Estoque_Minimo', 'ID']:
                if col in p.columns:
                    p[col] = pd.to_numeric(p[col], errors='coerce').fillna(0).astype(int)
            for col in ['Preco_Custo', 'Preco_Venda']:
                if col in p.columns:
                    p[col] = pd.to_numeric(p[col], errors='coerce').fillna(0.0)
        if not m.empty:
            m.columns = m.columns.str.strip()
            for col in ['Total_Gasto', 'Valor_Unitario', 'Qtd']:
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
    st.markdown(f"<div style='padding:0.4rem 1rem 0.6rem'><span style='font-size:0.75rem;color:#6B7280'>👤 <b style=\"color:#9CA3AF\">{usuario_nome}</b></span></div>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    for label in ["📊 Dashboard", "➕ Cadastrar Produto", "🔄 Movimentações", "🏷️ Categorias", "📈 Relatórios"]:
        ativo = st.session_state.menu == label
        st.markdown(f'<div class="{"menu-btn-active" if ativo else ""}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.menu = label; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-util">', unsafe_allow_html=True)
    if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_refresh"):
        st.cache_data.clear(); st.rerun()
    st.markdown('</div><div class="btn-util">', unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
        st.session_state.logado = False; st.session_state.usuario_atual = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#4B5563;font-size:0.72rem;text-align:center;padding:0.5rem 0'>© SofiHub 2026</p>", unsafe_allow_html=True)

menu = st.session_state.menu

# Header logo
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    if os.path.exists("logo.jpg.png"):
        st.image("logo.jpg.png", use_container_width=True)

# ── Helpers ──
def adicionar_status(df):
    df = df.copy()
    if 'Qtd_Atual' in df.columns and 'Estoque_Minimo' in df.columns:
        def s(r):
            if r['Qtd_Atual'] <= 0: return '🔴 Zerado'
            elif r['Qtd_Atual'] <= r['Estoque_Minimo']: return '🟠 Baixo'
            else: return '🟢 OK'
        df.insert(df.columns.get_loc('Qtd_Atual') + 1, 'Status', df.apply(s, axis=1))
    return df

def exportar_excel(df, nome_aba="Dados"):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df.to_excel(w, index=False, sheet_name=nome_aba)
    return out.getvalue()

def filtrar_mov(df, prod=None, tipo=None, d_ini=None, d_fim=None):
    if df.empty: return df
    d = df.copy()
    if prod and prod != "Todos": d = d[d['Produto'] == prod]
    if tipo and tipo != "Todos": d = d[d['Tipo'] == tipo]
    if d_ini and 'Data_dt' in d.columns: d = d[d['Data_dt'] >= pd.Timestamp(d_ini)]
    if d_fim and 'Data_dt' in d.columns: d = d[d['Data_dt'] <= pd.Timestamp(d_fim) + pd.Timedelta(days=1)]
    return d

def periodo_datas(opcao, mes_custom=None, ano_custom=None):
    hoje = datetime.now()
    if opcao == "Mês atual":
        ini = date(hoje.year, hoje.month, 1)
        fim = hoje.date()
    elif opcao == "Mês específico" and mes_custom and ano_custom:
        ini = date(ano_custom, mes_custom, 1)
        ultimo_dia = (date(ano_custom, mes_custom % 12 + 1, 1) - timedelta(days=1)) if mes_custom < 12 else date(ano_custom, 12, 31)
        fim = ultimo_dia
    elif opcao == "Trimestre atual":
        trim = (hoje.month - 1) // 3
        ini = date(hoje.year, trim * 3 + 1, 1)
        fim = hoje.date()
    elif opcao == "Semestre atual":
        ini = date(hoje.year, 1, 1) if hoje.month <= 6 else date(hoje.year, 7, 1)
        fim = hoje.date()
    elif opcao == "Ano atual":
        ini = date(hoje.year, 1, 1)
        fim = hoje.date()
    else:
        ini = date(hoje.year, hoje.month, 1)
        fim = hoje.date()
    return ini, fim

MESES_PT = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
            7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

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
        st.markdown(f'<div class="card card-green"><div class="card-title">Total Produtos</div><div class="card-value" style="color:#22C55E">{total_prod}</div><div class="card-hint">👆 Ver todos</div></div>', unsafe_allow_html=True)
        if st.button("Ver Produtos", key="btn_prod", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.rerun()
    with c2:
        st.markdown(f'<div class="card card-orange"><div class="card-title">Estoque Total</div><div class="card-value" style="color:#F05A28">{total_estq}</div><div class="card-hint">👆 Ver estoque</div></div>', unsafe_allow_html=True)
        if st.button("Ver Estoque", key="btn_estq", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.rerun()
    with c3:
        st.markdown(f'<div class="card card-red"><div class="card-title">⚠️ Alertas</div><div class="card-value" style="color:#EF4444">{total_alert}</div><div class="card-hint">👆 Ver alertas</div></div>', unsafe_allow_html=True)
        if st.button("Ver Alertas", key="btn_alert", use_container_width=True):
            st.session_state.menu = "📈 Relatórios"; st.rerun()
    with c4:
        st.markdown(f'<div class="card card-blue"><div class="card-title">Categorias</div><div class="card-value" style="color:#3B82F6">{total_cat}</div><div class="card-hint">👆 Gerenciar</div></div>', unsafe_allow_html=True)
        if st.button("Ver Categorias", key="btn_cat", use_container_width=True):
            st.session_state.menu = "🏷️ Categorias"; st.rerun()

    # ── Resumo por período ──
    st.divider()
    st.markdown("#### 📅 Resumo por Período")

    hoje = datetime.now()
    rp1, rp2, rp3 = st.columns(3)
    opcao_periodo = rp1.selectbox("Período", ["Mês atual", "Mês específico", "Trimestre atual", "Semestre atual", "Ano atual"], key="dash_periodo")
    mes_sel = ano_sel = None
    if opcao_periodo == "Mês específico":
        mes_sel = rp2.selectbox("Mês", list(MESES_PT.keys()), format_func=lambda x: MESES_PT[x], index=hoje.month - 1, key="dash_mes")
        ano_sel = rp3.number_input("Ano", min_value=2020, max_value=2030, value=hoje.year, key="dash_ano")

    d_ini_dash, d_fim_dash = periodo_datas(opcao_periodo, mes_sel, ano_sel)

    entradas_p = saidas_p = valor_ent = valor_sai = 0
    if not df_m.empty and 'Data_dt' in df_m.columns and 'Tipo' in df_m.columns:
        df_periodo = filtrar_mov(df_m, d_ini=d_ini_dash, d_fim=d_fim_dash)
        df_ent_p = df_periodo[df_periodo['Tipo'].str.contains('Entrada', na=False, case=False)]
        df_sai_p = df_periodo[df_periodo['Tipo'].str.contains('Saída|Saida', na=False, case=False)]
        entradas_p = int(df_ent_p['Qtd'].sum()) if 'Qtd' in df_ent_p.columns else 0
        saidas_p   = int(df_sai_p['Qtd'].sum()) if 'Qtd' in df_sai_p.columns else 0
        valor_ent  = df_ent_p['Total_Gasto'].sum() if 'Total_Gasto' in df_ent_p.columns else 0
        valor_sai  = df_sai_p['Total_Gasto'].sum() if 'Total_Gasto' in df_sai_p.columns else 0

    label_periodo = f"{d_ini_dash.strftime('%d/%m/%Y')} → {d_fim_dash.strftime('%d/%m/%Y')}"
    st.caption(f"📆 {label_periodo}")

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="card card-green"><div class="card-title">Entradas</div><div class="card-value" style="color:#22C55E">{entradas_p}</div><div class="card-hint">unidades</div></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="card card-red"><div class="card-title">Saídas</div><div class="card-value" style="color:#EF4444">{saidas_p}</div><div class="card-hint">unidades</div></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="card card-purple"><div class="card-title">Gasto em Entradas</div><div class="card-value" style="color:#8B5CF6;font-size:1.4rem">R$ {valor_ent:,.2f}</div><div class="card-hint">total pago</div></div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="card card-yellow"><div class="card-title">Saldo do Período</div><div class="card-value" style="color:#F59E0B;font-size:1.4rem">{entradas_p - saidas_p:+d}</div><div class="card-hint">entradas - saídas</div></div>', unsafe_allow_html=True)

    # ── Gráfico estoque ──
    st.divider()
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
        busca = st.text_input("🔍 Buscar por nome, categoria, SKU...")
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
                novo = pd.DataFrame([{"ID": novo_id, "SKU": sku, "Nome": nome, "Categoria": categoria,
                                       "Unidade": unidade, "Qtd_Atual": qtd_inicial, "Estoque_Minimo": estoque_min,
                                       "Preco_Custo": preco_custo, "Preco_Venda": preco_venda, "Localizacao": localizacao}])
                conn.update(worksheet="Produtos", data=pd.concat([df_p, novo], ignore_index=True))
                st.cache_data.clear(); st.success(f"✅ Produto '{nome}' cadastrado!"); st.rerun()

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

                st.markdown('<div class="form-section"><div class="form-section-title">🔢 Quantidade, Unidade e Valor</div>', unsafe_allow_html=True)
                col3, col4, col5 = st.columns(3)
                qtd_mov    = col3.number_input("Quantidade", min_value=1, step=1)
                unidades_mov = ["un", "kg", "g", "L", "ml", "cx", "pç", "m", "m²"]
                # Pré-seleciona a unidade do produto escolhido
                unidade_prod = "un"
                if not df_p.empty and 'Unidade' in df_p.columns:
                    rows = df_p[df_p['Nome'] == produto_mov]
                    if not rows.empty:
                        u = str(rows.iloc[0].get('Unidade', 'un'))
                        if u in unidades_mov:
                            unidade_prod = u
                uni_idx = unidades_mov.index(unidade_prod) if unidade_prod in unidades_mov else 0
                unidade_mov = col4.selectbox("Unidade", unidades_mov, index=uni_idx)
                valor_unit  = col5.number_input("Valor Unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
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
                                          "Tipo": tipo_mov, "Qtd": qtd_mov, "Unidade": unidade_mov,
                                          "Valor_Unitario": valor_unit, "Total_Gasto": qtd_mov * valor_unit,
                                          "Observacao": observacao, "Usuario": usuario_nome}])
                    conn.update(worksheet="Movimentacoes", data=pd.concat([df_m, log], ignore_index=True))
                    st.cache_data.clear(); st.success(f"✅ {tipo_mov} de {qtd_mov} {unidade_mov} de {produto_mov} registrada!"); st.rerun()
        else:
            st.info("Cadastre produtos primeiro.")

    with tab_hist:
        if not df_m.empty:
            st.markdown("##### 🔍 Filtros")
            fc1, fc2, fc3, fc4 = st.columns(4)
            prods_h = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            tipos_h = ["Todos"] + sorted(df_m['Tipo'].dropna().unique().tolist()) if 'Tipo' in df_m.columns else ["Todos"]
            fp  = fc1.selectbox("Produto", prods_h, key="h_prod")
            ft  = fc2.selectbox("Tipo", tipos_h, key="h_tipo")
            di  = fc3.date_input("De",  value=None, key="h_de")
            df_ = fc4.date_input("Até", value=None, key="h_ate")

            df_hist = filtrar_mov(df_m, prod=fp, tipo=ft, d_ini=di, d_fim=df_)

            # Caixa de total
            if not df_hist.empty:
                total_ent_h = int(df_hist[df_hist['Tipo'].str.contains('Entrada', na=False, case=False)]['Qtd'].sum()) if 'Qtd' in df_hist.columns else 0
                total_sai_h = int(df_hist[df_hist['Tipo'].str.contains('Saída|Saida', na=False, case=False)]['Qtd'].sum()) if 'Qtd' in df_hist.columns else 0
                total_val_h = df_hist['Total_Gasto'].sum() if 'Total_Gasto' in df_hist.columns else 0
                m1, m2, m3 = st.columns(3)
                m1.metric("📥 Total Entradas", f"{total_ent_h} un")
                m2.metric("📤 Total Saídas",   f"{total_sai_h} un")
                m3.metric("💰 Valor Total",     f"R$ {total_val_h:,.2f}")

            df_show = df_hist.drop(columns=['Data_dt'], errors='ignore').iloc[::-1].reset_index(drop=True)
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            excel_h = exportar_excel(df_show, "Histórico")
            st.download_button("📥 Exportar Excel", data=excel_h,
                               file_name=f"historico_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhuma movimentação registrada ainda.")

    with tab_media:
        st.markdown("##### 📊 Média de Entradas por Produto")
        if not df_m.empty and 'Data_dt' in df_m.columns:
            mc1, mc2, mc3, mc4 = st.columns(4)
            prods_m = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            fp_m = mc1.selectbox("Produto", prods_m, key="m_prod")
            di_m = mc2.date_input("De",  value=None, key="m_de")
            df_m2 = mc3.date_input("Até", value=None, key="m_ate")

            df_ent = df_m[df_m['Tipo'].str.contains('Entrada', na=False, case=False)].copy()
            df_ent = filtrar_mov(df_ent, prod=fp_m, d_ini=di_m, d_fim=df_m2)

            if not df_ent.empty:
                df_ent['Mes'] = df_ent['Data_dt'].dt.to_period('M').astype(str)
                n_meses = max(df_ent['Mes'].nunique(), 1)
                resumo = df_ent.groupby('Produto').agg(
                    Total_Unidades=('Qtd', 'sum'),
                    Total_Valor=('Total_Gasto', 'sum'),
                    Num_Entradas=('Qtd', 'count')
                ).reset_index()
                resumo['Média Unid/Mês'] = (resumo['Total_Unidades'] / n_meses).round(1)
                resumo['Média R$/Mês']   = resumo['Total_Valor'] / n_meses
                resumo['Média R$/Mês fmt'] = resumo['Média R$/Mês'].apply(lambda x: f"R$ {x:,.2f}")

                st.info(f"📅 Calculado sobre **{n_meses} mês(es)**.")
                st.dataframe(resumo[['Produto','Total_Unidades','Total_Valor','Num_Entradas','Média Unid/Mês','Média R$/Mês fmt']].rename(columns={'Média R$/Mês fmt':'Média R$/Mês'}),
                             use_container_width=True, hide_index=True)

                st.markdown("##### 📈 Entradas ao Longo do Tempo")
                df_g = df_ent.groupby('Mes')['Qtd'].sum().reset_index()
                df_g.columns = ['Mês', 'Unidades']
                st.bar_chart(df_g.set_index('Mês'))

                excel_m = exportar_excel(resumo.drop(columns=['Média R$/Mês'], errors='ignore'), "Médias")
                st.download_button("📥 Exportar Excel", data=excel_m,
                                   file_name=f"medias_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Nenhuma entrada encontrada para os filtros selecionados.")
        else:
            st.info("Sem dados para calcular médias.")

# =====================
# CATEGORIAS
# =====================
elif menu == "🏷️ Categorias":
    st.markdown('<div class="section-header">🏷️ Gerenciar Categorias</div>', unsafe_allow_html=True)
    col_f, col_l = st.columns(2)
    with col_f:
        st.markdown("#### ➕ Nova Categoria")
        with st.form("nova_categoria", clear_on_submit=True):
            nova_cat      = st.text_input("Nome *")
            descricao_cat = st.text_input("Descrição (opcional)")
            if st.form_submit_button("✅ Adicionar", use_container_width=True):
                if not nova_cat: st.error("❌ Nome obrigatório!")
                else:
                    nova_linha = pd.DataFrame([{"Nome": nova_cat, "Descricao": descricao_cat}])
                    conn.update(worksheet="Categorias", data=pd.concat([df_c, nova_linha], ignore_index=True))
                    st.cache_data.clear(); st.success(f"✅ '{nova_cat}' adicionada!"); st.rerun()
    with col_l:
        st.markdown("#### 📋 Cadastradas")
        if not df_c.empty and 'Nome' in df_c.columns:
            for i, row in df_c.iterrows():
                cc1, cc2 = st.columns([4, 1])
                desc = row.get('Descricao', '')
                desc_txt = f" — {desc}" if pd.notna(desc) and str(desc).strip() else ""
                cc1.markdown(f"**{row['Nome']}**{desc_txt}")
                if cc2.button("🗑️", key=f"del_cat_{i}"):
                    st.session_state[f"confirmar_del_{i}"] = True
                if st.session_state.get(f"confirmar_del_{i}"):
                    st.warning(f"⚠️ Excluir **{row['Nome']}**?")
                    cs, cn = st.columns(2)
                    if cs.button("✅ Sim", key=f"sim_{i}"):
                        conn.update(worksheet="Categorias", data=df_c.drop(index=i).reset_index(drop=True))
                        st.cache_data.clear(); st.session_state.pop(f"confirmar_del_{i}", None); st.success("🗑️ Removida!"); st.rerun()
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
                st.download_button("📥 Exportar Excel", data=exportar_excel(df_alerta, "Estoque Baixo"),
                                   file_name=f"estoque_baixo_{datetime.now().strftime('%d%m%Y')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.success("✅ Todos os produtos estão com estoque adequado!")
        else:
            st.info("Nenhum dado disponível.")

    with tab_r2:
        st.markdown("#### 📦 Todos os Produtos")
        if not df_p.empty:
            rc1, rc2 = st.columns(2)
            cats_disp  = ["Todas"] + (df_p['Categoria'].dropna().unique().tolist() if 'Categoria' in df_p.columns else [])
            filtro_cat = rc1.selectbox("Filtrar por Categoria", cats_disp)
            df_rel = df_p if filtro_cat == "Todas" else df_p[df_p['Categoria'] == filtro_cat]

            # Totais dos produtos filtrados
            if not df_rel.empty:
                tot1, tot2, tot3 = st.columns(3)
                tot1.metric("📦 Produtos", len(df_rel))
                tot2.metric("🔢 Qtd Total", int(df_rel['Qtd_Atual'].sum()) if 'Qtd_Atual' in df_rel.columns else 0)
                val_estq = (df_rel['Qtd_Atual'] * df_rel['Preco_Custo']).sum() if 'Preco_Custo' in df_rel.columns else 0
                tot3.metric("💰 Valor em Estoque", f"R$ {val_estq:,.2f}")

            st.dataframe(adicionar_status(df_rel) if not df_rel.empty else df_rel, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar Excel", data=exportar_excel(df_rel, "Produtos"),
                               file_name=f"produtos_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_r3:
        st.markdown("#### 💰 Movimentações")
        if not df_m.empty:
            rc1, rc2, rc3, rc4 = st.columns(4)
            prods_r = ["Todos"] + sorted(df_m['Produto'].dropna().unique().tolist()) if 'Produto' in df_m.columns else ["Todos"]
            tipos_r = ["Todos"] + sorted(df_m['Tipo'].dropna().unique().tolist()) if 'Tipo' in df_m.columns else ["Todos"]
            fp_r = rc1.selectbox("Produto", prods_r, key="r_prod")
            ft_r = rc2.selectbox("Tipo",    tipos_r, key="r_tipo")
            di_r = rc3.date_input("De",  value=None, key="r_de")
            df_r = rc4.date_input("Até", value=None, key="r_ate")

            df_mov = filtrar_mov(df_m, prod=fp_r, tipo=ft_r, d_ini=di_r, d_fim=df_r)

            # Caixa de totais
            if not df_mov.empty:
                t1, t2, t3 = st.columns(3)
                te = int(df_mov[df_mov['Tipo'].str.contains('Entrada', na=False, case=False)]['Qtd'].sum()) if 'Qtd' in df_mov.columns else 0
                ts = int(df_mov[df_mov['Tipo'].str.contains('Saída|Saida', na=False, case=False)]['Qtd'].sum()) if 'Qtd' in df_mov.columns else 0
                tv = df_mov['Total_Gasto'].sum() if 'Total_Gasto' in df_mov.columns else 0
                t1.metric("📥 Entradas no período", f"{te} un")
                t2.metric("📤 Saídas no período",   f"{ts} un")
                t3.metric("💵 Valor total",          f"R$ {tv:,.2f}")

            df_mov_show = df_mov.drop(columns=['Data_dt'], errors='ignore').iloc[::-1].reset_index(drop=True)
            st.dataframe(df_mov_show, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar Excel", data=exportar_excel(df_mov_show, "Movimentações"),
                               file_name=f"movimentacoes_{datetime.now().strftime('%d%m%Y')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Nenhuma movimentação registrada.")
