# Exemplos de Uso - Memorial Automator

Este documento contém exemplos práticos de como usar o sistema.

## 📚 Índice

1. [Exemplos via cURL](#exemplos-via-curl)
2. [Exemplos via Python](#exemplos-via-python)
3. [Exemplos via JavaScript](#exemplos-via-javascript)
4. [Exemplos de Responses](#exemplos-de-responses)

---

## Exemplos via cURL

### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-23T15:30:00.000000"
}
```

### 2. Gerar Memorial (Básico)

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/projeto.pdf"
```

### 3. Gerar Memorial com Cliente Específico

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/projeto.pdf" \
  -F "client_id=construtora_abc"
```

### 4. Gerar Memorial com Análise de Imagens

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/projeto.pdf" \
  -F "include_images=true"
```

### 5. Gerar Memorial com Instruções Customizadas

```bash
curl -X POST "http://localhost:8000/api/v1/generate_memorial" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/projeto.pdf" \
  -F "client_id=default" \
  -F "custom_instructions=Dar ênfase especial nas especificações de sustentabilidade e eficiência energética"
```

---

## Exemplos via Python

### 1. Exemplo Básico

```python
import requests

url = "http://localhost:8000/api/v1/generate_memorial"

# Abrir o arquivo PDF
with open("projeto.pdf", "rb") as pdf_file:
    files = {"file": pdf_file}
    response = requests.post(url, files=files)

# Verificar resposta
if response.status_code == 200:
    result = response.json()
    print("Memorial gerado com sucesso!")
    print(f"Páginas processadas: {result['pages_processed']}")
    print(f"Tempo de processamento: {result['processing_time_seconds']}s")
    print("\nMemorial:")
    print(result['memorial_text'])
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

### 2. Exemplo Completo com Tratamento de Erros

```python
import requests
from pathlib import Path
import json


class MemorialAutomatorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def health_check(self):
        """Verifica se a API está online"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API não está respondendo: {e}")
            return None
    
    def generate_memorial(
        self,
        pdf_path,
        client_id="default",
        include_images=False,
        custom_instructions=None,
        timeout=300
    ):
        """
        Gera um memorial descritivo a partir de um PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            client_id: ID do cliente (para templates específicos)
            include_images: Se deve incluir análise de imagens
            custom_instructions: Instruções customizadas adicionais
            timeout: Timeout em segundos (padrão: 5 minutos)
        
        Returns:
            dict: Resposta da API com o memorial gerado
        """
        # Validar arquivo
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        if pdf_file.suffix.lower() != '.pdf':
            raise ValueError("Arquivo deve ser um PDF")
        
        # Preparar request
        url = f"{self.api_url}/generate_memorial"
        
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            data = {
                'client_id': client_id,
                'include_images': str(include_images).lower()
            }
            
            if custom_instructions:
                data['custom_instructions'] = custom_instructions
            
            print(f"📤 Enviando {pdf_file.name}...")
            print(f"   Cliente: {client_id}")
            print(f"   Análise de imagens: {include_images}")
            
            try:
                response = requests.post(
                    url,
                    files=files,
                    data=data,
                    timeout=timeout
                )
                response.raise_for_status()
                
                result = response.json()
                print(f"✅ Memorial gerado com sucesso!")
                
                return result
                
            except requests.exceptions.Timeout:
                raise TimeoutError(
                    f"Processamento excedeu o timeout de {timeout}s"
                )
            except requests.exceptions.HTTPError as e:
                error_detail = "Desconhecido"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', str(e))
                except:
                    pass
                raise Exception(f"Erro na API: {error_detail}")
    
    def save_memorial(self, memorial_text, output_path):
        """Salva o memorial em um arquivo"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(memorial_text)
        print(f"💾 Memorial salvo em: {output_path}")


# Exemplo de uso
if __name__ == "__main__":
    client = MemorialAutomatorClient()
    
    # Verificar se API está online
    health = client.health_check()
    if not health:
        print("❌ API não está respondendo. Inicie o servidor primeiro.")
        exit(1)
    
    print(f"✅ API online - Version: {health['version']}\n")
    
    # Gerar memorial
    try:
        result = client.generate_memorial(
            pdf_path="projeto_exemplo.pdf",
            client_id="default",
            include_images=False,
            custom_instructions="Dar ênfase em aspectos de sustentabilidade"
        )
        
        # Exibir informações
        print(f"\n📊 Informações do Processamento:")
        print(f"   Páginas: {result['pages_processed']}")
        print(f"   Tempo: {result['processing_time_seconds']}s")
        
        if result.get('warnings'):
            print(f"   ⚠️  Avisos: {', '.join(result['warnings'])}")
        
        # Exibir dados estruturados
        if result.get('structured_data'):
            print(f"\n📋 Dados Extraídos:")
            data = result['structured_data']
            print(f"   Projeto: {data.get('project_name', 'N/A')}")
            print(f"   Cliente: {data.get('client_name', 'N/A')}")
            print(f"   Área: {data.get('area_total_m2', 'N/A')} m²")
            print(f"   Localização: {data.get('localizacao_obra', 'N/A')}")
        
        # Salvar memorial
        client.save_memorial(
            result['memorial_text'],
            "memorial_descritivo_final.txt"
        )
        
        # Também salvar em JSON para referência
        with open("memorial_completo.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Dados completos salvos em: memorial_completo.json")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        exit(1)
```

### 3. Exemplo Assíncrono (async/await)

```python
import aiohttp
import asyncio
from pathlib import Path


async def generate_memorial_async(pdf_path: str):
    """Versão assíncrona da geração de memorial"""
    url = "http://localhost:8000/api/v1/generate_memorial"
    
    async with aiohttp.ClientSession() as session:
        with open(pdf_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file',
                          f,
                          filename=Path(pdf_path).name,
                          content_type='application/pdf')
            data.add_field('client_id', 'default')
            
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error = await response.text()
                    raise Exception(f"Erro {response.status}: {error}")


async def process_multiple_pdfs(pdf_paths: list):
    """Processa múltiplos PDFs em paralelo"""
    tasks = [generate_memorial_async(path) for path in pdf_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


# Exemplo de uso
if __name__ == "__main__":
    # Processar um único PDF
    result = asyncio.run(generate_memorial_async("projeto1.pdf"))
    print(result['memorial_text'])
    
    # Processar múltiplos PDFs em paralelo
    pdfs = ["projeto1.pdf", "projeto2.pdf", "projeto3.pdf"]
    results = asyncio.run(process_multiple_pdfs(pdfs))
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Erro no PDF {i+1}: {result}")
        else:
            print(f"✅ PDF {i+1} processado com sucesso")
```

---

## Exemplos via JavaScript

### 1. Exemplo com Fetch API

```javascript
async function generateMemorial(pdfFile) {
    const formData = new FormData();
    formData.append('file', pdfFile);
    formData.append('client_id', 'default');
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/generate_memorial', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Memorial gerado:', result);
        return result;
        
    } catch (error) {
        console.error('Erro:', error);
        throw error;
    }
}

// Uso com input de arquivo HTML
document.getElementById('pdfInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await generateMemorial(file);
        document.getElementById('output').textContent = result.memorial_text;
    }
});
```

### 2. Exemplo com Axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function generateMemorial(pdfPath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(pdfPath));
    form.append('client_id', 'default');
    form.append('include_images', 'false');
    
    try {
        const response = await axios.post(
            'http://localhost:8000/api/v1/generate_memorial',
            form,
            {
                headers: form.getHeaders(),
                timeout: 300000 // 5 minutos
            }
        );
        
        console.log('✅ Memorial gerado com sucesso!');
        console.log(`Páginas: ${response.data.pages_processed}`);
        console.log(`Tempo: ${response.data.processing_time_seconds}s`);
        
        // Salvar memorial em arquivo
        fs.writeFileSync('memorial_output.txt', response.data.memorial_text);
        console.log('💾 Memorial salvo em memorial_output.txt');
        
        return response.data;
        
    } catch (error) {
        if (error.response) {
            console.error('❌ Erro da API:', error.response.data);
        } else {
            console.error('❌ Erro:', error.message);
        }
        throw error;
    }
}

// Uso
generateMemorial('./projeto.pdf')
    .then(result => {
        console.log('Processo concluído!');
    })
    .catch(err => {
        console.error('Falha no processamento');
    });
```

