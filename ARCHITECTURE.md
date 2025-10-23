# Arquitetura do Sistema - Memorial Automator

Este documento descreve a arquitetura técnica e o design do sistema.

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         Cliente                             │
│            (Web, Mobile, CLI, API Client)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│                        (main.py)                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  POST /api/v1/generate_memorial                       │  │
│  │  GET  /health                                         │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐
    │  PDF    │ │Document │ │  Agent   │
    │Extractor│ │ Parser  │ │ Service  │
    └────┬────┘ └────┬────┘ └────┬─────┘
         │           │           │
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐
    │PyMuPDF  │ │OpenAI   │ │OpenAI    │
    │ (fitz)  │ │GPT-4o   │ │GPT-4     │
    └─────────┘ └─────────┘ └──────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              ┌────────────┐        ┌───────────┐
              │  Writer    │        │ Reviewer  │
              │   Agent    │        │   Agent   │
              └────────────┘        └───────────┘
                     │                     │
                     └──────────┬──────────┘
                                ▼
                        ┌───────────────┐
                        │  Memorial     │
                        │  Descritivo   │
                        │  (Output)     │
                        └───────────────┘
```

## 🏗️ Camadas da Aplicação

### 1. Camada de Apresentação (API Layer)

**Arquivo:** `app/main.py`

**Responsabilidades:**
- Exposição de endpoints REST
- Validação de requisições
- Gerenciamento de uploads
- Orquestração do pipeline
- Tratamento de erros HTTP
- Formatação de respostas

**Tecnologias:**
- FastAPI (framework web)
- Uvicorn (servidor ASGI)
- Pydantic (validação de dados)

### 2. Camada de Serviços (Business Logic)

#### 2.1 PDF Extractor Service

**Arquivo:** `app/services/pdf_extractor.py`

**Responsabilidades:**
- Extração de texto de PDFs
- Extração de imagens
- Extração de metadados
- Tratamento de PDFs corrompidos

**Tecnologias:**
- PyMuPDF (fitz)
- Pillow (processamento de imagens)

**Métodos Principais:**
```python
extract(file_path, extract_images) -> dict
  └─> Retorna: {text, images, metadata, pages}

extract_text_only(file_path) -> str
  └─> Otimizado para extração rápida apenas de texto
```

#### 2.2 Document Parser Service

**Arquivo:** `app/services/document_parser.py`

**Responsabilidades:**
- Análise inteligente de texto com IA
- Estruturação de dados
- Extração de informações-chave
- Interpretação de contexto técnico

**Tecnologias:**
- OpenAI GPT-4o (multimodal)
- JSON Schema para estruturação

**Métodos Principais:**
```python
structure_data(raw_data) -> StructuredProjectData
  └─> Usa IA para converter texto bruto em dados estruturados

structure_data_with_images(raw_data) -> StructuredProjectData
  └─> [Futuro] Análise multimodal incluindo imagens
```

**Prompt Engineering:**
O parser usa um sistema de prompt sofisticado que:
1. Define claramente a estrutura JSON esperada
2. Instrui sobre extração precisa de informações
3. Especifica comportamento para dados ausentes

#### 2.3 Agent Service

**Arquivo:** `app/services/agent_service.py`

**Responsabilidades:**
- Gerenciamento dos agentes de IA
- Carregamento de contextos (ABNT, templates)
- Orquestração Writer → Reviewer
- Construção de prompts especializados

**Tecnologias:**
- OpenAI GPT-4 Turbo

**Agentes:**

##### Writer Agent (Agente Redator)
```python
run_writer_agent(structured_data, abnt_rules, client_template, custom_instructions)
  └─> Gera o rascunho inicial do memorial
```

**Características:**
- Temperature: 0.7 (criativo mas controlado)
- Prompt estruturado com contexto completo
- Foco em conformidade e completude

##### Reviewer Agent (Agente Revisor)
```python
run_reviewer_agent(draft_memorial, structured_data, abnt_rules, client_template)
  └─> Revisa e refina o memorial
