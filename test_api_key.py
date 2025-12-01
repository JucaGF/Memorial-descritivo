"""Script para testar se a chave da OpenAI está válida."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# Testa carregamento
api_key = os.getenv("OPENAI_API_KEY", "")
print("=" * 80)
print("TESTE DE CHAVE DA OPENAI")
print("=" * 80)
print(f"\nChave carregada: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
print(f"Tamanho da chave: {len(api_key)} caracteres")

if not api_key or api_key == "sk-your-api-key-here":
    print("\n❌ ERRO: Chave não configurada ou inválida!")
    exit(1)

# Testa com OpenAI
print("\nTestando conexão com OpenAI...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # Testa chamada simples
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Responda apenas: OK"}
        ],
        max_tokens=10
    )
    
    print(f"✅ Sucesso! Resposta: {response.choices[0].message.content}")
    print(f"Modelo usado: {response.model}")
    print(f"Tokens usados: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"\n❌ ERRO ao conectar com OpenAI:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    
    if "429" in str(e) or "insufficient_quota" in str(e):
        print("\n⚠️  A chave está correta mas SEM CRÉDITOS na conta OpenAI!")
        print("Acesse: https://platform.openai.com/account/billing")
    elif "401" in str(e) or "invalid" in str(e).lower():
        print("\n⚠️  A chave parece estar INVÁLIDA ou REVOGADA!")
    
    exit(1)

print("\n" + "=" * 80)
print("Tudo funcionando! ✅")
print("=" * 80)