---

## Exemplos de Responses

### Response de Sucesso

```json
{
  "memorial_text": "MEMORIAL DESCRITIVO\n\n1. IDENTIFICAÇÃO DO EMPREENDIMENTO\n\n**Projeto:** Edifício Residencial Solar\n**Cliente/Proprietário:** Construtora ABC Ltda\n**Localização:** Rua das Flores, 123 - Centro - São Paulo/SP\n...",
  "structured_data": {
    "project_name": "Edifício Residencial Solar",
    "client_name": "Construtora ABC Ltda",
    "area_total_m2": 1250.5,
    "localizacao_obra": "Rua das Flores, 123 - Centro - São Paulo/SP",
    "lista_materiais": [
      "Concreto fck 30 MPa",
      "Aço CA-50",
      "Blocos cerâmicos 14x19x29cm",
      "Telhas cerâmicas"
    ],
    "especificacoes_tecnicas": {
      "estrutura": "Concreto armado",
      "fundacao": "Sapatas isoladas",
      "cobertura": "Telha cerâmica sobre estrutura de madeira"
    },
    "tipo_construcao": "Residencial multifamiliar",
    "responsavel_tecnico": "Eng. João Silva",
    "data_projeto": "2025-10-01",
    "numero_pavimentos": 8,
    "observacoes": "Projeto atende NBR 15575 - Desempenho de edificações"
  },
  "processing_time_seconds": 42.5,
  "pages_processed": 15,
  "warnings": []
}
```

