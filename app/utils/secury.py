from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_senha_hash(senha_limpa: str) -> str:
    return pwd_context.hash(senha_limpa)

def verfica_senha(senha_limpa: str, senha_encriptada: str) -> bool:
    return pwd_context.verify(senha_limpa, senha_encriptada)