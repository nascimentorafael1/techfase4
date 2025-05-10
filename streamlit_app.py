import streamlit as st
st.set_page_config(layout="wide")

# Definindo as páginas diretamente
home = st.Page(
    'paginas/home.py',
    title="Home",
    icon='🏠',
    default=True
)

storytelling = st.Page(
    'paginas/storytelling.py',
    title="Storytelling",
    icon='📄',
    default=False
)

dashboard = st.Page(
    'paginas/dashboard.py',
    title="Dashboard",
    icon='📊',
    default=False
)

predicao = st.Page(
    'paginas/predicao.py',
    title="Previsão",
    icon='📈',
    default=False
)

dados = st.Page(
    'paginas/dados.py',
    title="Dados Técnicos",
    icon='🛠️',
    default=False
)

# Criando a navegação com st.navigation
pg = st.navigation(
    {
        "Selecione uma Opção": [home, storytelling, dashboard, predicao, dados],
    }
)

st.logo("img/preco-do-petroleo-v3.png", size= "large") 


# Iniciar navegação
pg.run()



# Selecionar logotipos: https://fonts.google.com/icons