```

**Características:**
- Temperature: 0.2 (muito preciso)
- Abordagem chain-of-thought
- Checklist de verificação:
  1. Consistência de dados
  2. Conformidade ABNT
  3. Aderência ao template
  4. Clareza e coerência

### 3. Camada de Modelos (Data Layer)

**Arquivo:** `app/models/schemas.py`

**Modelos Pydantic:**

```python
StructuredProjectData       # Dados estruturados extraídos
GenerateMemorialRequest     # Request do endpoint
GenerateMemorialResponse    # Response do endpoint
ErrorResponse              # Respostas de erro
HealthCheckResponse        # Health check
PDFExtractionResult        # Resultado da extração
```

### 4. Camada de Configuração

**Arquivo:** `app/core/config.py`

**Responsabilidades:**
- Gerenciamento de variáveis de ambiente
- Configurações da aplicação
- Configurações dos modelos de IA
- Validação de configurações

**Pattern:** Singleton com cache (`@lru_cache`)

## 🔄 Fluxo de Dados

### Pipeline Completo

```
1. Upload de PDF
   ↓
2. Validação (tipo, tamanho)
   ↓
3. Salvamento temporário
   ↓
4. Extração de Dados (PDFExtractor)
   │  ├─> Texto
   │  ├─> Imagens (opcional)
   │  └─> Metadados
   ↓
5. Estruturação com IA (DocumentParser)
   │  └─> StructuredProjectData
   ↓
6. Carregamento de Contextos (AgentService)
   │  ├─> Regras ABNT
   │  └─> Template do Cliente
   ↓
7. Geração de Rascunho (Writer Agent)
   │  └─> Draft Memorial
   ↓
8. Revisão e Refinamento (Reviewer Agent)
   │  └─> Final Memorial
   ↓
9. Formatação de Resposta
   ↓
10. Limpeza de Arquivos Temporários
   ↓
11. Retorno ao Cliente
```

### Tempo de Processamento Típico

| Etapa | Tempo (aprox.) |
|-------|----------------|
| Upload e validação | < 1s |
| Extração PDF (15 páginas) | 2-5s |
| Estruturação com IA | 10-15s |
| Writer Agent | 15-20s |
| Reviewer Agent | 10-15s |
| **Total** | **40-60s** |

## 🔐 Segurança e Boas Práticas

### 1. Gerenciamento de Arquivos Temporários

```python
# Arquivos são sempre deletados após processamento
finally:
    if temp_file_path and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
```

### 2. Validação de Entrada

```python
# Validação de tipo de arquivo
if not file.filename.endswith('.pdf'):
    raise HTTPException(status_code=400, detail="Only PDF files")

# Validação de tamanho
if len(file_content) > settings.max_upload_size:
    raise HTTPException(status_code=400, detail="File too large")
```

### 3. Tratamento de Erros

```python
# Hierarquia de exceções
try:
    # Processamento
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))
```

### 4. Logging

```python
# Logging estruturado em cada camada
logger.info(f"Starting PDF extraction from: {file_path}")
logger.warning(f"PDF has {pages} pages, exceeds limit")
logger.error(f"Error extracting PDF: {str(e)}", exc_info=True)
```

## 🧠 Estratégia de IA

### Temperature Settings

| Agente | Temperature | Motivo |
|--------|-------------|--------|
| Parser | 0.3 | Precisão na extração de dados |
| Writer | 0.7 | Criatividade controlada |
| Reviewer | 0.2 | Máxima precisão na revisão |

### Prompt Engineering

#### Princípios:

1. **Clareza de Contexto**: Fornecer todo contexto necessário
2. **Instruções Explícitas**: Não deixar ambiguidades
3. **Exemplos**: Quando possível, incluir exemplos
4. **Estrutura**: Usar markdown e seções claras
5. **Validação**: Especificar formato de saída (JSON, texto)

#### Pattern de Prompts:

```
[ROLE DEFINITION]
Você é um [especialista em X]...

[TASK DESCRIPTION]
Sua tarefa é [objetivo claro]...

[INPUT DATA]
**DADOS:**
{dados}

[CONTEXT]
**REGRAS:**
{regras}

**TEMPLATE:**
{template}

[INSTRUCTIONS]
**INSTRUÇÕES:**
1. [passo 1]
2. [passo 2]
...

