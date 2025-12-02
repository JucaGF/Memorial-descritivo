"""Teste detalhado da API OpenAI."""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
print("=" * 80)
print("DIAGNÓSTICO DETALHADO DA API")
print("=" * 80)
print(f"\n1. Tipo de chave: {'Projeto' if api_key.startswith('sk-proj-') else 'Usuário'}")
print(f"2. Tamanho: {len(api_key)} chars")
print(f"3. Início: {api_key[:15]}...")
print(f"4. Final: ...{api_key[-15:]}")

client = OpenAI(api_key=api_key)

print("\n" + "=" * 80)
print("TESTANDO DIFERENTES MODELOS")
print("=" * 80)

models_to_test = [
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "gpt-5-mini",  # Se existir
]

for model in models_to_test:
    print(f"\n➤ Testando: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responda: OK"}],
            max_tokens=5
        )
        print(f"  ✅ Funcionou! Tokens: {response.usage.total_tokens}")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            print(f"  ❌ Quota excedida (429)")
        elif "404" in error_msg or "does not exist" in error_msg:
            print(f"  ⚠️  Modelo não existe")
        elif "401" in error_msg:
            print(f"  ❌ Não autorizado (chave inválida)")
        else:
            print(f"  ❌ Erro: {error_msg[:100]}")

print("\n" + "=" * 80)
print("DICAS:")
print("=" * 80)
print("• Se TODOS falharam com 429: problema de quota/billing")
print("• Se 404: modelo não existe")
print("• Chaves sk-proj-* podem ter limites por projeto")
print("• Verifique: https://platform.openai.com/account/limits")
