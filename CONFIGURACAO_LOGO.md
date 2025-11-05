# 🏢 Configuração de Logo - Memorial Maker

## ✅ **O QUE MUDOU**

A logo TecPred agora é **incluída automaticamente** em todos os memoriais!

### **Antes:**
```
❌ Usuário tinha que fazer upload da logo toda vez
❌ UI tinha campo de upload separado
❌ CLI precisava do parâmetro --logo
```

### **Agora:**
```
✅ Logo configurada UMA VEZ
✅ Incluída automaticamente em TODOS os memoriais
✅ Não precisa mais fazer upload
✅ Sistema usa logo padrão do diretório assets/
```

---

## 📍 **ONDE COLOCAR A LOGO**

### **Localização:**
```
/home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png
```

### **Estrutura de diretórios:**
```
Memorial-descritivo/
├── assets/
│   ├── logo_tecpred.png          ← COLOQUE AQUI
│   ├── COMO_ADICIONAR_LOGO.md     ← Instruções detalhadas
│   └── README.md                  ← Info sobre assets
├── memorial_maker/
├── ui/
└── ...
```

---

## 🚀 **COMO ADICIONAR (3 Formas)**

### **Forma 1: Script Automático** ⭐ (Mais Fácil)

```bash
cd /home/joaquim/Projects/Memorial-descritivo
./add_logo.sh
```

O script vai perguntar:
1. Copiar de arquivo local? → Digite o caminho
2. Baixar da internet? → Digite a URL
3. Pronto! ✅

---

### **Forma 2: Copiar Manualmente**

```bash
# Copie sua logo para o diretório assets
cp /caminho/para/sua/logo.png \
   /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png

# Verifique
ls -lh /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png
```

---

### **Forma 3: Download Direto**

```bash
cd /home/joaquim/Projects/Memorial-descritivo/assets

# Opção A: wget
wget https://url-da-logo.com/logo.png -O logo_tecpred.png

# Opção B: curl
curl -o logo_tecpred.png https://url-da-logo.com/logo.png
```

---

## 🎨 **ESPECIFICAÇÕES DA LOGO**

### **Formato:**
- ✅ **PNG** (recomendado - fundo transparente)
- ✅ JPG/JPEG (alternativa)

### **Dimensões Ideais:**
- Largura: 400-600px
- Altura: 100-150px
- Proporção: Horizontal (4:1 ou 3:1)

### **Qualidade:**
- Resolução: 300 DPI
- Peso: < 500 KB
- Cores: RGB ou CMYK

---

## 🎯 **COMO FUNCIONA**

### **Interface Streamlit (UI):**
```python
# Antes - Upload manual
with col3:
    logo_file = st.file_uploader("PNG do logo", ...)

# Agora - Automático
st.info("🏢 Logo TecPred será incluído automaticamente")
# Sistema busca: assets/logo_tecpred.png
```

### **CLI:**
```bash
# Antes - Parâmetro obrigatório
memorial-make generate --logo=/caminho/logo.png ...

# Agora - Automático (parâmetro opcional)
memorial-make generate --pdf-dir=... --modelos-dir=...
# Sistema busca: assets/logo_tecpred.png automaticamente

# Ou com logo customizada (sobrescreve padrão)
memorial-make generate --logo=/outra/logo.png ...
```

---

## ✅ **VERIFICAR SE ESTÁ CONFIGURADO**

```bash
cd /home/joaquim/Projects/Memorial-descritivo

# Verifica se arquivo existe
if [ -f "assets/logo_tecpred.png" ]; then
    echo "✅ Logo configurada!"
    ls -lh assets/logo_tecpred.png
    file assets/logo_tecpred.png
else
    echo "❌ Logo não encontrada"
    echo "Execute: ./add_logo.sh"
fi
```

---

## 🎨 **ONDE A LOGO APARECE**

No memorial DOCX gerado:
- 📍 **Posição:** Cabeçalho da primeira página
- 📐 **Alinhamento:** Centralizado ou esquerda
- 📏 **Tamanho:** Ajustado automaticamente
- 🎨 **Estilo:** Mantém proporções originais

---

## 🔧 **TROUBLESHOOTING**

### **Problema: Logo não aparece**

```bash
# 1. Verifica se existe
ls -la assets/logo_tecpred.png

# 2. Verifica permissões
chmod 644 assets/logo_tecpred.png

# 3. Verifica tipo de arquivo
file assets/logo_tecpred.png
# Deve mostrar: PNG image data...
```

### **Problema: Logo distorcida**

Solução:
- Redimensione para 400x100px mantendo proporção
- Use ferramenta: ImageMagick, GIMP, ou online

```bash
# Com ImageMagick (se instalado)
convert assets/logo_tecpred.png \
  -resize 400x100 \
  -background transparent \
  -gravity center \
  -extent 400x100 \
  assets/logo_tecpred_resized.png

mv assets/logo_tecpred_resized.png assets/logo_tecpred.png
```

### **Problema: Arquivo muito grande**

```bash
# Otimizar PNG (reduz tamanho sem perder qualidade)
optipng assets/logo_tecpred.png

# Ou converter para JPG se não precisar transparência
convert assets/logo_tecpred.png \
  -quality 85 \
  assets/logo_tecpred.jpg
```

---

## 📚 **DOCUMENTAÇÃO RELACIONADA**

- `assets/COMO_ADICIONAR_LOGO.md` - Guia detalhado
- `assets/README.md` - Info sobre diretório assets
- `add_logo.sh` - Script de instalação
- `QUICK_START.md` - Guia de uso rápido

---

## 🎉 **VANTAGENS**

### **Para o Usuário:**
- ✅ Configura UMA VEZ, usa SEMPRE
- ✅ Não precisa procurar arquivo toda vez
- ✅ Interface mais limpa
- ✅ Menos passos para gerar memorial

### **Para o Sistema:**
- ✅ Logo padronizada em todos os documentos
- ✅ Consistência visual
- ✅ Menos erros (não esquece logo)
- ✅ Facilita automação

---

## ⚠️ **IMPORTANTE**

### **Se não adicionar a logo:**
- ⚠️ Memorial será gerado **SEM logo**
- ✅ Sistema **NÃO quebra**
- ✅ Funciona normalmente
- 💡 **Recomendação:** Adicione logo para documentos mais profissionais

### **Para usar logo diferente:**
- CLI: Use `--logo=/caminho/outra.png`
- UI: Não tem opção (sempre usa padrão)

---

## 🚀 **PRÓXIMO PASSO**

1. **Adicione a logo agora:**
   ```bash
   ./add_logo.sh
   ```

2. **Teste gerando um memorial:**
   ```bash
   streamlit run ui/app.py
   ```

3. **Verifique se logo aparece no DOCX gerado!**

---

**🎊 Logo configurada? Perfeito! Agora todos os memoriais terão a identidade TecPred!**

