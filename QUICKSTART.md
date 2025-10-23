# 🚀 Quick Start - Memorial Automator

Comece a usar o sistema em 5 minutos!

## ⚡ Instalação Rápida

```bash
# 1. Clone/navegue até o diretório
cd /home/joaquim/Projects/Memorial-descritivo

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure sua chave OpenAI
echo 'OPENAI_API_KEY=sua_chave_aqui' > .env

# 5. Inicie o servidor
./start.sh
```

## 🎯 Primeiro Uso

### Via Interface Web (Swagger UI)

1. Abra seu navegador: **http://localhost:8000/docs**
2. Clique em **POST /api/v1/generate_memorial**
3. Clique em **Try it out**
4. Faça upload de um PDF de projeto
5. Clique em **Execute**
6. Veja o memorial gerado! 🎉

### Via Python

```python
import requests

# Upload e processar PDF
url = "http://localhost:8000/api/v1/generate_memorial"
files = {"file": open("seu_projeto.pdf", "rb")}
response = requests.post(url, files=files)

# Exibir resultado
result = response.json()
print(result["memorial_text"])
```

### Via cURL

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -F "file=@seu_projeto.pdf" \
  > memorial.json
```

## 📝 Customização Básica

### 1. Adicione Regras ABNT

Edite `context_files/abnt_rules.txt`:

```bash
nano context_files/abnt_rules.txt
```

Adicione suas regras específicas da ABNT.

### 2. Customize o Template

Edite `context_files/client_template.txt`:

```bash
nano context_files/client_template.txt
```

Defina a estrutura desejada para o memorial.

## 🔧 Configurações Importantes

### Arquivo `.env`

```env
# Sua chave OpenAI (OBRIGATÓRIO)
OPENAI_API_KEY=sk-...

# Modelos de IA
OPENAI_MODEL=gpt-4o              # Parser (multimodal)
OPENAI_WRITER_MODEL=gpt-4-turbo  # Redator
OPENAI_REVIEWER_MODEL=gpt-4-turbo # Revisor

# Temperaturas (0.0 = preciso, 1.0 = criativo)
WRITER_TEMPERATURE=0.7
PARSER_TEMPERATURE=0.3
REVIEWER_TEMPERATURE=0.2
```

## 📊 Testando

### Teste básico

```bash
# Verifica se API está online
curl http://localhost:8000/health
```

### Teste completo

```bash
# Com o script de teste
python test_api.py seu_projeto.pdf
```

## 💡 Dicas Rápidas

### 1. Melhorando a Qualidade

- ✅ **Preencha bem** os arquivos de contexto (ABNT rules e template)
- ✅ **Use PDFs de boa qualidade** (texto extraível, não escaneado)
- ✅ **Adicione instruções customizadas** quando necessário

### 2. Performance

- 📊 PDFs de 10-20 páginas: ~40-60 segundos
- 📊 PDFs de 50+ páginas: 2-5 minutos
- 📊 PDFs de 100+ páginas: 5-10 minutos

### 3. Troubleshooting

**Erro: "OpenAI API key not found"**
```bash
# Verifique se o .env existe e tem a chave
cat .env | grep OPENAI_API_KEY
```

**Erro: "Connection refused"**
```bash
# Certifique-se de que o servidor está rodando
./start.sh
```

**Erro: "Only PDF files are supported"**
```bash
# Verifique a extensão do arquivo
file seu_arquivo.pdf
```

## 🎓 Próximos Passos

1. ✅ Leia o [README.md](README.md) completo
2. 📖 Consulte [SETUP.md](SETUP.md) para configuração detalhada
3. 💻 Veja [EXAMPLES.md](EXAMPLES.md) para mais exemplos de código
4. 🏗️ Entenda a [ARCHITECTURE.md](ARCHITECTURE.md) do sistema

## 🆘 Precisa de Ajuda?

- 📚 Documentação interativa: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc
- 🐛 Verifique os logs do servidor

---

**Pronto!** Você já está gerando memoriais descritivos automaticamente! 🚀✨

