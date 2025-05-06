# Importando bibiotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


# Carregando dataframe
url = 'http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view'
df_ipea_brent = pd.read_html(url 
                             ,encoding='utf-8' 
                             ,attrs={'id':'grd_DXMainTable'} 
                             ,thousands= '.'
                             ,skiprows=1 
                             )[0] 
df_ipea_brent.columns = ['data', 'preco_uss']
df_ipea_brent['data'] = pd.to_datetime(df_ipea_brent['data'])
df_ipea_brent['preco_uss'] = df_ipea_brent['preco_uss'].str.replace(',','.')
df_ipea_brent['preco_uss'] = pd.Series(df_ipea_brent['preco_uss'], dtype='Float64')
df_ipea_brent = df_ipea_brent.set_index('data')
nome_dia_semana = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}
df_ipea_brent['dia'] = df_ipea_brent.index.day
df_ipea_brent['mes'] = df_ipea_brent.index.month
df_ipea_brent['ano'] = df_ipea_brent.index.year
df_ipea_brent['dia_semana'] = df_ipea_brent.index.weekday
df_ipea_brent['nome_dia_semana'] = df_ipea_brent['dia_semana'].map(nome_dia_semana)
df_ipea_brent['bimestre'] = ((df_ipea_brent['mes'] - 1) // 2) + 1
df_ipea_brent['trimestre'] = ((df_ipea_brent['mes'] - 1) // 3) + 1
df_ipea_brent['semestre'] = ((df_ipea_brent['mes'] - 1) // 6) + 1


#DataFrame de eventos

dados_eventos_novos = [
    {
        "data": datetime(1990, 9, 27),
        "titulo": "Guerra do Golfo",
        "preco": 41.45
    },
    {
        "data": datetime(2000, 9, 7),
        "titulo": "Crise Asiática",
        "preco": 37.43
    },
    {
        "data": datetime(2004, 10, 30),
        "titulo": "Tensões no Oriente Médio",
        "preco": 52.28
    },
    {
        "data": datetime(2008, 7, 7),
        "titulo": "Crescimento da Demanda Global",
        "preco": 143.00
    },
    {
        "data": datetime(2008, 12, 30),
        "titulo": "Falência do Lehman Brothers",
        "preco": 33.73
    },
    {
        "data": datetime(2010, 5, 7),
        "titulo": "Primavera Árabe",
        "preco": 88.09
    },
    {
        "data": datetime(2015, 1, 14),
        "titulo": "Excesso de Oferta Global",
        "preco": 47.66
    },
    {
        "data": datetime(2016, 1, 20),
        "titulo": "Recuperação Econômica Global",
        "preco": 26.01
    },
    {
        "data": datetime(2020, 4, 21),
        "titulo": "COVID-19 – Colapso da Demanda",
        "preco": 9.12
    },
    {
        "data": datetime(2022, 3, 8),
        "titulo": "Invasão da Ucrânia pela Rússia",
        "preco": 133.18
    },
    {
        "data": datetime(2025, 4, 11),
        "titulo": "Aumento da Produção nos EUA",
        "preco": 66.00
    }
]

df_eventos_novos = pd.DataFrame(dados_eventos_novos)
df_eventos_novos.set_index("data", inplace=True)




# Array e DataFrames filtrados
anos = df_ipea_brent['ano'].unique()
precos_anuais = [df_ipea_brent[df_ipea_brent['ano'] == ano]['preco_uss'].mean().round(2) for ano in anos]



#Funções

def plot_preco_brent(df, ano_inicial, ano_final, df_eventos=None, range_y=None):
    # Filtra o DataFrame principal pela data
    df_filtrado = df[(df['ano'] >= ano_inicial) & (df['ano'] <= ano_final)]

    fig = go.Figure()

    # Linha principal do preço
    fig.add_trace(go.Scatter(
        x=df_filtrado.index,
        y=df_filtrado['preco_uss'],
        mode='lines',
        name='Preço do Brent (USD)',
        line=dict(color='#71C5E8', width=2),
        customdata=df_filtrado[['nome_dia_semana']].values,
        hovertemplate=(
            "<b>Data:</b> %{x|%d/%m/%Y}<br>" +
            "<b>Preço:</b> %{y:.2f} USD<br>" +
            "<b>Dia da Semana:</b> %{customdata[0]}<br>" +
            "<extra></extra>"
        )
    ))

    # Adiciona anotações, se df_eventos for fornecido
    if df_eventos is not None:
        df_eventos_filtrado = df_eventos[(df_eventos.index.year >= ano_inicial) & (df_eventos.index.year <= ano_final)]

        for data, row in df_eventos_filtrado.iterrows():
            fig.add_annotation(
                x=data,
                y=row['preco'],
                xref='x',
                yref='y',
                text=f"<b>{row['titulo']}</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor='orange',
                ax=0,
                ay=-40,
                bgcolor='rgba(0,0,0,0.6)',
                bordercolor='orange',
                font=dict(size=10, color='white'),
                align='center'
            )

    # Configurações do layout
    layout_config = dict(
        title=f'Preço do Petróleo Brent no período de {ano_inicial} até {ano_final}',
        xaxis_title='Ano',
        yaxis_title='Preço em USD',
        template='plotly_dark',
        xaxis=dict(
            tickformat='%Y',
            dtick="M24"
        )
    )

    if range_y:
        layout_config['yaxis'] = dict(range=range_y)

    fig.update_layout(**layout_config)

    st.plotly_chart(fig)


######

st.title('Storytelling')
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "💡 Insight", "📅 Análise Temporal","🛢️ Estoques"])

with tab1:
   st.write('Abaixo apresentamos a variação do preço brent ao longo dos anos, é possível filtrar o período e passar o mouse na linha do tempo para visualizar os valores')
   st.empty() # Cria um espaço em branco

   # Filtrando ano
   ano_ini, ano_fim = st.slider(
      'Selecione o período de anos',
      min_value=anos.min(),
      max_value=anos.max(),
      value=(anos.min(), anos.max()),  # Definindo o intervalo padrão como todo o período
      step=1,  # Incremento de 1 ano
   )


   plot_preco_brent(df_ipea_brent,ano_ini,ano_fim)

   ##
   st.write('''  
      <div style="text-align: justify; font-size: 18px; color: #71C5E8">
         <strong>Visão Geral do Comportamento do Preço do Petróleo Brent</strong>
            </div>
            ''', unsafe_allow_html=True)



   st.write('''
            <div style="text-align: justify;">
               **Texto explicando o gráfico acima**
            </div>
            ''', unsafe_allow_html=True)

################## ********************************


with tab2:
      # Inicializa o estado na primeira execução
      if 'periodo_selecionado' not in st.session_state:
         st.session_state['periodo_selecionado'] = '1987 - 2000'  # padrão inicial

      st.write('Selecione o período')
      
      # Funções para alterar o estado
      col1, col2, col3 = st.columns(3)
      with col1:
         if st.button("1987 - 2000"):
               st.session_state['periodo_selecionado'] = '1987 - 2000'
      with col2:
         if st.button("2000 - 2013"):
               st.session_state['periodo_selecionado'] = '2000 - 2013'
      with col3:
         if st.button("2013 - 2025"):
               st.session_state['periodo_selecionado'] = '2013 - 2025'

      # Mostra o gráfico conforme a seleção
      if st.session_state['periodo_selecionado'] == '1987 - 2000':
         plot_preco_brent(df_ipea_brent, 1987, 2000,df_eventos_novos, [0, 200])
      elif st.session_state['periodo_selecionado'] == '2000 - 2013':
         plot_preco_brent(df_ipea_brent, 2000, 2013,df_eventos_novos, [0, 200])
      elif st.session_state['periodo_selecionado'] == '2013 - 2025':
         plot_preco_brent(df_ipea_brent, 2013, 2025,df_eventos_novos, [0, 200])


with tab3:
 st.write('''
            <div style="text-align: justify;">
               **Em breve a análise temporal**
            </div>
            ''', unsafe_allow_html=True)  

with tab4:
 st.write('''
            <div style="text-align: justify;">
               **Em breve a análise de estoques**
            </div>
            ''', unsafe_allow_html=True)  