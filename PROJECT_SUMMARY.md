# Memorial Maker - Sumário do Projeto

## 🎯 Visão Geral

**Memorial Maker** é um MVP completo de geração automática de Memorial Descritivo de Telecomunicações a partir de projetos em PDF, usando:
- **Docling** para extração inteligente de PDFs
- **RAG** (Retrieval-Augmented Generation) para estilo/estrutura
- **LLMs** (OpenAI) para redação técnica profissional
- **Orquestração paralela** para performance otimizada

## 📦 Componentes Implementados

### 1. Configuração e Estrutura Base ✅

- `pyproject.toml` - Configuração do pacote Python
- `requirements.txt` - Dependências
- `README.md` - Documentação principal
- `INSTALL.md` - Guia de instalação
- `USAGE.md` - Guia de uso detalhado
- `.gitignore` - Arquivos ignorados pelo Git
- `setup.sh` - Script de instalação automatizada

### 2. Módulo de Configuração ✅

**`memorial_maker/config.py`**
- Settings com Pydantic
- Configurações de LLM (modelo, temperatura, tokens)
- Parâmetros de extração (DPI, OCR, ROIs)
- Mapeamento canônico (cabos, pontos, divisores, etc.)
- Normas técnicas padrão
- Regex patterns para extração

### 3. Utilitários ✅

**`memorial_maker/utils/`**
- `io_paths.py` - Gerenciamento de caminhos e diretórios
- `logging.py` - Sistema de logging com Rich
- `cv_utils.py` - Funções de Computer Vision (OpenCV)

### 4. Extração de Dados ✅

**`memorial_maker/extract/`**

#### `docling_extract.py` - Extração primária
- Usa Docling para parsing inteligente de PDFs
- Extrai blocos de texto, tabelas, hierarquia
- Classifica páginas (planta, corte, legenda, etc.)
- Detecta pavimentos e keywords
- Exporta JSON por página

#### `pdf_fallback.py` - Fallback robusto
- PyMuPDF para extração de texto bruto
- OpenCV para processamento de imagens
- OCR com Tesseract por ROI
- Complementa extração Docling quando necessário

#### `carimbo.py` - Parser de carimbo
- Extrai informações do carimbo (projeto, revisão, data, escala)
- Heurísticas para campos padrão
- Merge de carimbos de múltiplas páginas

#### `tables.py` - Extração de tabelas
- Detecta tabelas via linhas horizontais/verticais
- OCR célula-a-célula
- Fallback com Tabula (opcional)
- Classifica tabelas (legenda, sumário, normas)

### 5. Normalização e Consolidação ✅

**`memorial_maker/normalize/`**

#### `canonical_map.py` - Mapeamento canônico
- Normaliza variações de termos para chaves padrão
- Extrai diâmetros (mm, polegadas)
- Extrai alturas (H=)
- Extrai divisores (1/2, 1/3, etc.)
- Extrai datas, escalas
- ItemExtractor: extrai itens estruturados de texto/tabelas

#### `consolidate.py` - Consolidação de dados
- Agrega dados de múltiplas fontes/páginas
- Organiza por pavimento e serviço
- Gera JSON mestre
- Exporta CSVs (itens, totais, salas)

### 6. RAG (Retrieval-Augmented Generation) ✅

**`memorial_maker/rag/`**

#### `index_style.py` - Indexação de estilo
- Carrega memoriais-modelo (DOC/DOCX)
- Indexa com FAISS + OpenAI Embeddings
- Detecta seções automaticamente
- Retrieval de exemplos de estilo (top-k)

#### `generate_sections.py` - Geração de seções
- Orquestração **assíncrona** (paralela) de 7 seções
- Filtro de contexto factual por seção
- Integração com LLM (ChatOpenAI)
- Fallback sequencial se paralelo falhar
- Temperatura=0 para determinismo

#### `prompts/` - Prompts por seção ✅
- `base_instructions.txt` - Regras gerais
- `s1_introducao.txt` - Seção 1
- `s2_dados_obra.txt` - Seção 2
- `s3_normas.txt` - Seção 3
- `s4_servicos.txt` - Seção 4 (intro)
- `s4_1_voz.txt` - Subseção 4.1
- `s4_2_dados.txt` - Subseção 4.2
- `s4_3_video.txt` - Subseção 4.3
- `s4_4_intercom.txt` - Subseção 4.4
- `s4_5_monitoramento.txt` - Subseção 4.5
- `s5_sala_monitoramento.txt` - Seção 5
- `s6_passivos_ativos.txt` - Seção 6
- `s7_testes_aceitacao.txt` - Seção 7

