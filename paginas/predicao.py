# Importando bibiotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import joblib
from prophet import Prophet
import numpy as np
import plotly.graph_objects as go


st.title('Previsão')


# dataset original (aquele usado no treinamento)
df_treino = pd.read_csv("https://github.com/nascimentorafael1/techfase4/raw/refs/heads/main/data/train_prophet.csv")

df_treino = df_treino.tail(160)
df_treino = df_treino[['ds','y']]
df_treino.rename(columns={ 'y': 'yhat'}, inplace=True)
df_treino['yhat_lower'] = np.nan 
df_treino['yhat_upper'] = np.nan


df_ipea_brent = pd.read_csv("https://github.com/nascimentorafael1/techfase4/raw/refs/heads/main/data/df_ipea_brent.csv")

df_eia_prod_mundial = pd.read_csv("https://github.com/nascimentorafael1/techfase4/raw/refs/heads/main/data/df_eia_prod_mundial.csv")

# Carregar modelo Prophet
def carregar_modelo():
    caminho = 'modelo/prophet_modelo.joblib'
    print(f"Procurando modelo em: {caminho}")
    return joblib.load(caminho)

modelo = carregar_modelo()


# Entrada do usuário
periodos = st.number_input("Dias para prever:", min_value=1, max_value=22, value=1)

if periodos > 0:
    # Criar datas futuras (não usa)
    #futuro = modelo.make_future_dataframe(periods=periodos)

    df_modelo_prever = df_ipea_brent[['data','valor','ano']]
    
    df_modelo_prever['data'] = pd.to_datetime(df_modelo_prever['data'], format='%Y-%m-%d')

    df_modelo_prever['ano'] = df_modelo_prever['data'].dt.year

    df_modelo_prever['mes'] = df_modelo_prever['data'].dt.month

    medias_mensais_modelo = df_ipea_brent.groupby(['ano', 'mes'])['valor'].mean().reset_index()
    medias_mensais_modelo = medias_mensais_modelo.rename(columns={'valor': 'media_mensal'})

    medias_anuais_modelo = df_ipea_brent.groupby('ano')['valor'].mean().reset_index()
    medias_anuais_modelo = medias_anuais_modelo.rename(columns={'valor': 'media_anual'})

    df_modelo_prever = df_modelo_prever.reset_index()

    df_modelo_prever = df_modelo_prever.merge(medias_mensais_modelo, on=['ano', 'mes'], how='left')
    df_modelo_prever = df_modelo_prever.merge(medias_anuais_modelo, on=['ano'], how='left')

    df_modelo_prever[f'rolling_mean_{5}'] = df_modelo_prever['valor'].rolling(window=5).mean().shift(1)
    df_modelo_prever[f'rolling_min_{5}'] = df_modelo_prever['valor'].rolling(window=5).min().shift(1) 
    df_modelo_prever[f'rolling_max_{5}'] = df_modelo_prever['valor'].rolling(window=5).max().shift(1)
    for lag in range(1, 5 + 1):
        df_modelo_prever[f'lag_{lag}'] = df_modelo_prever['valor'].shift(lag)

    df_modelo_prever = df_modelo_prever[df_modelo_prever['data'] > df_treino['ds'].max()]

    df_modelo_prever = df_modelo_prever.drop(columns=['valor','mes'])

    df_modelo_prever = df_modelo_prever.rename(columns={'data': 'ds'})

    producao_pretroleo_anual_lag_1 = df_eia_prod_mundial[df_eia_prod_mundial['ano'] == (df_modelo_prever.ano.max() - 1)].valor_mensal.sum()

    df_modelo_prever['prod_valor_anual'] = producao_pretroleo_anual_lag_1
    
    df_modelo_prever = df_modelo_prever.head(periodos)

    # Fazer previsão
    forecast = modelo.predict(df_modelo_prever)

 
    
    # Separando as colunas que irão para o gráfico
    previsao = forecast[['ds','yhat','yhat_lower','yhat_upper']]
    
    # Garantir tenha ligação entre os dataframe no gráfico
    previsao =  pd.concat([previsao, df_treino.tail(1)], ignore_index=True)
    
    # Garantir que 'ds' esteja como datetime
    previsao['ds'] = pd.to_datetime(previsao['ds'])
    df_treino['ds'] = pd.to_datetime(df_treino['ds'])
    
    previsao = previsao.sort_values(by='ds', ascending=True)
    
    # Iniciar o gráfico
    fig = go.Figure()

    # Linha sólida: histórico (valores reais de df_treino)
    fig.add_trace(go.Scatter(
        x=df_treino['ds'],
        y=df_treino['yhat'],  # Supondo que 'y' seja a coluna de valores reais no histórico
        mode='lines',
        name='Histórico',
        line=dict(color='#3A8FB7', dash='solid')  # Azul escuro
    ))

    # Linha pontilhada: previsão (valores previstos de previsao)
    fig.add_trace(go.Scatter(
        x=previsao['ds'],
        y=previsao['yhat'],
        mode='lines',
        name='Previsão',
        line=dict(color='#71C5E8', dash='dot')  # Azul mais claro
    ))

    # Área de confiança na previsão
    fig.add_trace(go.Scatter(
        x=pd.concat([previsao['ds'], previsao['ds'][::-1]]),
        y=pd.concat([previsao['yhat_upper'], previsao['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(113, 197, 232, 0.2)',  # Azul claro, mais suave
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Intervalo de Confiança'
    ))

    # Layout para o gráfico (tema escuro)
    fig.update_layout(
        title="Previsão do valor do petróleo brent",
        yaxis_title="Valor Petróleo Brent",
        template="plotly_dark",  # Tema escuro
    )
    
    # Personalizar o conteúdo do hover (tooltip)
    fig.update_traces(
    hovertemplate="Data: %{x|%d/%m/%Y}<br>Valor: %{y:.2f}<extra></extra>"
)
    
    fig.update_xaxes(
    tickformat="%d/%m/%y",  # ou outro formato desejado
    )

    # Mostrar o gráfico no Streamlit
    st.plotly_chart(fig)
    
    col1, col2 = st.columns(2)
    
    variacao_valores = ((previsao['yhat'].tail(1).iloc[0] / df_treino['yhat'].tail(1).iloc[0]) - 1) * 100

    with col1:
        st.write('**Último Valor do Histórico**')
        data_historico = df_treino['ds'].tail(1).iloc[0].strftime('%d/%m/%Y')
        st.metric(label=data_historico, value=df_treino['yhat'].tail(1).iloc[0].round(2))
    
    with col2:
        st.write('**Último Valor do Previsto**')
        data_historico = previsao['ds'].tail(1).iloc[0].strftime('%d/%m/%Y')
        st.metric(label=data_historico, value=previsao['yhat'].tail(1).iloc[0].round(2), delta=f"{variacao_valores:.2f}%", delta_color="inverse")

   
