import pandas as pd
import numpy as np
import streamlit as st
import os
import warnings
import plotly.express as px
from datetime import datetime
import calendar

warnings.filterwarnings('ignore')

usuario = os.getlogin()
#diretorio = f'C:\\Users\\{usuario}\\OneDrive - NTT DATA EMEAL\\Escritorio\\PEM_NPEM DEC-FEC\\'
data_atualizacao_str = "02/09/2024"
data_atualizacao = datetime.strptime(data_atualizacao_str, "%d/%m/%Y") # Converte a string de data para um objeto datetime
dia = data_atualizacao.day
mes = data_atualizacao.month
ano = data_atualizacao.year
dia_formatado = f"{dia:02d}"
mes_formatado = f"{mes:02d}"





# Configurando o Streamlit
st.set_page_config(page_title='DEC/FEC Enel Rio', layout='wide')

with st.container():
    st.title('Análise DEC/FEC Enel Rio')
    st.write(f'Base atualizada semanalmente. Última atualização feita em {dia_formatado}/{mes_formatado}/{ano}.')
    st.write('Desenvolvido por [João Henrique Pires](https://www.linkedin.com/in/joao-henrique-pires/).')
    st.write('')





# Leitura das bases
base_dec = pd.read_excel('DEC-FEC Conjuntos.xlsx', sheet_name='DEC')
base_fec = pd.read_excel('DEC-FEC Conjuntos.xlsx', sheet_name='FEC')
base_dec_polo_enel = pd.read_excel('DEC-FEC Polos.xlsx', sheet_name='DEC')
base_fec_polo_enel = pd.read_excel('DEC-FEC Polos.xlsx', sheet_name='FEC')

@st.cache_data
def ler_arquivos(dir):
    base_clientes = pd.read_csv(dir, sep='|', on_bad_lines='skip')
    base_conjuntos = pd.read_csv(dir, sep='|', on_bad_lines='skip')
    base_meta_aneel_conjuntos = pd.read_csv(dir, sep='|', on_bad_lines='skip')
    base_meta_aneel_polos = pd.read_csv(dir, sep='|', on_bad_lines='skip')
    return base_clientes, base_conjuntos, base_meta_aneel_conjuntos, base_meta_aneel_polos
base_clientes = ler_arquivos('Clientes 2024.txt')
base_clientes = base_clientes[0]
base_conjuntos = ler_arquivos('Conjuntos.txt')
base_conjuntos = base_conjuntos[0]
base_meta_aneel_conjuntos = ler_arquivos('Meta Aneel Conjuntos 2024.txt')
base_meta_aneel_conjuntos = base_meta_aneel_conjuntos[0]
base_meta_aneel_polos = ler_arquivos('Meta Aneel Polos Enel 2024.txt')
base_meta_aneel_polos = base_meta_aneel_polos[0]





# Tratativas
# Quantidade de colunas bases DEC e FEC
qtd_cols = base_dec.shape[1]
meses = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}
ultima_coluna = base_dec.columns[-1]
abreviatura_mes = ultima_coluna[:3]
numero_ultimo_mes = meses[abreviatura_mes]

data_atual = datetime.now()
dia_do_ano = data_atual.timetuple().tm_yday
total_dias_ano = 366 if calendar.isleap(data_atual.year) else 365
percentual_ano = (dia_do_ano / total_dias_ano)


# Cálculo da média de clientes
base_clientes['Média Clientes'] = base_clientes.iloc[:, 1:].mean(axis=1).round(0)
# Linha abaixo pega as últimas 12 colunas, usar somente quando tivermos 12 colunas na base de clientes
#base_clientes['Média Clientes'] = base_clientes.iloc[:, -12:].mean(axis=1).round(0)





base_dec_polo = pd.merge(base_dec, base_conjuntos, on='Conjunto', how='left')
colunas_para_mover_dec = base_dec_polo.columns[-3:].tolist() #extraindo as ultimas 3 colunas que vieram do merge
base_dec_menor = base_dec_polo.drop(columns=colunas_para_mover_dec) #removendo as colunas da base original
base_dec_novo = pd.concat([base_dec_menor.iloc[:, :1], base_dec_polo[colunas_para_mover_dec], base_dec_menor.iloc[:, 1:]], axis=1) #inserindo as colunas na posição específica
base_dec_polo = base_dec_novo.copy()
#base_dec_polo

base_fec_polo = pd.merge(base_fec, base_conjuntos, on='Conjunto', how='left')
colunas_para_mover_fec = base_fec_polo.columns[-3:].tolist() #extraindo as ultimas 3 colunas que vieram do merge
base_fec_menor = base_fec_polo.drop(columns=colunas_para_mover_fec) #removendo as colunas da base original
base_fec_novo = pd.concat([base_fec_menor.iloc[:, :1], base_fec_polo[colunas_para_mover_fec], base_fec_menor.iloc[:, 1:]], axis=1) #inserindo as colunas na posição específica
base_fec_polo = base_fec_novo.copy()
#base_fec_polo





