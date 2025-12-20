# 📄 Memorial Maker

**Geração Inteligente de Memorial Descritivo de Telecomunicações com IA**

O **Memorial Maker** é um sistema avançado que automatiza a criação de Memoriais Descritivos para projetos de telecomunicações. Ele extrai dados técnicos de plantas e projetos (PDFs), utiliza RAG (Retrieval-Augmented Generation) para manter a consistência de estilo com memoriais anteriores e gera documentos profissionais em formato Word (.docx).

---

## ✨ Funcionalidades Principais

*   🔍 **Extração Técnica com Unstructured.io**: Extração precisa de textos e tabelas de PDFs, com suporte a OCR de alta qualidade para plantas escaneadas.
*   🏷️ **Detecção Automática de Carimbos**: Identifica informações críticas como nome do projeto, construtora, empreendimento e endereço diretamente das legendas dos desenhos.
*   🧠 **RAG de Estilo (FAISS + OpenAI)**: Indexa seus memoriais-modelo e recupera exemplos de escrita e estrutura para garantir que o novo memorial siga o padrão da sua empresa.
*   ⚡ **Geração Paralela com GPT-4**: Utiliza processamento assíncrono para gerar todas as seções do memorial simultaneamente, reduzindo drasticamente o tempo de espera.
*   📝 **Escrita Profissional em DOCX**: 
    - Capa personalizada com dados do projeto.
    - Sumário automático (TOC).
    - Cabeçalhos e rodapés de largura total (marca d'água/logo).
    - Estilos de títulos e corpo de texto padronizados (Arial).
*   🖥️ **Interface Streamlit**: Ambiente web amigável para upload de arquivos, configuração e download dos resultados.

---

## 🚀 Instalação e Setup

### 1. Requisitos
*   Python 3.10 ou superior.
*   Chave de API da OpenAI.

### 2. Preparação do Ambiente
```bash
# Clone o repositório e acesse a pasta
cd Memorial-descritivo

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale o pacote em modo editável
pip install -e .
```

### 3. Configuração (.env)
Crie um arquivo `.env` na raiz do projeto (use o `env.example` como base):
```bash
cp env.example .env
```
Edite o `.env` com suas configurações:
```bash
OPENAI_API_KEY=sk-proj-...
UNSTRUCTURED_STRATEGY=fast  # Use "hi_res" para PDFs escaneados ou com tabelas complexas
LLM_MODEL=gpt-4o-mini        # Ou "gpt-4o" para máxima qualidade
```

---

## 💻 Como Usar

### Interface Web (Recomendado)
```bash
streamlit run ui/app.py
```
1.  Acesse o link gerado (padrão: `http://localhost:8501`).
2.  Faça o upload dos **PDFs das plantas**.
3.  (Opcional) Faça o upload de **memoriais de referência** para o RAG.
4.  Clique em **"Gerar Memorial"** e aguarde o processo.
5.  Baixe o arquivo `.docx` final.

### Scripts de Teste e Diagnóstico
```bash
# Testar extração de dados
python test_extraction.py

# Gerar imagens de cabeçalho/rodapé em largura total
python prepare_header_footer_images.py
```

---

## 📁 Estrutura do Projeto

```text
Memorial-descritivo/
├── memorial_maker/          # 📦 Pacote principal
│   ├── extract/             # 🔍 Extração de dados (Unstructured)
│   ├── normalize/           # 🧹 Limpeza e estruturação de dados
│   ├── rag/                 # 🧠 Geração e Retrieval de Estilo
│   ├── writer/              # 📝 Escrita de DOCX e estilização
│   └── config.py            # ⚙️ Configurações centralizadas (Pydantic)
├── ui/                      # 🖥️ Interface Streamlit
├── assets/                  # 🎨 Logos, cabeçalhos e rodapés
├── memorial/                # 📂 Repositório de memoriais-modelo
├── projetos_plantas/        # 📂 PDFs de entrada para testes
├── out/                     # 📂 Arquivos gerados e JSONs de debug
└── pyproject.toml           # 📋 Definição do pacote e dependências
```

---

## 🔧 Configurações Avançadas

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `UNSTRUCTURED_STRATEGY` | Estratégia de extração (`fast`, `hi_res`, `ocr_only`) | `fast` |
| `EXTRACT_TABLES` | Tenta detectar e extrair tabelas estruturadas | `true` |
| `LLM_MODEL` | Modelo da OpenAI para geração | `gpt-4o-mini` |
| `PARALLEL_EXECUTION` | Executa a geração das seções em paralelo | `true` |

---

## 🛠️ Tecnologias Utilizadas

*   **[Unstructured.io](https://unstructured.io/)**: Motor principal de extração de dados de documentos.
*   **[LangChain](https://langchain.com/)**: Orquestração de LLM e RAG.
*   **[FAISS](https://github.com/facebookresearch/faiss)**: Busca vetorial para referências de estilo.
*   **[python-docx](https://python-docx.readthedocs.io/)**: Manipulação e criação de arquivos Word.
*   **[Streamlit](https://streamlit.io/)**: Interface de usuário reativa.

---

## 📝 Notas de Versão (Simplificação Recente)
Recentemente o projeto passou por uma grande limpeza para melhorar a manutenibilidade:
- Removidos múltiplos extratores redundantes, focando no poder do **Unstructured**.
- Redução de ~65% na complexidade do código.
- Instalação simplificada e setup mais rápido.

---

## 🐛 Solução de Problemas
- **Erro de Importação**: Certifique-se de que instalou com `pip install -e .`.
- **Extração Incompleta**: Altere `UNSTRUCTURED_STRATEGY` para `hi_res` no `.env`.
- **API OpenAI**: Verifique se sua chave possui créditos e acesso aos modelos configurados.
