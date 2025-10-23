"""
Agent Service - Orchestrates the Writer and Reviewer AI agents.
These agents work together to create and refine the memorial descritivo.
"""

from typing import Dict, Any, Tuple
import logging
from pathlib import Path
from openai import OpenAI
from app.core.config import get_settings
from app.models.schemas import StructuredProjectData

logger = logging.getLogger(__name__)


class AgentService:
    """
    Manages the Writer and Reviewer agents for memorial generation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.context_dir = Path(self.settings.context_files_dir)
    
    def load_context_files(self, client_id: str = "default") -> Tuple[str, str]:
        """
        Load ABNT rules and client template from context files.
        
        Args:
            client_id: ID of the client (for client-specific templates)
            
        Returns:
            Tuple of (abnt_rules, client_template)
        """
        try:
            # Load ABNT rules
            abnt_file = self.context_dir / self.settings.abnt_rules_file
            if abnt_file.exists():
                with open(abnt_file, 'r', encoding='utf-8') as f:
                    abnt_rules = f.read()
            else:
                logger.warning(f"ABNT rules file not found: {abnt_file}")
                abnt_rules = "[ARQUIVO DE REGRAS ABNT NÃO ENCONTRADO]"
            
            # Load client template (try client-specific first, then default)
            template_file = self.context_dir / f"client_template_{client_id}.txt"
            if not template_file.exists():
                template_file = self.context_dir / self.settings.client_template_file
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    client_template = f.read()
            else:
                logger.warning(f"Client template file not found: {template_file}")
                client_template = "[ARQUIVO DE TEMPLATE DO CLIENTE NÃO ENCONTRADO]"
            
            logger.info(f"Loaded context files for client: {client_id}")
            return abnt_rules, client_template
            
        except Exception as e:
            logger.error(f"Error loading context files: {str(e)}")
            raise Exception(f"Failed to load context files: {str(e)}")
    
    def run_writer_agent(
        self,
        structured_data: StructuredProjectData,
        abnt_rules: str,
        client_template: str,
        custom_instructions: str = None
    ) -> str:
        """
        Run the Writer Agent to create the initial draft of the memorial.
        
        Args:
            structured_data: Structured project data
            abnt_rules: ABNT rules text
            client_template: Client template text
            custom_instructions: Optional custom instructions
            
        Returns:
            Draft memorial text
        """
        try:
            logger.info("Starting Writer Agent")
            
            # Build the prompt
            prompt = self._build_writer_prompt(
                structured_data,
                abnt_rules,
                client_template,
                custom_instructions
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.settings.openai_writer_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um Engenheiro Redator especializado em memoriais descritivos. "
                                   "Seu trabalho é criar documentos técnicos claros, precisos e profissionais."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.writer_temperature,
                max_tokens=4000
            )
            
            draft = response.choices[0].message.content
            
            logger.info(f"Writer Agent completed. Draft length: {len(draft)} characters")
            return draft
            
        except Exception as e:
            logger.error(f"Error in Writer Agent: {str(e)}")
            raise Exception(f"Writer Agent failed: {str(e)}")
    
    def run_reviewer_agent(
        self,
        draft_memorial: str,
        structured_data: StructuredProjectData,
        abnt_rules: str,
        client_template: str
    ) -> str:
        """
        Run the Reviewer Agent to review and refine the memorial draft.
        
        Args:
            draft_memorial: Draft memorial from Writer Agent
            structured_data: Original structured data
            abnt_rules: ABNT rules text
            client_template: Client template text
            
        Returns:
            Final reviewed memorial text
        """
        try:
            logger.info("Starting Reviewer Agent")
            
            # Build the prompt
            prompt = self._build_reviewer_prompt(
                draft_memorial,
                structured_data,
                abnt_rules,
                client_template
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.settings.openai_reviewer_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um Engenheiro Revisor de QA especializado em garantir a qualidade "
                                   "de memoriais descritivos. Você verifica consistência, conformidade e clareza."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.settings.reviewer_temperature,
                max_tokens=4500
            )
            
            final_memorial = response.choices[0].message.content
            
            logger.info(f"Reviewer Agent completed. Final length: {len(final_memorial)} characters")
            return final_memorial
            
        except Exception as e:
            logger.error(f"Error in Reviewer Agent: {str(e)}")
            raise Exception(f"Reviewer Agent failed: {str(e)}")
    
    def _build_writer_prompt(
        self,
        structured_data: StructuredProjectData,
        abnt_rules: str,
        client_template: str,
        custom_instructions: str = None
    ) -> str:
        """
        Build the prompt for the Writer Agent.
        """
        data_json = structured_data.model_dump_json(indent=2, exclude_none=True)
        
        prompt = f"""Você é um Engenheiro Redator especializado em memoriais descritivos.
