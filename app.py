import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configurações iniciais
st.set_page_config(page_title="Sistema Pro - Gestão Murilo", layout="wide")

st.title("🚀 Sistema de Gestão de Estoque Profissional")

# Conexão com Google Sheets (Substitua pela URL da sua planilha abaixo)
url = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_GOOGLE"

conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler dados
def carregar_dados():
    produtos = conn.read(spreadsheet=url, worksheet="Produtos")
    movs = conn.read(spreadsheet=url, worksheet="Movimentacoes")
    return produtos, movs

df_produtos, df_movs = carregar_dados()

# --- BARRA LATERAL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2897/2897785.png", width=100)
menu = st.sidebar.selectbox("Menu Principal", ["Painel de Controle", "Entradas/Saídas", "Cadastro de Itens", "Relatórios Exportáveis"])

# --- 1. PAINEL DE CONTROLE (DASHBOARD) ---
if menu == "Painel de Controle":
    st.subheader("📊 Visão Geral do Negócio")
    
    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Itens Cadastrados", len(df_produtos))
    valor_total = (df_produtos['Qtd_Atual'] * df_produtos['Preco_Custo']).sum()
    c2.metric("Capital Imobilizado", f"R$ {valor_total:,.2f}")
    
    itens_criticos = df_produtos[df_produtos['Qtd_Atual'] <= df_produtos['Estoque_Minimo']]
    c3.metric("Alertas de Reposição", len(itens_criticos), delta_color="inverse")

    if not itens_criticos.empty:
        st.error("⚠️ PRODUTOS ABAIXO DO MÍNIMO!")
        st.dataframe(itens_criticos[['SKU', 'Nome', 'Qtd_Atual', 'Estoque_Minimo']], use_container_width=True)

    st.divider()
    st.subheader("📦 Inventário Atual")
    st.dataframe(df_produtos, use_container_width=True)

# --- 2. ENTRADAS E SAÍDAS (LÓGICA DE BAIXA) ---
elif menu == "Entradas/Saídas":
    st.subheader("🔄 Registrar Movimentação")
    
    with st.form("movimentacao"):
        sku_sel = st.selectbox("Selecione o Produto (SKU - Nome)", 
                               df_produtos['SKU'] + " - " + df_produtos['Nome'])
        tipo = st.radio("Operação", ["Entrada (Compra/Reposição)", "Saída (Venda/Uso)"])
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        motivo = st.text_input("Motivo/Observação (Ex: Venda Cliente X)")
        
        btn_confirmar = st.form_submit_button("Confirmar e Atualizar Estoque")

    if btn_confirmar:
        sku_puro = sku_sel.split(" - ")[0]
        idx = df_produtos.index[df_produtos['SKU'] == sku_puro][0]
        qtd_atual = df_produtos.at[idx, 'Qtd_Atual']
        
        if "Saída" in tipo and qtd_atual < quantidade:
            st.error("❌ Erro: Estoque insuficiente para essa saída!")
        else:
            # Calcula novo saldo
            novo_saldo = qtd_atual + quantidade if "Entrada" in tipo else qtd_atual - quantidade
            df_produtos.at[idx, 'Qtd_Atual'] = novo_saldo
            
            # Registra no Histórico
            nova_mov = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "SKU": sku_puro,
                "Produto": sku_sel.split(" - ")[1],
                "Tipo": tipo,
                "Qtd": quantidade,
                "Motivo": motivo,
                "Usuario": "Murilo"
            }])
            
            # Atualiza a Planilha Google
            conn.update(spreadsheet=url, worksheet="Produtos", data=df_produtos)
            
            # Adiciona ao histórico (concatenando com o que já existe)
            df_movs_atualizado = pd.concat([df_movs, nova_mov], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Movimentacoes", data=df_movs_atualizado)
            
            st.success(f"✅ Sucesso! Novo saldo de {sku_puro}: {novo_saldo} unidades.")
            st.balloons()

# --- 3. RELATÓRIOS ---
elif menu == "Relatórios Exportáveis":
    st.subheader("📑 Gerar Relatórios")
    
    # Botão Excel
    csv = df_produtos.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Inventário Completo (Excel/CSV)", csv, "estoque_murilo.csv", "text/csv")
    
    st.divider()
    st.write("### Histórico Recente de Movimentações")
    st.table(df_movs.tail(10)) # Mostra as últimas 10
