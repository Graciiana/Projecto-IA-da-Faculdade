from pydantic import BaseModel, Field, EmailStr

class NovaAvaliacao(BaseModel):
    user_id: int = Field(..., description="ID do utilizador")
    item_id: int = Field(..., description="ID do item/produto")
    rating: float = Field(..., ge=1.0, le=5.0, description="Nota de 1 a 5")


class CadastroUtilizador(BaseModel):
    nome: str = Field(..., min_length=2, max_length=50)
    apelido: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")


class LoginUtilizador(BaseModel):
    email: EmailStr = Field(..., description="Email do utilizador")
    password: str = Field(..., description="Senha digitada")