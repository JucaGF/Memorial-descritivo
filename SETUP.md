# Guia de Instalação e Configuração - Memorial Automator

Este guia fornece instruções detalhadas para configurar e executar o sistema.

## 📋 Pré-requisitos

- **Python 3.10 ou superior**
- **pip** (gerenciador de pacotes Python)
- **Conta OpenAI** com chave de API
- **Git** (opcional, para clonar o repositório)

## 🔧 Passo a Passo de Instalação

### 1. Preparar o Ambiente

```bash
# Navegue até o diretório do projeto
cd /home/joaquim/Projects/Memorial-descritivo

# Crie um ambiente virtual Python
python -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows
```

### 2. Instalar Dependências

```bash
# Instale todas as dependências do projeto
pip install -r requirements.txt
```

**Dependências principais:**
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `openai` - Cliente OpenAI
- `PyMuPDF` - Extração de PDF
- `pydantic` - Validação de dados

### 3. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo (se ainda não existir um .env)
cp .env.example .env

# Edite o arquivo .env
nano .env  # ou use seu editor preferido
```

**Configure a chave da OpenAI (OBRIGATÓRIO):**

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

Para obter sua chave:
1. Acesse [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave e cole no arquivo `.env`

**Outras configurações importantes:**

```env
# Modelos de IA (ajuste conforme necessidade)
OPENAI_MODEL=gpt-4o              # Modelo multimodal para parsing
OPENAI_WRITER_MODEL=gpt-4-turbo  # Modelo para escrita
OPENAI_REVIEWER_MODEL=gpt-4-turbo # Modelo para revisão

# Temperaturas dos agentes (0.0 = determinístico, 1.0 = criativo)
WRITER_TEMPERATURE=0.7     # Mais criativo para redação
PARSER_TEMPERATURE=0.3     # Mais preciso para extração
REVIEWER_TEMPERATURE=0.2   # Muito preciso para revisão

# Debug (defina como True para desenvolvimento)
DEBUG=False
```

### 4. Configurar Arquivos de Contexto

Os arquivos de contexto são cruciais para a qualidade dos memoriais gerados.

#### 4.1 Regras ABNT

Edite o arquivo `context_files/abnt_rules.txt`:

```bash
nano context_files/abnt_rules.txt
```

**O que incluir:**
- Normas ABNT específicas para memoriais descritivos
- NBRs relevantes (NBR 6118, NBR 15575, etc.)
- Regras de formatação
- Terminologia técnica obrigatória
- Estrutura de documentos técnicos

**Exemplo:**
```
# REGRAS ABNT PARA MEMORIAIS DESCRITIVOS

## NBR 6118:2014 - Projeto de estruturas de concreto
- Toda especificação de concreto deve incluir fck mínimo
- Cobrimento nominal mínimo: 2,5cm (ambiente urbano)

## NBR 15575 - Desempenho de edificações
- Mencionar nível de desempenho pretendido
...
```

#### 4.2 Template do Cliente

Edite o arquivo `context_files/client_template.txt`:

```bash
nano context_files/client_template.txt
```

**O que incluir:**
- Estrutura exata desejada para o memorial
- Seções obrigatórias
- Formato de cabeçalhos e rodapés
- Informações que devem sempre aparecer
- Ordem das seções

**O arquivo já vem com um template exemplo que pode ser customizado.**

#### 4.3 Templates Específicos por Cliente (Opcional)

Para ter templates diferentes por cliente:

```bash
# Crie templates específicos com o padrão: client_template_{CLIENT_ID}.txt
cp context_files/client_template.txt context_files/client_template_cliente1.txt
nano context_files/client_template_cliente1.txt
```

No request da API, use:
```json
{
  "client_id": "cliente1"
}
```

## 🚀 Executando o Sistema

### Método 1: Script de Start (Recomendado)

```bash
./start.sh
```

### Método 2: Comando Direto

```bash
# Ative o ambiente virtual primeiro
source venv/bin/activate

# Execute o servidor
python -m app.main
# OU
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Método 3: Modo Debug

```bash
# Para desenvolvimento com auto-reload
uvicorn app.main:app --reload --log-level debug
```

## ✅ Verificando a Instalação

### 1. Teste de Health Check

```bash
# Em outro terminal
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-23T..."
}
```

### 2. Teste com PDF

Use o script de teste fornecido:

