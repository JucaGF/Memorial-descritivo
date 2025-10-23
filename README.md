# Memorial Automator

Sistema de automação para criação de memoriais descritivos a partir de projetos de engenharia/arquitetura em PDF.

## 🎯 Objetivo

Automatizar a geração de memoriais descritivos técnicos usando IA, garantindo conformidade com normas ABNT e templates de clientes.

## ✨ Interface Web

O sistema agora conta com uma **interface web moderna e intuitiva**!

**Acesse:** http://localhost:8000 (após iniciar o servidor)

**Características:**
- 🎨 Design moderno com gradientes e animações
- 📱 Totalmente responsivo (desktop, tablet, mobile)
- 🚀 Drag & Drop para upload de PDFs
- ⚡ Feedback visual em tempo real
- 📊 Estatísticas detalhadas do processamento
- 💾 Download em múltiplos formatos (TXT, JSON)
- 📋 Copiar para clipboard

**Screenshot:**
![Interface](docs/interface-preview.png)

Veja mais detalhes em [UI_GUIDE.md](UI_GUIDE.md)

## 🏗️ Arquitetura

O sistema utiliza um pipeline de processamento com dois agentes de IA:

```
PDF Upload → Extração → Estruturação (IA) → Agente Redator → Agente Revisor → Memorial Final
```

### Componentes:

1. **Módulo de Upload** - API FastAPI para receber PDFs
2. **Extrator de PDF** - PyMuPDF para extração de texto e imagens
3. **Parser de Documentos** - IA para estruturar informações
4. **Agente Redator** - IA para gerar rascunho do memorial
5. **Agente Revisor** - IA para revisar e finalizar o documento

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- pip

### Passos:

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd Memorial-descritivo
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua chave da OpenAI
```

5. Configure os arquivos de contexto:
   - Edite `context_files/abnt_rules.txt` com as regras ABNT específicas
   - Edite `context_files/client_template.txt` com o template do cliente

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o
DEBUG=False
```

### Arquivos de Contexto

- **abnt_rules.txt**: Regras e normas ABNT para memoriais descritivos
- **client_template.txt**: Template/estrutura desejada pelo cliente

## 🔧 Uso

### Iniciar o servidor:

```bash
python -m app.main
# ou
uvicorn app.main:app --reload
```

O servidor estará disponível em: `http://localhost:8000`

### Documentação da API:

Acesse a documentação interativa em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoint Principal:

**POST** `/api/v1/generate_memorial`

**Parâmetros:**
- `file`: PDF do projeto (multipart/form-data)
- `client_id`: ID do cliente (opcional, padrão: "default")
- `include_images`: Incluir análise de imagens (opcional)
- `custom_instructions`: Instruções adicionais (opcional)

**Resposta:**
```json
{
  "memorial_text": "Texto completo do memorial...",
  "structured_data": {
    "project_name": "Nome do Projeto",
    "client_name": "Nome do Cliente",
    "area_total_m2": 250.5,
    ...
  },
  "processing_time_seconds": 45.2,
  "pages_processed": 15,
  "warnings": []
}
```

### Exemplo com cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@projeto.pdf" \
  -F "client_id=default"
```

### Exemplo com Python:

```python
import requests

url = "http://localhost:8000/api/v1/generate_memorial"
files = {"file": open("projeto.pdf", "rb")}
data = {"client_id": "default"}

response = requests.post(url, files=files, data=data)
result = response.json()

print(result["memorial_text"])
```

## 📁 Estrutura do Projeto

```
memorial_automator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py   # PDF extraction
│   │   ├── document_parser.py # AI-powered parsing
│   │   └── agent_service.py   # Writer & Reviewer agents
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic models
├── context_files/
│   ├── abnt_rules.txt         # ABNT rules
│   └── client_template.txt    # Client template
├── temp_uploads/              # Temporary file storage
├── requirements.txt
├── .env
└── README.md
```

## 🧠 Como Funciona

### 1. Extração de PDF
- Extrai texto completo do PDF usando PyMuPDF
- Captura metadados (autor, data, etc.)
- Opcionalmente extrai imagens para análise

### 2. Estruturação com IA
- Um LLM analisa o texto extraído
- Identifica informações-chave (nome do projeto, área, materiais, etc.)
- Retorna dados estruturados em JSON

### 3. Agente Redator
- Recebe dados estruturados + regras ABNT + template do cliente
- Gera um rascunho completo do memorial descritivo
- Segue estritamente o formato especificado

### 4. Agente Revisor
- Analisa o rascunho quanto a:
  - Consistência com dados originais
  - Conformidade com ABNT
  - Aderência ao template
  - Clareza e profissionalismo
- Retorna versão final corrigida

## 🔒 Segurança

- Arquivos temporários são deletados após processamento
- Validação de tipo e tamanho de arquivo
- Tratamento de erros robusto
- Logs detalhados para auditoria

## 🚧 Melhorias Futuras

- [ ] Análise multimodal de imagens (plantas, diagramas)
- [ ] Suporte a templates múltiplos por cliente
- [ ] Cache de resultados
- [ ] Processamento assíncrono para PDFs grandes
- [ ] Interface web para upload e visualização
- [ ] Exportação em formatos variados (Word, PDF formatado)
- [ ] Integração com sistemas de gerenciamento de projetos

## 📝 Licença

[Especifique sua licença]

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato em [seu-email]

