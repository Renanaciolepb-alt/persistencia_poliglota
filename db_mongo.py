from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"

# Função para conectar ao MongoDB
def conectar_mongo():
    client = MongoClient(MONGO_URI)
    db = client['geoprocessamento_db']
    return db

# Função para inserir um novo local de interesse
def inserir_local(nome_local, cidade, latitude, longitude, descricao):
    db = conectar_mongo()
    locais = db.locais
    documento = {
        "nome_local": nome_local,
        "cidade": cidade,
        "coordenadas": {
            "latitude": latitude,
            "longitude": longitude
        },
        "descricao": descricao
    }
    locais.insert_one(documento)

# Função para buscar locais por cidade
def buscar_locais_por_cidade(cidade):
    db = conectar_mongo()
    locais = db.locais.find({"cidade": cidade})
    return list(locais)

# Função para buscar todos os locais
def buscar_todos_locais():
    db = conectar_mongo()
    locais = db.locais.find({})
    return list(locais)