# Criação de base DEC/FEC Análises
base_dec_analises = pd.DataFrame()
base_dec_analises = base_dec[['Conjunto']]
# Cálculo de DEC acumulado ano
base_dec_analises['DEC Acumulado - 2024'] = base_dec.iloc[:, (qtd_cols - numero_ultimo_mes):].sum(axis=1)
# Merge para pegar a meta Aneel
base_dec_analises = pd.merge(base_dec_analises, base_meta_aneel_conjuntos[['Conjunto', 'DEC']], on='Conjunto', how='left')
base_dec_analises.rename(columns = {'DEC':'Meta Aneel DEC'}, inplace = True)
# Criação de coluna "% Consumido da Meta Anual"
base_dec_analises['% Consumido da Meta Anual'] = base_dec_analises['DEC Acumulado - 2024'] / base_dec_analises['Meta Aneel DEC']
# Cálculo DEC TAM
base_dec_analises['DEC TAM'] = base_dec.iloc[:, qtd_cols - 12:].sum(axis=1)
# Criação de coluna "% Consumido TAM"
base_dec_analises['% Consumido TAM'] = base_dec_analises['DEC TAM'] / base_dec_analises['Meta Aneel DEC']
#base_dec_analises

base_fec_analises = pd.DataFrame()
base_fec_analises = base_fec[['Conjunto']]
# Cálculo de FEC acumulado ano
base_fec_analises['FEC Acumulado - 2024'] = base_fec.iloc[:, (qtd_cols - numero_ultimo_mes):].sum(axis=1)
# Merge para pegar a meta Aneel
base_fec_analises = pd.merge(base_fec_analises, base_meta_aneel_conjuntos[['Conjunto', 'FEC']], on='Conjunto', how='left')
base_fec_analises.rename(columns = {'FEC':'Meta Aneel FEC'}, inplace = True)
# Criação de coluna "% Consumido da Meta Anual"
base_fec_analises['% Consumido da Meta Anual'] = base_fec_analises['FEC Acumulado - 2024'] / base_fec_analises['Meta Aneel FEC']
# Cálculo FEC TAM
base_fec_analises['FEC TAM'] = base_fec.iloc[:, qtd_cols - 12:].sum(axis=1)
# Criação de coluna "% Consumido TAM"
base_fec_analises['% Consumido TAM'] = base_fec_analises['FEC TAM'] / base_fec_analises['Meta Aneel FEC']
#base_fec_analises





# DF estado dos Conjuntos 2024
base_estado_conjuntos_dec = base_dec.iloc[:, [0] + list(range(14,qtd_cols))] # quando mudar o ano, alterar o 14 para 26
base_estado_conjuntos_dec_TAM = base_estado_conjuntos_dec.iloc[:, 1:]
base_estado_conjuntos_dec_TAM = base_estado_conjuntos_dec_TAM.rolling(window=12, axis=1).sum()
base_estado_conjuntos_dec_TAM['Conjunto'] = base_estado_conjuntos_dec['Conjunto']
base_estado_conjuntos_dec_TAM = base_estado_conjuntos_dec_TAM.drop(base_estado_conjuntos_dec_TAM.columns[:11], axis=1)
base_estado_conjuntos_dec_TAM = base_estado_conjuntos_dec_TAM[['Conjunto'] + [col for col in base_estado_conjuntos_dec_TAM.columns if col != 'Conjunto']]
base_estado_conjuntos_dec_TAM.columns = [base_estado_conjuntos_dec_TAM.columns[0]] + [f"TAM {col}" for col in base_estado_conjuntos_dec_TAM.columns[1:]]
#base_estado_conjuntos_dec_TAM

# DF estado dos Conjuntos 2024
base_estado_conjuntos_fec = base_fec.iloc[:, [0] + list(range(14,qtd_cols))] # quando mudar o ano, alterar o 14 para 26
base_estado_conjuntos_fec_TAM = base_estado_conjuntos_fec.iloc[:, 1:]
base_estado_conjuntos_fec_TAM = base_estado_conjuntos_fec_TAM.rolling(window=12, axis=1).sum()
base_estado_conjuntos_fec_TAM['Conjunto'] = base_estado_conjuntos_fec['Conjunto']
base_estado_conjuntos_fec_TAM = base_estado_conjuntos_fec_TAM.drop(base_estado_conjuntos_fec_TAM.columns[:11], axis=1)
base_estado_conjuntos_fec_TAM = base_estado_conjuntos_fec_TAM[['Conjunto'] + [col for col in base_estado_conjuntos_fec_TAM.columns if col != 'Conjunto']]
base_estado_conjuntos_fec_TAM.columns = [base_estado_conjuntos_fec_TAM.columns[0]] + [f"TAM {col}" for col in base_estado_conjuntos_fec_TAM.columns[1:]]
#base_estado_conjuntos_fec_TAM





