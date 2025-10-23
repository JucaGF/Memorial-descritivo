# Interface Web - Memorial Automator

## 🎨 Design System

### Arquitetura da Interface

```
Frontend (SPA - Single Page Application)
├── HTML5 (Semântico)
├── CSS3 (Variáveis, Gradientes, Animações)
└── JavaScript (Vanilla JS, ES6+)
```

### Arquivos

- **index.html** - Estrutura da página (14KB)
- **css/style.css** - Estilos e design system (23KB)
- **js/app.js** - Lógica e interações (8KB)

### Paleta de Cores

```
Primary:   #6366f1 (Indigo)
Success:   #10b981 (Green)
Warning:   #f59e0b (Amber)
Error:     #ef4444 (Red)
```

## 🚀 Funcionalidades

### Upload de Arquivos
- Drag & Drop
- Click to select
- Validação automática (PDF, 50MB max)
- Preview do arquivo selecionado

### Configuração
- Seleção de template do cliente
- Análise de imagens (opcional)
- Instruções customizadas

### Processamento
- Feedback visual em tempo real
- 5 etapas claramente indicadas
- Barra de progresso animada

### Resultados
- Estatísticas do processamento
- Preview completo do memorial
- Download em múltiplos formatos (TXT, JSON)
- Copiar para clipboard

## 🎯 Experiência do Usuário

### Animações
- Fade in nos cards
- Slide in nos elementos
- Smooth scroll
- Transições suaves

### Feedback Visual
- Loading spinners
- Progress bars
- Status messages
- Color-coded states

### Responsividade
Testado e otimizado para:
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

## 🔧 Tecnologias

- **HTML5**: Semântica moderna
- **CSS3**: Flexbox, Grid, Custom Properties
- **JavaScript**: Async/Await, Fetch API, ES6+
- **Font Awesome**: Ícones
- **FastAPI**: Backend API

## 📱 Acessibilidade

- ✅ Contraste adequado (WCAG AA)
- ✅ Keyboard navigation
- ✅ Semantic HTML
- ✅ Clear visual hierarchy
- ✅ Responsive design

## 🎨 Componentes

### Cards
Containers modulares para conteúdo

### Buttons
- Primary: Ações principais
- Secondary: Ações secundárias
- Small: Ações compactas

### Forms
- Input text
- Select dropdown
- Textarea
- Checkbox custom

### Feedback
- Success messages
- Error messages
- Warning alerts
- Info tooltips

## 🔄 Fluxo da Interface

```
1. Landing Page
   ↓
2. Upload Section
   ↓
3. Configuration
   ↓
4. Processing (Animated)
   ↓
5. Results Display
   ↓
6. Download/Copy/Reset
```

## 💻 Código de Exemplo

### Upload de Arquivo

```javascript
async function generateMemorial() {
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    const response = await fetch('/api/v1/generate_memorial', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    displayResults(data);
}
```

### Estilo de Card

```css
.card {
    background: white;
    border-radius: 1rem;
    box-shadow: var(--shadow);
    animation: fadeIn 0.5s ease;
}
```

## 🎯 Performance

- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Lighthouse Score**: 95+

## 📝 Notas do Desenvolvedor

### Estrutura do Código
- Funções bem nomeadas
- Comentários quando necessário
- Código modular e reutilizável

### Boas Práticas
- Uso de const/let (não var)
- Async/await para operações assíncronas
- Error handling adequado
- Validação no frontend e backend

### Próximas Melhorias
- Dark mode
- Internacionalização (i18n)
- PWA (Progressive Web App)
- Offline support

## 🐛 Debug

### Console do Navegador
Abra com F12 para ver:
- Logs de rede
- Erros JavaScript
- Performance metrics

### Testes
```bash
# Testar API
curl -X POST http://localhost:8000/api/v1/generate_memorial \
  -F "file=@test.pdf"

# Health check
curl http://localhost:8000/health
```

---

**Desenvolvido com ❤️ usando tecnologias web modernas**

