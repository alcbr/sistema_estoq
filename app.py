import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de página
st.set_page_config(page_title="Sistema Murilo - Gestão", layout="wide")

# Configuração do link da sua planilha
SHEET_ID = "1STMwOAe88ZdRrN749aYNLepkeWpv9jiwHZpODRONubw"
# Links para exportação direta de cada aba
URL_PRODUTOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
URL_MOVS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1626210046" # GID da aba Movimentacoes

st.title("📦 Gestão de Estoque Profissional")

# Função para carregar os dados
def carregar_dados():
    try:
        # Lendo os dados. Se estiver vazio (apenas cabeçalho), ele cria um DataFrame limpo
        produtos = pd.read_csv(URL_PRODUTOS).dropna(how='all')
        movs = pd.read_csv(URL_MOVS).dropna(how='all')
        return produtos, movs
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_produtos, df_movs = carregar_dados()

# Menu lateral
menu = st.sidebar.selectbox("Navegação", ["Dashboard", "Registrar Movimentação", "Relatórios"])

# --- LÓGICA DO DASHBOARD ---
if menu == "Dashboard":
    st.subheader("📊 Resumo do Inventário")
    
    if df_produtos.empty or len(df_produtos) == 0:
        st.info("Sua planilha está pronta! Comece cadastrando um item ou adicionando dados na linha 2 do Google Sheets.")
    else:
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Itens Cadastrados", len(df_produtos))
        
        # Converter colunas para número para evitar erros de cálculo
        df_produtos['Qtd_Atual'] = pd.to_numeric(df_produtos['Qtd_Atual'], errors='coerce').fillna(0)
        df_produtos['Preco_Custo'] = pd.to_numeric(df_produtos['Preco_Custo'], errors='coerce').fillna(0)
        
        valor_total = (df_produtos['Qtd_Atual'] * df_produtos['Preco_Custo']).sum()
        c2.metric("Valor Total (Custo)", f"R$ {valor_total:,.2f}")
        
        alertas = df_produtos[df_produtos['Qtd_Atual'] <= df_produtos['Estoque_Minimo']]
        c3.metric("Alertas de Reposição", len(alertas))

        st.divider()
        st.dataframe(df_produtos, use_container_width=True)

# --- LÓGICA DE MOVIMENTAÇÃO ---
elif menu == "Registrar Movimentação":
    st.subheader("🔄 Entrada e Saída de Estoque")
    
    if df_produtos.empty:
        st.warning("Adicione produtos na aba 'Produtos' primeiro para poder movimentar.")
    else:
        with st.form("mov"):
            lista = (df_produtos['SKU'].astype(str) + " - " + df_produtos['Nome'].astype(str)).tolist()
            escolha = st.selectbox("Selecione o Produto", lista)
            tipo = st.radio("Operação", ["Entrada", "Saída"])
            qtd = st.number_input("Quantidade", min_value=1, step=1)
            motivo = st.text_input("Observação/Motivo")
            btn = st.form_submit_button("Confirmar Movimentação")
            
            if btn:
                st.success(f"Movimentação de {qtd} unidades registrada para {escolha}!")
                st.info("Para salvar de volta no Google Sheets, o próximo passo é configurar as 'Credentials'.")

# --- RELATÓRIOS ---
elif menu == "Relatórios":
    st.subheader("📑 Histórico e Exportação")
    if not df_movs.empty:
        st.dataframe(df_movs, use_container_width=True)
    else:
        st.write("Nenhuma movimentação registrada ainda.")
    
    csv = df_produtos.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Excel (CSV)", csv, "estoque.csv", "text/csv")
