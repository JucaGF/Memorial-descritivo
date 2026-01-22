"""Geração de seções do memorial usando LLM (paralelo)."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    HumanMessage = None
    SystemMessage = None

from memorial_maker.config import settings
from memorial_maker.rag.index_style import StyleIndexer
from memorial_maker.rag.static_templates import StaticTemplateLoader, STATIC_TEMPLATES
from memorial_maker.utils.logging import get_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = get_logger("rag.generate")


class SectionGenerator:
    """Gerador de seções do memorial."""

    def __init__(self, style_indexer: StyleIndexer, prompts_dir: Path, memorial_type: str = "telecom"):
        """Inicializa gerador.
        
        Args:
            style_indexer: Indexador de estilo
            prompts_dir: Diretório com prompts
            memorial_type: Tipo de memorial ("telecom" ou "eletrico")
        """
        self.style_indexer = style_indexer
        self.prompts_dir = prompts_dir
        self.memorial_type = memorial_type
        
        # Initialize static template loader for electrical memorials
        if memorial_type == "eletrico":
            templates_dir = prompts_dir / "eletrico" / "static_templates"
            self.static_loader = StaticTemplateLoader(templates_dir)
        else:
            self.static_loader = None
        
        # Configura LLM (GPT-5 não suporta top_p)
        if not LANGCHAIN_AVAILABLE:
            self.llm = None
            logger.warning("LangChain não disponível. Geração de seções desabilitada.")
        else:
            llm_params = {
                "model": settings.llm_model,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
                "openai_api_key": settings.openai_api_key,
            }
            
            # Adiciona top_p apenas para modelos que suportam (não GPT-5)
            if not settings.llm_model.startswith("gpt-5"):
                llm_params["top_p"] = settings.llm_top_p
            
            self.llm = ChatOpenAI(**llm_params)
        
        # Carrega instruções base
        self.base_instructions = self._load_prompt("base_instructions.txt")
    
    def _load_prompt(self, filename: str) -> str:
        """Carrega arquivo de prompt."""
        # Try memorial-specific directory first
        if self.memorial_type == "eletrico":
            type_path = self.prompts_dir / "eletrico" / filename
        else:  # telecom
            type_path = self.prompts_dir / "telecom" / filename
        
        if type_path.exists():
            path = type_path
        else:
            # Fallback to base directory (e.g., base_instructions.txt)
            path = self.prompts_dir / filename
        
        if not path.exists():
            logger.warning(f"Prompt não encontrado: {filename} (tipo: {self.memorial_type})")
            return ""
        
        logger.debug(f"Carregando prompt: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _filter_context_for_section(
        self,
        section: str,
        master_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Filtra dados relevantes para uma seção."""
        
        obra = master_data.get("obra", {})
        servicos = master_data.get("servicos", [])
        pavimentos = master_data.get("pavimentos", [])
        itens = master_data.get("itens", [])
        salas = master_data.get("salas_tecnicas", [])
        
        # Contexto base
        base_ctx = {
            "empreendimento": obra.get("empreendimento", ""),
            "construtora": obra.get("construtora", ""),
        }
        
        # Filtros específicos por seção
        if section == "s1_introducao":
            return {
                **base_ctx,
                "servicos_presentes": servicos,
                "tipologia_obra": ", ".join(pavimentos[:3]) if pavimentos else "",
            }
        
        elif section == "s2_dados_obra":
            return {
                "obra": obra,
                "carimbo": obra.get("carimbo", {}),
                "pavimentos": pavimentos,
            }
        
        elif section == "s3_normas":
            from memorial_maker.config import NORMAS_PADRAO
            return {
                "normas_padrao": NORMAS_PADRAO,
                "normas_detectadas": [],  # TODO: extrair de textos se mencionadas
            }
        
        elif section == "s4_servicos":
            return {
                "servicos_presentes": servicos,
            }
        
        elif section == "s4_1_voz":
            pontos_tel = [i for i in itens if i.get("tipo") == "point_telefone"]
            pontos_int = [i for i in itens if i.get("tipo") == "point_interfone"]
            return {
                **base_ctx,
                "pontos_telefone": pontos_tel,
                "pontos_interfone": pontos_int,
            }
        
        elif section == "s4_2_dados":
            pontos_rj45 = [i for i in itens if i.get("tipo") == "point_rj45"]
            wifi_in = [i for i in itens if i.get("tipo") == "wifi_indoor"]
            wifi_out = [i for i in itens if i.get("tipo") == "wifi_outdoor"]
            cat6 = [i for i in itens if "cat6" in i.get("cabos", [])]
            return {
                **base_ctx,
                "point_rj45": pontos_rj45,
                "wifi_indoor": wifi_in,
                "wifi_outdoor": wifi_out,
                "cat6": len(cat6) > 0,
            }
        
        elif section == "s4_3_video":
            tv_col = [i for i in itens if i.get("tipo") == "point_tv_coletiva"]
            tv_ass = [i for i in itens if i.get("tipo") == "point_tv_assinatura"]
            divisores = {}
            for i in itens:
                div = i.get("divisor")
                pav = i.get("pavimento")
                if div and pav:
                    if pav not in divisores:
                        divisores[pav] = []
                    divisores[pav].append(div)
            
            return {
                **base_ctx,
                "point_tv_coletiva": tv_col,
                "point_tv_assinatura": tv_ass,
                "divisores": divisores,
                "rg6_u90": True,  # Assumir se tem TV
                "mb10": True,
                "cci2": True,
            }
        
        elif section == "s4_4_intercom":
            pontos_int = [i for i in itens if i.get("tipo") == "point_interfone"]
            return {
                **base_ctx,
                "point_interfone": pontos_int,
                "porteiro": len(pontos_int) > 0,
                "botoeira": len(pontos_int) > 0,
                "cci2": True,
            }
        
        elif section == "s4_5_monitoramento":
            cam_bullet = [i for i in itens if i.get("tipo") == "cam_bullet"]
            cam_dome = [i for i in itens if i.get("tipo") == "cam_dome"]
            return {
                **base_ctx,
                "cam_bullet": cam_bullet,
                "cam_dome": cam_dome,
                "cat6": True,
            }
        
        elif section == "s5_sala_monitoramento":
            return {
                **base_ctx,
                "sala_monitoramento": salas[0] if salas else {},
            }
        
        elif section == "s6_passivos_ativos":
            # Coleta materiais únicos
            materiais = set()
            for item in itens:
                cabos = item.get("cabos", [])
                materiais.update(cabos)
                tipo = item.get("tipo", "")
                if "rj45" in tipo:
                    materiais.add("tomada_rj45")
                if "tv" in tipo:
                    materiais.add("tomada_tv")
            
            return {
                "materiais": list(materiais),
            }
        
        elif section == "s7_testes_aceitacao":
            # Contexto mínimo
            return {
                "cat6_presente": any("cat6" in i.get("cabos", []) for i in itens),
            }
        
        # Electrical sections
        elif self.memorial_type == "eletrico":
            return self._filter_context_for_electrical_section(section, master_data)
        
        return {}

    def _filter_context_for_electrical_section(
        self,
        section: str,
        master_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Filtra dados relevantes para seções elétricas."""
        obra = master_data.get("obra", {})
        itens = master_data.get("itens", [])
        pavimentos = master_data.get("pavimentos", [])
        
        base_ctx = {
            "empreendimento": obra.get("empreendimento", ""),
            "construtora": obra.get("construtora", ""),
            "endereco": obra.get("endereco", ""),
            "pavimentos": pavimentos,
        }
        
        # Extract electrical-specific data from extractions
        extractions = master_data.get("extractions", [])
        full_text_parts = []
        for extraction in extractions:
            if isinstance(extraction, dict):
                text_items = extraction.get("text", [])
                for text_item in text_items:
                    if isinstance(text_item, dict):
                        full_text_parts.append(text_item.get("text", ""))
                    else:
                        full_text_parts.append(str(text_item))
        
        full_text = "\n".join(full_text_parts) if full_text_parts else ""
        
        # Detect systems from text patterns
        entrada_energia = any(
            kw in full_text.lower() for kw in ["entrada", "fornecimento", "concessionária", "medidor"]
        )
        luz_forca = any(
            kw in full_text.lower() for kw in ["iluminação", "luz", "força", "tomada", "circuito"]
        )
        luz_essencial = any(
            kw in full_text.lower() for kw in ["essencial", "emergência", "gerador", "subestação"]
        )
        protecao_aterramento = any(
            kw in full_text.lower() for kw in ["aterramento", "proteção", "dr", "disjuntor"]
        )
        
        # Material detection
        eletrodutos = any(
            kw in full_text.lower() for kw in ["eletroduto", "conduíte", "calha"]
        )
        fios_cabos = any(
            kw in full_text.lower() for kw in ["fio", "cabo", "condutor", "mm²"]
        )
        luminarias = any(
            kw in full_text.lower() for kw in ["luminária", "lâmpada", "lampada", "reator"]
        )
        quadros = any(
            kw in full_text.lower() for kw in ["quadro", "disjuntor", "dr", "qgf", "qdl"]
        )
        
        if section == "s1_sumario":
            return {
                **base_ctx,
                "sections_presentes": master_data.get("structured_extraction", {}).get("sections_present", []),
            }
        elif section == "s2_memorial_descritivo":
            return {
                **base_ctx,
                "sistemas_presentes": master_data.get("structured_extraction", {}).get("systems_present", []),
            }
        elif section == "s2_1_introducao":
            return {
                **base_ctx,
                "sistemas_presentes": master_data.get("structured_extraction", {}).get("systems_present", []),
            }
        elif section == "s2_2_generalidades":
            return {
                **base_ctx,
                "normas_aplicaveis": ["NBR 5410", "NBR 14039"],
                "caracteristicas_projeto": master_data.get("structured_extraction", {}).get("project_characteristics", {}),
            }
        elif section == "s2_3_descricao_servicos":
            return {
                **base_ctx,
                "sistemas_presentes": master_data.get("structured_extraction", {}).get("systems_present", []),
            }
        elif section == "s2_3_1_entrada_energia":
            return {
                **base_ctx,
                "entrada_energia": {
                    "presente": entrada_energia,
                    "dados": master_data.get("structured_extraction", {}).get("utility_entrance", {}),
                },
            }
        elif section == "s2_3_2_luz_forca":
            return {
                **base_ctx,
                "luz_forca": {
                    "presente": luz_forca,
                    "dados": master_data.get("structured_extraction", {}).get("lighting_power", {}),
                },
            }
        elif section == "s2_3_3_luz_essencial":
            return {
                **base_ctx,
                "luz_essencial": {
                    "presente": luz_essencial,
                    "dados": master_data.get("structured_extraction", {}).get("substation_essential", {}),
                },
            }
        elif section == "s2_3_4_protecao_aterramento":
            return {
                **base_ctx,
                "protecao_aterramento": {
                    "presente": protecao_aterramento,
                    "dados": master_data.get("structured_extraction", {}).get("grounding_protection", {}),
                },
            }
        elif section == "s2_3_5_montagem_aparelhos":
            return {
                **base_ctx,
                "montagem_aparelhos": master_data.get("structured_extraction", {}).get("appliances", {}),
            }
        elif section == "s3_especificacao_materiais":
            return {
                **base_ctx,
                "materiais_presentes": master_data.get("structured_extraction", {}).get("materials_present", []),
            }
        elif section == "s3_1_introducao_materiais":
            return {
                **base_ctx,
                "materiais_presentes": master_data.get("structured_extraction", {}).get("materials_present", []),
            }
        elif section == "s3_2_instalacoes_eletricas":
            return {
                **base_ctx,
                "materiais_presentes": master_data.get("structured_extraction", {}).get("materials_present", []),
            }
        elif section == "s3_2_1_eletrodutos":
            return {
                **base_ctx,
                "eletrodutos": {
                    "presente": eletrodutos,
                    "dados": master_data.get("structured_extraction", {}).get("conduits", {}),
                },
            }
        elif section == "s3_2_2_fios_cabos":
            return {
                **base_ctx,
                "fios_cabos": {
                    "presente": fios_cabos,
                    "dados": master_data.get("structured_extraction", {}).get("wires_cables", {}),
                },
            }
        elif section == "s3_2_3_luminarias":
            return {
                **base_ctx,
                "luminarias": {
                    "presente": luminarias,
                    "dados": master_data.get("structured_extraction", {}).get("luminaires", {}),
                },
            }
        elif section == "s3_2_4_quadros":
            return {
                **base_ctx,
                "quadros": {
                    "presente": quadros,
                    "dados": master_data.get("structured_extraction", {}).get("panels", {}),
                },
            }
        
        return base_ctx

    async def _generate_structured_extraction_async(
        self,
        master_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Stage 1: Generate structured extraction identifying electrical systems.
        
        Args:
            master_data: JSON mestre consolidado
            
        Returns:
            Structured JSON with identified systems and presence markers
        """
        logger.info("Stage 1: Generating structured extraction for electrical systems...")
        
        # Extract full text from master_data
        full_text_parts = []
        extractions = master_data.get("extractions", [])
        for extraction in extractions:
            if isinstance(extraction, dict):
                text_items = extraction.get("text", [])
                for text_item in text_items:
                    if isinstance(text_item, dict):
                        full_text_parts.append(text_item.get("text", ""))
                    else:
                        full_text_parts.append(str(text_item))
        
        full_text = "\n".join(full_text_parts) if full_text_parts else ""
        
        # Build context for structured extraction
        obra = master_data.get("obra", {})
        context = {
            "empreendimento": obra.get("empreendimento", ""),
            "construtora": obra.get("construtora", ""),
            "extracted_text": full_text[:10000],  # Limit text length
        }
        
        system_msg = SystemMessage(content="""Você é um analisador técnico especializado em projetos elétricos.
Analise os dados extraídos e retorne APENAS um JSON válido identificando os sistemas elétricos presentes no projeto.

Retorne um JSON com a seguinte estrutura:
{
  "utility_entrance": {"present": true/false, "details": {...}},
  "lighting_power": {"present": true/false, "details": {...}},
  "substation_essential": {"present": true/false, "details": {...}},
  "grounding_protection": {"present": true/false, "details": {...}},
  "project_characteristics": {...},
  "materials_present": ["eletrodutos", "fios_cabos", "luminarias", "quadros"],
  "sections_present": ["s2_3_1_entrada_energia", "s2_3_2_luz_forca", ...],
  "uncertainty_markers": [...]
}

Seja conservador: marque como presente apenas se houver evidência clara nos dados extraídos.""")
        
        human_prompt = f"""
Analise os seguintes dados extraídos de um projeto elétrico e identifique quais sistemas estão presentes:

## DADOS EXTRAÍDOS:
```json
{json.dumps(context, ensure_ascii=False, indent=2)}
```

Retorne APENAS o JSON estruturado identificando os sistemas presentes. Não inclua texto adicional, apenas o JSON.
"""
        
        human_msg = HumanMessage(content=human_prompt)
        
        try:
            response = await self.llm.ainvoke([system_msg, human_msg])
            content = response.content.strip()
            
            # Extract JSON from response (may have markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            structured = json.loads(content)
            logger.info(f"Structured extraction completed: {len(structured.get('sections_present', []))} sections identified")
            return structured
            
        except Exception as e:
            logger.error(f"Error in structured extraction: {e}")
            # Return conservative default (assume basic systems present)
            logger.info("Using fallback structured extraction with all sections included")
            return {
                "utility_entrance": {"present": True},
                "lighting_power": {"present": True},
                "substation_essential": {"present": False},
                "grounding_protection": {"present": True},
                "project_characteristics": {},
                "materials_present": ["eletrodutos", "fios_cabos", "luminarias", "quadros"],
                "sections_present": [
                    # Section 4 subsections - always include the main ones
                    "s4_1_entrada_energia",
                    "s4_3_aterramento",
                    "s4_4_eletrodutos_leitos",
                    "s4_5_condutores",
                    "s4_6_medicao_energia",
                    "s4_7_cores",
                    "s4_8_luz_forca",
                    "s4_10_protecao_aterramento",
                    "s4_11_montagem_aparelhos",
                    "s4_12_itens_nao_inclusos",
                    # s4_2 and s4_9 are conditional (substation/emergency)
                ],
                "uncertainty_markers": [],
            }


    async def _generate_section_async(
        self,
        section_id: str,
        master_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """Gera uma seção de forma assíncrona."""
        logger.info(f"Gerando seção: {section_id}")
        logger.debug(f"Memorial type: {self.memorial_type}")
        
        try:
            # For electrical memorials, check if there's a static template first
            if self.memorial_type == "eletrico" and self.static_loader:
                # Check if section has a static template
                template_name = STATIC_TEMPLATES.get(section_id)
                if template_name and self.static_loader.has_template(template_name):
                    logger.info(f"Usando template estático para {section_id}: {template_name}")
                    static_content = self.static_loader.load_template(template_name)
                    if static_content:
                        return {"section_id": section_id, "content": static_content}
            
            # No static template, proceed with LLM generation
            # Carrega prompt específico
            section_prompt = self._load_prompt(f"{section_id}.txt")
            if not section_prompt:
                logger.error(f"Prompt não encontrado para {section_id}")
                return {"section_id": section_id, "content": "", "error": "Prompt não encontrado"}
            
            # Filtra contexto
            context_factual = self._filter_context_for_section(section_id, master_data)
            
            # Recupera exemplos de estilo
            section_name = section_id.replace("s", "").replace("_", "")
            if section_name.startswith("4"):
                # Subseções de serviços
                section_name = section_id.split("_")[-1]  # voz, dados, etc.
            
            style_examples = self.style_indexer.retrieve_style_examples(section_name, top_k=3)
            style_text = "\n\n---\n\n".join(style_examples) if style_examples else ""
            
            # Monta prompt final
            system_msg = SystemMessage(content=self.base_instructions)
            
            human_prompt = f"""
{section_prompt}

## EXEMPLOS DE ESTILO (apenas para referência de tom/estrutura):
{style_text if style_text else "(Sem exemplos disponíveis)"}

## CONTEXTO FACTUAL (use APENAS estes dados):
```json
{json.dumps(context_factual, ensure_ascii=False, indent=2)}
```

Gere agora o texto da seção em PT-BR técnico, seguindo as regras.
"""
            
            human_msg = HumanMessage(content=human_prompt)
            
            # Chama LLM
            response = await self.llm.ainvoke([system_msg, human_msg])
            content = response.content.strip()
            
            logger.info(f"Seção {section_id} gerada: {len(content)} chars")
            logger.debug(f"Preview: {content[:100]}...")
            return {"section_id": section_id, "content": content}
            
        except Exception as e:
            logger.error(f"Erro ao gerar seção {section_id}: {e}")
            return {"section_id": section_id, "content": "", "error": str(e)}

    async def generate_all_sections_async(
        self,
        master_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """Gera todas as seções em paralelo.
        
        Args:
            master_data: JSON mestre consolidado
            
        Returns:
            Dicionário {section_id: content}
        """
        logger.info(f"Gerando todas as seções em paralelo (tipo: {self.memorial_type})...")
        
        # For electrical memorials, use two-stage approach
        if self.memorial_type == "eletrico":
            # Stage 1: Structured extraction
            structured_extraction = await self._generate_structured_extraction_async(master_data)
            
            # Add structured extraction to master_data for context filtering
            master_data["structured_extraction"] = structured_extraction
            
            # Determine which sections to generate based on structured extraction
            sections_present = structured_extraction.get("sections_present", [])
            
            # Base sections that are always included (matching reference memorial structure)
            base_sections = [
                "s0_sumario",  # Static TOC
                "s1_introducao",  # Section 1
                "s2_dados_obra",  # Section 2
                "s3_requisitos_gerais",  # Section 3
                "s3_1_disposicoes_gerais",  # 3.1
                "s3_2_disposicoes_base_projeto",  # 3.2
                "s4_visao_geral",  # Section 4 intro
                "s5_especificacao_materiais",  # Section 5 intro
                "s5_1_instalacoes_eletricas",  # 5.1
                "s5_2_fios_cabos",  # 5.2
                "s5_3_luminarias",  # 5.3
                "s5_4_quadros",  # 5.4
            ]
            
            # Section 4 subsections that are conditional (only if evidence found)
            optional_section4_subsections = [
                "s4_1_entrada_energia",  # 4.1
                "s4_2_subestacao",  # 4.2
                "s4_2_1_dados_construtivos",  # 4.2.1
                "s4_3_aterramento",  # 4.3
                "s4_4_eletrodutos_leitos",  # 4.4
                "s4_5_condutores",  # 4.5
                "s4_6_medicao_energia",  # 4.6
                "s4_7_cores",  # 4.7
                "s4_8_luz_forca",  # 4.8
                "s4_9_luz_essencial",  # 4.9
                "s4_10_protecao_aterramento",  # 4.10
                "s4_11_montagem_aparelhos",  # 4.11
                "s4_12_itens_nao_inclusos",  # 4.12
            ]
            
            # Build final section list
            sections_ids = base_sections.copy()
            # Add section 4 subsections based on evidence
            for section_id in optional_section4_subsections:
                if section_id in sections_present:
                    sections_ids.append(section_id)
            
            logger.info(f"Generating {len(sections_ids)} sections for electrical memorial")
            
        else:
            # Telecom memorials: use existing section list
            sections_ids = [
                "s1_introducao",
                "s2_dados_obra",
                "s3_normas",
                "s4_servicos",
                "s4_1_voz",
                "s4_2_dados",
                "s4_3_video",
                "s4_4_intercom",
                "s4_5_monitoramento",
                "s5_sala_monitoramento",
                "s6_passivos_ativos",
                "s7_testes_aceitacao",
            ]
        
        try:
            # Executa em paralelo
            tasks = [
                self._generate_section_async(sid, master_data)
                for sid in sections_ids
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Organiza resultados (only include non-empty sections)
            sections = {}
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Exceção durante geração: {result}")
                    continue
                
                section_id = result.get("section_id")
                content = result.get("content", "").strip()
                # Only include sections with actual content
                if content and len(content) > 50:  # Minimum content length
                    sections[section_id] = content
                else:
                    logger.debug(f"Omitting empty section: {section_id}")
                    logger.debug(f"Content length: {len(content)}")
            
            logger.info(f"Geradas {len(sections)} seções com sucesso (tipo: {self.memorial_type})")
            logger.info(f"Seções geradas: {list(sections.keys())}")
            return sections
            
        except Exception as e:
            logger.error(f"Erro na geração paralela: {e}")
            # Fallback: tenta sequencial
            logger.info("Tentando geração sequencial...")
            return await self._generate_sequential(sections_ids, master_data)

    async def _generate_sequential(
        self,
        sections_ids: List[str],
        master_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """Fallback: gera seções sequencialmente."""
        sections = {}
        
        for section_id in sections_ids:
            result = await self._generate_section_async(section_id, master_data)
            content = result.get("content", "")
            if content:
                sections[section_id] = content
        
        return sections

    def generate_all_sections(
        self,
        master_data: Dict[str, Any],
        parallel: bool = True,
    ) -> Dict[str, str]:
        """Versão síncrona (wrapper).
        
        Args:
            master_data: JSON mestre
            parallel: Se True, tenta paralelo; senão, sequencial
            
        Returns:
            Dicionário {section_id: content}
        """
        if parallel and settings.parallel_execution:
            # Tenta paralelo
            try:
                return asyncio.run(self.generate_all_sections_async(master_data))
            except Exception as e:
                logger.warning(f"Falha no paralelo, tentando sequencial: {e}")
                # Força sequencial
                settings.parallel_execution = False
        
        # Sequencial - determine sections based on memorial type
        if self.memorial_type == "eletrico":
            # For electrical, we need structured extraction first
            structured_extraction = asyncio.run(self._generate_structured_extraction_async(master_data))
            master_data["structured_extraction"] = structured_extraction
            
            sections_present = structured_extraction.get("sections_present", [])
            base_sections = [
                "s0_sumario",
                "s1_introducao",
                "s2_dados_obra",
                "s3_requisitos_gerais",
                "s3_1_disposicoes_gerais",
                "s3_2_disposicoes_base_projeto",
                "s4_visao_geral",
                "s5_especificacao_materiais",
                "s5_1_instalacoes_eletricas",
                "s5_2_fios_cabos",
                "s5_3_luminarias",
                "s5_4_quadros",
            ]
            
            # Section 4 subsections that are conditional
            optional_section4_subsections = [
                "s4_1_entrada_energia",
                "s4_2_subestacao",
                "s4_2_1_dados_construtivos",
                "s4_3_aterramento",
                "s4_4_eletrodutos_leitos",
                "s4_5_condutores",
                "s4_6_medicao_energia",
                "s4_7_cores",
                "s4_8_luz_forca",
                "s4_9_luz_essencial",
                "s4_10_protecao_aterramento",
                "s4_11_montagem_aparelhos",
                "s4_12_itens_nao_inclusos",
            ]
            
            # Build section list: base + conditional section 4 subsections
            sections_ids = base_sections + [s for s in optional_section4_subsections if s in sections_present]
        else:
            sections_ids = [
                "s1_introducao",
                "s2_dados_obra",
                "s3_normas",
                "s4_servicos",
                "s4_1_voz",
                "s4_2_dados",
                "s4_3_video",
                "s4_4_intercom",
                "s4_5_monitoramento",
                "s5_sala_monitoramento",
                "s6_passivos_ativos",
                "s7_testes_aceitacao",
            ]
        
        return asyncio.run(self._generate_sequential(sections_ids, master_data))