# Criando DF com o estado do conjunto em 2024
base_estado_conjuntos_dec = pd.DataFrame()
base_estado_conjuntos_dec['Conjunto'] = base_conjuntos['Conjunto']
base_estado_conjuntos_dec.insert(loc=1, column='Meta Aneel DEC', value=base_dec_analises['Meta Aneel DEC'])
for coluna in base_estado_conjuntos_dec_TAM.columns[1:]:
    base_estado_conjuntos_dec[f'{coluna}'] = base_estado_conjuntos_dec_TAM[coluna] / base_estado_conjuntos_dec['Meta Aneel DEC']
for coluna in base_estado_conjuntos_dec.columns[2:]:
    base_estado_conjuntos_dec[coluna] = np.where(base_estado_conjuntos_dec[coluna] < 1, 'Normal',
                                        np.where(base_estado_conjuntos_dec[coluna] <= 1.4, 'Atenção',
                                        'Crítico'))
base_estado_conjuntos_dec = base_estado_conjuntos_dec.drop('Meta Aneel DEC', axis=1)
base_estado_conjuntos_dec.columns = base_estado_conjuntos_dec.columns.str.replace('TAM ', '', regex=False)
#base_estado_conjuntos_dec

# Criando DF com o estado do conjunto em 2024
base_estado_conjuntos_fec = pd.DataFrame()
base_estado_conjuntos_fec['Conjunto'] = base_conjuntos['Conjunto']
base_estado_conjuntos_fec.insert(loc=1, column='Meta Aneel FEC', value=base_fec_analises['Meta Aneel FEC'])
for coluna in base_estado_conjuntos_fec_TAM.columns[1:]:
    base_estado_conjuntos_fec[f'{coluna}'] = base_estado_conjuntos_fec_TAM[coluna] / base_estado_conjuntos_fec['Meta Aneel FEC']
for coluna in base_estado_conjuntos_fec.columns[2:]:
    base_estado_conjuntos_fec[coluna] = np.where(base_estado_conjuntos_fec[coluna] < 1, 'Normal',
                                        np.where(base_estado_conjuntos_fec[coluna] <= 1.22, 'Atenção',
                                        'Crítico'))
base_estado_conjuntos_fec = base_estado_conjuntos_fec.drop('Meta Aneel FEC', axis=1)
base_estado_conjuntos_fec.columns = base_estado_conjuntos_fec.columns.str.replace('TAM ', '', regex=False)
#base_estado_conjuntos_fec





base_estado_conjuntos_dec_melt = pd.melt(base_estado_conjuntos_dec, id_vars=['Conjunto'], var_name='Mês', value_name='Estado Conjunto')
base_estado_conjuntos_dec_consolidado = pd.crosstab(base_estado_conjuntos_dec_melt['Estado Conjunto'], base_estado_conjuntos_dec_melt['Mês'])
base_estado_conjuntos_dec_consolidado_DF = pd.DataFrame(base_estado_conjuntos_dec_consolidado)
ordem_colunas = ['jan/24', 'fev/24', 'mar/24', 'abr/24', 'mai/24', 'jun/24', 'jul/24', 'ago/24']
ordem_categorias = ['Normal', 'Atenção', 'Crítico']
base_estado_conjuntos_dec_consolidado_DF = base_estado_conjuntos_dec_consolidado_DF[ordem_colunas]
base_estado_conjuntos_dec_consolidado_DF = base_estado_conjuntos_dec_consolidado_DF.reset_index()
base_estado_conjuntos_dec_consolidado_DF['Estado Conjunto'] = pd.Categorical(base_estado_conjuntos_dec_consolidado_DF['Estado Conjunto'], categories=ordem_categorias, ordered=True)
base_estado_conjuntos_dec_consolidado_DF = base_estado_conjuntos_dec_consolidado_DF.sort_values(by='Estado Conjunto')
#base_estado_conjuntos_dec_consolidado_DF

base_estado_conjuntos_fec_melt = pd.melt(base_estado_conjuntos_fec, id_vars=['Conjunto'], var_name='Mês', value_name='Estado Conjunto')
base_estado_conjuntos_fec_consolidado = pd.crosstab(base_estado_conjuntos_fec_melt['Estado Conjunto'], base_estado_conjuntos_fec_melt['Mês'])
base_estado_conjuntos_fec_consolidado_DF = pd.DataFrame(base_estado_conjuntos_fec_consolidado)
ordem_colunas = ['jan/24', 'fev/24', 'mar/24', 'abr/24', 'mai/24', 'jun/24', 'jul/24', 'ago/24']
ordem_categorias = ['Normal', 'Atenção', 'Crítico']
base_estado_conjuntos_fec_consolidado_DF = base_estado_conjuntos_fec_consolidado_DF[ordem_colunas]
base_estado_conjuntos_fec_consolidado_DF = base_estado_conjuntos_fec_consolidado_DF.reset_index()
base_estado_conjuntos_fec_consolidado_DF['Estado Conjunto'] = pd.Categorical(base_estado_conjuntos_fec_consolidado_DF['Estado Conjunto'], categories=ordem_categorias, ordered=True)
base_estado_conjuntos_fec_consolidado_DF = base_estado_conjuntos_fec_consolidado_DF.sort_values(by='Estado Conjunto')
#base_estado_conjuntos_fec_consolidado_DF





