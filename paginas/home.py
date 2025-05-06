# Importando bibiotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.title('PETRÓLEO BRENT :fuelpump:')
st.subheader("Tech Challenger - Fase 4 - Data Analytics - Pós Tech - 7DTAT - FIAP")



st.image("https://raw.githubusercontent.com/nascimentorafael1/techfase4/refs/heads/main/img/capa-1000x286.jpg")

st.subheader("Introdução")




st.write('''
         <div style="text-align: justify;">
            O petróleo Brent é produzido no Mar do Norte (Europa). Trata-se de um tipo de petróleo bruto leve e doce, o que facilita o processo 
            de refino para a produção de gasolina, diesel e outros combustíveis. O Brent é utilizado como referência para precificar o preço do 
            petróleo e, consequentemente, dos combustíveis, em nível global
         </div>
         ''', unsafe_allow_html=True)


st.subheader("Objetivo")

st.write('''
         <div style="text-align: justify;">
            Como objetivo do Tech Challenger Fase 4, atuamos como uma consultoria e desenvolvemos um dashboard interativo com insights sobre a 
            variação do preço do petróleo Brent, incorporando fatores como geopolítica, crises econômicas e demanda global. Além disso, criamos 
            um modelo de Machine Learning de série temporal com base nos dados históricos de preço do petróleo Brent
         </div>
         ''', unsafe_allow_html=True)


st.subheader("Navegação")

st.write('''
         <div style="text-align: justify;">
               <p>Utilize o menu lateral para navegar pelo projeto e explorar os resultados disponíveis.</p>
               <p>A estrutura do projeto está organizada da seguinte forma:</p>
               <ol>
                  <li>
                     <strong>Storytelling:</strong> Apresenta uma análise contextual com insights sobre o histórico dos preços do petróleo Brent.
                  </li>
                  <li>
                     <strong>Dashboard:</strong> Exibe visualizações interativas relacionadas aos dados do petróleo Brent.
                  </li>
                  <li>
                     <strong>Predição:</strong> Realiza previsões diárias dos preços do petróleo Brent com base nos dados analisados.
                  </li>
                  <li>
                     <strong>Dados Técnicos:</strong> Detalha a estrutura do projeto e fornece o link para acesso ao código no GitHub.
                  </li>
               </ol>
         </div>
         ''', unsafe_allow_html=True)