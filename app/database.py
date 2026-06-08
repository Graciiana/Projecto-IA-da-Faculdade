import sqlite3
import os
import pandas as pd

DB_NAME = "recomendacao.db"
MOVIELENS_RATINGS_CSV = "ratings.csv"

def inicializar_bd():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
                   user_id INTEGER,
                   item_id INTEGER,
                   rating REAL,
                   PRIMARY KEY (user_id, item_id)   
                   )
    """)

    cursor.execute("SELECT COUNT(*) FROM avaliacoes")
    if cursor.fetchone()[0] == 0:
        print("A base de dados está vazia. A iniciar a importação do MovieLens...")
        
        # Verificar se o arquivo csv do MovieLens existe na mesma pasta do projeto
        if os.path.exists(MOVIELENS_RATINGS_CSV):
            # Ler o arquivo CSV usando o Pandas de forma super rápida
            df_movielens = pd.read_csv(MOVIELENS_RATINGS_CSV)
            
            # O MovieLens original usa os cabeçalhos: userId, movieId, rating, timestamp
            # Vamos selecionar apenas o que nos interessa e renomear para bater com o banco
            df_para_banco = df_movielens[['userId', 'movieId', 'rating']].rename(
                columns={
                    'userId': 'user_id',
                    'movieId': 'item_id',
                    'rating': 'rating'
                }
            )

            # Injeta todo o conteúdo do arquivo de uma só vez na tabela
            df_para_banco.to_sql("avaliacoes", conn, if_exists="append", index=False)
            conn.commit()
            print(f"Sucesso! {len(df_para_banco)} avaliações do MovieLens foram carregadas.")
        else:
            print(f"Aviso: O arquivo '{MOVIELENS_RATINGS_CSV}' não foi encontrado. Coloca-o nesta pasta.")
            
    conn.close()

def buscar_dados_para_treino():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM avaliacoes", conn)
    conn.close()
    return df

def obter_itens_mais_populares(n=3):
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT item_id, AVG(rating) as media_rating
        FROM avaliacoes
        GROUP BY item_id
        ORDER BY media_rating DESC, COUNT(user_id) DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(n,))
    conn.close()
    return df.to_dict(orient="records")