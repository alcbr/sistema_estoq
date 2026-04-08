import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÕES DE PÁGINA
st.set_page_config(page_title="SofiHub - Gestão e Compras", layout="wide", page_icon="📦")

# Estilização CSS personalizada
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        p = conn.read(worksheet="Produtos", ttl=0).dropna(how='all')
        m = conn.read(worksheet="Movimentacoes", ttl=0).dropna(how='all')
        c = conn.read(worksheet="Categorias", ttl=0).dropna(how='all')
        
        # Conversão numérica para evitar erros de cálculo
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

# 3. BARRA LATERAL (LOGO E MENU)
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.title("📦 SofiHub")
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", [
        "📊 Inventário", 
        "🆕 Cadastrar Item", 
        "🔄 Compras e Saídas", 
        "🏷️ Categorias", 
        "📋 Histórico de Valores"
    ])
    st.markdown("---")
    st.caption("SofiHub v1.4 | Murilo")

# --- ABA: INVENTÁRIO (Com Filtro 4) ---
if menu == "📊 Inventário":
    st.title("📊 Controle de Estoque")
    if not df_p.empty:
        # Busca inteligente
        busca = st.text_input("🔍 Pesquisar por nome, SKU, categoria ou localização...")
        
        # Lógica do Filtro
        if busca:
            df_view = df_p[df_p.apply(lambda row: busca.lower() in str(row).lower(), axis=1)]
        else:
            df_view = df_p

        # Métricas visuais
        c1, c2, c3 = st.columns(3)
        c1.metric("Itens Totais", int(df_p['Qtd_Atual'].sum()))
        c2.metric("Alertas Críticos", len(df_p[df_p['Qtd_Atual'] <= df_p['Estoque_Minimo']]))
        c3.metric("Categorias", len(df_c))

        st.divider()
        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum item cadastrado no sistema.")

# --- ABA: CADASTRAR ITEM ---
elif menu == "🆕 Cadastrar Item":
    st.title("🆕 Novo Produto")
    lista_cats = df_c['Nome'].tolist() if not df_c.empty else ["Geral"]
    
    with st.form("cad_item"):
        c1, c2 = st.columns(2)
        n_nome = c1.text_input("Nome do Produto")
        n_sku = c2.text_input("SKU / Código")
        
        c3, c4 = st.columns(2)
        n_cat = c3.selectbox("Categoria", lista_cats)
        n_loc = c4.text_input("Localização Física (Ex: Prateleira A1)")
        
        c5, c6 = st.columns(2)
        n_min = c5.number_input("Estoque Mínimo (Alerta)", min_value=0, step=1)
        n_ini = c6.number_input("Quantidade Inicial", min_value=0, step=1)
        
        if st.form_submit_button("SALVAR NO SOFIHUB"):
            if n_nome:
                novo_p = pd.DataFrame([{
                    "ID": len(df_p)+1, "SKU": n_sku, "Nome": n_nome, 
                    "Categoria": n_cat, "Qtd_Atual": n_ini, 
                    "Estoque_Minimo": n_min, "Localizacao": n_loc
                }])
                df_p_new = pd.concat([df_p, novo_p], ignore_index=True)
                conn.update(worksheet="Produtos", data=df_p_new)
                st.cache_data.clear()
                st.success("✅ Produto cadastrado!")
                st.rerun()
            else:
                st.error("O nome do produto é obrigatório.")

# --- ABA: COMPRAS E SAÍDAS (Com Histórico de Valores) ---
elif menu == "🔄 Compras e Saídas":
    st.title("🔄 Registrar Movimentação")
    if not df_p.empty:
        with st.form("mov_fin"):
            prod_sel = st.selectbox("Selecione o Produto", df_p['Nome'].tolist())
            tipo = st.radio("Tipo de Operação", ["Entrada (Compra)", "Saída (Uso/Venda)"])
            qtd = st.number_input("Quantidade", min_value=1, step=1)
            
            v_unit = st.number_input("Valor Unitário Pago (R$)", min_value=0.0, format="%.2f", help="Apenas para Entradas")
            motivo = st.text_input("Observação / Motivo")
            
            if st.form_submit_button("EXECUTAR"):
                idx = df_p.index[df_p['Nome'] == prod_sel][0]
                estoque_atual = df_p.at[idx, 'Qtd_Atual']
                
                # Validação de saída
                if "Saída" in tipo and estoque_atual < qtd:
                    st.error("❌ Erro: Estoque insuficiente!")
                else:
                    novo_saldo = estoque_atual + qtd if "Entrada" in tipo else estoque_atual - qtd
                    df_p.at[idx, 'Qtd_Atual'] = novo_saldo
                    conn.update(worksheet="Produtos", data=df_p)
                    
                    # Registro no Histórico
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
                    st.success(f"✅ Movimentação concluída! Novo saldo: {novo_saldo}")
                    st.rerun()

# --- ABA: CATEGORIAS (Adicionar e Excluir) ---
elif menu == "🏷️ Categorias":
    st.title("🏷️ Gerenciar Categorias")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nova Categoria")
        nova_cat = st.text_input("Nome")
        if st.button("Adicionar"):
            if nova_cat and nova_cat not in df_c['Nome'].values:
                df_c_new = pd.concat([df_c, pd.DataFrame([{"Nome": nova_cat}])], ignore_index=True)
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.success("Adicionada!")
                st.rerun()

    with col2:
        st.subheader("Excluir Existente")
        if not df_c.empty:
            cat_del = st.selectbox("Selecione", df_c['Nome'].tolist())
            if st.button("Confirmar Exclusão"):
                df_c_new = df_c[df_c['Nome'] != cat_del]
                conn.update(worksheet="Categorias", data=df_c_new)
                st.cache_data.clear()
                st.warning("Removida!")
                st.rerun()

# --- ABA: HISTÓRICO DE VALORES ---
elif menu == "📋 Histórico de Valores":
    st.title("📋 Relatório de Compras e Gastos")
    if not df_m.empty:
        # Ordenar pelo mais recente
        df_hist = df_m.sort_index(ascending=False)
        
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        # Rodapé Financeiro
        total_compras = df_hist['Total_Gasto'].sum()
        st.info(f"💰 Total investido em compras registradas: R$ {total_compras:,.2f}")
    else:
        st.write("Sem movimentações no histórico.")
