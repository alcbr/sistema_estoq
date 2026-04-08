import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configurações de Identidade Visual e Página
st.set_page_config(page_title="SofiHub - Gestão Inteligente", layout="wide", page_icon="🚀")

# Estilização CSS para forçar a paleta da Logo SofiHub
st.markdown("""
    <style>
    /* Fundo e Texto Geral */
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
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #D64C20 !important; }
    
    /* Cards de Métricas */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão e Carregamento de Dados
# Certifique-se de que o Secret 'connections.gsheets.spreadsheet' está configurado no Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Tenta ler as abas. ttl=0 garante dados em tempo real
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        return p, m
    except Exception:
        # Estrutura reserva caso a planilha esteja vazia ou dê erro 400
        cols_p = ["ID", "SKU", "Nome", "Categoria", "Qtd_Atual", "Estoque_Minimo", "Preco_Custo", "Preco_Venda", "Localizacao"]
        cols_m = ["Data_Hora", "SKU", "Produto", "Tipo", "Qtd", "Motivo", "Usuario"]
        return pd.DataFrame(columns=cols_p), pd.DataFrame(columns=cols_m)

df_p, df_m = carregar_dados()

# 3. Barra Lateral (Menu e Logo)
with st.sidebar:
    # Substitua pelo link direto da sua logo após subir no GitHub
    st.image("https://raw.githubusercontent.com/alcbr/sistema_estoq/main/logo.jpg", width=200) 
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard", "🆕 Cadastrar Item", "🔄 Movimentar Estoque", "🔧 Editar / Excluir", "📋 Relatórios"])
    st.markdown("---")
    st.caption("SofiHub v1.0 | Hub de Soluções Tecnológicas")

# --- ABA 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Painel de Controle")
    
    if not df_p.empty:
        # Tratamento de números
        df_p['Qtd_Atual'] = pd.to_numeric(df_p['Qtd_Atual'], errors='coerce').fillna(0)
        df_p['Estoque_Minimo'] = pd.to_numeric(df_p['Estoque_Minimo'], errors='coerce').fillna(0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Itens Cadastrados", len(df_p))
        
        alertas = df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]
        c2.metric("Alertas de Reposição", len(alertas), delta_color="inverse")
        
        ultima = df_m['Data_Hora'].iloc[-1] if not df_m.empty else "Sem registros"
        c3.metric("Última Atividade", str(ultima).split()[0])

        st.markdown("### 📋 Inventário em Tempo Real")
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("O SofiHub está pronto para uso. Comece cadastrando um item no menu lateral.")

# --- ABA 2: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        f_sku = col1.text_input("Código SKU / Identificador")
        f_nome = col2.text_input("Nome do Produto")
        f_cat = col1.selectbox("Categoria", ["Hardware", "Software", "Serviços", "Suprimentos"])
        f_loc = col2.text_input("Localização Física")
        
        col3, col4 = st.columns(2)
        f_qtd = col3.number_input("Quantidade Inicial", min_value=0, step=1)
        f_min = col4.number_input("Estoque de Alerta (Mínimo)", min_value=1, step=1)
        
        if st.form_submit_button("SALVAR NO SOFIHUB"):
            novo = pd.DataFrame([{"ID": len(df_p)+1, "SKU": f_sku, "Nome": f_nome, "Categoria": f_cat, 
                                 "Qtd_Atual": f_qtd, "Estoque_Minimo": f_min, "Localizacao": f_loc}])
            df_atualizado = pd.concat([df_p, novo], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_atualizado)
            st.success("✅ Produto cadastrado com sucesso!")
            st.rerun()

# --- ABA 3: MOVIMENTAR ESTOQUE ---
elif menu == "🔄 Movimentar Estoque":
    st.title("🔄 Ajuste de Saldo")
    if not df_p.empty:
        with st.form("form_mov"):
            prod_sel = st.selectbox("Selecione o Item", df_p['Nome'].tolist())
            tipo_op = st.radio("Tipo de Movimentação", ["Entrada (+)", "Saída (-)"])
            valor_qtd = st.number_input("Quantidade", min_value=1, step=1)
            obs_log = st.text_input("Motivo / Observação")
            
            if st.form_submit_button("EXECUTAR"):
                idx = df_p.index[df_p['Nome'] == prod_sel][0]
                estoque_velho = df_p.at[idx, 'Qtd_Atual']
                
                if "Saída" in tipo_op and estoque_velho < valor_qtd:
                    st.error("❌ Saldo insuficiente!")
                else:
                    novo_saldo = estoque_velho + valor_qtd if "Entrada" in tipo_op else estoque_velho - valor_qtd
                    df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                    
                    # Salva Produto
                    conn.update(worksheet="Produtos", data=df_p)
                    
                    # Salva Histórico
                    log = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                                        "SKU": df_p.at[idx, 'SKU'], "Produto": prod_sel, 
                                        "Tipo": tipo_op, "Qtd": valor_qtd, "Motivo": obs_log, "Usuario": "Murilo"}])
                    df_m_new = pd.concat([df_m, log], ignore_index=True)
                    conn.update(worksheet="Movimentacoes", data=df_m_new)
                    
                    st.success(f"✅ Estoque atualizado: {novo_saldo} unidades.")
                    st.rerun()

# --- ABA 4: EDITAR / EXCLUIR ---
elif menu == "🔧 Editar / Excluir":
    st.title("🔧 Manutenção de Cadastro")
    if not df_p.empty:
        item_escolhido = st.selectbox("Escolha o Item", df_p['Nome'].tolist())
        idx_e = df_p.index[df_p['Nome'] == item_escolhido][0]
        
        t1, t2 = st.tabs(["📝 Editar Informações", "🗑️ Remover Item"])
        
        with t1:
            e_nome = st.text_input("Nome", value=df_p.at[idx_e, 'Nome'])
            e_min = st.number_input("Estoque Mínimo", value=int(df_p.at[idx_e, 'Estoque_Minimo']))
            if st.button("SALVAR ALTERAÇÕES"):
                df_p.at[idx_e, 'Nome'] = e_nome
                df_p.at[idx_e, 'Estoque_Minimo'] = e_min
                conn.update(worksheet="Produtos", data=df_p)
                st.success("Dados atualizados!")
                st.rerun()

        with t2:
            st.warning(f"Isso removerá '{item_escolhido}' permanentemente.")
            if st.button("CONFIRMAR EXCLUSÃO"):
                df_p = df_p.drop(idx_e)
                conn.update(worksheet="Produtos", data=df_p)
                st.info("Item removido.")
                st.rerun()

# --- ABA 5: RELATÓRIOS ---
elif menu == "📋 Relatórios":
    st.title("📋 Histórico e Exportação")
    st.dataframe(df_m.sort_index(ascending=False), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    csv = df_p.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Inventário Completo (CSV)", csv, "SofiHub_Estoque.csv", "text/csv")