# Sidebar
st.sidebar.image('https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Enel_Group_logo.svg/1024px-Enel_Group_logo.svg.png', use_column_width=True)
st.sidebar.markdown('# APM Rio')
st.sidebar.write('---')

sidebar_ano = st.sidebar.selectbox('Ano', ('23', '24'), index=None)
#sidebar_ano = sidebar_ano[-2:]
#sidebar_ano = input('ano')
sidebar_UT = st.sidebar.selectbox('Unidade Territorial', sorted(base_conjuntos['Área'].unique()), index=None)
base_conjuntos_filtro_UT = base_conjuntos[base_conjuntos['Área'] == sidebar_UT]
sidebar_polo = st.sidebar.selectbox('Polo', sorted(base_conjuntos_filtro_UT ['Regional'].unique()), index=None)





# Gráficos filtrados pela Sidebar
base_dec_polo_filtro = base_dec_polo[base_dec_polo['Regional'] == sidebar_polo] # filtrando o DF pelo polo escolhido
primeira_coluna_dec = base_dec_polo_filtro.iloc[:, [0]] # pegando a primeira coluna do DF filtrado
colunas_ano_filtrado_dec = base_dec_polo_filtro.filter(like=f'{sidebar_ano}') # pegando o DF no ano escolhido
df_resultado_dec = pd.concat([primeira_coluna_dec, colunas_ano_filtrado_dec], axis=1).reset_index(drop=True)
df_transformado_dec = pd.melt(df_resultado_dec, id_vars=['Conjunto'], var_name='Mês', value_name='DEC')
totais_por_mes_dec = df_transformado_dec.groupby('Conjunto')['DEC'].sum().reset_index()
totais_por_mes_dec = totais_por_mes_dec.merge(base_meta_aneel_conjuntos[['Conjunto', 'DEC']], on='Conjunto').rename(columns={'DEC_x':'DEC','DEC_y':'Meta DEC'})

base_fec_polo_filtro = base_fec_polo[base_fec_polo['Regional'] == sidebar_polo]
primeira_coluna_fec = base_fec_polo_filtro.iloc[:, [0]]
colunas_ano_filtrado_fec = base_fec_polo_filtro.filter(like=f'{sidebar_ano}')
df_resultado_fec = pd.concat([primeira_coluna_fec, colunas_ano_filtrado_fec], axis=1).reset_index(drop=True)
df_transformado_fec = pd.melt(df_resultado_fec, id_vars=['Conjunto'], var_name='Mês', value_name='FEC')
totais_por_mes_fec = df_transformado_fec.groupby('Conjunto')['FEC'].sum().reset_index()
totais_por_mes_fec = totais_por_mes_fec.merge(base_meta_aneel_conjuntos[['Conjunto', 'FEC']], on='Conjunto').rename(columns={'FEC_x':'FEC','FEC_y':'Meta FEC'})


base_dec_polo_enel_ano = base_dec_polo_enel[base_dec_polo_enel['Meses'].str.contains(f'/{sidebar_ano}')]
base_dec_polo_enel_ano = base_dec_polo_enel_ano.iloc[:, [0] + list(range(-3, 0))]
base_dec_polo_enel_ano_transformado = pd.melt(base_dec_polo_enel_ano, id_vars=['Meses'], var_name='UT', value_name='DEC')
totais_por_mes_polo_enel_ano_dec = base_dec_polo_enel_ano_transformado.groupby('UT')['DEC'].sum().reset_index()

base_fec_polo_enel_ano = base_fec_polo_enel[base_fec_polo_enel['Meses'].str.contains(f'/{sidebar_ano}')]
base_fec_polo_enel_ano = base_fec_polo_enel_ano.iloc[:, [0] + list(range(-3, 0))]
base_fec_polo_enel_ano_transformado = pd.melt(base_fec_polo_enel_ano, id_vars=['Meses'], var_name='UT', value_name='FEC')
totais_por_mes_polo_enel_ano_fec = base_fec_polo_enel_ano_transformado.groupby('UT')['FEC'].sum().reset_index()


base_dec_polos = base_dec_polo_enel.iloc[:, :-3]
base_dec_polos = base_dec_polos[base_dec_polos['Meses'].str.contains(f'/{sidebar_ano}')]
base_dec_polos_transformado = pd.melt(base_dec_polos, id_vars=['Meses'], var_name='Polos', value_name='DEC')
totais_por_mes_polos_dec = base_dec_polos_transformado.groupby('Polos')['DEC'].sum().reset_index()

