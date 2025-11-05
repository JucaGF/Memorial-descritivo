# 🏢 Como Adicionar Logo TecPred

## 📍 Localização

A logo deve estar em:
```
/home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png
```

---

## 🖼️ Requisitos da Logo

### **Formato:**
- PNG (com fundo transparente - recomendado)
- JPG/JPEG (alternativa)

### **Dimensões Sugeridas:**
- **Largura:** 400-600px
- **Altura:** 100-150px
- **Proporção:** Horizontal (landscape)

### **Qualidade:**
- Resolução: 300 DPI (para impressão)
- Peso: < 500 KB

---

## 📥 Como Adicionar

### **Opção 1: Copiar Manualmente**

```bash
# Se você já tem a logo
cp /caminho/para/sua/logo.png /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png
```

### **Opção 2: Download (se disponível online)**

```bash
cd /home/joaquim/Projects/Memorial-descritivo/assets
wget https://www.tecpred.com.br/logo.png -O logo_tecpred.png

# Ou usando curl
curl -o logo_tecpred.png https://www.tecpred.com.br/logo.png
```

### **Opção 3: Converter de outro formato**

```bash
# Se você tem em JPG e quer converter para PNG
cd /home/joaquim/Projects/Memorial-descritivo/assets
convert logo_tecpred.jpg logo_tecpred.png

# Instalar ImageMagick se necessário:
# sudo dnf install ImageMagick
```

---

## ✅ Verificar se foi adicionada corretamente

```bash
cd /home/joaquim/Projects/Memorial-descritivo
ls -lh assets/logo_tecpred.png

# Deve mostrar algo como:
# -rw-r--r--. 1 joaquim joaquim 234K nov  5 09:00 assets/logo_tecpred.png
```

---

## 🎨 Como a Logo Aparece no Memorial

A logo será incluída automaticamente:
- **Localização:** Cabeçalho da primeira página
- **Posição:** Topo esquerdo ou centralizado
- **Tamanho:** Ajustado automaticamente para caber no cabeçalho

---

## 🔧 Testar

Após adicionar a logo, teste gerando um memorial:

```bash
# Via CLI
memorial-make generate \
  --pdf-dir=projetos_plantas \
  --modelos-dir=memorial \
  --out-dir=test_out

# Ou via UI
streamlit run ui/app.py
```

A logo deve aparecer no DOCX gerado!

---

## ⚠️ Troubleshooting

### **Logo não aparece no memorial**

```bash
# 1. Verifique se o arquivo existe
ls -la /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png

# 2. Verifique permissões
chmod 644 /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png

# 3. Verifique se é PNG válido
file /home/joaquim/Projects/Memorial-descritivo/assets/logo_tecpred.png
# Deve retornar: PNG image data...
```

### **Logo aparece distorcida**

- Verifique as proporções da imagem original
- Use dimensões sugeridas: 400x100px ou similar
- Mantenha proporção horizontal

### **Logo muito grande/pequena**

O sistema ajusta automaticamente, mas se não ficar bom:
- Reduza para 400px de largura
- Mantenha proporção original

---

## 📝 Exemplo Completo

```bash
# 1. Navegue até o diretório
cd /home/joaquim/Projects/Memorial-descritivo/assets

# 2. Copie sua logo (exemplo)
cp ~/Downloads/logo_tecpred.png .

# 3. Verifique
ls -lh logo_tecpred.png
file logo_tecpred.png

# 4. Teste gerando memorial
cd ..
streamlit run ui/app.py
```

---

## 🎯 **Pronto!**

Depois de adicionar a logo, ela será incluída automaticamente em **todos os memoriais gerados**, tanto pela UI quanto pelo CLI!

Não é mais necessário fazer upload toda vez! 🎉

