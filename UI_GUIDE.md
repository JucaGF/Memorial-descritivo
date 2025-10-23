# Interface Gráfica - Memorial Automator

## 🎨 Visão Geral

A interface web do Memorial Automator foi projetada com foco em **usabilidade**, **modernidade** e **responsividade**. Ela oferece uma experiência intuitiva para gerar memoriais descritivos a partir de PDFs.

## 🌟 Características da Interface

### Design Moderno
- **Gradientes suaves** e cores vibrantes
- **Animações fluidas** para feedback visual
- **Sombras e elevações** para profundidade
- **Tipografia clara** e legível
- **Ícones intuitivos** (Font Awesome)

### Responsividade
- ✅ **Desktop** (1920px+)
- ✅ **Laptop** (1024px+)
- ✅ **Tablet** (768px+)
- ✅ **Mobile** (320px+)

### Funcionalidades

#### 1. Upload de Arquivo
- **Drag & Drop**: Arraste o PDF diretamente
- **Click to Select**: Clique para abrir o seletor de arquivos
- **Validação**: Apenas PDF, máximo 50MB
- **Feedback Visual**: Animação ao arrastar

#### 2. Configurações
- **Template do Cliente**: Selecione o template específico
- **Análise de Imagens**: Ative análise multimodal (em desenvolvimento)
- **Instruções Customizadas**: Adicione requisitos específicos

#### 3. Processamento
- **Barra de Progresso**: Acompanhe o processamento
- **Steps Visuais**: 5 etapas claramente indicadas
  1. Upload
  2. Extração
  3. Análise IA
  4. Redação
  5. Revisão
- **Status em Tempo Real**: Mensagens de status

#### 4. Resultados
- **Estatísticas**: Páginas, tempo, projeto, área
- **Avisos**: Alertas importantes do processamento
- **Preview do Memorial**: Visualização completa
- **Ações**:
  - 📋 Copiar para clipboard
  - 💾 Download como TXT
  - 📄 Download como JSON (dados completos)

## 🎯 Como Usar

### Passo 1: Iniciar o Servidor

```bash
cd /home/joaquim/Projects/Memorial-descritivo
source venv/bin/activate
./start.sh
```

Ou manualmente:
```bash
python -m app.main
# ou
uvicorn app.main:app --reload
```

### Passo 2: Acessar a Interface

Abra seu navegador e acesse:
```
http://localhost:8000
```

### Passo 3: Gerar Memorial

1. **Upload do PDF**
   - Arraste o arquivo ou clique para selecionar
   - Aguarde a validação

2. **Configure as Opções**
   - Selecione o template do cliente
   - Marque "incluir análise de imagens" se necessário
   - Adicione instruções customizadas (opcional)

3. **Clique em "Gerar Memorial Descritivo"**
   - Acompanhe o progresso
   - Aguarde o processamento (40-60s para PDFs normais)

4. **Visualize e Baixe**
   - Veja as estatísticas
   - Copie ou baixe o resultado
   - Gere outro memorial se necessário

## 📂 Estrutura dos Arquivos

```
static/
├── index.html          # Página principal
├── css/
│   └── style.css      # Estilos da interface
└── js/
    └── app.js         # Lógica e interações
```

## 🎨 Paleta de Cores

```css
--primary: #6366f1      /* Azul vibrante */
--primary-dark: #4f46e5 /* Azul escuro */
--primary-light: #818cf8 /* Azul claro */
--secondary: #f59e0b     /* Laranja */
--success: #10b981       /* Verde */
--error: #ef4444         /* Vermelho */
--warning: #f59e0b       /* Amarelo */
```

## 🔧 Personalização

### Alterar Cores

Edite as variáveis CSS em `static/css/style.css`:

```css
:root {
    --primary: #SEU_COR;
    /* ... outras cores ... */
}
```

### Adicionar Templates de Cliente

1. Edite `static/index.html`:
```html
<select id="client-id" class="form-control">
    <option value="default">Template Padrão</option>
    <option value="seu_cliente">Seu Cliente</option>
</select>
```

2. Crie o arquivo de template:
```bash
cp context_files/client_template.txt context_files/client_template_seu_cliente.txt
```

### Modificar Textos

Todos os textos estão em `static/index.html` e podem ser editados diretamente.

## 🚀 Funcionalidades Avançadas

### Feedback Visual

- **Loading Spinner**: Durante o processamento
- **Progress Bar**: Indica progresso
- **Step Indicators**: Mostra etapa atual
- **Animações**: Transições suaves

### Tratamento de Erros

- Validação de tipo de arquivo
- Validação de tamanho
- Mensagens de erro claras
- Opção de tentar novamente

### UX/UI Best Practices

✅ **Feedback Imediato**: Toda ação tem feedback visual
✅ **Estados Claros**: Loading, success, error bem definidos
✅ **Acessibilidade**: Cores com contraste adequado
✅ **Mobile-First**: Design responsivo
✅ **Performance**: Otimizado para carregamento rápido

## 🌐 Navegação

### Menu Principal
- **Novo Memorial**: Volta para a seção de upload
- **Sobre**: Informações sobre o sistema
- **API Docs**: Link para documentação da API

### Seções

1. **Hero**: Apresentação do sistema
2. **Upload**: Interface de upload e configuração
3. **Processing**: Feedback de processamento
4. **Results**: Exibição dos resultados
5. **About**: Como funciona
6. **Footer**: Links e informações

## 📱 Screenshots

### Desktop
![Desktop View](docs/screenshots/desktop.png)

### Mobile
![Mobile View](docs/screenshots/mobile.png)

### Processing
![Processing](docs/screenshots/processing.png)

### Results
![Results](docs/screenshots/results.png)

## 🐛 Troubleshooting

### Interface não carrega
```bash
# Verifique se o servidor está rodando
curl http://localhost:8000/health

# Verifique se os arquivos static existem
ls -la static/
```

### Erro ao fazer upload
- Verifique se o arquivo é PDF
- Verifique o tamanho (máx 50MB)
- Verifique a conexão com a API

### Processamento trava
- Verifique os logs do servidor
- Verifique se a chave OpenAI está configurada
- Verifique se há erros no console do navegador (F12)

## 🎓 Boas Práticas

### Para Usuários
1. Use PDFs com texto extraível (não escaneados)
2. Forneça instruções customizadas quando necessário
3. Escolha o template correto do cliente
4. Aguarde o processamento completo

### Para Desenvolvedores
1. Mantenha os arquivos organizados
2. Teste em diferentes navegadores
3. Teste responsividade
4. Otimize imagens e recursos
5. Documente mudanças

## 🔐 Segurança

- Arquivos são processados temporariamente
- Dados não são armazenados permanentemente
- Use HTTPS em produção
- Implemente autenticação se necessário

## 📈 Próximas Melhorias

- [ ] Upload múltiplo de arquivos
- [ ] Histórico de memoriais gerados
- [ ] Exportação para Word/PDF formatado
- [ ] Comparação de versões
- [ ] Colaboração em tempo real
- [ ] Templates visuais editáveis
- [ ] Preview de PDF integrado

## 💡 Dicas

- Use Ctrl+F para buscar no memorial gerado
- Copie seções específicas conforme necessário
- Baixe o JSON para análise detalhada
- Use instruções customizadas para melhor precisão

---

**Interface desenvolvida com ❤️ para Memorial Automator**
**Versão: 1.0.0**
**Data: 2025-10-23**

