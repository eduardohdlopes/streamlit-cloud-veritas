import streamlit as st
import boto3
import sqlite3
import hashlib
from pathlib import Path
import os

# Configurações do app
usuarios = st.secrets["db_users"]
condominios = st.secrets["condominios"]

# Configuração da página
st.set_page_config(page_title="Portal de Upload", layout="wide")

# Inicializar estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'condominio' not in st.session_state:
    st.session_state.condominio = None

# Função para criar banco de dados
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS condominios
                 (nome TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# Função para verificar credenciais
def verify_credentials(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", 
              (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result is not None

# Função para upload no S3
def upload_to_s3(file, condominio):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
            aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
        )
        
        # Criar path com nome do condomínio
        file_path = f"{condominio}/{file.name}"
        
        # Upload para S3
        s3.upload_fileobj(
            file,
            'mybucket-veritas',
            file_path
        )
        return True
    except Exception as e:
        st.error(f"Erro no upload: {str(e)}")
        return False

# Interface principal
def main():
    if not st.session_state.logged_in:
        # Tela de login
        st.title("Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if verify_credentials(username, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
                
    else:
        # Tela após login
        st.title("Portal de Upload")
        
        if not st.session_state.condominio:
            # Seleção do condomínio
            condominios = ["Condomínio A", "Condomínio B", "Condomínio C"]  # Substituir pela lista real
            condominio = st.selectbox("Selecione o Condomínio", condominios)
            
            if st.button("Confirmar"):
                st.session_state.condominio = condominio
                st.rerun()
                
        else:
            # Tela de upload
            st.write(f"Condomínio selecionado: {st.session_state.condominio}")
            uploaded_file = st.file_uploader("Escolha um arquivo", type=['pdf', 'doc', 'docx'])
            
            if uploaded_file:
                if st.button("Enviar arquivo"):
                    if upload_to_s3(uploaded_file, st.session_state.condominio):
                        st.success("Arquivo enviado com sucesso!")
                    
            if st.button("Trocar Condomínio"):
                st.session_state.condominio = None
                st.rerun()
                
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.condominio = None
                st.rerun()

if __name__ == "__main__":
    init_db()
    main()
