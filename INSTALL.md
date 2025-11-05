# Guia de Instalação - Memorial Maker

## Pré-requisitos

### 1. Python 3.10+

```bash
python3 --version  # Deve ser >= 3.10
```

### 2. Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por
```

**Fedora:**
```bash
sudo dnf install tesseract tesseract-langpack-por
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Baixe o instalador de: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Ghostscript (Opcional, para Tabula)

**Ubuntu/Debian:**
```bash
sudo apt install ghostscript
```

**Fedora:**
```bash
sudo dnf install ghostscript
```

## Instalação do Memorial Maker

### 1. Clone/Navegue para o diretório

```bash
cd /home/joaquim/Projects/Memorial-descritivo
```

### 2. Crie ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale dependências

```bash
pip install --upgrade pip
pip install -e .
```

### 4. Configure variáveis de ambiente

```bash
cp .env.example .env
nano .env  # ou vim, code, etc.
```

Edite `.env` e adicione sua API key:
```
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o
```

## Verificação da Instalação

### Teste CLI

```bash
memorial-make --help
```

Deve exibir a ajuda do comando.

### Teste Streamlit

```bash
streamlit run ui/app.py
```

Deve abrir o navegador com a interface.

### Execute testes

```bash
pytest tests/ -v
```

## Uso Básico

### CLI

```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --logo "./tecpred_logo.png" \
  --out-dir "./out" \
  --parallel
```

### UI (Streamlit)

```bash
streamlit run ui/app.py
```

1. Configure API Key na barra lateral
2. Faça upload dos PDFs, modelos e logo
3. Clique em "Gerar Memorial Descritivo"
4. Aguarde o processamento
5. Baixe o DOCX gerado

## Estrutura de Saídas

```
out/
  extraido/
    pagina_001_MGAMAK_TELECOM_01.json
    pagina_002_MGAMAK_TELECOM_02.json
    ...
    mestre.json
    itens_por_pavimento.csv
    totais_por_servico.csv
    salas_tecnicas.csv
  memorial/
    MEMORIAL_MGAMAK_2025-11-04.docx
  logs/
    execution.log
    roi_carimbo_p001.png
    roi_legenda_p002.png
```

## Troubleshooting

### Erro: "Tesseract not found"

**Linux:**
```bash
which tesseract  # Verifica localização
export TESSERACT_CMD=/usr/bin/tesseract
```

**Windows:**
Adicione ao PATH ou configure:
```python
# No .env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Erro: "OpenAI API key not found"

Verifique:
1. Arquivo `.env` existe?
2. `OPENAI_API_KEY` está configurada?
3. API key válida?

```bash
echo $OPENAI_API_KEY  # Deve mostrar sua key
```

### Erro: "Docling import error"

```bash
pip install --upgrade docling
```

### Erro: "Rate limit exceeded" (OpenAI)

Use modo sequencial:
```bash
memorial-make --sequential ...
```

Ou aumente timeout entre requisições editando `config.py`.

## Atualização

```bash
git pull  # Se usando Git
pip install -e . --upgrade
```

## Desinstalação

```bash
deactivate  # Sai do venv
rm -rf venv  # Remove ambiente virtual
```






