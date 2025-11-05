"""Smoke tests básicos do pipeline."""

import pytest
from pathlib import Path
import tempfile
import shutil

from memorial_maker.config import settings
from memorial_maker.utils.io_paths import setup_output_dirs
from memorial_maker.normalize.canonical_map import CanonicalMapper, ItemExtractor
from memorial_maker.normalize.consolidate import DataConsolidator


class TestCanonicalMapper:
    """Testes do mapeador canônico."""
    
    def test_find_canonical_cabo(self):
        """Testa mapeamento de cabos."""
        mapper = CanonicalMapper()
        
        assert mapper.find_canonical("CAT-6") == "cat6"
        assert mapper.find_canonical("cat 6") == "cat6"
        assert mapper.find_canonical("RG-06/U#90%") == "rg6_u90"
        assert mapper.find_canonical("CCI-2") == "cci2"
    
    def test_find_canonical_ponto(self):
        """Testa mapeamento de pontos."""
        mapper = CanonicalMapper()
        
        assert mapper.find_canonical("RJ-45") == "point_rj45"
        assert mapper.find_canonical("TV coletiva") == "point_tv_coletiva"
        assert mapper.find_canonical("interfone") == "point_interfone"
    
    def test_extract_diametro(self):
        """Testa extração de diâmetro."""
        mapper = CanonicalMapper()
        
        result = mapper.extract_diametro("∅32mm")
        assert result == {"mm": 32}
        
        result = mapper.extract_diametro('3/4"')
        assert result == {"polegadas": "3/4"}
    
    def test_extract_altura(self):
        """Testa extração de altura."""
        mapper = CanonicalMapper()
        
        assert mapper.extract_altura("H=1,40m") == 1.40
        assert mapper.extract_altura("H = 2.50 m") == 2.50
    
    def test_extract_divisor(self):
        """Testa extração de divisor."""
        mapper = CanonicalMapper()
        
        assert mapper.extract_divisor("DIVISOR 1/2") == "div_1_2"
        assert mapper.extract_divisor("divisor 1x4") == "div_1_4"


class TestItemExtractor:
    """Testes do extrator de itens."""
    
    def test_extract_from_text_simple(self):
        """Testa extração de texto simples."""
        extractor = ItemExtractor()
        
        text = """
        RJ-45 - 4 unidades
        Altura: H=1,40m
        Cabo: CAT-6
        """
        
        items = extractor.extract_from_text(text)
        
        assert len(items) > 0
        # Verifica se extraiu algo relevante
    
    def test_extract_from_text_with_context(self):
        """Testa extração com contexto de página."""
        extractor = ItemExtractor()
        
        text = "RJ-45 - 10 pontos"
        context = {"pavimento": "8º", "tipo": "planta"}
        
        items = extractor.extract_from_text(text, context)
        
        if items:
            assert items[0].get("pavimento") == "8º"


class TestDataConsolidator:
    """Testes do consolidador."""
    
    def test_extract_servicos(self):
        """Testa extração de serviços."""
        consolidator = DataConsolidator()
        
        items = [
            {"tipo": "point_rj45", "quantidade": 10},
            {"tipo": "point_tv_coletiva", "quantidade": 5},
            {"tipo": "cam_bullet", "quantidade": 3},
        ]
        
        servicos = consolidator._extract_servicos(items)
        
        assert "dados" in servicos
        assert "video" in servicos
        assert "monitoramento" in servicos
    
    def test_extract_pavimentos(self):
        """Testa extração e ordenação de pavimentos."""
        consolidator = DataConsolidator()
        
        items = [
            {"pavimento": "8º"},
            {"pavimento": "Térreo"},
            {"pavimento": "Subsolo"},
            {"pavimento": "1º"},
        ]
        
        extractions = [{"pages": [{"pavimento": p["pavimento"]} for p in items]}]
        
        pavimentos = consolidator._extract_pavimentos(extractions, items)
        
        # Deve ordenar: Subsolo, Térreo, 1º, 8º
        assert pavimentos[0].lower() == "subsolo"
        assert "térreo" in pavimentos[1].lower() or "terreo" in pavimentos[1].lower()


class TestOutputDirs:
    """Testa criação de diretórios."""
    
    def test_setup_output_dirs(self):
        """Testa setup de diretórios de saída."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "out"
            
            dirs = setup_output_dirs(out_dir)
            
            assert dirs["extraido"].exists()
            assert dirs["memorial"].exists()
            assert dirs["logs"].exists()


class TestEndToEnd:
    """Teste end-to-end simplificado."""
    
    @pytest.mark.skipif(
        not settings.openai_api_key,
        reason="Requer OPENAI_API_KEY configurada"
    )
    def test_mock_pipeline(self):
        """Testa pipeline com dados mockados."""
        # Mock de dados extraídos
        mock_extractions = [
            {
                "source": "test.pdf",
                "pages": [
                    {
                        "page_num": 1,
                        "type": "planta",
                        "pavimento": "Térreo",
                        "blocks": [
                            {"text": "RJ-45 - 10 pontos"}
                        ],
                        "rois": {
                            "carimbo": {
                                "parsed": {
                                    "empreendimento": "Edifício Teste",
                                    "construtora": "Construtora ABC",
                                }
                            }
                        }
                    }
                ]
            }
        ]
        
        # Mock de itens normalizados
        mock_items = [
            {
                "tipo": "point_rj45",
                "quantidade": 10,
                "pavimento": "Térreo",
                "cabos": ["cat6"],
            }
        ]
        
        # Consolida
        consolidator = DataConsolidator()
        master_data = consolidator.consolidate(mock_extractions, mock_items)
        
        # Verificações
        assert "obra" in master_data
        assert "itens" in master_data
        assert len(master_data["itens"]) == 1
        assert "dados" in master_data.get("servicos", [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])






