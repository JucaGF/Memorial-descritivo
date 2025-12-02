# 📄 Memorial Maker

**Geração automática de Memorial Descritivo de Telecomunicações com IA**

Sistema que extrai dados de plantas técnicas (PDFs) e gera memoriais descritivos profissionais usando **Unstructured.io** para extração de dados e **GPT-4** para redação inteligente.

---

## 🎯 Funcionalidades

- ✅ **Extração inteligente** de PDFs usando Unstructured.io
- ✅ **Detecção de tabelas** e estruturação de dados
- ✅ **Geração de texto** com GPT-4 (OpenAI)
- ✅ **Interface web** simples com Streamlit
- ✅ **Exportação para Word** (.docx) com formatação

---

## 🚀 Instalação Rápida

### 1. Requisitos
- Python 3.10+
- Conta OpenAI com API key

### 2. Setup
```bash
# Clone ou navegue até o projeto
cd Memorial-descritivo

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instale dependências
pip install -e .
```

### 3. Configuração
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite e adicione sua chave OpenAI
nano .env  # ou seu editor preferido
```

Adicione no `.env`:
```bash
OPENAI_API_KEY=sk-proj-...
UNSTRUCTURED_STRATEGY=fast  # ou "hi_res" para melhor OCR
```

---

## 💻 Como Usar

### Interface Web (Recomendado)
```bash
source venv/bin/activate
streamlit run ui/app.py
```

Acesse: **http://localhost:8501**

1. �� Faça upload dos PDFs de projeto
2. 📝 (Opcional) Faça upload de memoriais-modelo
3. ⚙️ Clique em "Gerar Memorial"
4. 💾 Baixe o arquivo `.docx` gerado

### Teste de Extração
```bash
# Coloque seus PDFs em projetos_plantas/
python test_extraction.py
```

---

## 📁 Estrutura do Projeto

```
Memorial-descritivo/
├── memorial_maker/          # 📦 Pacote principal
│   ├── extract/             #   └─ Extração com Unstructured
│   ├── normalize/           #   └─ Normalização de dados
│   ├── rag/                 #   └─ Geração com LLM
│   ├── writer/              #   └─ Escrita de DOCX
│   └── utils/               #   └─ Utilitários
├── ui/                      # 🖥️  Interface Streamlit
├── projetos_plantas/        # 📂 PDFs de entrada
├── memorial/                # 📂 Memoriais-modelo (RAG)
├── out/                     # 📂 Arquivos gerados
├── test_extraction.py       # 🧪 Script de teste
└── requirements.txt         # 📋 Dependências
```

---

## 🔧 Configurações Avançadas

### Estratégias de Extração (Unstructured)

No arquivo `.env`:

```bash
# fast: rápido, sem OCR (padrão)
UNSTRUCTURED_STRATEGY=fast

# hi_res: melhor qualidade, com OCR
UNSTRUCTURED_STRATEGY=hi_res

# ocr_only: apenas OCR
UNSTRUCTURED_STRATEGY=ocr_only
```

### Modelos LLM

```bash
# Modelo padrão
LLM_MODEL=gpt-4o-mini

# Para melhor qualidade
LLM_MODEL=gpt-4o

# Mais barato
LLM_MODEL=gpt-3.5-turbo
```

---

## 🐛 Solução de Problemas

### ❌ "No module named 'memorial_maker'"
```bash
pip install -e .
```

### ❌ "OpenAI API key not found"
Verifique se o arquivo `.env` existe e contém `OPENAI_API_KEY=sk-proj-...`

### ❌ Extração vazia ou incompleta
- Use `UNSTRUCTURED_STRATEGY=hi_res` para PDFs escaneados
- Verifique se o PDF contém texto selecionável
- Execute `python test_extraction.py` para diagnóstico

### ❌ Tabelas não detectadas
Configure no `.env`:
```bash
UNSTRUCTURED_STRATEGY=hi_res
EXTRACT_TABLES=true
```

---

## 📚 Mais Informações

### Tecnologias Usadas
- **[Unstructured.io](https://unstructured.io/)** - Extração de PDFs
- **[LangChain](https://langchain.com/)** - Framework para LLM
- **[OpenAI GPT-4](https://openai.com/)** - Geração de texto
- **[Streamlit](https://streamlit.io/)** - Interface web
- **[python-docx](https://python-docx.readthedocs.io/)** - Geração de Word

### Desenvolvimento
```bash
# Testes
pytest tests/

# Formatação
black memorial_maker/
```
