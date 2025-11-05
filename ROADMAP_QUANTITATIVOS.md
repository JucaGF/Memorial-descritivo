# 📊 Roadmap - Implementação de Quantitativos

**Status:** 🟡 Planejado (não implementado)  
**Prioridade:** Baixa (sistema funcional sem isso)  
**Estimativa:** 2-3 dias de desenvolvimento

---

## 🎯 **Objetivo**

Extrair automaticamente quantitativos detalhados das plantas técnicas para:
- Gerar tabelas de materiais no memorial
- Criar CSVs com totalizações
- Listar quantidades por pavimento
- Facilitar orçamentação

---

## 📋 **Análise Atual**

### **O que temos:**
```python
# Texto extraído dos PDFs (exemplo real):
"""
RESUMO DE PONTOS - TV COLETIVA

Nº DO PONTO | SHAFT | DESCRIÇÃO | PAVIMENTO | CABO
1           | 2     | APTO. 801 | 8         | 1RG-06/U#90%
2           | 1     | LOUNGE    | 8         | 1RG-06/U#90%
3           | 1     | APTO. 701 | 7         | 1RG-06/U#90%
"""
```

### **O que precisamos extrair:**
```python
{
    "item_type": "point_tv_coletiva",
    "description": "APTO. 801",
    "quantity": 1,
    "unit": "ponto",
    "floor": "8",
    "cable": "RG-06/U#90%",
    "shaft": "2"
}
```

---

## 🔍 **Fase 1: Análise Detalhada** (1 dia)

### **1.1. Mapear Formatos de Tabelas**

Identificar todos os tipos de tabela nos PDFs:

- [ ] **Resumo de Pontos** (TV, Dados, Voz)
  - Formato: `Nº | SHAFT | DESCRIÇÃO | PAVIMENTO | CABO`
  - Localização: Corte esquemático
  
- [ ] **Lista de Materiais**
  - Formato: `ITEM | DESCRIÇÃO | UNID | QUANT`
  - Localização: Plantas baixas
  
- [ ] **Legenda de Símbolos**
  - Formato: Símbolo → Descrição → Quantidade
  - Localização: Todas as plantas

- [ ] **Carimbo Técnico**
  - Dados: Projeto, data, revisão, prancha
  - Localização: Canto inferior direito

### **1.2. Coletar Amostras**

```bash
# Para cada tipo de PDF:
python scripts/extract_samples.py \
  --pdf projetos_plantas/MGAMAK_TELECOM_01_SUBSOLO.pdf \
  --output samples/subsolo.json
```

Resultado esperado:
```json
{
  "tables": [...],
  "legend_items": [...],
  "stamp": {...},
  "text_blocks": [...]
}
```

---

## 🛠️ **Fase 2: Desenvolvimento de Parsers** (2 dias)

### **2.1. Parser de Tabelas**

Arquivo: `memorial_maker/extract/table_parser.py`

```python
class TableParser:
    """Parser específico para tabelas de quantitativos"""
    
    def parse_resumo_pontos(self, text: str) -> List[Dict]:
        """
        Extrai tabela de resumo de pontos
        
        Input:
            Nº DO PONTO | SHAFT | DESCRIÇÃO | PAVIMENTO | CABO
            1           | 2     | APTO. 801 | 8         | 1RG-06/U#90%
        
        Output:
            [{"point_number": 1, "shaft": 2, "description": "APTO. 801", ...}]
        """
        
    def parse_lista_materiais(self, text: str) -> List[Dict]:
        """Extrai tabela de materiais"""
        
    def parse_legenda(self, text: str) -> List[Dict]:
        """Extrai legenda de símbolos"""
```

### **2.2. Parser de Carimbos**

Arquivo: `memorial_maker/extract/stamp_parser.py`

