import streamlit as st
import pandas as pd
import hashlib
import io
from datetime import datetime

# -----------------------------
# 🔐 Função para criptografar senha
# -----------------------------
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# -----------------------------
# 👤 Usuários
# -----------------------------
USUARIOS = {
    "murilobraga": {
        "senha": hash_senha("1234321"),
        "nome": "Murilo"
    },
    "visitante": {
        "senha": hash_senha("1234321"),
        "nome": "Visitante"
    }
}

# -----------------------------
# 📦 Sessão
# -----------------------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None

if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=[
        "ID", "Nome", "Categoria", "Quantidade", "Preço", "Data"
    ])

# -----------------------------
# 📤 Exportar Excel (CORRIGIDO)
# -----------------------------
def exportar_excel(df, nome_aba):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    return buf.getvalue()

# -----------------------------
# 🔑 Tela de login
# -----------------------------
def tela_login():
    st.title("🔐 Login")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            if usuario in USUARIOS and USUARIOS[usuario]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.usuario_atual = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

# -----------------------------
# 📦 Sistema de estoque
# -----------------------------
def sistema():
    usuario_nome = USUARIOS[st.session_state.usuario_atual]["nome"]

    st.sidebar.success(f"Bem-vindo, {usuario_nome}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()

    menu = st.sidebar.selectbox("Menu", [
        "Dashboard",
        "Cadastrar Produto",
        "Estoque",
        "Relatórios"
    ])

    df = st.session_state.estoque

    # -----------------------------
    # 📊 Dashboard
    # -----------------------------
    if menu == "Dashboard":
        st.title("📊 Dashboard")

        total_produtos = len(df)
        total_estoque = df["Quantidade"].sum() if not df.empty else 0
        valor_total = (df["Quantidade"] * df["Preço"]).sum() if not df.empty else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Produtos", total_produtos)
        col2.metric("Quantidade Total", total_estoque)
        col3.metric("Valor Total", f"R$ {valor_total:.2f}")

    # -----------------------------
    # ➕ Cadastrar produto
    # -----------------------------
    elif menu == "Cadastrar Produto":
        st.title("➕ Cadastrar Produto")

        nome = st.text_input("Nome do produto")
        categoria = st.text_input("Categoria")
        quantidade = st.number_input("Quantidade", min_value=0)
        preco = st.number_input("Preço", min_value=0.0)

        if st.button("Salvar"):
            if nome:
                novo = pd.DataFrame([{
                    "ID": len(df) + 1,
                    "Nome": nome,
                    "Categoria": categoria,
                    "Quantidade": quantidade,
                    "Preço": preco,
                    "Data": datetime.now()
                }])

                st.session_state.estoque = pd.concat([df, novo], ignore_index=True)
                st.success("Produto cadastrado!")
                st.rerun()
            else:
                st.warning("Digite o nome do produto")

    # -----------------------------
    # 📦 Estoque
    # -----------------------------
    elif menu == "Estoque":
        st.title("📦 Estoque")

        if df.empty:
            st.info("Nenhum produto cadastrado")
        else:
            st.dataframe(df)

            excel = exportar_excel(df, "Estoque")

            st.download_button(
                label="📥 Baixar Excel",
                data=excel,
                file_name="estoque.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # -----------------------------
    # 📈 Relatórios
    # -----------------------------
    elif menu == "Relatórios":
        st.title("📈 Relatórios")

        if df.empty:
            st.info("Sem dados")
        else:
            categoria = st.selectbox("Filtrar por categoria", ["Todas"] + list(df["Categoria"].unique()))

            if categoria != "Todas":
                df_rel = df[df["Categoria"] == categoria]
            else:
                df_rel = df

            st.dataframe(df_rel)

            excel = exportar_excel(df_rel, "Relatorio")

            st.download_button(
                label="📥 Baixar Relatório",
                data=excel,
                file_name="relatorio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -----------------------------
# 🚀 Execução
# -----------------------------
if st.session_state.logado:
    sistema()
else:
    tela_login()
