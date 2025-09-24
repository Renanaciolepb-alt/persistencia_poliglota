import sqlite3

# Função para conectar ao banco de dados
def conectar_db():
    conn = sqlite3.connect('dados_geograficos.db')
    return conn

# Função para criar a tabela, caso ela não exista
def criar_tabela():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            estado TEXT NOT NULL,
            pais TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Função para inserir uma nova cidade
def inserir_cidade(nome, estado, pais):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cidades (nome, estado, pais) VALUES (?, ?, ?)", (nome, estado, pais))
    conn.commit()
    conn.close()

# Função para buscar todas as cidades
def buscar_cidades():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, estado FROM cidades")
    cidades = cursor.fetchall()
    conn.close()
    return cidades

# Inicializa o banco e a tabela ao carregar o módulo
criar_tabela()