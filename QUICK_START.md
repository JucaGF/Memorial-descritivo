# 🚀 Quick Start - Gerar Memorial Agora

**Sistema pronto para uso!** (Versão sem quantitativos detalhados)

---

## 📋 **Passo a Passo**

### 1. **Limpe o cache e ative o ambiente:**
```bash
cd /home/joaquim/Projects/Memorial-descritivo
rm -rf /tmp/memorial_maker/*
source venv/bin/activate
```

### 2. **Execute a UI:**
```bash
streamlit run ui/app.py
```

### 3. **Acesse no navegador:**
```
http://localhost:8501
```

### 4. **Na interface:**

#### **Barra Lateral (⚙️ Configurações):**
1. ✅ Adicione sua **OpenAI API Key**
2. ✅ Modelo: Deixe **gpt-5** (padrão)
3. ✅ DPI: 300 (padrão)
4. ✅ Processamento paralelo: ✓ (marcado)

#### **Área Principal:**

**1. Upload de Arquivos:**
- 📄 **PDFs de Projeto:** Upload dos 5 PDFs de `projetos_plantas/`
- 📋 **Memoriais-Modelo:** Upload dos `.docx` de `memorial/` (opcional)
- 🖼️ **Logo TecPred:** Upload do logo (opcional)

**2. Gerar Memorial:**
- Clique no botão **🎯 Gerar Memorial Descritivo**
- ⏳ Aguarde ~2-5 minutos (extração + geração)

**3. Download:**
- 📥 Baixe o arquivo `.docx` gerado
- 👁️ Veja prévia das seções
- 📊 (CSVs estarão vazios por enquanto - normal)

---

## 📝 **O QUE O MEMORIAL VAI TER:**

### ✅ **Seções Completas:**
1. **Introdução** - Escopo e objetivo do projeto
2. **Dados da Obra** - Informações do empreendimento
3. **Normas Técnicas** - NBR 14565, EIA/TIA, etc.
4. **Serviços Contemplados:**
   - 4.1. Voz (PABX, telefonia)
   - 4.2. Dados (rede estruturada, CAT-6, Wi-Fi)
   - 4.3. Vídeo (TV coletiva, CFTV)
   - 4.4. Intercomunicação (interfones)
   - 4.5. Monitoramento (CFTV, câmeras)
5. **Sala de Monitoramento** - ER, rack, requisitos
6. **Elementos Passivos e Ativos** - Materiais, cabeamento
7. **Testes e Aceitação** - Procedimentos, certificação

### ⚠️ **Não vai ter (por enquanto):**
- ❌ Tabelas de quantitativos detalhados
- ❌ CSVs com totalizações
- ❌ Levantamento exato de materiais

### ✅ **Mas vai ter:**
- ✅ Descrição técnica completa dos sistemas
- ✅ Especificações de materiais e cabos
- ✅ Metodologias e procedimentos
- ✅ Texto profissional gerado por GPT-5
- ✅ Estilo baseado nos memoriais-modelo

---

## 💡 **DICAS:**

### **Se der erro:**
1. **Verifique API Key** - Tem que ser válida e com créditos
2. **Limpe cache** - `rm -rf /tmp/memorial_maker/*`
3. **Reinicie Streamlit** - Ctrl+C e execute novamente
4. **Teste com 1 PDF primeiro** - Mais rápido para debug

### **Para melhor qualidade:**
1. ✅ Faça upload dos memoriais-modelo (fornece exemplos de estilo)
2. ✅ Use processamento paralelo (mais rápido)
3. ✅ Verifique se API key tem acesso ao GPT-5

### **Estratégias de extração:**
- **Atual:** `fast` - Rápido, bom para texto
- **Futura:** `hi_res` - Lento, detecta tabelas (para quantitativos)

---

## 🔮 **PRÓXIMOS PASSOS (Futuro)**

Implementar extração de quantitativos:

### **Fase 1: Análise**
- [ ] Mapear formato exato das tabelas nos PDFs
- [ ] Identificar padrões de legendas
- [ ] Definir estrutura de dados esperada

### **Fase 2: Parser Customizado**
- [ ] Criar regex/parser para formato específico dos PDFs
- [ ] Extrair: item, descrição, unidade, quantidade, pavimento
- [ ] Validar extração em PDFs de teste

### **Fase 3: Normalização**
- [ ] Mapear variações de nomes (CAT-6, cat6, CAT 6)
- [ ] Consolidar por tipo de serviço
- [ ] Totalizar por pavimento e geral

### **Fase 4: Integração**
- [ ] Gerar CSVs corretos
- [ ] Adicionar tabelas ao DOCX
- [ ] Incluir quantitativos nas seções GPT-5

---

## 🎯 **RESULTADO ESPERADO AGORA:**

```
Memorial Descritivo de Telecomunicações

1. Introdução
   ✅ Texto técnico sobre escopo do projeto
   
2. Dados da Obra
   ✅ Nome do empreendimento: MGAMAK
   ✅ Localização extraída dos PDFs
   
3. Normas Técnicas
   ✅ Lista de normas aplicáveis
   
4. Serviços Contemplados
   ✅ Descrição de cada sistema:
      - Cabeamento estruturado CAT-6
      - Rede Wi-Fi
      - TV coletiva via cabo coaxial
      - Sistema de interfonia
      - CFTV e monitoramento
   
5-7. Demais seções técnicas
   ✅ Especificações completas
   ✅ Metodologias
   ✅ Procedimentos de teste
```

---

## 🆘 **SE ALGO DER ERRADO:**

### **Erro de API Key:**
```
Error code: 401 - Invalid API key
```
**Solução:** Verifique se copiou a key correta

### **Erro de modelo:**
```
Model gpt-5 does not exist
```
**Solução:** Use `gpt-4o` se GPT-5 não estiver disponível

### **Timeout:**
```
Request timed out
```
**Solução:** Reduza número de PDFs ou use `--sequential`

### **Cache com arquivos antigos:**
```
Erro ao carregar .doc
```
**Solução:** `rm -rf /tmp/memorial_maker/*`

---

## 📞 **LOGS E DEBUG:**

Arquivos importantes:
```
out/logs/execution.log           - Log da execução CLI
/tmp/memorial_maker/[session]/   - Arquivos temporários UI
out/extraido/                    - JSONs e CSVs extraídos
out/memorial/                    - DOCX gerado
```

Ativar modo verbose:
```bash
memorial-make generate --pdf-dir=... --modelos-dir=... -v
```

---

**🎉 AGORA É SÓ EXECUTAR E GERAR SEU MEMORIAL!**

Qualquer problema, consulte:
- `TROUBLESHOOTING.md` - Problemas comuns
- `MIGRATION_NOTES.md` - Detalhes técnicos
- `README.md` - Documentação geral