### 7. Writer DOCX ✅

**`memorial_maker/writer/`**

#### `docx_styles.py` - Estilos e formatação
- Configura estilos do documento (Heading 1/2, Normal, List)
- Capa com logo e dados do projeto
- Numeração automática de seções
- Formatação PT-BR (vírgula decimal)

#### `write_docx.py` - Montagem do documento
- MemorialWriter: classe principal
- Monta 7 seções na ordem correta
- Adiciona cabeçalhos e conteúdo
- Salva DOCX final

### 8. Interface CLI ✅

**`memorial_maker/cli.py`**
- CLI completa com Typer
- Opções configuráveis (DPI, modelo, paralelo, etc.)
- Barra de progresso com Rich
- Validações de entrada
- Logs detalhados

Comando:
```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --logo "./logo.png" \
  --out-dir "./out"
```

### 9. Interface Web (Streamlit) ✅

**`ui/app.py`**
- Interface intuitiva e amigável
- Upload de múltiplos arquivos (PDFs, modelos, logo)
- Configuração de parâmetros na sidebar
- Barra de progresso durante processamento
- Download do DOCX gerado
- Prévia das seções geradas
- Visualização de CSVs
- Gerenciamento de sessão

### 10. Testes ✅

**`tests/test_smoke.py`**
- Testes unitários de CanonicalMapper
- Testes de ItemExtractor
- Testes de DataConsolidator
- Teste end-to-end com dados mock
- Configurado com pytest

## 🏗️ Arquitetura

```
                          ┌─────────────┐
                          │   PDFs de   │
                          │   Projeto   │
                          └──────┬──────┘
                                 │
                    ┌────────────▼────────────┐
                    │   EXTRAÇÃO              │
                    │   • Docling (primário)  │
                    │   • Fallback (OCR/CV)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   NORMALIZAÇÃO          │
                    │   • Canonical Map       │
                    │   • Item Extractor      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   CONSOLIDAÇÃO          │
                    │   • JSON Mestre         │
                    │   • CSVs (pavimento/    │
                    │     serviço/salas)      │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                                               │
┌────────▼────────┐                         ┌───────────▼──────────┐
│  RAG DE ESTILO  │                         │  CONTEXTO FACTUAL    │
│  • Indexa       │                         │  • Filtra por seção  │
│    modelos      │                         │  • Dados reais       │
│  • Retrieval    │                         │                      │
└────────┬────────┘                         └───────────┬──────────┘
         │                                               │
         └───────────────────┬───────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │   GERAÇÃO LLM           │
                │   • 7 seções (paralelo) │
                │   • Prompts específicos │
                │   • Temperatura=0       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │   WRITER DOCX           │
                │   • Capa com logo       │
                │   • 7 seções formatadas │
                │   • Estilos PT-BR       │
                └────────────┬────────────┘
                             │
                    ┌────────▼────────┐
                    │  MEMORIAL.docx  │
                    └─────────────────┘
```

## 📋 Estrutura de Dados

### JSON Mestre
```json
{
  "obra": {
    "construtora": "...",
    "empreendimento": "...",
    "endereco": "...",
    "tipologia": "...",
    "pavimentos": ["Subsolo", "Térreo", "1º", ...],
    "carimbo": { "projeto": "...", "revisao": "...", "data": "..." }
  },
  "servicos": ["voz", "dados", "video", "intercomunicacao", "monitoramento"],
  "itens": [
    {
      "pavimento": "8º",
      "tipo": "point_rj45",
      "quantidade": 4,
      "altura_m": 1.40,
      "diam_mm": 32,
      "cabos": ["cat6"],
      "divisor": "1/2",
      "observacao": "..."
    }
  ],
  "salas_tecnicas": [
    {
      "nome": "Sala de Monitoramento",
      "localizacao": "Térreo",
      "requisitos": [...]
    }
  ]
}
```

## 🎯 Critérios de Aceite (Todos ✅)

