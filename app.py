import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de página
st.set_page_config(page_title="Sistema Murilo - Gestão", layout="wide")

# URL da sua planilha formatada para exportação CSV
SHEET_ID = "1STMwOAe88ZdRrN749aYNLepkeWpv9jiwHZpODRONubw"
URL_PRODUTOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Produtos"
URL_MOVS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Movimentacoes"

st.title("📦 Gestão de Estoque Profissional")

# Função para carregar dados de forma robusta
def carregar_dados():
    try:
        produtos = pd.read_csv(URL_PRODUTOS)
        movs = pd.read_csv(URL_MOVS)
        return produtos, movs
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_produtos, df_movs = carregar_dados()

# --- MENU LATERAL ---
st.sidebar.header("Navegação")
menu = st.sidebar.selectbox("Ir para:", ["Dashboard", "Registrar Saída/Entrada", "Relatórios"])

if df_produtos.empty:
    st.warning("⚠️ Verifique se as abas 'Produtos' e 'Movimentacoes' existem na planilha e se há cabeçalhos.")
else:
    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.subheader("📊 Resumo do Estoque")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Itens", len(df_produtos))
        
        # Garante que as colunas numéricas sejam números
        df_produtos['Qtd_Atual'] = pd.to_numeric(df_produtos['Qtd_Atual'], errors='coerce').fillna(0)
        df_produtos['Preco_Custo'] = pd.to_numeric(df_produtos['Preco_Custo'], errors='coerce').fillna(0)
        
        valor_total = (df_produtos['Qtd_Atual'] * df_produtos['Preco_Custo']).sum()
        c2.metric("Valor em Estoque", f"R$ {valor_total:,.2f}")
        
        alertas = df_produtos[df_produtos['Qtd_Atual'] <= df_produtos['Estoque_Minimo']]
        c3.metric("Alertas Críticos", len(alertas))

        if not alertas.empty:
            st.error("### 🚨 ITENS ABAIXO DO MÍNIMO")
            st.dataframe(alertas[['SKU', 'Nome', 'Qtd_Atual', 'Estoque_Minimo']])

        st.write("---")
        st.subheader("📋 Inventário Completo")
        st.dataframe(df_produtos, use_container_width=True)

    # --- MOVIMENTAÇÃO ---
    elif menu == "Registrar Saída/Entrada":
        st.subheader("🔄 Movimentar Item")
        
        with st.form("form_mov"):
            lista_produtos = (df_produtos['SKU'] + " - " + df_produtos['Nome']).tolist()
            escolha = st.selectbox("Selecione o Produto", lista_produtos)
            tipo = st.radio("Tipo", ["Entrada", "Saída"])
            qtd = st.number_input("Quantidade", min_value=1, step=1)
            motivo = st.text_input("Observação")
            submit = st.form_submit_button("Confirmar")

        if submit:
            sku_selecionado = escolha.split(" - ")[0]
            st.info(f"Registro de {tipo} para {sku_selecionado} processado localmente.")
            st.warning("Dica: Para gravar na planilha automaticamente, use o recurso 'Secrets' do Streamlit Cloud.")

    # --- RELATÓRIOS ---
    elif menu == "Relatórios":
        st.subheader("📑 Exportação")
        
        csv = df_produtos.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha para Excel", csv, "estoque.csv", "text/csv")
        
        st.write("### Últimas Movimentações")
        st.dataframe(df_movs.tail(10))