base_fec_polos = base_fec_polo_enel.iloc[:, :-3]
base_fec_polos = base_fec_polos[base_fec_polos['Meses'].str.contains(f'/{sidebar_ano}')]
base_fec_polos_transformado = pd.melt(base_fec_polos, id_vars=['Meses'], var_name='Polos', value_name='FEC')
totais_por_mes_polos_fec = base_fec_polos_transformado.groupby('Polos')['FEC'].sum().reset_index()


base_dec_analises_com_polo = base_dec_analises.merge(base_conjuntos[['Conjunto', 'Regional']], on='Conjunto')
base_dec_analise_ytd = base_dec_analises_com_polo[base_dec_analises_com_polo['Regional'] == sidebar_polo]
base_dec_analise_ytd = base_dec_analise_ytd.sort_values(by='% Consumido da Meta Anual', ascending=True)
def definir_cor_DEC_ytd(valor):
    if valor > 1:
        return 'DEC Irreversível'
    elif percentual_ano <= valor <= 1:
        return 'DEC em Atenção'
    else:
        return 'DEC Controlado'
base_dec_analise_ytd['Status DEC YTD'] = base_dec_analise_ytd['% Consumido da Meta Anual'].apply(definir_cor_DEC_ytd)

base_fec_analises_com_polo = base_fec_analises.merge(base_conjuntos[['Conjunto', 'Regional']], on='Conjunto')
base_fec_analise_ytd = base_fec_analises_com_polo[base_fec_analises_com_polo['Regional'] == sidebar_polo]
base_fec_analise_ytd = base_fec_analise_ytd.sort_values(by='% Consumido da Meta Anual', ascending=True)
def definir_cor_FEC_ytd(valor):
    if valor > 1:
        return 'FEC Irreversível'
    elif percentual_ano <= valor <= 1:
        return 'FEC em Atenção'
    else:
        return 'FEC Controlado'
base_fec_analise_ytd['Status FEC YTD'] = base_fec_analise_ytd['% Consumido da Meta Anual'].apply(definir_cor_FEC_ytd)


base_dec_analise_tam = base_dec_analise_ytd.sort_values(by='% Consumido TAM', ascending=True)
def definir_cor_DEC_tam(valor):
    if valor >= 1.4:
        return 'Conjunto Crítico'
    elif valor < 1:
        return 'Conjunto Normal'
    else:
        return 'Conjunto em Atenção'
base_dec_analise_tam['Status DEC TAM'] = base_dec_analise_tam['% Consumido TAM'].apply(definir_cor_DEC_tam)

base_fec_analise_tam = base_fec_analise_ytd.sort_values(by='% Consumido TAM', ascending=True)
def definir_cor_FEC_tam(valor):
    if valor >= 1.22:
        return 'Conjunto Crítico'
    elif valor < 1:
        return 'Conjunto Normal'
    else:
        return 'Conjunto em Atenção'
base_fec_analise_tam['Status FEC TAM'] = base_fec_analise_tam['% Consumido TAM'].apply(definir_cor_FEC_tam)


base_estado_conjuntos_dec_consolidado_DF_melt = base_estado_conjuntos_dec_consolidado_DF.melt(id_vars=['Estado Conjunto'], var_name='Mês', value_name='Num Conjuntos')

base_estado_conjuntos_fec_consolidado_DF_melt = base_estado_conjuntos_fec_consolidado_DF.melt(id_vars=['Estado Conjunto'], var_name='Mês', value_name='Num Conjuntos')


base_dec_analises_com_polo_tam = base_dec_analises_com_polo.sort_values(by='% Consumido TAM', ascending=True)
base_dec_analises_com_polo_tam['Status DEC TAM'] = base_dec_analises_com_polo_tam['% Consumido TAM'].apply(definir_cor_DEC_tam)

base_dec_analises_com_polo_ytd = base_dec_analises_com_polo.sort_values(by='% Consumido da Meta Anual', ascending=True)
base_dec_analises_com_polo_ytd['Status DEC YTD'] = base_dec_analises_com_polo_ytd['% Consumido da Meta Anual'].apply(definir_cor_DEC_ytd)





tab1, tab2, tab3, tab4 = st.tabs(["Enel Rio", "Conjuntos", "Métrica Anual", "Listagem Conjuntos"])