```python
class StampParser:
    """Parser para carimbos técnicos"""
    
    def extract_stamp_data(self, pdf_path: Path) -> Dict:
        """
        Extrai dados do carimbo (canto inferior direito)
        
        Output:
            {
                "project_name": "MGAMAK",
                "date": "28-04-2025",
                "revision": "00",
                "sheet": "01",
                "drawing_type": "SUBSOLO",
                "scale": "1:100"
            }
        """
```

### **2.3. Normalização Avançada**

Arquivo: `memorial_maker/normalize/quantity_extractor.py`

```python
class QuantityExtractor:
    """Extrator de quantidades com reconhecimento de padrões"""
    
    PATTERNS = {
        "cabo_cat6": r"(?:cabo\s+)?cat[-\s]?6.*?(\d+)\s*m",
        "ponto_rj45": r"(?:ponto\s+)?rj[-\s]?45.*?(\d+)",
        "cabo_rg6": r"rg[-\s]?0?6.*?(\d+)\s*m",
        # ... mais padrões
    }
    
    def extract_quantities(self, elements: List[Dict]) -> List[Dict]:
        """Extrai quantidades de todos os elementos"""
```

---

## 🔄 **Fase 3: Integração** (1 dia)

### **3.1. Atualizar Pipeline de Extração**

Modificar `extract/unstructured_extract.py`:

```python
def extract_pdf_with_quantities(pdf_path: Path, output_dir: Path) -> Dict:
    """Extração completa com quantitativos"""
    
    # 1. Extração base (Unstructured)
    base_result = extract_pdf_unstructured(pdf_path, output_dir)
    
    # 2. Parse de tabelas
    parser = TableParser()
    quantities = parser.parse_all_tables(base_result)
    
    # 3. Parse de carimbo
    stamp_parser = StampParser()
    stamp_data = stamp_parser.extract_stamp_data(pdf_path)
    
    # 4. Consolidação
    return {
        **base_result,
        "quantities": quantities,
        "stamp": stamp_data,
    }
```

### **3.2. Atualizar Consolidação**

Modificar `normalize/consolidate.py`:

```python
def consolidate_quantities(extractions: List[Dict]) -> Dict:
    """Consolida quantidades de múltiplos PDFs"""
    
    totals_by_service = defaultdict(lambda: defaultdict(int))
    totals_by_floor = defaultdict(lambda: defaultdict(int))
    
    for extraction in extractions:
        for item in extraction.get("quantities", []):
            service = item["service_type"]
            floor = item.get("floor", "GERAL")
            quantity = item["quantity"]
            
            totals_by_service[service][item["item_type"]] += quantity
            totals_by_floor[floor][item["item_type"]] += quantity
    
    return {
        "by_service": totals_by_service,
        "by_floor": totals_by_floor,
    }
```

### **3.3. Gerar CSVs Corretos**

```python
def export_quantities_csv(data: Dict, output_dir: Path):
    """Exporta CSVs com quantidades"""
    
    # 1. Totais por serviço
    pd.DataFrame(data["by_service"]).to_csv(
        output_dir / "totais_por_servico.csv"
    )
    
    # 2. Totais por pavimento
    pd.DataFrame(data["by_floor"]).to_csv(
        output_dir / "totais_por_pavimento.csv"
    )
    
    # 3. Lista completa de materiais
    # ... implementação
```

---

## 📝 **Fase 4: Testes** (0.5 dia)

### **4.1. Testes Unitários**

```python
# tests/test_table_parser.py
def test_parse_resumo_pontos():
    text = """
    Nº | SHAFT | DESCRIÇÃO | PAVIMENTO
    1  | 2     | APTO. 801 | 8
    """
    result = TableParser().parse_resumo_pontos(text)
    assert len(result) == 1
    assert result[0]["point_number"] == 1
```

### **4.2. Testes de Integração**

```bash
# Teste com PDFs reais
python -m pytest tests/test_quantities_integration.py -v
```

---

## 🎨 **Fase 5: UI** (0.5 dia)

