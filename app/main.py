import sqlite3
from fastapi import FastAPI, HTTPException
from app.shema_model import NovaAvaliacao, CadastroUtilizador, LoginUtilizador
from app.utils.secury import gerar_senha_hash, verfica_senha
from fastapi.middleware.cors import CORSMiddleware

from app.database import inicializar_bd, DB_NAME
from app.recomender import MotorRecomendacao

app = FastAPI(
    title="Sistema de Recomendação",
    description="Infraestrutura completa de endpoints para o projeto de IA."
)


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # Permite que o teu Front-End aceda à API
    allow_credentials=True,
    allow_methods=["*"],       # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],       # Permite todos os cabeçalhos de rede
)

motor = MotorRecomendacao()



@app.on_event("startup")
def iniciar_aplicacao():
    inicializar_bd()
    motor.treinar()


@app.get("/")
def home():
    return {
        "status": "Online",
        "contexto": "Projeto de Inteligência Artificial - Recomendador",
        "tempo_ultimo_treino_segundos": round(motor.tempo_ultimo_treino, 6)
    }


@app.get("/api/recomendar/{item_id}")
def api_recomendar(item_id: int, quantidade: int = 3):
    resultado = motor.recomendar(
        item_id=item_id,
        n_recomendacoes=quantidade
    )

    return {
        "item_solicitado": item_id,
        "resultado": resultado
    }


@app.post("/api/avaliar")
def api_adicionar_avaliacao(dados: NovaAvaliacao):

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO avaliacoes
            (user_id, item_id, rating)
            VALUES (?, ?, ?)
        """, (
            dados.user_id,
            dados.item_id,
            dados.rating
        ))

        conn.commit()
        conn.close()

        return {
            "status": "Sucesso",
            "mensagem": "Avaliação registada/atualizada."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro crítico de BD: {str(e)}"
        )


@app.post("/api/treinar")
def api_retreinar_modelo():

    if motor.treinar():
        return {
            "status": "Sucesso",
            "mensagem": "Modelo re-treinado com os novos dados.",
            "tempo_execucao_segundos": round(
                motor.tempo_ultimo_treino,
                6
            )
        }

    raise HTTPException(
        status_code=500,
        detail="Erro ao processar matriz de treino."
    )


## Endpoint para o cadastro do utilizador
@app.post("/api/utizadores/cadastro")
def cadastro_utiliazdor(dados: CadastroUtilizador):
    try:
        senha_segura = gerar_senha_hash(dados.password)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        query = """
        INSERT INTO utilizadores (nome, apelido, email, password)
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(query, (
            dados.nome,
            dados.apelido,
            dados.email,
            senha_segura 
        ))

        conn.commit()
        conn.close()

        return {
            "status": "Sucesso",
            "mensagem": f"Utilizador {dados.nome} registado com sucesso no SQLite!"
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
           status_code=400,
           detail="Erro: Este e-mail já se encontra registado." 
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro crítico de base de dados: {str(e)}"
        )

#ENDPOINT PARA LOGIN

@app.post("/api/utilizadores/login")
def login_utilizador(dados: LoginUtilizador):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        #Procura o utilizador no SQLite pelo e-mail digitado
        query = "SELECT user_id, nome, password FROM utilizadores WHERE email = ?"
        cursor.execute(query, (dados.email,))
        utilizador = cursor.fetchone()
        conn.close()

        # Se e-mail não existir no banco, ignora/trava o login com um raise
        if not utilizador:
            raise HTTPException(
                status_code=400, 
                detail="Erro: E-mail ou palavra-passe incorretos."
            )

        user_id, nome, senha_encriptada_no_banco = utilizador

        # Ela recebe: (senha_limpa_do_front, hash_salvo_no_sqlite)
        senha_valida = verfica_senha(dados.password, senha_encriptada_no_banco)


        if not senha_valida:
            raise HTTPException(
                status_code=400, 
                detail="Erro: E-mail ou palavra-passe incorretos."
            )
        return {
            "status": "Sucesso",
            "mensagem": f"Bem-vindo de volta, {nome}!",
            "user_id": user_id # Devolvemos o ID para o Front saber quem está logado
        }

    except HTTPException as http_err:
        # Repassa o erro do raise para o FastAPI não mascarar como erro 500
        raise http_err
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no servidor: {str(e)}"
        )