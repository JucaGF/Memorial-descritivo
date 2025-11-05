# Guia de Uso - Memorial Maker

## Visão Geral

O Memorial Maker gera automaticamente Memoriais Descritivos de Telecomunicações a partir de:
- **PDFs de projeto** (plantas, cortes, legendas)
- **Memoriais-modelo** (para estilo/estrutura)
- **Logo da empresa** (para capa)

## Fluxo de Trabalho

```
PDFs → Extração → Normalização → RAG → Geração LLM → DOCX
  ↓      ↓           ↓              ↓        ↓         ↓
Docling  Fallback  Canônico    Estilo   Seções    Memorial
         OCR       JSON/CSV    Modelos  1-7       Final
```

## Usando a CLI

### Comando Básico

```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --out-dir "./out"
```

### Com Todas as Opções

```bash
memorial-make \
  --pdf-dir "./projetos_plantas" \
  --modelos-dir "./memorial" \
  --logo "./tecpred_logo.png" \
  --out-dir "./output" \
  --dpi 300 \
  --llm-model "gpt-4o" \
  --parallel \
  --verbose
```

### Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--pdf-dir` | Diretório com PDFs (obrigatório) | - |
| `--modelos-dir` | Diretório com memoriais-modelo (obrigatório) | - |
| `--logo` | Caminho para logo (PNG) | None |
| `--out-dir` | Diretório de saída | `./out` |
| `--dpi` | DPI para renderização | `300` |
| `--llm-model` | Modelo LLM | `gpt-4o` |
| `--parallel` | Processar seções em paralelo | `True` |
| `--sequential` | Processar seções sequencialmente | `False` |
| `--verbose` | Modo verbose (debug) | `False` |

## Usando a UI (Streamlit)

### 1. Inicie a aplicação

```bash
streamlit run ui/app.py
```

### 2. Configure (sidebar)

- **OpenAI API Key**: Sua chave de API
- **Modelo LLM**: Escolha o modelo (gpt-4o recomendado)
- **DPI**: Qualidade de renderização (300 recomendado)
- **Processamento paralelo**: Ative para velocidade (requer quota)

### 3. Upload de Arquivos

- **PDFs de Projeto**: Arraste ou clique para selecionar
- **Memoriais-Modelo**: 1-2 arquivos DOC/DOCX de referência
- **Logo TecPred**: PNG/JPG do logo para a capa

### 4. Gerar Memorial

- Clique em "🎯 Gerar Memorial Descritivo"
- Aguarde o processamento (pode levar 2-5 minutos)
- Baixe o DOCX gerado

### 5. Explorar Resultados

- **Prévia das Seções**: Visualize o conteúdo gerado
- **Dados Extraídos**: Veja CSVs com itens/pavimentos/serviços

## Estrutura dos PDFs de Entrada

### PDFs Esperados

1. **Plantas de pavimentos**
   - Subsolo, Térreo, Pavimentos tipo, Cobertura
   - Com símbolos de pontos (RJ-45, TV, etc.)
   - Legendas/simbologia

2. **Cortes esquemáticos**
   - Backbone vertical
   - Divisores de RF/ópticos
   - Caminhos de cabos

3. **Detalhes**
   - Sala técnica/monitoramento
   - Quadros de distribuição
   - Especificações de materiais

### Elementos Detectados

- **Pontos**: RJ-45, TV, interfone, Wi-Fi, câmeras
- **Cabos**: CAT-6, RG-06/U#90%, CCI-2
- **Divisores**: 1/2, 1/3, 1/4, 1/5
- **Infraestrutura**: Racks, quadros VDI, D.G., caixas
- **Medidas**: Alturas (H=), diâmetros (∅), polegadas
- **Carimbo**: Projeto, revisão, data, escala

## Memoriais-Modelo

### Propósito

Os memoriais-modelo servem **apenas** para:
- **Estilo de redação** (tom técnico)
- **Ordem das seções** (1-7, 4.1-4.5)
- **Estrutura dos parágrafos**
- **Terminologia padrão**

⚠️ **NÃO** são usados para:
- Quantidades (números)
- Medidas específicas
- Dados do projeto

### Estrutura Esperada

Os modelos devem ter as 7 seções:
1. Introdução
2. Dados da Obra
3. Normas Técnicas
4. Serviços Contemplados
   - 4.1 Voz
   - 4.2 Dados
   - 4.3 Vídeo
   - 4.4 Intercomunicação
   - 4.5 Monitoramento
