import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import inicializar_bd, DB_NAME
from app.recomender import MotorRecomendacao

app = FastAPI(
    title="Sistema de Recomendação",
    description="Infraestrutura completa de endpoints para o projeto de IA."
)

motor = MotorRecomendacao()


class NovaAvaliacao(BaseModel):
    user_id: int = Field(..., description="ID do utilizador")
    item_id: int = Field(..., description="ID do item/produto")
    rating: float = Field(..., ge=1.0, le=5.0, description="Nota de 1 a 5")


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