import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA E IDENTIDADE SOFIHUB
st.set_page_config(page_title="SofiHub - Gestão Inteligente", layout="wide", page_icon="🚀")

# Estilização CSS para forçar a paleta da Logo SofiHub (Azul Petróleo e Laranja)
st.markdown("""
    <style>
    /* Cores de Fundo e Texto */
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, p, label { color: #0A2540 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Botões com o Laranja SofiHub */
    .stButton>button {
        background-color: #F05A28 !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #D64C20 !important; }
    
    /* Cards de Métricas Estilizados */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM GOOGLE SHEETS
# Certifique-se de configurar o link da planilha no menu 'Secrets' do Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Tenta ler as abas. ttl=0 garante que os dados não fiquem em cache antigo
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        return p, m
    except Exception:
        # Estrutura padrão caso a planilha esteja vazia ou dê erro inicial
        cols_p = ["ID", "SKU", "Nome", "Categoria", "Qtd_Atual", "Estoque_Minimo", "Preco_Custo", "Preco_Venda", "Localizacao"]
        cols_m = ["Data_Hora", "SKU", "Produto", "Tipo", "Qtd", "Motivo", "Usuario"]
        return pd.DataFrame(columns=cols_p), pd.DataFrame(columns=cols_m)

df_p, df_m = carregar_dados()

# 3. BARRA LATERAL (MENU E LOGO)
with st.sidebar:
    # Tenta carregar a logo da raiz do repositório
    caminho_logo = "logo.jpg"
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.markdown("### 🚀 SofiHub")
        st.caption("Faça o upload da 'logo.jpg' no GitHub para exibir sua marca.")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard", "🆕 Cadastrar Item", "🔄 Movimentar Estoque", "🔧 Editar / Excluir", "📋 Relatórios"])
    st.markdown("---")
    st.caption("v1.0 | Hub de Soluções Tecnológicas")

# --- ABA 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Painel de Controle SofiHub")
    
    if not df_p.empty:
        # Garantir que colunas numéricas sejam tratadas corretamente
        df_p['Qtd_Atual'] = pd.to_numeric(df_p['Qtd_Atual'], errors='coerce').fillna(0)
        df_p['Estoque_Minimo'] = pd.to_numeric(df_p['Estoque_Minimo'], errors='coerce').fillna(0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Produtos Cadastrados", len(df_p))
        
        alertas = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]
        c2.metric("Itens Críticos", len(alertas), delta_color="inverse")
        
        capital = (df_p['Qtd_Atual'] * pd.to_numeric(df_p['Preco_Custo'], errors='coerce').fillna(0)).sum()
        c3.metric("Capital em Estoque", f"R$ {capital:,.2f}")

        st.markdown("### 📋 Inventário Atual")
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        if not alertas.empty:
            st.warning(f"⚠️ Atenção: {len(alertas)} itens precisam de reposição imediata!")
    else:
        st.info("👋 Bem-vindo ao SofiHub! Comece cadastrando itens no menu lateral para visualizar o Dashboard.")

# --- ABA 2: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Cadastro de Novo Produto")
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        f_sku = col1.text_input("Código SKU")
        f_nome = col2.text_input("Nome do Produto")
        f_cat = col1.selectbox("Categoria", ["TI", "Suprimentos", "Hardware", "Marketing", "Outros"])
        f_loc = col2.text_input("Localização Física")
        
        col3, col4 = st.columns(2)
        f_qtd = col3.number_input("Quantidade Inicial", min_value=0, step=1)
        f_min = col4.number_input("Estoque Mínimo (Alerta)", min_value=1, step=1)
        
        col5, col6 = st.columns(2)
        f_custo = col5.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
        f_venda = col6.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("SALVAR NO SOFIHUB"):
            novo_item = pd.DataFrame([{
                "ID": len(df_p)+1, "SKU": f_sku, "Nome": f_nome, "Categoria": f_cat, 
                "Qtd_Atual": f_qtd, "Estoque_Minimo": f_min, "Preco_Custo": f_custo, 
                "Preco_Venda": f_venda, "Localizacao": f_loc
            }])
            df_final = pd.concat([df_p, novo_item], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_final)
            st.success("✅ Produto registrado com sucesso!")
            st.rerun()

# --- ABA 3: MOVIMENTAR ESTOQUE ---
elif menu == "🔄 Movimentar Estoque":
    st.title("🔄 Movimentação de Saldo")
    if not df_p.empty:
        with st.form("form_mov"):
            prod_sel = st.selectbox("Selecione o Produto", df_p['Nome'].tolist())
            tipo_op = st.radio("Tipo de Movimentação", ["Entrada (Aumentar)", "Saída (Diminuir)"])
            valor_qtd = st.number_input("Quantidade", min_value=1, step=1)
            obs_log = st.text_input("Motivo da alteração")
            
            if st.form_submit_button("EXECUTAR AJUSTE"):
                idx = df_p.index[df_p['Nome'] == prod_sel][0]
                estoque_velho = df_p.at[idx, 'Qtd_Atual']
                
                if "Saída" in tipo_op and estoque_velho < valor_qtd:
                    st.error("❌ Erro: Quantidade insuficiente em estoque!")
                else:
                    novo_saldo = estoque_velho + valor_qtd if "Entrada" in tipo_op else estoque_velho - valor_qtd
                    df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                    conn.update(worksheet="Produtos", data=df_p)
                    
                    # Salva no Histórico
                    log = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                                        "SKU": df_p.at[idx, 'SKU'], "Produto": prod_sel, 
                                        "Tipo": tipo_op, "Qtd": valor_qtd, "Motivo": obs_log, "Usuario": "Murilo"}])
                    df_m_new = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_new)
                    
                    st.success(f"✅ Sucesso! Novo saldo de {prod_sel}: {novo_saldo}")
                    st.rerun()
    else:
        st.warning("Cadastre produtos primeiro para realizar movimentações.")

# --- ABA 4: EDITAR / EXCLUIR ---
elif menu == "🔧 Editar / Excluir":
    st.title("🔧 Manutenção de Inventário")
    if not df_p.empty:
        item_escolhido = st.selectbox("Escolha o Item", df_p['Nome'].tolist())
        idx_e = df_p.index[df_p['Nome'] == item_escolhido][0]
        
        t1, t2 = st.tabs(["📝 Editar Informações", "🗑️ Remover Item"])
        
        with t1:
            e_nome = st.text_input("Novo Nome", value=df_p.at[idx_e, 'Nome'])
            e_min = st.number_input("Novo Estoque Mínimo", value=int(df_p.at[idx_e, 'Estoque_Minimo']))
            if st.button("SALVAR ALTERAÇÕES"):
                df_p.at[idx_e, 'Nome'] = e_nome
                df_p.at[idx_e, 'Estoque_Minimo'] = e_min
                conn.update(worksheet="Produtos", data=df_p)
                st.success("Dados atualizados!")
                st.rerun()

        with t2:
            st.error(f"CUIDADO: Você está excluindo '{item_escolhido}' do SofiHub.")
            if st.button("CONFIRMAR EXCLUSÃO PERMANENTE"):
                df_p = df_p.drop(idx_e)
                conn.update(worksheet="Produtos", data=df_p)
                st.warning("Item deletado.")
                st.rerun()

# --- ABA 5: RELATÓRIOS ---
elif menu == "📋 Relatórios":
    st.title("📋 Relatórios e Auditoria")
    st.subheader("Histórico de Movimentações")
    st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
    
    st.divider()
    csv = df_p.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha de Inventário (CSV)", csv, "SofiHub_Inventario.csv", "text/csv")
