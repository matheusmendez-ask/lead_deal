import pandas as pd
import pandas_gbq
import numpy as np
import datetime
import json
import requests
import datetime as dt
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st

# CSS personalizado
st.markdown(
    """
   <style>
        /* Inputs de texto com bordas arredondadas */
        .stTextInput>div>div>input {
            border-radius: 20px;
        }

        /* Botões com estilo personalizado */
        .stButton>button {
            border-radius: 20px;
            border: 1px solid #144383; /* Azul */
            color: white; /* Texto branco */
            background-color: #144383; /* Azul */
            padding: 10px 24px;
            cursor: pointer;
            font-size: 16px;
        }

        /* Efeito ao passar o mouse sobre os botões */
        .stButton>button:hover {
            background-color: #D3D3D3; /* Cinza claro */
            color: #144383; /* Texto azul */
        }

        /* Estilo para textos em markdown */
        .reportview-container .markdown-text-container {
            font-family: monospace;
        }

        /* Cor personalizada para markdown */
        .stMarkdown {
            color: #FF4B4B; /* Vermelho */
        }

        /* Feedback de sucesso com cor de fundo personalizada */
        .st-success {
            background-color: #D4EDDA;
        }

        /* Feedback de informação com cor de fundo personalizada */
        .st-info {
            background-color: #D1ECF1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Definição dos usuários e senhas
usuarios = {
    'Matheus': 'senhaMatheus',
    'Augusto': 'senhaAugusto',
    'Julio': 'senhaAna',
    'Ju': 'senhaJu',
    'Bruce': 'senhaBruce',
    'Paulo': 'senhaPaulo',
    'Omar': 'senhaOmar',
    'Paulo Lecir': 'senhaLecir',
    'Ivonete': 'senhaIvonete',
    'Marcio': 'senhaMarcio',
    'Leylane': 'senhaLeylane',
    'Guido': 'senhaGuido',
    'Luana': 'senhaLuana'
}

# Definição dos IDs
usuario_ids = {
    'Augusto': 53125,
    'Julio': 54135,
    'Douglas': 59360,
    'Omar': 59361,
    'Lucas': 60740,
    'Paulo Lecir': 69244,
    'Paulo': 53121,
    'Dennys': 76798,
    'Suelen': 77246,
    'Bruce': 77652,
    'Raissa': 79821,
    'Judite': 82581,
    'Guido': 96629,
    'Marcio': 96751,
    'Luana': 97839,
    'Ivonete': 104104,
    'Leylane': 107537,
    'Matheus': 88311
}

# Função de verificação de login
def verificar_login():
    usuario = st.sidebar.text_input('Usuário', key='usuario_input')
    senha = st.sidebar.text_input('Senha', type='password', key='senha_input')
    if st.sidebar.button('Login'):
        if usuario in usuarios and usuarios[usuario] == senha:
            st.session_state['autenticado'] = True
            st.session_state['usuario_atual'] = usuario
            st.session_state['created_by_id'] = usuario_ids.get(usuario, 0)  # Pega o ID do usuário ou 0 se não encontrar
            st.session_state['responsible_id'] = usuario_ids.get(usuario, 0)  # Mesmo ID para responsável
            st.sidebar.success('Você está logado!')
            # Recarrega a página para aplicar o novo estilo de fundo
            st.experimental_rerun()
        else:
            st.session_state['autenticado'] = False
            st.sidebar.error('Usuário ou senha inválidos.')
# Função de logout
def realizar_logout():
    if st.sidebar.button('Logout'):
        st.session_state['autenticado'] = False
        del st.session_state['usuario_atual']
# Inicialização do estado da sessão para autenticação, se necessário
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

verificar_login()
realizar_logout()

# Função para criar o pedido e enviar para a API
def criar_pedido(url, token, pedido_data):
    # Defina os headers da requisição
    headers = {
        'token': f'{token}',
        'formato': 'JSON',
        'pedido': pedido_data
        }
    data = headers
    # Assegure-se de que pedido_data já está no formato correto para ser convertido em JSON
    response = requests.post(url, data=data, json=pedido_data)
    return response

# Carrega dados e mostra a calculadora se o usuário estiver autenticado
if st.session_state.get('autenticado', False):
    
    st.title("Feiras BCMED")
    
    def criar_contato(nome, telefone, email, apikey, created_by_id, responsible_id):
        url = "https://api.moskitcrm.com/v2/contacts"
        payload = {
                "name": nome,
                "phones": [{"number": telefone}],
                "emails": [{"address": email}],
                "createdBy": {"id": created_by_id},  # ID do usuário que criou o negócio
                "responsible": {"id": responsible_id},
            }
        headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "apikey": apikey
            }
        response = requests.post(url, json=payload, headers=headers)
            
        return response

    def criar_deal(nome_cliente, telefone, email, apikey, created_by_id, responsible_id, origem, status):
        response_contato = criar_contato(nome_cliente, telefone, email, apikey, created_by_id, responsible_id)
        if response_contato.status_code == 200:
                
            contato_id = response_contato.json().get('id')
                    
            url = "https://api.moskitcrm.com/v2/deals"
                    
            payload = {
                        "name": "Negócio - " + nome_cliente,
                        "contacts": [{"id": contato_id}],
                        "origin": origem,
                        "status": status,
                        "stage": {"id": 157609},  # ID do estágio do negócio
                        "createdBy": {"id": created_by_id},  
                        "responsible": {"id": responsible_id},
                    }
            headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "apikey": apikey
                    }
            response_negocio = requests.post(url, json=payload, headers=headers)
                    
            return response_negocio
        else:
            return response_contato
        
    with st.form("negocio_form"):
            nome_cliente = st.text_input("Nome do Cliente")
            fone = st.text_input("Telefone")
            email = st.text_input("E-mail")
            feira = st.selectbox("Evento", ["Estetica in SP", "SBTI"])
            submit_button = st.form_submit_button("Criar Negócio")

            if submit_button:
                laleo = "388887a3-3754-4f1e-baec-ad55c0f49720"
                created_by_id = st.session_state['created_by_id']
                responsible_id = st.session_state['responsible_id']
                response_moskit = criar_deal(nome_cliente, fone, email, laleo, created_by_id, responsible_id, feira, "OPEN")

                if response_moskit.status_code == 200:
                    st.success("Negócio criado com sucesso no Moskit CRM!")
                    st.json(response_moskit.json())
                else:
                    st.error(f"Erro ao criar negócio no Moskit CRM: {response_moskit.text}")
