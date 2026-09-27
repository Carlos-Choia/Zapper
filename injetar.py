import os
import random

ARQUIVO_DISCO = "disco_emulado.img"
TAM_SETOR = 256

# Texto especial para registrar a história no disquete virtual
texto_historico = (
    "ZAPPER VS 1.3 - CRIADO EM 1986 POR CARLOS CHOIA. "
    "RECUPERADO E EMULADO COM SUCESSO EM 2026 NO WINDOWS 11. "
    "LOGICA DE BAIXO NIVEL E PROGRAMACAO RAIZ NUNCA MORREM! "
    "ENG. DE SOFTWARE TRS-80 / CP 500. "
)

# Transforma o texto em bytes
bytes_texto = texto_historico.encode('ascii', errors='ignore')

if os.path.exists(ARQUIVO_DISCO):
    with open(ARQUIVO_DISCO, "r+b") as f:
        # Injeta o texto no Setor 1 (Trilha 0, Setor 1 -> posição 0)
        f.seek(0)
        f.write(bytes_texto[:TAM_SETOR].ljust(TAM_SETOR, b'\x00'))
        
        # Injeta dados binários variados no Setor 2 para teste de modo Decimal
        f.seek(TAM_SETOR)
        dados_aleatorios = bytes([random.randint(1, 254) for _ in range(TAM_SETOR)])
        f.write(dados_aleatorios)
        
    print("🎉 Dados reais injetados com sucesso nos setores 1 e 2 do disco virtual!")
else:
    print("Erro: O arquivo 'disco_emulado.img' nao foi encontrado na pasta.")
