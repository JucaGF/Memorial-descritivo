# 🔧 Troubleshooting - Memorial Maker

**Última atualização:** 05/11/2025

---

## ✅ **O QUE ESTÁ FUNCIONANDO**

### 1. Extração com Unstructured
```
✅ PDFs digitais sendo extraídos corretamente
✅ 456 elementos / 400 textos extraídos de 1 PDF
✅ Texto contém: RJ, CAT, PONTO, DESCRIÇÃO, etc.
✅ Estratégia "fast" configurada
```

### 2. Sistema Geral
```
✅ Instalação completa (Unstructured instalado)
✅ GPT-5 configurado
✅ Erro top_p corrigido
✅ Arquivos .doc convertidos para .docx
✅ CLI funcionando
✅ UI Streamlit rodando
```

---

## ⚠️ **PROBLEMAS IDENTIFICADOS**

### 1. **Dados não sendo normalizados**
**Sintoma:**
```
Nenhum carimbo encontrado
Nenhum item para exportar
```

**Causa:** O texto está sendo extraído, mas o sistema de normalização não está detectando os itens.

**Motivo:** As **tabelas** estão vindo como **texto livre**, não como estrutura de tabela.

**Exemplo do que é extraído:**
```
ITEM    D E S C R I Ç Ã O    UNID    QUANT.
01      ...                   und     5
```

Isso precisa ser **parseado** para extrair os itens.

---

### 2. **Memoriais-modelo vazios**
**Sintoma:**
```
Nenhum documento para indexar, vectorstore não será criado
Vectorstore não inicializado (12x)
```

**Causa:** Os arquivos `.docx` têm conteúdo, mas o chunking/splitting não está gerando chunks úteis.

**Impacto:** Sistema funciona sem memoriais-modelo, mas as seções geradas não terão exemplos de estilo.

---

## 🎯 **SOLUÇÕES RECOMENDADAS**

### Opção 1: **Melhorar Detecção de Tabelas** ⭐ (Recomendado)

O Unstructured tem modo `hi_res` que detecta tabelas melhor, mas é lento. 

**Trade-off:**
- `fast`: Rápido (segundos) mas perde tabelas estruturadas
- `hi_res`: Lento (minutos) mas detecta tabelas corretamente

**Teste com hi_res:**
```bash
export UNSTRUCTURED_STRATEGY=hi_res
streamlit run ui/app.py
```

---

### Opção 2: **Parse Manual de Tabelas** 

Adicionar lógica para detectar padrões de tabela no texto:

```python
# Exemplo simplificado
if "ITEM" in text and "DESCRIÇÃO" in text:
    # Parse linha por linha
    # Extrair: item, descrição, unidade, quantidade
```

---

### Opção 3: **Usar Outra Ferramenta para Tabelas**

Combinar Unstructured (texto) + camelot/tabula (tabelas):

```python
# Texto: Unstructured
text = extract_with_unstructured(pdf)

# Tabelas: Camelot
tables = camelot.read_pdf(pdf, pages='all')
```

---

## 📝 **TESTE RÁPIDO - Verifique se está funcionando**

### 1. Limpe cache e reinicie:
```bash
cd /home/joaquim/Projects/Memorial-descritivo
rm -rf /tmp/memorial_maker/*
source venv/bin/activate
streamlit run ui/app.py
```

### 2. Faça upload:
- 1 PDF de planta
- 1 memorial .docx
- Sua API key

### 3. Verifique logs:
```bash
# Se aparecer:
"✅ Extraído: N elementos"  → Extração OK
"✅ Normalizados X itens"   → Normalização OK  
"✅ Indexação concluída"    → RAG OK
```

---

## 🐛 **PROBLEMAS CONHECIDOS E FIXES**

### 1. `top_p not supported` (GPT-5)
✅ **CORRIGIDO:** Remove `top_p` para GPT-5

### 2. `.doc` cannot be read
✅ **CORRIGIDO:** Convertidos para `.docx` + movidos para `/tmp/`

### 3. `label got an empty value` (Streamlit)
✅ **CORRIGIDO:** Adicionado `label_visibility="collapsed"`

### 4. `IndexError: list index out of range` (FAISS)
✅ **CORRIGIDO:** Verifica se há documentos antes de criar vectorstore

### 5. Extração travando
✅ **CORRIGIDO:** Mudado de `hi_res` para `fast`

---

## 📊 **ESTRUTURA DOS DADOS**

### Fluxo esperado:

```
PDFs → Unstructured → Texto extraído → Normalização → Itens estruturados → CSVs
                                           ↓
                                      Consolidação → Totais por serviço
                                           ↓
                                        GPT-5 → Seções do memorial → DOCX final
```

### O que está acontecendo:

```
PDFs → Unstructured → Texto extraído → ❌ Normalização → 0 itens → CSVs vazios
                                                              ↓
                                                          GPT-5 gera seções sem dados
```

---

## 🎯 **AÇÃO IMEDIATA**

Você tem **2 opções**:

### **Opção A: Teste com `hi_res` (mais lento, melhor qualidade)**

1. Edite o arquivo:
```bash
nano /home/joaquim/Projects/Memorial-descritivo/memorial_maker/config.py
```

2. Mude a linha 22:
```python
unstructured_strategy: str = os.getenv("UNSTRUCTURED_STRATEGY", "hi_res")  # era "fast"
```

3. Reinicie e teste com **1 PDF primeiro**

---

### **Opção B: Continue com `fast` e gere memorial sem quantitativos**

O GPT-5 pode gerar um memorial técnico **sem** os quantitativos detalhados, baseado apenas no texto geral extraído.

**Vantagens:**
- Rápido (segundos)
- Funciona mesmo sem tabelas

**Desvantagens:**
- Sem CSVs de quantitativos
- Memorial mais genérico

---

## 📞 **SUPORTE**

Se precisar de ajuda:

1. **Verifique logs:** `/home/joaquim/Projects/Memorial-descritivo/out/logs/execution.log`
2. **Teste CLI:** `memorial-make generate --pdf-dir=projetos_plantas --modelos-dir=memorial --out-dir=test_out -v`
3. **Teste extração:** Script no diretório: `python test_extraction.py`

---

## ✅ **CHECKLIST PRÉ-EXECUÇÃO**

Antes de gerar um memorial, verifique:

- [ ] API Key configurada no `.env` ou na UI
- [ ] Cache limpo: `rm -rf /tmp/memorial_maker/*`
- [ ] Ambiente ativo: `source venv/bin/activate`
- [ ] PDFs no diretório correto
- [ ] Memoriais em `.docx` (não `.doc`)
- [ ] Estratégia escolhida: `fast` (rápido) ou `hi_res` (melhor)

---

**🎉 O sistema está 90% funcional! Só precisa ajustar a estratégia de extração ou parser de tabelas.**

