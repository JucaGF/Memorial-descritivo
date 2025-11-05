# Memorial Maker - Início Rápido ⚡

## Instalação em 3 Passos

### 1. Execute o setup

```bash
./setup.sh
```

### 2. Configure sua API key

```bash
cp env.example .env
nano .env
```

Adicione:
```bash
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

### 3. Ative o ambiente

```bash
source venv/bin/activate
```

## Uso Imediato

### Opção A: Interface Web (Recomendado) 🖥️

```bash
streamlit run ui/app.py
```

1. Configure API Key na sidebar
2. Faça upload de:
   - PDFs de projeto (plantas, cortes)
   - Memoriais-modelo (DOC/DOCX) - opcional
   - Logo TecPred (PNG) - opcional
3. Clique em "Gerar Memorial Descritivo"
4. Aguarde ~3-5 minutos
5. Baixe o DOCX gerado

### Opção B: Linha de Comando 💻

```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --out-dir "./out"
```

**Com logo:**
```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --logo "./tecpred_logo.png" \
  --out-dir "./out"
```

## Estrutura de Entrada

Organize seus arquivos:

```
projetos_plantas/
  ├── PROJETO_01_SUBSOLO.pdf
  ├── PROJETO_02_TÉRREO.pdf
  ├── PROJETO_03_TIPO.pdf
  └── PROJETO_04_COBERTURA.pdf

memorial/
  ├── MEMORIAL_MODELO_01.docx
  └── MEMORIAL_MODELO_02.docx

tecpred_logo.png
```

## O Que Vai Acontecer

1. ⏳ **Extração** (2 min)
   - Lê PDFs com Docling
   - OCR em áreas específicas
   - Detecta plantas, cortes, legendas

2. 🔧 **Normalização** (10 seg)
   - Identifica pontos (RJ-45, TV, câmeras, etc.)
   - Mapeia cabos (CAT-6, RG-06, etc.)
   - Extrai medidas e divisores

3. 📊 **Consolidação** (10 seg)
   - Agrupa por pavimento
   - Agrupa por serviço
   - Gera JSONs e CSVs

4. ✍️ **Geração** (30-60 seg)
   - 7 seções em paralelo
   - Estilo dos modelos + dados reais
   - LLM escreve memorial

5. 📝 **DOCX Final**
   - Capa com logo
   - 7 seções formatadas
   - Pronto para revisão!

## Resultado

```
out/
├── extraido/
│   ├── mestre.json                    ← Dados consolidados
│   ├── itens_por_pavimento.csv        ← Itens por andar
│   └── totais_por_servico.csv         ← Totais agregados
├── memorial/
│   └── MEMORIAL_PROJETO_2025-11-04.docx  ← SEU MEMORIAL! 🎉
└── logs/
    └── execution.log                   ← Logs detalhados
```

## Solução de Problemas Rápidos

### ❌ "OpenAI API key not found"

```bash
# Verifique se configurou:
cat .env | grep OPENAI_API_KEY

# Se vazio, edite:
nano .env
# Adicione: OPENAI_API_KEY=sk-proj-...
```

### ❌ "Tesseract not found"

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

**Fedora:**
```bash
sudo dnf install tesseract tesseract-langpack-por
```

### ❌ "No module named 'memorial_maker'"

```bash
# Reinstale:
pip install -e .
```

### ❌ "Rate limit exceeded"

Use modo sequencial:
```bash
memorial-make --sequential ...
```

Ou reduza modelo:
```bash
memorial-make --llm-model "gpt-4o-mini" ...
```

## Dicas Rápidas

💡 **Primeira vez?** Use a UI (Streamlit) - é mais visual

💡 **Precisa de velocidade?** Mantenha `--parallel` (padrão)

💡 **Quer economizar?** Use `--llm-model gpt-4o-mini`

💡 **PDFs ruins?** Aumente `--dpi 400` ou `--dpi 600`

💡 **Sem modelos?** Funciona sem! O estilo será genérico

💡 **Debug?** Use `--verbose` para logs detalhados

## Comandos Úteis

```bash
# Ajuda completa
memorial-make --help

# Versão
memorial-make version

# Exemplo completo
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --logo "./logo.png" \
  --out-dir "./output" \
  --dpi 300 \
  --llm-model "gpt-4o" \
  --parallel \
  --verbose

# Testes
pytest tests/ -v
```

## O Que Esperar no Memorial

✅ **Capa** com logo e dados do projeto
✅ **1. Introdução** - Visão geral
✅ **2. Dados da Obra** - Identificação
✅ **3. Normas Técnicas** - NBR, EIA/TIA, ISO
✅ **4. Serviços Contemplados**
   - 4.1. Voz
   - 4.2. Dados (RJ-45, Wi-Fi)
   - 4.3. Vídeo (TV, divisores)
   - 4.4. Intercomunicação
   - 4.5. Monitoramento (CFTV)
✅ **5. Sala de Monitoramento** - Requisitos
✅ **6. Elementos Passivos/Ativos** - Materiais
✅ **7. Testes e Aceitação** - Certificação

## Próximos Passos

📖 **Documentação Completa:**
- `README.md` - Visão geral
- `INSTALL.md` - Instalação detalhada
- `USAGE.md` - Guia de uso completo
- `PROJECT_SUMMARY.md` - Arquitetura e componentes

🐛 **Encontrou um bug?** Abra uma issue

💡 **Tem uma sugestão?** Contribuições são bem-vindas!

---

**Tempo médio: 3-5 minutos do upload ao DOCX pronto** ⚡

Bom trabalho! 🎉