with tab1:
    st.markdown("<h3 style='text-align: center;'>Enel Rio</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    graf_dec_ut_enel = px.bar(base_dec_polo_enel_ano_transformado, x='UT', y='DEC', color='Meses', title='DEC', width=430, height=380)
    graf_dec_ut_enel.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.8,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['UT'],
            y=row['DEC'],
            text=f"{row['DEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_polo_enel_ano_dec.iterrows()])

    graf_fec_ut_enel = px.bar(base_fec_polo_enel_ano_transformado, x='UT', y='FEC', color='Meses', title='FEC', width=430, height=380)
    graf_fec_ut_enel.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.8,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['UT'],
            y=row['FEC'],
            text=f"{row['FEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_polo_enel_ano_fec.iterrows()])

    col1.plotly_chart(graf_dec_ut_enel)
    col2.plotly_chart(graf_fec_ut_enel)

    st.write('---')





    st.markdown("<h3 style='text-align: center;'>Polos</h3>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    
    graf_dec_polos = px.bar(base_dec_polos_transformado, x='Polos', y='DEC', color='Meses', title='DEC', width=430, height=400)
    graf_dec_polos.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.85,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['Polos'],
            y=row['DEC'],
            text=f"{row['DEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_polos_dec.iterrows()])

    graf_fec_polos = px.bar(base_fec_polos_transformado, x='Polos', y='FEC', color='Meses', title='FEC', width=430, height=400)
    graf_fec_polos.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.85,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['Polos'],
            y=row['FEC'],
            text=f"{row['FEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_polos_fec.iterrows()])

    col3.plotly_chart(graf_dec_polos)
    col4.plotly_chart(graf_fec_polos)

    st.write('---')





with tab2:
    st.markdown("<h3 style='text-align: center;'>Conjuntos</h3>", unsafe_allow_html=True)

    st.subheader(f'Polo {sidebar_polo}')

    col5, col6, col7 = st.columns(3)
    col8, col9 = st.columns(2)
    col10, col11 = st.columns(2)
    col12, col13 = st.columns(2)

    num_dec_controlado = base_dec_analise_ytd['Status DEC YTD'].value_counts().get('DEC Controlado', 0)
    num_dec_atencao = base_dec_analise_ytd['Status DEC YTD'].value_counts().get('DEC em Atenção', 0)
    num_dec_irreversivel = base_dec_analise_ytd['Status DEC YTD'].value_counts().get('DEC Irreversível', 0)

    col5.metric(label="Conjuntos Normais", value=f"{num_dec_controlado}")
    col6.metric(label="Conjuntos em Atenção", value=f"{num_dec_atencao}")
    col7.metric(label="Conjuntos Críticos", value=f"{num_dec_irreversivel}")

    graf_dec_conjuntos = px.bar(df_transformado_dec, x='Conjunto', y='DEC', color='Mês', title='DEC', width=430)
    graf_dec_conjuntos.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.9,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['Conjunto'],
            y=row['DEC'],
            text=f"{row['DEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_dec.iterrows()])
    graf_dec_conjuntos.add_scatter(x=df_transformado_dec['Conjunto'], y=totais_por_mes_dec['Meta DEC'], mode="lines+markers+text", name="Meta DEC", line=dict(color="black", dash="dash"), text=totais_por_mes_dec['Meta DEC'], textposition="top center", textfont=dict(color='black'))

    graf_fec_conjuntos = px.bar(df_transformado_fec, x='Conjunto', y='FEC', color='Mês', title='FEC', width=430)
    graf_fec_conjuntos.update_layout(
        title_x=0.5,
        xaxis_title='',  # Remove o título do eixo x
        yaxis_title='',  # Remove o título do eixo y
        legend=dict(
            orientation="h",  # Define a orientação horizontal
            yanchor="bottom",  # Ancorar a legenda na parte inferior
            y=-0.9,           # Ajustar a posição vertical da legenda
            xanchor="center",  # Ancorar horizontalmente no centro
            x=0.5),
        annotations=[dict(
            x=row['Conjunto'],
            y=row['FEC'],
            text=f"{row['FEC']:.2f}", # Formata o valor com duas casas decimais
            showarrow=False, 
            font=dict(size=12),
            xanchor='center', 
            yanchor='bottom') for index, row in totais_por_mes_fec.iterrows()])
    graf_fec_conjuntos.add_scatter(x=df_transformado_fec['Conjunto'], y=totais_por_mes_fec['Meta FEC'], mode="lines+markers+text", name="Meta FEC", line=dict(color="black", dash="dash"), text=totais_por_mes_fec['Meta FEC'], textposition="top center", textfont=dict(color='black'))

    graf_dec_conjuntos_ytd = px.bar(base_dec_analise_ytd, x='% Consumido da Meta Anual' , y='Conjunto', title='DEC YTD 2024',
                                    orientation='h', text=base_dec_analise_ytd['% Consumido da Meta Anual'], width=430, height=400,
                                    color='Status DEC YTD', color_discrete_map={'DEC Irreversível': 'red', 'DEC em Atenção': 'yellow', 'DEC Controlado': 'green'})
    graf_dec_conjuntos_ytd.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    graf_dec_conjuntos_ytd.update_layout(xaxis_title='', yaxis_title='', title_x=0.5,
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.4,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    graf_fec_conjuntos_ytd = px.bar(base_fec_analise_ytd, x='% Consumido da Meta Anual' , y='Conjunto', title='FEC YTD 2024',
                                    orientation='h', text=base_fec_analise_ytd['% Consumido da Meta Anual'], width=430, height=400,
                                    color='Status FEC YTD', color_discrete_map={'FEC Irreversível': 'red', 'FEC em Atenção': 'yellow', 'FEC Controlado': 'green'})
    graf_fec_conjuntos_ytd.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    graf_fec_conjuntos_ytd.update_layout(xaxis_title='', yaxis_title='', title_x=0.5,
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.4,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    graf_dec_conjuntos_tam = px.bar(base_dec_analise_tam, x='% Consumido TAM', y='Conjunto', title='DEC LTM 2024',
                                    orientation='h', text=base_dec_analise_tam['% Consumido TAM'], width=430, height=400,
                                    color='Status DEC TAM', color_discrete_map={'Conjunto Crítico': 'red', 'Conjunto em Atenção': 'yellow', 'Conjunto Normal': 'green'})
    graf_dec_conjuntos_tam.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    graf_dec_conjuntos_tam.update_layout(xaxis_title='', yaxis_title='', title_x=0.5,
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.6,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    graf_fec_conjuntos_tam = px.bar(base_fec_analise_tam, x='% Consumido TAM', y='Conjunto', title='FEC LTM 2024',
                                    orientation='h', text=base_fec_analise_tam['% Consumido TAM'], width=430, height=400,
                                    color='Status FEC TAM', color_discrete_map={'Conjunto Crítico': 'red', 'Conjunto em Atenção': 'yellow', 'Conjunto Normal': 'green'})
    graf_fec_conjuntos_tam.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    graf_fec_conjuntos_tam.update_layout(xaxis_title='', yaxis_title='', title_x=0.5,
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.6,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))


    col8.plotly_chart(graf_dec_conjuntos)
    col9.plotly_chart(graf_fec_conjuntos)

    col10.plotly_chart(graf_dec_conjuntos_ytd)
    col11.plotly_chart(graf_fec_conjuntos_ytd)

    col12.plotly_chart(graf_dec_conjuntos_tam)
    col13.plotly_chart(graf_fec_conjuntos_tam)

    st.write('---')





with tab3:
    st.markdown("<h3 style='text-align: center;'>Métrica Conjuntos Enel Rio</h3>", unsafe_allow_html=True)

    st.subheader("DEC")

    col14, col15, col16 = st.columns(3)

    metrica_conjuntos_dec_ultimas_col = pd.DataFrame(base_estado_conjuntos_dec_consolidado_DF.iloc[:, [0, -2, -1]].copy())
    metrica_conjuntos_dec_ultimas_col['Delta Mês'] = metrica_conjuntos_dec_ultimas_col.iloc[:, -1] - metrica_conjuntos_dec_ultimas_col.iloc[:, -2]
    metrica_conjuntos_dec_ultimas_col['% Mês'] = ((metrica_conjuntos_dec_ultimas_col.iloc[:, -2] - metrica_conjuntos_dec_ultimas_col.iloc[:, -3]) / metrica_conjuntos_dec_ultimas_col.iloc[:, -3]) * 100

    col14.metric(label="Conjuntos Normais", value=f"{metrica_conjuntos_dec_ultimas_col.iloc[0, -3]}", delta=f"{metrica_conjuntos_dec_ultimas_col.iloc[0, -2]} Conjuntos ({metrica_conjuntos_dec_ultimas_col.iloc[0, -1]:.1f}%)")
    col15.metric(label="Conjuntos em Atenção", value=f"{metrica_conjuntos_dec_ultimas_col.iloc[1, -3]}", delta=f"{metrica_conjuntos_dec_ultimas_col.iloc[1, -2]} Conjuntos ({metrica_conjuntos_dec_ultimas_col.iloc[1, -1]:.1f}%)", delta_color="inverse")
    col16.metric(label="Conjuntos Críticos", value=f"{metrica_conjuntos_dec_ultimas_col.iloc[2, -3]}", delta=f"{metrica_conjuntos_dec_ultimas_col.iloc[2, -2]} Conjuntos ({metrica_conjuntos_dec_ultimas_col.iloc[2, -1]:.1f}%)", delta_color="inverse")

    graf_base_estado_conjuntos_dec_consolidado_DF_melt = px.bar(base_estado_conjuntos_dec_consolidado_DF_melt, x="Mês", y="Num Conjuntos", width=860, height=300,
                                                                color="Estado Conjunto", text=base_estado_conjuntos_dec_consolidado_DF_melt['Num Conjuntos'],
                                                                color_discrete_map={'Crítico': 'FireBrick', 'Atenção': 'Gold', 'Normal': 'DarkGreen'})
    graf_base_estado_conjuntos_dec_consolidado_DF_melt.update_layout(xaxis_title='', yaxis_title='', title_x=0.5, title_text='',
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.5,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    with st.container():
        graf_base_estado_conjuntos_dec_consolidado_DF_melt

    st.subheader("FEC")

    col17, col18, col19 = st.columns(3)

    metrica_conjuntos_fec_ultimas_col = pd.DataFrame(base_estado_conjuntos_fec_consolidado_DF.iloc[:, [0, -2, -1]].copy())
    metrica_conjuntos_fec_ultimas_col['Delta Mês'] = metrica_conjuntos_fec_ultimas_col.iloc[:, -1] - metrica_conjuntos_fec_ultimas_col.iloc[:, -2]
    metrica_conjuntos_fec_ultimas_col['% Mês'] = ((metrica_conjuntos_fec_ultimas_col.iloc[:, -2] - metrica_conjuntos_fec_ultimas_col.iloc[:, -3]) / metrica_conjuntos_fec_ultimas_col.iloc[:, -3]) * 100

    col17.metric(label="Conjuntos Normais", value=f"{metrica_conjuntos_fec_ultimas_col.iloc[0, -3]}", delta=f"{metrica_conjuntos_fec_ultimas_col.iloc[0, -2]} Conjuntos ({metrica_conjuntos_fec_ultimas_col.iloc[0, -1]:.1f}%)")
    col18.metric(label="Conjuntos em Atenção", value=f"{metrica_conjuntos_fec_ultimas_col.iloc[1, -3]}", delta=f"{metrica_conjuntos_fec_ultimas_col.iloc[1, -2]} Conjuntos ({metrica_conjuntos_fec_ultimas_col.iloc[1, -1]:.1f}%)", delta_color="inverse")
    col19.metric(label="Conjuntos Críticos", value=f"{metrica_conjuntos_fec_ultimas_col.iloc[2, -3]}", delta=f"{metrica_conjuntos_fec_ultimas_col.iloc[2, -2]} Conjuntos ({metrica_conjuntos_fec_ultimas_col.iloc[2, -1]:.1f}%)", delta_color="inverse")

    graf_base_estado_conjuntos_fec_consolidado_DF_melt = px.bar(base_estado_conjuntos_fec_consolidado_DF_melt, x="Mês", y="Num Conjuntos", width=860, height=300,
                                                                color="Estado Conjunto", text=base_estado_conjuntos_fec_consolidado_DF_melt['Num Conjuntos'],
                                                                color_discrete_map={'Crítico': 'FireBrick', 'Atenção': 'Gold', 'Normal': 'DarkGreen'})
    graf_base_estado_conjuntos_fec_consolidado_DF_melt.update_layout(xaxis_title='', yaxis_title='', title_x=0.5, title_text='',
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.5,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    with st.container():
        graf_base_estado_conjuntos_fec_consolidado_DF_melt

    st.write('---')





with tab4:
    st.markdown("<h3 style='text-align: center;'>Status Conjuntos DEC TAM 2024</h3>", unsafe_allow_html=True)

    graf_dec_conjuntos_horizontal_tam = px.bar(base_dec_analises_com_polo_tam, x='% Consumido TAM', y='Conjunto', orientation='h',
                                            text=base_dec_analises_com_polo_tam['% Consumido TAM'],
                                            width=860, height=1600, color='Status DEC TAM',
                                            color_discrete_map={'Conjunto Crítico': 'FireBrick', 'Conjunto em Atenção': 'gold', 'Conjunto Normal': 'darkgreen'})
    graf_dec_conjuntos_horizontal_tam.update_traces(texttemplate='%{text:.2%}', textposition='outside')
    graf_dec_conjuntos_horizontal_tam.update_layout(xaxis_title='', yaxis_title='', title_x=0.5, title_text='',
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.05,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    with st.container():
        graf_dec_conjuntos_horizontal_tam

    st.markdown("<h3 style='text-align: center;'>Status Conjuntos DEC YTD 2024</h3>", unsafe_allow_html=True)

    graf_dec_conjuntos_horizontal_ytd = px.bar(base_dec_analises_com_polo_ytd, x='% Consumido da Meta Anual', y='Conjunto', orientation='h',
                                            text=base_dec_analises_com_polo_ytd['% Consumido da Meta Anual'],
                                            width=860, height=1600, color='Status DEC YTD',
                                            color_discrete_map={'DEC Irreversível': 'FireBrick', 'DEC em Atenção': 'gold', 'DEC Controlado': 'darkgreen'})
    graf_dec_conjuntos_horizontal_ytd.update_traces(texttemplate='%{text:.2%}', textposition='outside')
    graf_dec_conjuntos_horizontal_ytd.update_layout(xaxis_title='', yaxis_title='', title_x=0.5, title_text='',
        legend=dict(
        orientation="h",  # Define a orientação horizontal
        yanchor="bottom",  # Ancorar a legenda na parte inferior
        y=-0.05,           # Ajustar a posição vertical da legenda
        xanchor="center",  # Ancorar horizontalmente no centro
        x=0.5))

    with st.container():
        graf_dec_conjuntos_horizontal_ytd

    st.write('---')









