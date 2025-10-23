"""
Document Parser Service - Uses AI to analyze and structure extracted PDF data.
This is the "brain" of the extraction process, converting raw text into structured information.
"""

from typing import Dict, Any, List
import json
import logging
from openai import OpenAI
from app.core.config import get_settings
from app.models.schemas import StructuredProjectData

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Analyzes raw PDF data and structures it into meaningful project information.
    Uses multimodal AI to extract key information from text and images.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
    
    def structure_data(self, raw_data: Dict[str, Any]) -> StructuredProjectData:
        """
        Analyze raw PDF data and return structured project information.
        
        Args:
            raw_data: Dictionary containing 'text', 'images', and 'metadata' from PDF extraction
            
        Returns:
            StructuredProjectData object with extracted information
        """
        try:
            logger.info("Starting document parsing with AI")
            
            text = raw_data.get("text", "")
            metadata = raw_data.get("metadata", {})
            images = raw_data.get("images", [])
            
            # Build the prompt for the AI
            prompt = self._build_parsing_prompt(text, metadata)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.parser_temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            ai_response = response.choices[0].message.content
            structured_json = json.loads(ai_response)
            
            # Convert to StructuredProjectData
            structured_data = StructuredProjectData(**structured_json)
            
            logger.info("Successfully parsed document into structured data")
            return structured_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            raise Exception(f"AI returned invalid JSON: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}")
            raise Exception(f"Failed to parse document: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the document parser.
        """
        return """Você é um assistente especializado em engenharia e arquitetura.
Sua tarefa é analisar documentos técnicos de projetos e extrair informações estruturadas.

Você deve ser preciso e extrair apenas informações que estão claramente presentes no documento.
Se uma informação não estiver disponível, retorne null para aquele campo.

IMPORTANTE: Sua resposta DEVE ser um JSON válido com a seguinte estrutura:
{
    "project_name": "Nome do projeto (string ou null)",
    "client_name": "Nome do cliente/proprietário (string ou null)",
    "area_total_m2": "Área total em metros quadrados (número ou null)",
    "localizacao_obra": "Endereço/localização da obra (string ou null)",
    "lista_materiais": ["Lista de materiais mencionados (array de strings)"],
    "especificacoes_tecnicas": {"chave": "valor de especificações técnicas (objeto)"},
    "tipo_construcao": "Tipo de construção (residencial, comercial, etc.) (string ou null)",
    "responsavel_tecnico": "Nome do responsável técnico (string ou null)",
    "data_projeto": "Data do projeto (string ou null)",
    "numero_pavimentos": "Número de pavimentos (número ou null)",
    "observacoes": "Observações relevantes (string ou null)",
    "raw_data": {"outros_dados": "campos adicionais relevantes (objeto)"}
}"""
    
    def _build_parsing_prompt(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Build the parsing prompt for the AI.
        """
        # Truncate text if too long (keep first and last parts)
        max_chars = 15000
        if len(text) > max_chars:
            half = max_chars // 2
            text = text[:half] + "\n\n[... CONTEÚDO TRUNCADO ...]\n\n" + text[-half:]
        
        prompt = f"""Analise o seguinte documento técnico de projeto de engenharia/arquitetura.

**METADADOS DO DOCUMENTO:**
{json.dumps(metadata, indent=2, ensure_ascii=False)}

**TEXTO EXTRAÍDO DO DOCUMENTO:**
{text}

**SUA TAREFA:**
Extraia e estruture as informações-chave deste projeto em formato JSON.

Procure especialmente por:
1. Nome do projeto e do cliente
2. Área total construída (em m²)
3. Localização/endereço da obra
4. Lista de materiais especificados
5. Especificações técnicas importantes
6. Tipo de construção
7. Responsável técnico
8. Data do projeto
9. Número de pavimentos
10. Quaisquer observações relevantes

Retorne APENAS o JSON estruturado, sem texto adicional."""

        return prompt
    
    def structure_data_with_images(self, raw_data: Dict[str, Any]) -> StructuredProjectData:
        """
        Advanced parsing that includes image analysis (for future implementation).
        Currently falls back to text-only parsing.
        """
        # TODO: Implement multimodal parsing with image analysis
        # This would use GPT-4 Vision to analyze architectural plans
        logger.warning("Image analysis not yet implemented, using text-only parsing")
        return self.structure_data(raw_data)

