# persistencia_poliglota
A arquitetura deste projeto segue uma abordagem de Persistência Poliglota, utilizando múltiplos modelos de banco de dados para atender a diferentes necessidades dentro da mesma aplicação. Essa arquitetura modular separa as responsabilidades, tornando o código mais limpo, escalável e fácil de manter.


1. Arquitetura
SQLite: Usado para dados estruturados e relacionais (cidades, estados), ideal para informações que não mudam frequentemente.

MongoDB: Armazena dados flexíveis e semiestruturados (pontos de interesse, coordenadas), perfeito para dados geoespaciais e documentos JSON.

Streamlit: Atua como a interface web, unificando tudo e permitindo a interação do usuário através de formulários, tabelas e mapas.

2. Funcionalidades e Consultas
A aplicação possui três funções principais, organizadas em abas:

Visualização no Mapa: Exibe todos os pontos de interesse cadastrados no MongoDB em um mapa interativo, mostrando onde estão localizados.

<img width="1152" height="905" alt="image" src="https://github.com/user-attachments/assets/e90d4ec1-df47-4bcd-9c5c-e36cf8e9a492" />

Consulta Integrada: Permite que o usuário selecione uma cidade (do SQLite) e veja apenas os pontos de interesse (do MongoDB) que pertencem a ela, demonstrando a integração entre os bancos de dados.

Busca por Proximidade: Localiza e exibe no mapa todos os pontos de interesse que estão dentro de um raio de distância específico de uma coordenada central, usando cálculos de geoprocessamento.

Essa arquitetura permite que a aplicação use o banco de dados mais adequado para cada tipo de informação, tornando-o mais eficiente e robusto.
