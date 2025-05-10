# Importando bibiotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose


# Carregando dataframe
url = 'http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650971490&oper=view'
df_ipea_brent = pd.read_html(url 
                             ,encoding='utf-8' 
                             ,attrs={'id':'grd_DXMainTable'} 
                             ,thousands= '.'
                             ,skiprows=1 
                             )[0] 
df_ipea_brent.columns = ['data', 'preco_uss']
df_ipea_brent['data'] = pd.to_datetime(df_ipea_brent['data'], format="%d/%m/%Y")
df_ipea_brent['preco_uss'] = df_ipea_brent['preco_uss'].str.replace(',','.')
df_ipea_brent['preco_uss'] = pd.Series(df_ipea_brent['preco_uss'], dtype='Float64')
df_ipea_brent = df_ipea_brent.set_index('data')
df_ipea_brent = df_ipea_brent.sort_index()
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

df_ipea_brent['variacao'] = df_ipea_brent['preco_uss'].diff() # vendo a diferença do dia atual pelo dia anterior

df_ipea_brent['p_variacao'] = ((df_ipea_brent['preco_uss'] / df_ipea_brent['preco_uss'].shift(1)) - 1) # Em porcentagem a diferença entre o dia atual e anterior

df_ipea_brent = df_ipea_brent.drop(df_ipea_brent.index[0])


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
df_grouped = df_ipea_brent.groupby('ano')['preco_uss'].mean().reset_index() # Agrupar por ano e calcular a média
df_grouped['diferenca'] = ((df_grouped['preco_uss'] / df_grouped['preco_uss'].shift(1)) - 1) # Calcular a diferença ano a ano
df_grouped = df_grouped.drop(df_grouped.index[0])


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
        customdata=df_filtrado[['nome_dia_semana','p_variacao']].values,
        hovertemplate=(
            "<b>Data:</b> %{x|%d/%m/%Y}<br>" +
            "<b>Preço:</b> %{y:.2f} USD<br>" +
            "<b>Variação Diária:</b> %{customdata[1]:.2%}<br>" +
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





def plot_preco_brent_anual(df_anual, ano_ini, ano_fim):
    # Filtrar o DataFrame
    df_ano = df_anual[(df_anual['ano'] >= ano_ini) & (df_anual['ano'] <= ano_fim)].copy()

    # Criar o gráfico de barras
    fig = go.Figure()

    # Adicionar as barras
    fig.add_trace(go.Bar(
        x=df_ano['ano'],
        y=df_ano['preco_uss'],
        text=df_ano['preco_uss'].apply(lambda x: f"$ {x:.2f}"),
        textposition='inside',
        insidetextfont=dict(color='rgb(14, 17, 23)'),
        marker_color='#71C5E8',
        showlegend=False,
        hoverinfo='skip'
    ))

    # Adicionar anotações com a variação percentual (coloridas)
    for i, row in df_ano.iterrows():
        if pd.notna(row['diferenca']):
            cor = 'lightcoral' if row['diferenca'] < 0 else 'lightskyblue'
            sinal = "+" if row['diferenca'] >= 0 else "−"
            fig.add_annotation(
                x=row['ano'],
                y=row['preco_uss'] + 5,
                text=f"<span style='color:{cor}'>{sinal}{abs(row['diferenca']):.2f}%</span>",
                showarrow=False,
                font=dict(size=11)
            )

    # Layout
    fig.update_layout(
        title=f'Preço Médio Anual do Petróleo Brent de {ano_ini} até {ano_fim}',
        font=dict(color='white'),
        xaxis=dict(tickmode='linear', tick0=ano_ini, dtick=1, title='Ano'),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        uniformtext_minsize=8,
        uniformtext_mode='show',
        showlegend=False,
        hovermode=False
    )

    st.plotly_chart(fig, use_container_width=True)




def plot_var_brent(df, ano_inicial, ano_final):
    # Filtra o DataFrame pelo intervalo de anos
    df_filtrado = df[(df['ano'] >= ano_inicial) & (df['ano'] <= ano_final)]

    # Criação da figura
    fig = go.Figure()

    # Linha da variação percentual
    fig.add_trace(go.Scatter(
        x=df_filtrado.index,
        y=df_filtrado['p_variacao'],
        mode='lines',
        name='Variação Percentual do Brent',
        line=dict(color='#71C5E8', width=2),
    ))

    # Configurações do layout
    fig.update_layout(
        title=f'Variação Percentual do Preço do Petróleo Brent de {ano_inicial} até {ano_final}',
        xaxis_title='Data',
        yaxis_title='Variação Percentual',
        template='plotly_dark',
        xaxis=dict(
            tickformat='%Y',
            dtick='M12'
        ),
        yaxis=dict(
        tickformat='.0%',  # Formatar como percentual com 2 casas decimais
    )
    )

    # Exibe no Streamlit
    st.plotly_chart(fig, use_container_width=True)



######

st.title('Storytelling')
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Visão Geral", "💡 Insight", "📅 Análise Temporal", "↗️ Variações","🛢️ Produção"])

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
         
    periodo2 = (
    "1987 - 2000",
    "2000 - 2013",
    "2013 - 2025"
    )
 
    periodo_valor2 = st.segmented_control(
      "Selecione o Período", list(periodo2), selection_mode="single", key="segmento_periodo_valor2", default = "1987 - 2000"
    )

   
    if periodo_valor2 == "1987 - 2000":     
         plot_preco_brent(df_ipea_brent, 1987, 2000,df_eventos_novos, [0, 200])
    if periodo_valor2 == "2000 - 2013": 
         plot_preco_brent(df_ipea_brent, 2000, 2013,df_eventos_novos, [0, 200])
    if periodo_valor2 == "2013 - 2025": 
         plot_preco_brent(df_ipea_brent, 2013, 2025,df_eventos_novos, [0, 200])


with tab3:
   st.empty()
   
   periodo = {
    "Mensal": 30,
    "Bimestral": 60,
    "Trimestral": 90,
    "Anual": 292
   }
 
   
   periodo_valor = st.segmented_control(
      "Selecione o Período", list(periodo.keys()), selection_mode="single", key="segmento_periodo_valor3", default= "Mensal"  
   )
   
   if periodo_valor != None:

      periodo_decomposicao = periodo[periodo_valor]
      st.write(f"Período selecionado: {periodo_decomposicao} dias")
      decomposicao = seasonal_decompose(df_ipea_brent['1988-01-01':'2024-12-31']['preco_uss'], model="additive", period=periodo_decomposicao)
      # Gráfico de Tendência
      fig_tendencia = go.Figure()
      # Plotando a Tendência
      fig_tendencia.add_trace(go.Scatter(
      x=decomposicao.trend.index,
      y=decomposicao.trend,
      mode='lines',
      name='Tendência',
      line=dict(color='blue')
      ))
   # Configuração do layout
      fig_tendencia.update_layout(
         title="Tendência",
         xaxis_title="Ano",
         yaxis_title="Valor",
         xaxis=dict(
            tickvals=anos,
            ticktext=[str(ano) for ano in anos],
            tickformat="%Y"
         ),
         template="plotly_dark"
        )
      # Exibir gráfico no Streamlit
      st.plotly_chart(fig_tendencia)
      ultimo_ano = decomposicao.seasonal.index.year.max()
      # Filtra os dados da sazonalidade para o último ano
      dados_sazonalidade = decomposicao.seasonal[decomposicao.seasonal.index.year == ultimo_ano]
      # Cria o gráfico
      fig_sazonalidade = go.Figure()
      fig_sazonalidade.add_trace(go.Scatter(
         x=dados_sazonalidade.index,
         y=dados_sazonalidade,
         mode='lines',
         name=f"Sazonalidade {ultimo_ano}",
         line=dict(color='green')
      ))
      # Configura o layout para exibir o mês no eixo x
      fig_sazonalidade.update_layout(
         title=f"Sazonalidade de {ultimo_ano}",
         xaxis_title="Mês",
         yaxis_title="Valor",
         xaxis=dict(
            tickformat="%b",  # Mostra apenas o nome abreviado do mês (Jan, Feb, etc.)
            ticklabelmode="period"  # Garante que o label represente o início do mês
         ),
         template="plotly_dark"
        )
      # Exibe o gráfico no Streamlit
      st.plotly_chart(fig_sazonalidade)

   

with tab4:
    periodo4 = (
    "1987 - 2000",
    "2000 - 2013",
    "2013 - 2025"
    )
 
   
    periodo_valor4 = st.segmented_control(
      "Selecione o Período", list(periodo4), selection_mode="single", key="segmento_periodo_valor4", default= "1987 - 2000"
    )

   
    if periodo_valor4 == "1987 - 2000":
        plot_preco_brent_anual(df_grouped, 1987, 2000)
        plot_var_brent(df_ipea_brent, 1987, 2000)
        
    if periodo_valor4 == "2000 - 2013":
        plot_preco_brent_anual(df_grouped, 2000, 2013)
        plot_var_brent(df_ipea_brent, 2000, 2013)
        
    if periodo_valor4 == "2013 - 2025":
        plot_preco_brent_anual(df_grouped, 2013, 2025)
        plot_var_brent(df_ipea_brent, 2013, 2025)

with tab5:
 st.write('''
            <div style="text-align: justify;">
               **Talvez mover o mês aqui possa ser uma boa ideia e deixar 2 linhas comparativas. Ou usar dispersão **
            </div>
            ''', unsafe_allow_html=True)
 
 df_ipea_brent_media = df_ipea_brent.groupby(['data','ano','mes']).preco_uss.mean().reset_index()
 df_ipea_brent_media.set_index('data', inplace=True)
 df_ipea_brent_media.sort_index(ascending=True, inplace=True)
 
 df_prod_petroleo_soma2 = pd.read_csv('https://github.com/nascimentorafael1/techfase4/raw/refs/heads/main/data/df_eia_prod_mundial.csv')
 df_prod_petroleo_soma2.set_index('data', inplace=True)
 df_prod_petroleo_soma2.sort_index(ascending=True, inplace=True)
 
 def plot_brent_vs_mmbpd(df_brent, df_mmbpd, ano_inicio1, ano_fim2):
    # Filtra os DataFrames pelo intervalo de anos desejado
    df_brent_filtrado = df_brent[(df_brent['ano'] >= ano_inicio1) & (df_brent['ano'] <= ano_fim2)]
    df_mmbpd_filtrado = df_mmbpd[(df_mmbpd['ano'] >= ano_inicio1) & (df_mmbpd['ano'] <= ano_fim2)]

    # Cria a figura
    fig = go.Figure()

    # Linha do preço do Brent (azul escuro)
    fig.add_trace(go.Scatter(
        x=df_brent_filtrado.index,
        y=df_brent_filtrado['preco_uss'],
        mode='lines',
        name='Preço Brent (USD)',
        line=dict(color='#0d3b66', width=3),
        yaxis='y2'
    ))

    # Barras da produção de petróleo (azul claro)
    fig.add_trace(go.Bar(
        x=df_mmbpd_filtrado.index,
        y=df_mmbpd_filtrado['valor_mensal'],
        name='Produção de Petróleo (MMBPD)',
        marker_color='#71C5E8',
        yaxis='y1'
    ))

    # Layout com dois eixos Y
    fig.update_layout(
        title=f'Produção de Petróleo (MMBPD) vs Preço Brent (USD) — {ano_inicio1} a {ano_fim2}',
        xaxis_title='Ano',
        yaxis=dict(title='Produção (MMBPD)', side='left', showgrid=False),
        yaxis2=dict(title='Preço Brent (USD)', overlaying='y', side='right'),
        template='plotly_dark',
        legend=dict(x=0.01, y=0.99)
    )

    # Exibe no Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
 periodo5 = (
    "1987 - 2000",
    "2000 - 2013",
    "2013 - 2025"
    )
 
   
 periodo_valor5 = st.segmented_control(
      "Selecione o Período", list(periodo5), selection_mode="single", key="segmento_periodo_valor5", default= "1987 - 2000"
    )

   
 if periodo_valor5 == "1987 - 2000":
  plot_brent_vs_mmbpd(df_ipea_brent_media, df_prod_petroleo_soma2, 1987, 2000)

        
 if periodo_valor5 == "2000 - 2013":
  plot_brent_vs_mmbpd(df_ipea_brent_media, df_prod_petroleo_soma2, 2000, 2013)

        
 if periodo_valor5 == "2013 - 2025":
  plot_brent_vs_mmbpd(df_ipea_brent_media, df_prod_petroleo_soma2, 2013, 2025)




