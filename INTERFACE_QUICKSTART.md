# 🚀 Quick Start - Interface Web

## Iniciar em 3 Passos

### 1️⃣ Inicie o Servidor

```bash
cd /home/joaquim/Projects/Memorial-descritivo
source venv/bin/activate
./start.sh
```

Você verá:
```
🚀 Memorial Automator - Starting...
✅ Starting FastAPI server...
📖 API Documentation: http://localhost:8000/docs
```

### 2️⃣ Abra o Navegador

Acesse: **http://localhost:8000**

### 3️⃣ Use a Interface

1. **Arraste seu PDF** para a área de upload (ou clique para selecionar)
2. **Configure as opções** (template, instruções)
3. **Clique em "Gerar Memorial Descritivo"**
4. **Aguarde o processamento** (40-60 segundos)
5. **Baixe ou copie** o resultado!

---

## 📸 Preview Visual

### Tela Inicial
```
╔════════════════════════════════════════╗
║  Memorial Automator                    ║
║  ────────────────────────────────────  ║
║  Gere Memoriais Descritivos com IA    ║
╚════════════════════════════════════════╝

┌────────────────────────────────────────┐
│  📄 Upload do Projeto                  │
│                                        │
│    ┌──────────────────────────────┐   │
│    │                              │   │
│    │   📁 Arraste o PDF aqui      │   │
│    │   ou clique para selecionar  │   │
│    │                              │   │
│    │   Máximo 50MB • Apenas PDF   │   │
│    │                              │   │
│    └──────────────────────────────┘   │
│                                        │
│  ⚙️ Opções de Processamento            │
│  Cliente: [Template Padrão ▼]         │
│  □ Incluir análise de imagens          │
│  Instruções: [________________]        │
│                                        │
│      [✨ Gerar Memorial]               │
└────────────────────────────────────────┘
```

### Durante o Processamento
```
┌────────────────────────────────────────┐
│  Processando seu projeto...            │
│                                        │
│         ⟳ [Loading Spinner]            │
│                                        │
│  Extraindo dados do PDF...             │
│                                        │
│  ▓▓▓▓▓▓▓▓░░░░░░░░░░  60%              │
│                                        │
│  [✓] Upload                            │
│  [✓] Extração                          │
│  [●] Análise IA                        │
│  [ ] Redação                           │
│  [ ] Revisão                           │
└────────────────────────────────────────┘
```

### Resultados
```
┌────────────────────────────────────────┐
│  ✅ Memorial Gerado com Sucesso!       │
├────────────────────────────────────────┤
│  📊 Estatísticas                       │
│  ┌────────┬────────┬────────┬────────┐│
│  │ 📄 15  │ ⏱ 45s │ 🏗 Proj │ 📐 250m²││
│  │ Páginas│ Tempo  │ ABC    │ Área   ││
│  └────────┴────────┴────────┴────────┘│
│                                        │
│  📄 Memorial Descritivo                │
│  ┌────────────────────────────────┐   │
│  │ MEMORIAL DESCRITIVO            │   │
│  │                                │   │
│  │ 1. IDENTIFICAÇÃO               │   │
│  │ Projeto: Edifício ABC          │   │
│  │ Cliente: Construtora XYZ       │   │
│  │ ...                            │   │
│  └────────────────────────────────┘   │
│                                        │
│  [📋 Copiar] [💾 Download TXT] [📄 JSON] │
│                                        │
│      [🔄 Gerar Outro Memorial]         │
└────────────────────────────────────────┘
```

---

## 🎨 Recursos da Interface

### ✨ Animações Suaves
- Fade in nos elementos
- Transições fluidas
- Feedback visual imediato

### 🎯 Validação Inteligente
- Verifica tipo de arquivo
- Valida tamanho (max 50MB)
- Mensagens de erro claras

### 📱 Totalmente Responsivo
```
Desktop          Tablet           Mobile
┌─────────┐     ┌──────┐         ┌───┐
│         │     │      │         │   │
│  Full   │     │ Stack│         │ V │
│ Layout  │     │Layout│         │ E │
│         │     │      │         │ R │
└─────────┘     └──────┘         │ T │
                                 │   │
                                 └───┘
```

### 🚀 Performance
- Carregamento rápido
- Otimizado para todos os dispositivos
- Sem frameworks pesados

---

## 💡 Dicas de Uso

### Para Melhores Resultados

1. **Use PDFs de qualidade**
   - Texto extraível (não escaneado)
   - Bem formatado
   - Completo e legível

2. **Forneça Contexto**
   - Selecione o cliente correto
   - Use instruções customizadas
   - Seja específico nos requisitos

3. **Aguarde o Processamento**
   - Não feche a janela
   - Aguarde 40-60 segundos
   - Observe as etapas

### Atalhos do Teclado

- `Ctrl/Cmd + V` - Colar texto no campo de instruções
- `Ctrl/Cmd + C` - Copiar memorial (no preview)
- `Escape` - Cancelar upload (quando selecionado)

### Opções Avançadas

**Template do Cliente:**
- Selecione o template específico do seu cliente
- Cada cliente pode ter estrutura diferente
- Adicione novos templates em `context_files/`

**Análise de Imagens:**
- Em desenvolvimento
- Ativará análise multimodal
- Útil para plantas e diagramas

**Instruções Customizadas:**
```
Exemplos:
- "Dar ênfase em sustentabilidade"
- "Incluir detalhes de acabamento premium"
- "Foco em instalações elétricas"
- "Mencionar certificações ambientais"
```

---

## 🔧 Troubleshooting Rápido

### Problema: Interface não carrega
```bash
# Verificar se servidor está rodando
curl http://localhost:8000/health

# Reiniciar servidor
./start.sh
```

### Problema: Upload falha
- ✅ Verifique se é um PDF
- ✅ Verifique o tamanho (< 50MB)
- ✅ Verifique a conexão

### Problema: Processamento demora muito
- ⏱ PDFs grandes levam mais tempo
- ⏱ Primeira vez pode ser mais lenta
- ⏱ Verifique sua conexão com a OpenAI

### Problema: Resultado incompleto
- 📝 Verifique os arquivos de contexto
- 📝 Use instruções customizadas
- 📝 Tente um PDF mais completo

---

## 🎯 Próximos Passos

1. **Customize os Templates**
   ```bash
   nano context_files/client_template.txt
   ```

2. **Adicione Regras ABNT**
   ```bash
   nano context_files/abnt_rules.txt
   ```

3. **Explore a API**
   - Acesse: http://localhost:8000/docs
   - Teste os endpoints
   - Veja exemplos

4. **Leia a Documentação**
   - [UI_GUIDE.md](UI_GUIDE.md) - Guia completo da interface
   - [EXAMPLES.md](EXAMPLES.md) - Exemplos de código
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura do sistema

---

## ✅ Checklist de Uso

- [ ] Servidor está rodando
- [ ] Interface carregou corretamente
- [ ] PDF está pronto (< 50MB)
- [ ] Template do cliente selecionado
- [ ] Instruções adicionadas (opcional)
- [ ] Processamento iniciado
- [ ] Resultado visualizado
- [ ] Memorial baixado/copiado

---

**🎉 Pronto! Você está gerando memoriais com IA!**

Para suporte, veja os logs do servidor ou consulte a documentação completa.

