import streamlit as st
import pandas as pd
from db_sqlite import inserir_cidade, buscar_cidades
from db_mongo import inserir_local, buscar_locais_por_cidade, buscar_todos_locais
from geoprocessamento import listar_locais_proximos
import folium
from streamlit_folium import st_folium

# --- Configuração da Página ---
st.set_page_config(page_title="Projeto de Persistência Poliglota", layout="wide")
st.title("🗺️ Persistência Poliglota e Geoprocessamento")
st.markdown("Utilizando SQLite, MongoDB e Streamlit para análise geoespacial.")

# --- Barra Lateral (Sidebar) ---
st.sidebar.header("Cadastro")

# Seção para cadastrar Cidades/Estados (SQLite)
with st.sidebar.expander("➕ Cadastrar Nova Cidade (SQLite)"):
    with st.form("form_cidade", clear_on_submit=True):
        cidade_nome = st.text_input("Nome da Cidade")
        cidade_estado = st.text_input("Estado (Ex: PB)")
        cidade_pais = st.text_input("País (Ex: Brasil)")
        submitted_cidade = st.form_submit_button("Cadastrar Cidade")
        if submitted_cidade and cidade_nome and cidade_estado and cidade_pais:
            inserir_cidade(cidade_nome, cidade_estado, cidade_pais)
            st.success(f"Cidade '{cidade_nome}' cadastrada com sucesso!")

# Seção para cadastrar Locais (MongoDB)
with st.sidebar.expander("📍 Cadastrar Novo Ponto de Interesse (MongoDB)"):
    with st.form("form_local", clear_on_submit=True):
        local_nome = st.text_input("Nome do Local")
        cidades_disponiveis = [f"{nome} - {estado}" for nome, estado in buscar_cidades()]
        # Previne o erro quando não há cidades cadastradas
        local_cidade = st.selectbox("Selecione a Cidade", options=cidades_disponiveis) if cidades_disponiveis else st.empty()
        local_lat = st.number_input("Latitude", format="%.6f")
        local_lon = st.number_input("Longitude", format="%.6f")
        local_desc = st.text_area("Descrição")
        submitted_local = st.form_submit_button("Cadastrar Local")
        if submitted_local and all([local_nome, local_cidade, local_desc]):
            cidade_selecionada = local_cidade.split(' - ')[0]
            inserir_local(local_nome, cidade_selecionada, local_lat, local_lon, local_desc)
            st.success(f"Local '{local_nome}' cadastrado com sucesso!")

# --- Inicialização do st.session_state para persistência ---
if 'locais_por_cidade' not in st.session_state:
    st.session_state.locais_por_cidade = None
if 'resultados_proximidade' not in st.session_state:
    st.session_state.resultados_proximidade = None

# --- Corpo Principal da Aplicação ---

# Abas para organizar o conteúdo
tab1, tab2, tab3 = st.tabs(["🗺️ Visualização no Mapa", "🔍 Consulta Integrada", "🛰️ Busca por Proximidade"])

# Aba 1: Visualização no Mapa
with tab1:
    st.header("Visualização de Todos os Pontos de Interesse")
    todos_os_locais = buscar_todos_locais()

    if not todos_os_locais:
        st.warning("Nenhum local cadastrado no MongoDB ainda.")
    else:
        df_locais = pd.DataFrame(todos_os_locais)
        df_locais['latitude'] = df_locais['coordenadas'].apply(lambda c: c['latitude'])
        df_locais['longitude'] = df_locais['coordenadas'].apply(lambda c: c['longitude'])

        st.write(f"Total de {len(df_locais)} locais encontrados.")
        
        mapa_geral = folium.Map(location=[df_locais['latitude'].mean(), df_locais['longitude'].mean()], zoom_start=4)
        for _, local in df_locais.iterrows():
            folium.Marker(
                [local['latitude'], local['longitude']],
                popup=f"<b>{local['nome_local']}</b><br>{local['descricao']}",
                tooltip=local['nome_local']
            ).add_to(mapa_geral)
        
        st_folium(mapa_geral, width=1200, height=600)

