# Notas de Instalação

## ✅ Problema Resolvido: PyMuPDF

### O Problema Original
Durante a instalação dos requirements, o PyMuPDF tentava compilar do código fonte e falhava porque o compilador C++ (`g++`) não estava instalado:

```
/bin/sh: linha 1: g++: comando não encontrado
make: *** Error 127
```

### A Solução

**Opção 1: Usar wheel pré-compilado (Implementada)**
```bash
pip install --upgrade pip setuptools wheel
pip install pymupdf --no-build-isolation
# Instalar outras dependências
pip install fastapi uvicorn[standard] python-multipart pydantic pydantic-settings openai Pillow python-dotenv
```

**Opção 2: Instalar ferramentas de compilação (Alternativa)**
Se você preferir compilar do código fonte no futuro:
```bash
sudo dnf install gcc gcc-c++ python3-devel
pip install -r requirements.txt
```

## ✅ Status Atual

**Versões Instaladas:**
- ✅ pymupdf: 1.26.5 (wheel pré-compilado)
- ✅ fastapi: 0.119.1
- ✅ uvicorn: 0.38.0
- ✅ pydantic: 2.12.3
- ✅ openai: 2.6.0
- ✅ Pillow: 12.0.0
- ✅ Todas as dependências estão funcionando!

## 🚀 Próximos Passos

1. **Configure sua chave OpenAI:**
   ```bash
   echo 'OPENAI_API_KEY=sua_chave_aqui' > .env
   ```

2. **Edite os arquivos de contexto:**
   - `context_files/abnt_rules.txt` - Adicione regras ABNT
   - `context_files/client_template.txt` - Customize o template

3. **Inicie o servidor:**
   ```bash
   ./start.sh
   # ou
   source venv/bin/activate
   python -m app.main
   ```

4. **Teste a API:**
   - Swagger UI: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## 📦 Dependências Opcionais Removidas

Para evitar problemas de compilação, as seguintes dependências foram comentadas/removidas:
- `pytesseract` - Requer Tesseract OCR instalado no sistema
- `opencv-python` - Opcional, pode causar conflitos de compilação

Se você precisar dessas funcionalidades no futuro:
```bash
# Para Tesseract OCR
sudo dnf install tesseract tesseract-langpack-por
pip install pytesseract

# Para OpenCV
pip install opencv-python-headless  # Versão sem GUI, mais leve
```

## 💡 Dicas

- Use sempre o ambiente virtual: `source venv/bin/activate`
- Para atualizar dependências: `pip install --upgrade -r requirements.txt`
- O sistema funciona completamente sem OCR/OpenCV para PDFs com texto extraível
- A análise de imagens será implementada futuramente quando necessário

---

**Data da instalação:** 2025-10-23
**Sistema:** Fedora 42 (Python 3.13)