### Response com Warnings

```json
{
  "memorial_text": "...",
  "structured_data": {...},
  "processing_time_seconds": 78.3,
  "pages_processed": 250,
  "warnings": [
    "PDF has 250 pages, which exceeds recommended limit"
  ]
}
```

### Response de Erro (400 - Bad Request)

```json
{
  "detail": "Only PDF files are supported",
  "error_code": "400",
  "timestamp": "2025-10-23T15:30:00.000000"
}
```

### Response de Erro (500 - Internal Server Error)

```json
{
  "detail": "Failed to generate memorial: OpenAI API key not configured",
  "error_code": "500",
  "timestamp": "2025-10-23T15:30:00.000000"
}
```

---

## Integração com Sistemas Existentes

### Exemplo: Integração com Sistema de Gerenciamento de Projetos

```python
class ProjetoManager:
    def __init__(self):
        self.memorial_client = MemorialAutomatorClient()
    
    def processar_projeto(self, projeto_id, pdf_path):
        """
        Processa um projeto e salva o memorial no banco de dados
        """
        # Gerar memorial
        result = self.memorial_client.generate_memorial(
            pdf_path=pdf_path,
            client_id=self.get_client_id(projeto_id)
        )
        
        # Salvar no banco de dados
        self.save_to_database(
            projeto_id=projeto_id,
            memorial_text=result['memorial_text'],
            structured_data=result['structured_data'],
            processing_info={
                'pages': result['pages_processed'],
                'time': result['processing_time_seconds']
            }
        )
        
        # Enviar notificação
        self.notify_stakeholders(projeto_id, "Memorial gerado com sucesso")
        
        return result
```

---

## Dicas e Best Practices

### 1. Timeout Adequado
Para PDFs grandes, aumente o timeout:
```python
response = requests.post(url, files=files, timeout=600)  # 10 minutos
```

### 2. Tratamento de Erros Robusto
Sempre verifique o status code e trate erros apropriadamente.

### 3. Validação de Arquivo
Valide o arquivo antes de enviar:
```python
if Path(pdf_path).stat().st_size > 50 * 1024 * 1024:  # 50MB
    raise ValueError("Arquivo muito grande")
```

### 4. Retry Logic
Implemente retry para falhas transitórias:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_with_retry(pdf_path):
    return generate_memorial(pdf_path)
```

### 5. Logging
Sempre faça log das operações:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Processando {pdf_path}")
logger.info(f"Memorial gerado em {result['processing_time_seconds']}s")
```

---

Para mais exemplos, consulte a documentação interativa em:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

