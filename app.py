import streamlit as st
import hashlib

# -----------------------------
# 🔐 Função para criptografar senha
# -----------------------------
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# -----------------------------
# 👤 Usuários do sistema
# -----------------------------
USUARIOS = {
    "murilobraga": {
        "senha": hash_senha("1234321"),
        "nome": "Murilo Braga"
    },
    "visitante": {
        "senha": hash_senha("1234321"),
        "nome": "Visitante"
    }
}

# -----------------------------
# 📦 Controle de sessão
# -----------------------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None

# -----------------------------
# 🔑 Tela de login
# -----------------------------
def tela_login():
    st.title("🔐 Login")

    with st.form("login_form"):
        usuario = st.text_input("👤 Usuário")
        senha = st.text_input("🔒 Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            if usuario in USUARIOS and USUARIOS[usuario]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.usuario_atual = usuario
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")

# -----------------------------
# 🏠 Sistema principal
# -----------------------------
def sistema():
    usuario_nome = USUARIOS[st.session_state.usuario_atual]["nome"]

    st.sidebar.success(f"👋 Bem-vindo, {usuario_nome}")

    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()

    st.title("📊 Dashboard")
    st.write("Aqui vai seu sistema de estoque futuramente...")

# -----------------------------
# 🚀 Execução principal
# -----------------------------
if st.session_state.logado:
    sistema()
else:
    tela_login()
