import streamlit as st
import boto3
import hashlib
from pathlib import Path
import os

# Configuração da página
st.set_page_config(page_title="Portal de Upload", layout="wide")

# Tentar carregar configurações dos secrets
try:
    condominios = st.secrets["condominios"]
except:
    st.error("Lista de condomínios não configurada nos secrets")
    condominios = []

# Inicializar estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'condominio' not in st.session_state:
    st.session_state.condominio = None

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
            try:
                if (username in st.secrets.db_users and 
                    st.secrets.db_users[username] == password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenciais inválidas")
    except Exception as e:
        st.error(f"Erro na configuração: {str(e)}")
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
            except:
                st.error("Configuração de usuários não encontrada")
                
    else:
        # Tela após login
        st.title("Portal de Upload")
        
        if not st.session_state.condominio:
            # Seleção do condomínio
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
    main()