5. Sala de Monitoramento (ER/EF)
6. Elementos Passivos e Ativos
7. Testes e Aceitação

## Interpretando Saídas

### JSON Mestre (`mestre.json`)

```json
{
  "obra": {
    "construtora": "...",
    "empreendimento": "...",
    "endereco": "...",
    "pavimentos": ["Subsolo", "Térreo", "1º", ...]
  },
  "servicos": ["voz", "dados", "video", ...],
  "itens": [
    {
      "pavimento": "8º",
      "tipo": "point_rj45",
      "quantidade": 10,
      "altura_m": 1.40,
      "cabos": ["cat6"]
    }
  ],
  "salas_tecnicas": [...]
}
```

### CSVs

#### `itens_por_pavimento.csv`
| pavimento | tipo | quantidade | altura_m | cabos | divisor |
|-----------|------|------------|----------|-------|---------|
| Térreo | point_rj45 | 10 | 1.40 | ['cat6'] | - |
| 8º | cam_bullet | 2 | 3.00 | ['cat6'] | - |

#### `totais_por_servico.csv`
| servico | total |
|---------|-------|
| dados | 45 |
| video | 23 |
| monitoramento | 8 |

### Memorial DOCX

O documento final contém:
- **Capa** com logo e dados do projeto
- **7 seções** estruturadas e numeradas
- **Texto gerado por LLM** baseado em dados reais
- **Formatação profissional** (Arial, estilos consistentes)

## Dicas de Uso

### Para Melhores Resultados

1. **PDFs de qualidade**: Preferencialmente nativos (não escaneados)
2. **Legendas claras**: Com símbolos e descrições
3. **Carimbos completos**: Todos os campos preenchidos
4. **Modelos consistentes**: Mesma estrutura e terminologia
5. **Logo em alta resolução**: PNG com fundo transparente

### Ajustes de Qualidade

**DPI mais alto** (400-600):
- ✅ Melhora OCR de textos pequenos
- ❌ Processamento mais lento

**Processamento paralelo**:
- ✅ 3-5x mais rápido
- ❌ Requer quota maior da API

**Modelo LLM**:
- `gpt-4o`: Melhor qualidade, mais caro
- `gpt-4o-mini`: Bom custo-benefício
- `gpt-3.5-turbo`: Mais rápido, qualidade ok

### Otimização de Custos

1. Use `gpt-4o-mini` para testes
2. Ative processamento sequencial se quota baixa
3. Reduza DPI para PDFs de boa qualidade (200)
4. Use poucos modelos (1-2 suficientes para RAG)

## Solução de Problemas Comuns

### "Nenhum item extraído"

- Verifique se PDFs têm texto (não são só imagens)
- Aumente DPI para 400-600
- Confira se legendas/símbolos estão legíveis

### "Seção vazia no memorial"

- Normal se o dado não existe nos PDFs
- Verifique JSON mestre: campo está presente?
- Se sim, pode ser filtro de contexto muito restritivo

### "Números inventados"

- ⚠️ Isso **não deveria** acontecer
- Verifique temperatura do LLM (deve ser 0.0)
- Reporte como bug

### "Estilo diferente dos modelos"

- Modelos indexados corretamente?
- Tente com 2-3 modelos similares
- Verifique seções nos modelos (1-7 presentes?)

## Limitações Conhecidas

1. **OCR**: Pode falhar em PDFs muito complexos ou baixa qualidade
2. **Tabelas**: Detecção não é 100% confiável
3. **Símbolos customizados**: Pode não reconhecer símbolos muito específicos
4. **Multidioma**: Otimizado para PT-BR
5. **Grandes projetos**: >50 páginas podem ser lentos

## Roadmap Futuro

- [ ] Suporte a planilhas XLSX de quantitativos
- [ ] Extração de imagens/fotos dos PDFs
- [ ] Geração de diagramas de blocos
- [ ] Exportação para PDF (além de DOCX)
- [ ] Interface web (além de Streamlit local)
- [ ] Batch processing de múltiplos projetos

## Suporte

- **Documentação**: `README.md`, `INSTALL.md`, `USAGE.md`
- **Exemplos**: Veja PDFs em `projetos_plantas/`
- **Issues**: Reporte bugs/sugestões no repositório






