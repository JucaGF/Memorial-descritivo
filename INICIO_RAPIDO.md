# 🚀 Início Rápido - Memorial Maker

## ⚡ Setup em 3 Minutos

### 1️⃣ Instalação
```bash
# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale
pip install -e .
```

### 2️⃣ Configure API Key
```bash
# Copie o exemplo
cp env.example .env

# Edite (cole sua chave da OpenAI)
nano .env
```

No `.env`, adicione:
```
OPENAI_API_KEY=sk-proj-SEU_TOKEN_AQUI
```

### 3️⃣ Teste
```bash
# Coloque seus PDFs em projetos_plantas/
python test_extraction.py
```

---

## 🎯 Uso Diário

### Interface Web (Recomendado)
```bash
source venv/bin/activate
streamlit run ui/app.py
```

Abra: **http://localhost:8501**

1. 📤 Upload dos PDFs
2. ⚙️ Clique "Gerar Memorial"
3. 💾 Baixe o `.docx`

---

## 🔧 Configurações Rápidas

### Para PDFs Escaneados (OCR)
No `.env`:
```bash
UNSTRUCTURED_STRATEGY=hi_res
```

### Modelo LLM Diferente
```bash
LLM_MODEL=gpt-4o        # Melhor qualidade
LLM_MODEL=gpt-3.5-turbo # Mais barato
```

---

## 📁 Estrutura Básica

```
Memorial-descritivo/
├── projetos_plantas/    👈 Coloque seus PDFs aqui
├── memorial/            👈 Memoriais-modelo (opcional)
├── out/                 👈 Resultados aparecem aqui
└── test_extraction.py   👈 Teste primeiro
```

---

## 🆘 Problemas Comuns

### ❌ Erro: "No module named 'memorial_maker'"
```bash
pip install -e .
```

### ❌ Erro: "OpenAI API key not found"
Verifique se `.env` existe e tem `OPENAI_API_KEY=sk-...`

### ❌ Extração vazia
1. Use `UNSTRUCTURED_STRATEGY=hi_res`
2. Verifique se PDFs têm texto selecionável
3. Execute `python test_extraction.py` para diagnóstico

---

## 📖 Mais Informações

- **README.md** - Documentação completa
- **SIMPLIFICACAO.md** - Mudanças do projeto
- **RESUMO_FINAL.md** - Estatísticas

---

## ✨ Dicas

💡 Sempre ative o ambiente antes de usar:
```bash
source venv/bin/activate
```

💡 Para melhor extração, use PDFs com texto (não imagens escaneadas)

💡 O primeiro uso pode ser lento (download de modelos do Unstructured)

---

**Pronto! É só isso. Simples assim! 🎉**