### **5.1. Adicionar Visualização de Quantitativos**

Modificar `ui/app.py`:

```python
# Adicionar aba de quantitativos
with st.expander("📊 Quantitativos Extraídos", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Por Serviço")
        st.dataframe(df_by_service)
    
    with col2:
        st.subheader("Por Pavimento")
        st.dataframe(df_by_floor)
```

### **5.2. Adicionar Tabelas ao DOCX**

Modificar `writer/write_docx.py`:

```python
def add_quantities_table(doc: Document, data: Dict):
    """Adiciona tabela de quantitativos ao documento"""
    
    table = doc.add_table(rows=1, cols=4)
    # Header
    header = table.rows[0].cells
    header[0].text = "Item"
    header[1].text = "Descrição"
    header[2].text = "Unidade"
    header[3].text = "Quantidade"
    
    # Data rows
    for item in data:
        row = table.add_row().cells
        row[0].text = item["type"]
        row[1].text = item["description"]
        row[2].text = item["unit"]
        row[3].text = str(item["quantity"])
```

---

## 🚀 **Implementação Sugerida**

### **Passo 1: Desenvolvimento Local**
```bash
# Criar branch
git checkout -b feature/quantitativos

# Implementar fase por fase
# Testar com PDFs reais
# Commit incremental
```

### **Passo 2: Testes com PDFs Reais**
```bash
# Executar script de teste
python test_extraction.py --with-quantities

# Validar CSVs gerados
# Verificar precisão da extração
```

### **Passo 3: Deploy**
```bash
# Merge quando estável
git checkout main
git merge feature/quantitativos

# Atualizar documentação
# Notificar usuários
```

---

## 🎯 **Critérios de Sucesso**

### **Mínimo Viável:**
- [ ] Extrai 80%+ dos itens de tabelas
- [ ] CSV gerado sem erros
- [ ] Totais corretos por serviço

### **Desejável:**
- [ ] Extrai 95%+ dos itens
- [ ] Detecta legendas automaticamente
- [ ] Parse de carimbo funcionando

### **Excelente:**
- [ ] 100% de precisão em PDFs conhecidos
- [ ] Funciona com variações de formato
- [ ] UI rica com visualizações

---

## 📚 **Recursos Necessários**

### **Bibliotecas Adicionais (opcionais):**
```bash
pip install camelot-py[cv]  # Para tabelas complexas
pip install pdfplumber       # Alternativa para tabelas
pip install opencv-python    # Processamento de imagem
```

### **Tempo Estimado:**
- Análise: 1 dia
- Desenvolvimento: 2 dias
- Testes: 0.5 dia
- UI: 0.5 dia
- **Total: 4 dias**

### **Habilidades:**
- Python avançado (regex, parsing)
- Conhecimento de PDFs técnicos
- Experiência com pandas/CSV

---

## 💡 **Alternativas Mais Simples**

Se não quiser implementar tudo, opções:

### **Opção A: Upload Manual de CSVs**
- Usuário cria CSV com quantitativos
- Sistema apenas lê e inclui no memorial

### **Opção B: Estratégia hi_res do Unstructured**
- Usar `hi_res` em vez de `fast`
- Tabelas vêm estruturadas
- Menos código customizado

### **Opção C: Híbrido**
- Extrai texto básico (atual)
- GPT-5 gera seções
- Usuário revisa e adiciona quantitativos manualmente

---

## 📝 **Próximos Passos Imediatos**

1. ✅ **Usar sistema atual sem quantitativos** (funcional agora)
2. ⏳ Coletar 10-20 PDFs representativos
3. ⏳ Analisar padrões comuns
4. ⏳ Decidir abordagem (custom parser vs hi_res vs manual)
5. ⏳ Implementar fase por fase

---

**📌 Este documento é um guia para implementação futura. O sistema atual está funcional e pronto para uso!**

