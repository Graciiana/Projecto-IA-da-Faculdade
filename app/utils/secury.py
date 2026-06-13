import bcrypt

def gerar_senha_hash(senha_limpa: str) -> str:

    senha_bytes = senha_limpa.encode('utf-8')
    
    salt = bcrypt.gensalt()
    
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    
    return hash_bytes.decode('utf-8')

def verfica_senha(senha_limpa: str, senha_encriptada: str) -> bool:
    try:
        senha_bytes = senha_limpa.encode('utf-8')
        
        hash_bytes = senha_encriptada.encode('utf-8')
        
        return bcrypt.checkpw(senha_bytes, hash_bytes)
    except Exception:
        return False