```bash
# Primeiro, tenha um PDF de projeto disponível
python test_api.py caminho/para/projeto.pdf
```

### 3. Teste via Swagger UI

Abra no navegador: [http://localhost:8000/docs](http://localhost:8000/docs)

1. Clique em `POST /api/v1/generate_memorial`
2. Clique em "Try it out"
3. Faça upload de um PDF
4. Configure os parâmetros
5. Clique em "Execute"

## 🐛 Resolução de Problemas

### Erro: "No module named 'fitz'"

**Solução:**
```bash
pip install PyMuPDF
```

### Erro: "OpenAI API key not found"

**Solução:**
1. Verifique se o arquivo `.env` existe
2. Verifique se `OPENAI_API_KEY` está configurado
3. Reinicie o servidor após modificar o `.env`

### Erro: "Context file not found"

**Solução:**
```bash
# Certifique-se de que os diretórios existem
mkdir -p context_files temp_uploads

# Verifique se os arquivos de contexto existem
ls -la context_files/
```

### Erro: "File too large"

**Solução:**
Ajuste o limite no `.env`:
```env
MAX_UPLOAD_SIZE=104857600  # 100MB em bytes
```

### Erro de memória ao processar PDFs grandes

**Soluções:**
1. Reduza `MAX_PAGES_PER_PDF` no `.env`
2. Use modelos menores (`gpt-3.5-turbo` em vez de `gpt-4`)
3. Divida o PDF em partes menores

### Erro: "Rate limit exceeded" (OpenAI)

**Solução:**
1. Verifique seus limites de uso na OpenAI
2. Adicione delay entre requests
3. Upgrade seu plano da OpenAI

## 📊 Monitoramento e Logs

### Ver logs em tempo real

```bash
# Os logs aparecem no terminal onde o servidor está rodando
# Para salvar em arquivo:
uvicorn app.main:app --log-config logging.conf 2>&1 | tee logs/app.log
```

### Estrutura de logs

```
2025-10-23 10:30:15 - app.main - INFO - Starting memorial generation request
2025-10-23 10:30:16 - app.services.pdf_extractor - INFO - Extracted 15 pages
2025-10-23 10:30:25 - app.services.document_parser - INFO - Successfully parsed document
2025-10-23 10:30:35 - app.services.agent_service - INFO - Writer Agent completed
2025-10-23 10:30:45 - app.services.agent_service - INFO - Reviewer Agent completed
```

## 🔒 Segurança

### Boas Práticas

1. **NUNCA** commite o arquivo `.env` com chaves reais
2. Use `.gitignore` (já configurado)
3. Restrinja acesso ao diretório `temp_uploads/`
4. Em produção, use HTTPS
5. Configure rate limiting na API
6. Use autenticação para acesso à API

### Variáveis sensíveis

```bash
# Defina permissões restritas para o .env
chmod 600 .env
```

## 🚢 Deploy em Produção

### Usando Docker (Futuro)

```bash
# TODO: Adicionar Dockerfile
docker build -t memorial-automator .
docker run -p 8000:8000 --env-file .env memorial-automator
```

### Usando Systemd (Linux)

Crie um serviço: `/etc/systemd/system/memorial-automator.service`

```ini
[Unit]
Description=Memorial Automator API
After=network.target

[Service]
Type=simple
User=joaquim
WorkingDirectory=/home/joaquim/Projects/Memorial-descritivo
Environment="PATH=/home/joaquim/Projects/Memorial-descritivo/venv/bin"
ExecStart=/home/joaquim/Projects/Memorial-descritivo/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable memorial-automator
sudo systemctl start memorial-automator
sudo systemctl status memorial-automator
```

## 📞 Suporte

Se encontrar problemas não cobertos neste guia:

1. Verifique os logs da aplicação
2. Consulte a documentação da API: http://localhost:8000/docs
3. Revise os arquivos de contexto
4. Verifique os limites de uso da OpenAI

## ✅ Checklist de Instalação Completa

- [ ] Python 3.10+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado com `OPENAI_API_KEY`
- [ ] Arquivos de contexto editados:
  - [ ] `context_files/abnt_rules.txt`
  - [ ] `context_files/client_template.txt`
- [ ] Servidor iniciado com sucesso
- [ ] Health check respondendo corretamente
- [ ] Teste com PDF realizado com sucesso

Pronto! Seu sistema Memorial Automator está configurado e pronto para uso! 🎉