# Aba 2: Consulta Integrada
with tab2:
    st.header("Locais do MongoDB por Cidade do SQLite")
    lista_cidades = [f"{nome} - {estado}" for nome, estado in buscar_cidades()]
    if not lista_cidades:
        st.info("Cadastre uma cidade primeiro na barra lateral.")
    else:
        cidade_selecionada_consulta = st.selectbox("Selecione uma cidade para ver os pontos de interesse:", options=lista_cidades, key="consulta")
        nome_cidade_query = cidade_selecionada_consulta.split(' - ')[0]

        # Ação do botão: Armazena o resultado no st.session_state
        if st.button("Buscar Locais", key="btn_consulta"):
            locais_encontrados = buscar_locais_por_cidade(nome_cidade_query)
            st.session_state.locais_por_cidade = locais_encontrados
        
        # O código abaixo exibe o resultado salvo, sem depender do clique
        if st.session_state.locais_por_cidade is not None:
            locais_encontrados = st.session_state.locais_por_cidade
            if not locais_encontrados:
                st.warning(f"Nenhum ponto de interesse encontrado para '{nome_cidade_query}'.")
            else:
                st.subheader(f"Pontos de Interesse em {nome_cidade_query}:")
                df_resultado = pd.DataFrame(locais_encontrados)
                df_resultado['latitude'] = df_resultado['coordenadas'].apply(lambda c: c['latitude'])
                df_resultado['longitude'] = df_resultado['coordenadas'].apply(lambda c: c['longitude'])
                st.dataframe(df_resultado[['nome_local', 'descricao', 'latitude', 'longitude']])

                mapa_consulta = folium.Map(location=[df_resultado['latitude'].mean(), df_resultado['longitude'].mean()], zoom_start=13)
                for _, local in df_resultado.iterrows():
                    folium.Marker(
                        [local['latitude'], local['longitude']],
                        popup=local['descricao'],
                        tooltip=local['nome_local']
                    ).add_to(mapa_consulta)
                st_folium(mapa_consulta, width=1200, height=500)

# Aba 3: Busca por Proximidade
with tab3:
    st.header("Encontrar Locais Próximos de um Ponto")
    with st.form("form_proximidade"):
        st.write("Informe uma coordenada central e um raio em quilômetros.")
        prox_lat = st.number_input("Latitude Central", format="%.6f", value=-7.115320)
        prox_lon = st.number_input("Longitude Central", format="%.6f", value=-34.861000)
        raio = st.slider("Raio de busca (em Km)", min_value=1, max_value=100, value=10)
        submitted_prox = st.form_submit_button("Buscar Locais Próximos")

    # Ação do botão: Armazena o resultado no st.session_state
    if submitted_prox:
        st.session_state.resultados_proximidade = listar_locais_proximos(prox_lat, prox_lon, raio)
    
    # O código abaixo exibe o resultado salvo, sem depender do clique
    if st.session_state.resultados_proximidade is not None:
        locais_proximos_encontrados = st.session_state.resultados_proximidade
        if not locais_proximos_encontrados:
            st.warning(f"Nenhum local encontrado em um raio de {raio} km.")
        else:
            st.success(f"{len(locais_proximos_encontrados)} locais encontrados!")
            df_proximidade = pd.DataFrame(locais_proximos_encontrados)
            df_proximidade['latitude'] = df_proximidade['coordenadas'].apply(lambda c: c['latitude'])
            df_proximidade['longitude'] = df_proximidade['coordenadas'].apply(lambda c: c['longitude'])
            
            st.dataframe(df_proximidade[['nome_local', 'cidade', 'distancia_km', 'descricao']])

            mapa_proximidade = folium.Map(location=[prox_lat, prox_lon], zoom_start=12)
            folium.Circle(
                location=[prox_lat, prox_lon],
                radius=raio * 1000,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.1
            ).add_to(mapa_proximidade)
            folium.Marker(
                [prox_lat, prox_lon],
                popup="Ponto Central da Busca",
                icon=folium.Icon(color='blue')
            ).add_to(mapa_proximidade)
            
            for _, local in df_proximidade.iterrows():
                folium.Marker(
                    [local['latitude'], local['longitude']],
                    popup=f"{local['nome_local']} ({local['distancia_km']} km)",
                    tooltip=local['nome_local']
                ).add_to(mapa_proximidade)
            
            st_folium(mapa_proximidade, width=1200, height=600)