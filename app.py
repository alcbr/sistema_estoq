import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão e Compras", layout="wide", page_icon="📦")

# Estilização
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        
        # Garantir conversão numérica
        if not p.empty:
            p['Qtd_Atual'] = pd.to_numeric(p['Qtd_Atual'], errors='coerce').fillna(0)
            p['Estoque_Minimo'] = pd.to_numeric(p['Estoque_Minimo'], errors='coerce').fillna(0)
        if not m.empty:
            m['Valor_Unitario'] = pd.to_numeric(m['Valor_Unitario'], errors='coerce').fillna(0)
            m['Total_Gasto'] = pd.to_numeric(m['Total_Gasto'], errors='coerce').fillna(0)
            
        return p, m, c
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(columns=["Nome"])

df_p, df_m, df_c = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.title("📦 SofiHub")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📊 Inventário", "🆕 Cadastrar Item", "🔄 Compras e Saídas", "🏷️ Categorias", "📋 Histórico de Valores"])
    st.markdown("---")
    st.caption("SofiHub v1.3")

# --- ABA: INVENTÁRIO ---
if menu == "📊 Inventário":
    st.title("📊 Controle de Estoque")
    if not df_p.empty:
        # Busca inteligente
        busca = st.text_input("🔍 Pesquisar por nome, SKU ou categoria...")
        df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)] if busca else df_p

        c1, c2, c3 = st.columns(3)
        c1.metric("Itens Totais", int(df_p['Qtd_Atual'].sum()))
        c2.metric("Alertas de Mínimo", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        c3.metric("Categorias", len(df_c))

        st.divider()
        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item cadastrado.")

# --- ABA: COMPRAS E SAÍDAS ---
elif menu == "🔄 Compras e Saídas":
    st.title("🔄 Registrar Movimentação")
    if not df_p.empty:
        with st.form("form_mov"):
            prod_sel = st.selectbox("Produto", df_p['Nome'].tolist())
            tipo = st.radio("Tipo", ["Entrada (Compra)", "Saída (Uso/Venda)"])
            qtd = st.number_input("Quantidade", min_value=1, step=1)
            
            # Campo de Valor só faz sentido real na Entrada, mas deixamos aberto
            v_unit = st.number_input("Valor Unitário Pago (R$)", min_value=0.0, format="%.2f")
            motivo = st.text_input("Observação/Motivo")
            
            if st.form_submit_button("Confirmar"):
                idx = df_p.index[df_p['Nome'] == prod_sel][0]
                estoque_atual = df_p.at[idx, 'Qtd_Atual']
                
                novo_saldo = estoque_atual + qtd if "Entrada" in tipo else estoque_atual - qtd
                df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                conn.update(worksheet="Produtos", data=df_p)
                
                # Salva Histórico com Valor
                log = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "SKU": df_p.at[idx, 'SKU'],
                    "Produto": prod_sel,
                    "Tipo": tipo,
                    "Qtd": qtd,
                    "Valor_Unitario": v_unit,
                    "Total_Gasto": v_unit * qtd if "Entrada" in tipo else 0,
                    "Motivo": motivo,
                    "Usuario": "Murilo"
                }])
                df_m_new = pd.concat([df_m, log], ignore_index=True)
                conn.update(worksheet="Movimentacoes", data=df_m_new)
                
                st.cache_data.clear()
                st.success(f"Registrado! Saldo de {prod_sel}: {novo_saldo}")
                st.rerun()

# --- ABA: HISTÓRICO DE VALORES ---
elif menu == "📋 Histórico de Valores":
    st.title("📋 Histórico de Compras e Gastos")
    if not df_m.empty:
        df_hist = df_m.copy()
        # Converte para data para ordenar melhor
        df_hist = df_hist.sort_index(ascending=False)
        
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        total_inv = df_hist['Total_Gasto'].sum()
        st.info(f"💰 Volume total investido em compras: R$ {total_inv:,.2f}")
    else:
        st.write("Sem registros no histórico.")

# --- ABA: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    with st.form("cad"):
        n_nome = st.text_input("Nome")
        n_sku = st.text_input("SKU")
        n_cat = st.selectbox("Categoria", df_c['Nome'].tolist() if not df_c.empty else ["Geral"])
        n_min = st.number_input("Mínimo para Alerta", min_value=0)
        n_ini = st.number_input("Qtd Inicial", min_value=0)
        if st.form_submit_button("Salvar"):
            novo_p = pd.DataFrame([{"ID": len(df_p)+1, "SKU": n_sku, "Nome": n_nome, "Categoria": n_cat, "Qtd_Atual": n_ini, "Estoque_Minimo": n_min}])
            df_p_new = pd.concat([df_p, novo_p], ignore_index=True)
            conn.update(worksheet="Produtos", data=df_p_new)
            st.cache_data.clear()
            st.success("Cadastrado!")
            st.rerun()

# --- ABA: CATEGORIAS ---
elif menu == "🏷️ Categorias":
    st.title("🏷️ Categorias")
    nova = st.text_input("Nome da Categoria")
    if st.button("Adicionar"):
        if nova:
            df_c_new = pd.concat([df_c, pd.DataFrame([{"Nome": nova}])], ignore_index=True)
            conn.update(worksheet="Categorias", data=df_c_new)
            st.cache_data.clear()
            st.rerun()