Sua tarefa é escrever um rascunho de memorial descritivo técnico e profissional.

**DADOS EXTRAÍDOS DO PROJETO (JSON):**
```json
{data_json}
```

**REGRAS OBRIGATÓRIAS (ABNT):**
```
{abnt_rules}
```

**MODELO DE FORMATAÇÃO DO CLIENTE (SEÇÕES OBRIGATÓRIAS):**
```
{client_template}
```
"""

        if custom_instructions:
            prompt += f"""
**INSTRUÇÕES CUSTOMIZADAS ADICIONAIS:**
{custom_instructions}
"""

        prompt += """

**INSTRUÇÕES DE REDAÇÃO:**

1. **Use os DADOS EXTRAÍDOS** para preencher todas as informações do memorial.

2. **Siga ESTRITAMENTE o MODELO DE FORMATAÇÃO** do cliente. Mantenha todas as seções obrigatórias.

3. **Garanta conformidade com as REGRAS DA ABNT**. O documento deve estar tecnicamente correto.

4. **Linguagem Técnica:** Use terminologia de engenharia apropriada. Seja claro e objetivo.

5. **Informações Pendentes:** Se uma informação não estiver nos dados extraídos, use o placeholder "[INFORMAÇÃO PENDENTE: <descrição do campo>]".

6. **Estrutura Lógica:** Organize o conteúdo de forma coerente e profissional.

7. **Detalhamento:** Forneça detalhes técnicos suficientes, mas mantenha concisão.

**GERE O RASCUNHO DO MEMORIAL DESCRITIVO:**
"""

        return prompt
    
    def _build_reviewer_prompt(
        self,
        draft_memorial: str,
        structured_data: StructuredProjectData,
        abnt_rules: str,
        client_template: str
    ) -> str:
        """
        Build the prompt for the Reviewer Agent.
        """
        data_json = structured_data.model_dump_json(indent=2, exclude_none=True)
        
        prompt = f"""Você é um Engenheiro Revisor de QA especializado em garantir a qualidade de memoriais descritivos.
Sua tarefa é revisar o rascunho abaixo e fornecer a versão final corrigida.

**RASCUNHO A REVISAR:**
```
{draft_memorial}
```

**DADOS ORIGINAIS (FONTE DA VERDADE):**
```json
{data_json}
```

**REGRAS ABNT (CHECKLIST):**
```
{abnt_rules}
```

**MODELO DO CLIENTE (CHECKLIST):**
```
{client_template}
```

**INSTRUÇÕES DE REVISÃO (Pense passo a passo):**

Execute as seguintes verificações:

1. **[Consistência de Dados]**: 
   - O rascunho reflete corretamente os dados originais?
   - Valores numéricos (área, pavimentos, etc.) estão corretos?
   - Nomes e identificadores estão consistentes?

2. **[Conformidade ABNT]**: 
   - O rascunho segue as regras da ABNT fornecidas?
   - Existem violações de normas técnicas?
   - Terminologia técnica está correta?

3. **[Conformidade de Template]**: 
   - O rascunho segue o modelo do cliente?
   - Todas as seções obrigatórias estão presentes?
   - A estrutura está correta?

4. **[Coerência e Clareza]**: 
   - O texto está claro e profissional?
   - Não há contradições internas?
   - A linguagem é apropriada para um documento técnico?

5. **[Completude]**: 
   - Informações importantes foram omitidas?
   - Os placeholders "[INFORMAÇÃO PENDENTE]" são justificados?

**APÓS ESTA ANÁLISE:**

- Se encontrou erros ou melhorias necessárias, forneça a versão CORRIGIDA E MELHORADA do memorial.
- Se não há erros significativos, retorne o rascunho original com pequenos ajustes de formatação se necessário.
- Retorne APENAS o texto final do memorial, sem comentários ou explicações adicionais.

**VERSÃO FINAL DO MEMORIAL DESCRITIVO:**
"""

        return prompt