[OUTPUT FORMAT]
**FORMATO DE SAÍDA:**
[especificação clara]

[PROMPT]
[chamada para ação]
```

### Otimizações

1. **Context Window Management**
   - Truncate de textos longos
   - Manter partes relevantes (início e fim)
   - Limitar tamanho de imagens

2. **Token Optimization**
   - Usar `response_format={"type": "json_object"}` para respostas estruturadas
   - Limitar `max_tokens` apropriadamente
   - Cachear resultados quando possível

3. **Error Handling**
   - Retry logic para erros transientes da OpenAI
   - Fallback para modelos mais simples se necessário
   - Validação de respostas JSON

## 📊 Monitoramento e Observabilidade

### Métricas Importantes

1. **Performance**
   - Tempo de processamento por etapa
   - Tempo total de request
   - Tamanho de PDFs processados

2. **Qualidade**
   - Taxa de sucesso
   - Warnings gerados
   - Campos não encontrados em structured_data

3. **Uso de IA**
   - Tokens consumidos
   - Custo por request
   - Rate limits da OpenAI

### Logging Strategy

```python
# Níveis de log
DEBUG: Detalhes técnicos para desenvolvimento
INFO: Operações normais e progresso
WARNING: Situações incomuns mas recuperáveis
ERROR: Erros que impedem o processamento
```

## 🚀 Escalabilidade

### Considerações Futuras

1. **Processamento Assíncrono**
   ```python
   # Implementar com Celery ou RQ
   @celery.task
   def generate_memorial_async(pdf_path):
       ...
   ```

2. **Cache de Resultados**
   ```python
   # Redis para cache de PDFs já processados
   cache_key = hashlib.md5(pdf_content).hexdigest()
   if cached := redis.get(cache_key):
       return cached
   ```

3. **Load Balancing**
   - Múltiplas instâncias da API
   - Queue para processamento de PDFs
   - Separação de workers

4. **Database**
   - Armazenar memoriais gerados
   - Histórico de processamentos
   - Métricas e analytics

## 🔄 Extensibilidade

### Como Adicionar Novos Agentes

```python
# Em agent_service.py
def run_validator_agent(self, memorial, requirements):
    """Novo agente para validação adicional"""
    prompt = self._build_validator_prompt(memorial, requirements)
    response = self.client.chat.completions.create(...)
    return response.choices[0].message.content
```

### Como Adicionar Novos Formatos de Output

```python
# Em models/schemas.py
class GenerateMemorialPDFResponse(BaseModel):
    memorial_pdf: bytes
    memorial_text: str
    ...

# Em main.py
@app.post("/api/v1/generate_memorial_pdf")
async def generate_memorial_pdf(...):
    memorial_text = ...
    pdf_bytes = convert_to_pdf(memorial_text)
    return Response(content=pdf_bytes, media_type="application/pdf")
```

### Como Adicionar Templates por Tipo de Projeto

```python
# Estrutura de arquivos
context_files/
  ├─ templates/
  │  ├─ residential.txt
  │  ├─ commercial.txt
  │  └─ industrial.txt

# Em agent_service.py
def load_template_by_type(self, project_type: str):
    template_file = self.context_dir / "templates" / f"{project_type}.txt"
    ...
```

## 📚 Dependências Externas

### Críticas
- **OpenAI API**: Essencial para todos os agentes de IA
- **PyMuPDF**: Extração de PDF

### Opcionais
- **Tesseract**: OCR para texto em imagens
- **OpenCV**: Processamento avançado de imagens

## 🧪 Testing Strategy

### Testes Recomendados

```python
# tests/test_pdf_extractor.py
def test_extract_simple_pdf():
    extractor = PDFExtractor()
    result = extractor.extract("test.pdf")
    assert result["pages"] > 0
    assert len(result["text"]) > 0

# tests/test_agent_service.py
def test_writer_agent():
    service = AgentService()
    draft = service.run_writer_agent(...)
    assert len(draft) > 100
    assert "MEMORIAL DESCRITIVO" in draft
```

## 📖 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Última atualização:** 2025-10-23
**Versão do Sistema:** 0.1.0

