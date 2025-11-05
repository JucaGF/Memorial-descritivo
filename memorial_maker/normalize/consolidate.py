"""Consolidação e agregação de dados extraídos."""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from memorial_maker.utils.logging import get_logger
from memorial_maker.extract.carimbo import merge_carimbo_data

logger = get_logger("normalize.consolidate")


class DataConsolidator:
    """Consolida dados de múltiplas fontes/páginas."""

    def __init__(self):
        """Inicializa consolidador."""
        self.servicos_map = {
            "point_telefone": "voz",
            "point_interfone": "intercomunicacao",
            "point_rj45": "dados",
            "wifi_indoor": "dados",
            "wifi_outdoor": "dados",
            "point_tv_coletiva": "video",
            "point_tv_assinatura": "video",
            "cam_bullet": "monitoramento",
            "cam_dome": "monitoramento",
        }

    def consolidate(
        self,
        extractions: List[Dict[str, Any]],
        normalized_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Consolida todas as extrações.
        
        Args:
            extractions: Dados brutos de extração
            normalized_items: Itens já normalizados
            
        Returns:
            Dados consolidados (JSON mestre)
        """
        logger.info("Consolidando dados extraídos...")
        
        # Dados da obra (de carimbos)
        obra = self._consolidate_obra_data(extractions)
        
        # Pavimentos únicos
        pavimentos = self._extract_pavimentos(extractions, normalized_items)
        
        # Serviços presentes
        servicos = self._extract_servicos(normalized_items)
        
        # Salas técnicas
        salas = self._extract_salas_tecnicas(extractions)
        
        # Consolida JSON mestre
        master = {
            "obra": obra,
            "servicos": servicos,
            "pavimentos": pavimentos,
            "itens": normalized_items,
            "salas_tecnicas": salas,
        }
        
        logger.info(f"Consolidação: {len(pavimentos)} pavimentos, {len(servicos)} serviços, {len(normalized_items)} itens")
        return master

    def _consolidate_obra_data(self, extractions: List[Dict]) -> Dict[str, Any]:
        """Consolida dados da obra."""
        carimbo_data = merge_carimbo_data(extractions)
        
        obra = {
            "construtora": carimbo_data.get("construtora", ""),
            "empreendimento": carimbo_data.get("empreendimento", ""),
            "endereco": carimbo_data.get("endereco", ""),
            "tipologia": "",  # Será preenchido com pavimentos
            "pavimentos": [],
            "carimbo": {
                "projeto": carimbo_data.get("projeto", ""),
                "revisao": carimbo_data.get("revisao", ""),
                "data": carimbo_data.get("data", ""),
                "escala": carimbo_data.get("escala", ""),
                "autor": carimbo_data.get("autor", ""),
                "arquivo": carimbo_data.get("arquivo", ""),
            }
        }
        
        return obra

    def _extract_pavimentos(
        self,
        extractions: List[Dict],
        items: List[Dict],
    ) -> List[str]:
        """Extrai lista de pavimentos únicos."""
        pavimentos = set()
        
        # De páginas
        for extraction in extractions:
            for page in extraction.get("pages", []):
                pav = page.get("pavimento")
                if pav:
                    pavimentos.add(pav)
        
        # De itens
        for item in items:
            pav = item.get("pavimento")
            if pav:
                pavimentos.add(pav)
        
        # Ordena (subsolo, térreo, 1º, 2º, ..., cobertura)
        def sort_key(p):
            p_lower = p.lower()
            if "subsolo" in p_lower:
                return -1
            elif "térreo" in p_lower or "terreo" in p_lower:
                return 0
            elif "cobert" in p_lower:
                return 999
            else:
                import re
                match = re.search(r"(\d+)", p)
                if match:
                    return int(match.group(1))
                return 500
        
        sorted_pav = sorted(pavimentos, key=sort_key)
        return sorted_pav

    def _extract_servicos(self, items: List[Dict]) -> List[str]:
        """Extrai serviços presentes."""
        servicos = set()
        
        for item in items:
            tipo = item.get("tipo")
            if tipo:
                servico = self.servicos_map.get(tipo)
                if servico:
                    servicos.add(servico)
        
        # Ordem padrão
        ordem = ["voz", "dados", "video", "intercomunicacao", "monitoramento"]
        return [s for s in ordem if s in servicos]

    def _extract_salas_tecnicas(self, extractions: List[Dict]) -> List[Dict]:
        """Extrai informações de salas técnicas."""
        salas = []
        
        # Busca keywords de sala técnica/monitoramento
        keywords = ["sala de monitoramento", "sala técnica", "er", "ef", "rack"]
        
        for extraction in extractions:
            for page in extraction.get("pages", []):
                for block in page.get("blocks", []):
                    text = block.get("text", "").lower()
                    if any(kw in text for kw in keywords):
                        # Encontrou menção a sala técnica
                        salas.append({
                            "nome": "Sala de Monitoramento",
                            "localizacao": page.get("pavimento", ""),
                            "requisitos": [],  # Será preenchido pelo prompt
                        })
                        break
        
        # Remove duplicatas
        salas_unicas = []
        nomes_vistos = set()
        for sala in salas:
            nome = sala["nome"]
            if nome not in nomes_vistos:
                salas_unicas.append(sala)
                nomes_vistos.add(nome)
        
        return salas_unicas

    def export_csvs(self, master: Dict[str, Any], output_dir: Path):
        """Exporta CSVs.
        
        Args:
            master: JSON mestre consolidado
            output_dir: Diretório de saída
        """
        logger.info("Exportando CSVs...")
        
        # CSV: Itens por pavimento
        self._export_itens_por_pavimento(master, output_dir)
        
        # CSV: Totais por serviço
        self._export_totais_por_servico(master, output_dir)
        
        # CSV: Salas técnicas
        self._export_salas_tecnicas(master, output_dir)

    def _export_itens_por_pavimento(self, master: Dict, output_dir: Path):
        """Exporta itens_por_pavimento.csv."""
        items = master.get("itens", [])
        
        if not items:
            logger.warning("Nenhum item para exportar")
            return
        
        df = pd.DataFrame(items)
        
        # Reordena colunas
        cols = ["pavimento", "tipo", "quantidade", "altura_m", "cabos", "divisor", "observacao"]
        cols = [c for c in cols if c in df.columns]
        df = df[cols]
        
        output_path = output_dir / "itens_por_pavimento.csv"
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Exportado: {output_path}")

    def _export_totais_por_servico(self, master: Dict, output_dir: Path):
        """Exporta totais_por_servico.csv."""
        items = master.get("itens", [])
        
        # Agrupa por serviço
        servicos_map = {
            "point_telefone": "voz",
            "point_interfone": "intercomunicacao",
            "point_rj45": "dados",
            "wifi_indoor": "dados",
            "wifi_outdoor": "dados",
            "point_tv_coletiva": "video",
            "point_tv_assinatura": "video",
            "cam_bullet": "monitoramento",
            "cam_dome": "monitoramento",
        }
        
        totais = defaultdict(int)
        for item in items:
            tipo = item.get("tipo")
            qtd = item.get("quantidade", 1)
            servico = servicos_map.get(tipo, "outros")
            totais[servico] += qtd
        
        df = pd.DataFrame([
            {"servico": s, "total": t}
            for s, t in sorted(totais.items())
        ])
        
        output_path = output_dir / "totais_por_servico.csv"
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Exportado: {output_path}")

    def _export_salas_tecnicas(self, master: Dict, output_dir: Path):
        """Exporta salas_tecnicas.csv."""
        salas = master.get("salas_tecnicas", [])
        
        if not salas:
            logger.info("Nenhuma sala técnica encontrada")
            return
        
        df = pd.DataFrame(salas)
        
        output_path = output_dir / "salas_tecnicas.csv"
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Exportado: {output_path}")


def consolidate_and_export(
    extractions: List[Dict[str, Any]],
    normalized_items: List[Dict[str, Any]],
    output_dir: Path,
) -> Dict[str, Any]:
    """Consolida dados e exporta JSON mestre + CSVs.
    
    Args:
        extractions: Extrações brutas
        normalized_items: Itens normalizados
        output_dir: Diretório de saída
        
    Returns:
        JSON mestre
    """
    consolidator = DataConsolidator()
    
    # Consolida
    master = consolidator.consolidate(extractions, normalized_items)
    
    # Salva JSON mestre
    master_path = output_dir / "mestre.json"
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON mestre salvo: {master_path}")
    
    # Exporta CSVs
    consolidator.export_csvs(master, output_dir)
    
    return master