- [x] Gera DOCX com 7 seções na ordem solicitada (1-7, com 4.1-4.5)
- [x] Usa Docling como primário e fallbacks quando necessário
- [x] Exporta JSON/CSV coerentes (por pavimento/serviço)
- [x] Paraleliza seções quando possível; caso contrário, executa ordenado
- [x] Mantém tom e estrutura similares aos modelos (RAG de estilo)
- [x] Anti-alucinação: omite dados ausentes, não inventa
- [x] CLI funcional com Typer
- [x] UI funcional com Streamlit
- [x] Testes básicos implementados

## 🚀 Como Usar

### 1. Instalação Rápida

```bash
./setup.sh
```

### 2. Configuração

```bash
cp env.example .env
nano .env  # Adicione OPENAI_API_KEY
```

### 3. CLI

```bash
source venv/bin/activate
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --out-dir "./out"
```

### 4. UI

```bash
streamlit run ui/app.py
```

## 📊 Resultados

### Saídas Geradas

```
out/
├── extraido/
│   ├── pagina_001_*.json
│   ├── pagina_002_*.json
│   ├── mestre.json
│   ├── itens_por_pavimento.csv
│   ├── totais_por_servico.csv
│   └── salas_tecnicas.csv
├── memorial/
│   └── MEMORIAL_<PROJETO>_<DATA>.docx
└── logs/
    ├── execution.log
    ├── roi_carimbo_p001.png
    └── roi_legenda_p002.png
```

### Memorial DOCX Final

1. **Capa** - Logo + dados do projeto
2. **1. Introdução** - Visão geral do sistema
3. **2. Dados da Obra** - Identificação do projeto
4. **3. Normas Técnicas** - NBR, EIA/TIA, ISO, etc.
5. **4. Serviços Contemplados**
   - 4.1. Voz
   - 4.2. Dados
   - 4.3. Vídeo
   - 4.4. Intercomunicação
   - 4.5. Monitoramento
6. **5. Sala de Monitoramento** - Requisitos ER/EF
7. **6. Elementos Passivos e Ativos** - Materiais
8. **7. Testes e Aceitação** - Certificação

## 🔧 Tecnologias Utilizadas

- **Python 3.10+**
- **Docling** - Extração inteligente de PDFs
- **PyMuPDF** - Fallback de extração
- **OpenCV** - Processamento de imagens
- **Tesseract OCR** - Reconhecimento de caracteres
- **LangChain** - Framework RAG
- **OpenAI API** - LLMs (GPT-4o, embeddings)
- **FAISS** - Vector store
- **python-docx** - Geração de DOCX
- **Typer** - CLI moderna
- **Streamlit** - Interface web
- **Rich** - Terminal com estilo
- **Pydantic** - Validação de dados
- **Pandas** - Manipulação de dados
- **pytest** - Testes

## 📈 Performance

### Processamento Típico (5 PDFs, 15 páginas)

- **Extração**: ~2 min
- **Normalização**: ~10 seg
- **Geração (paralelo)**: ~30-60 seg
- **Total**: ~3-4 min

### Custos Estimados (OpenAI)

- **Embeddings** (indexação): ~$0.01
- **Geração** (7 seções, gpt-4o): ~$0.10-0.30
- **Total por memorial**: ~$0.15-0.35

## 🎓 Destaques Técnicos

1. **Extração Híbrida**: Docling + fallbacks robustos
2. **RAG Inteligente**: Estilo dos modelos, fatos dos PDFs
3. **Orquestração Assíncrona**: 7 seções em paralelo
4. **Anti-alucinação**: Temperatura 0, guardrails explícitos
5. **Normalização Semântica**: Dicionário canônico extenso
6. **Interface Dupla**: CLI para automação, UI para interação
7. **Estrutura Modular**: Fácil manutenção e extensão

## 🔮 Próximos Passos

- [ ] Suporte a planilhas XLSX
- [ ] Geração de diagramas de blocos
- [ ] Exportação para PDF
- [ ] Batch processing
- [ ] Deploy web (cloud)
- [ ] Modelos fine-tuned específicos
- [ ] Detecção de símbolos customizados (ML)
- [ ] Integração com CAD (DWG/DXF)

## 📄 Licença

MIT License

---

**Memorial Maker v0.1.0** - Geração automática de Memorial Descritivo de Telecomunicações com IA






