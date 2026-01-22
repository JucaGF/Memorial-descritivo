"""Interface Streamlit para Memorial Maker."""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import tempfile
import shutil
import uuid
from datetime import datetime

from memorial_maker.config import settings, MemorialType
from memorial_maker.utils.io_paths import setup_output_dirs, get_project_name
from memorial_maker.extract.unstructured_extract import extract_all_pdfs, extract_text_from_elements
from memorial_maker.normalize.canonical_map import ItemExtractor, normalize_all_items
from memorial_maker.normalize.consolidate import consolidate_and_export
from memorial_maker.rag.index_style import index_models
from memorial_maker.rag.generate_sections import SectionGenerator
from memorial_maker.writer.write_docx import write_memorial_docx

# Configure logging to show in terminal
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout, 
    force=True
)


# Configuração da página
st.set_page_config(
    page_title="Memorial Maker",
    page_icon="📄",
    layout="wide",
)


def init_session_state():
    """Inicializa estado da sessão."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "generated" not in st.session_state:
        st.session_state.generated = False
    if "output_path" not in st.session_state:
        st.session_state.output_path = None
    if "master_data" not in st.session_state:
        st.session_state.master_data = None
    if "sections" not in st.session_state:
        st.session_state.sections = None


def save_uploaded_files(uploaded_files, target_dir):
    """Salva arquivos uploaded em diretório temporário."""
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    
    for uploaded_file in uploaded_files:
        file_path = target_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        paths.append(file_path)
    
    return paths


def main():
    """Interface principal."""
    init_session_state()
    
    # Cabeçalho
    st.title("📄 Memorial Maker")
    
    # Memorial type selector
    memorial_type_display = st.selectbox(
        "Tipo de Memorial",
        ["Telecomunicações", "Elétrico"],
        key="memorial_type_display",
        index=0,
    )
    
    # Map display name to internal type
    memorial_type = MemorialType.ELECTRICAL if memorial_type_display == "Elétrico" else MemorialType.TELECOM
    
    # Update title based on type
    if memorial_type == MemorialType.ELECTRICAL:
        st.markdown("**Geração automática de Memorial Descritivo Elétrico**")
    else:
        st.markdown("**Geração automática de Memorial Descritivo de Telecomunicações**")
    
    st.markdown("---")
    
    # Upload de arquivos
    st.header("📤 1. Upload de Arquivos")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("PDFs de Projeto")
        pdf_files = st.file_uploader(
            "Plantas, cortes, legendas",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdfs",
        )
        if pdf_files:
            st.success(f"{len(pdf_files)} PDF(s) carregado(s)")
    
    with col2:
        st.subheader("Memoriais-Modelo")
        model_files = st.file_uploader(
            "DOC/DOCX de referência (opcional)",
            type=["doc", "docx"],
            accept_multiple_files=True,
            key="models",
        )
        if model_files:
            st.info(f"{len(model_files)} modelo(s) carregado(s)")
    
    # Info sobre logo
    st.info("🏢 Logo TecPred será incluído automaticamente no memorial")
    st.info("📋 Dados da obra (empreendimento, construtora, endereço) serão extraídos automaticamente do carimbo das plantas")
    
    st.markdown("---")
    
    # Botão de geração
    st.header("🚀 2. Gerar Memorial")
    
    if not pdf_files:
        st.warning("⚠️ Por favor, faça upload de pelo menos 1 PDF de projeto")
        return
    
    if not settings.openai_api_key:
        st.error("❌ Configure sua OpenAI API Key no arquivo .env")
        return
    
    # Verifica dependências críticas
    unstructured_error = False
    try:
        from memorial_maker.extract.unstructured_extract import UNSTRUCTURED_AVAILABLE
        if not UNSTRUCTURED_AVAILABLE:
            st.error("❌ **ERRO CRÍTICO**: Unstructured.io não está instalado. A extração de PDFs é impossível sem esta dependência. "
                     "Por favor, execute: `pip install unstructured[pdf]`")
            unstructured_error = True
    except Exception as e:
        st.error(f"❌ **ERRO CRÍTICO**: Falha ao carregar Unstructured: {e}")
        unstructured_error = True
    
    langchain_error = False
    try:
        from memorial_maker.rag.generate_sections import LANGCHAIN_AVAILABLE
        if not LANGCHAIN_AVAILABLE:
            st.warning("⚠️ **AVISO**: LangChain não está instalado. A geração de seções não funcionará.")
            langchain_error = True
    except:
        pass
    
    if unstructured_error:
        st.button("🎯 Gerar Memorial Descritivo", type="primary", use_container_width=True, disabled=True, 
                  help="Instale o Unstructured para habilitar esta função")
    elif st.button("🎯 Gerar Memorial Descritivo", type="primary", use_container_width=True):
        generate_memorial(pdf_files, model_files, settings.parallel_execution, memorial_type.value)
    
    # Resultados
    if st.session_state.generated:
        show_results()


def generate_memorial(pdf_files, model_files, parallel, memorial_type: str = "telecom"):
    """Executa pipeline de geração.
    
    Args:
        pdf_files: Lista de arquivos PDF
        model_files: Lista de arquivos modelo (opcional)
        parallel: Se True, executa em paralelo
        memorial_type: Tipo de memorial ("telecom" ou "eletrico")
    """
    
    # Diretório temporário da sessão
    runtime_dir = Path(tempfile.gettempdir()) / "memorial_maker" / st.session_state.session_id
    runtime_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_dir = runtime_dir / "pdfs"
    models_dir = runtime_dir / "models"
    
    with st.spinner("⏳ Processando..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Salva uploads
            status_text.text("📥 Salvando arquivos...")
            pdf_paths = save_uploaded_files(pdf_files, pdf_dir)
            
            if model_files:
                model_paths = save_uploaded_files(model_files, models_dir)
            else:
                model_paths = []
            
            # Logo TecPred padrão
            logo_path = Path(__file__).parent.parent / "assets" / "logo_tecpred.png"
            if not logo_path.exists():
                logo_path = None  # Se não existir, continua sem logo
            
            progress_bar.progress(10)
            
            # Setup output
            out_dir = runtime_dir / "out"
            dirs = setup_output_dirs(out_dir)
            
            project_name = get_project_name(pdf_paths)
            
            # 1. Extração com Unstructured
            status_text.text("📄 Extraindo dados dos PDFs com Unstructured...")
            
            def update_extraction_progress(current, total):
                status_text.text(f"📄 Extraindo PDF {current}/{total}...")
                # Map 0-100% of extraction to 10-40% of overall progress
                progress = 10 + int((current / total) * 30)
                progress_bar.progress(progress)
                
            extractions = extract_all_pdfs(
                pdf_dir, 
                dirs["extraido"], 
                memorial_type=memorial_type,
                progress_callback=update_extraction_progress
            )
            progress_bar.progress(40)
            
            # 2. Normalização
            status_text.text("🔧 Normalizando dados...")
            extractor = ItemExtractor()
            raw_items = []
            
            for extraction in extractions:
                # Extrai texto de todos os elementos
                full_text = extract_text_from_elements(extraction)
                
                # Extrai itens do texto
                items = extractor.extract_from_text(full_text, {
                    "filename": extraction.get("filename", ""),
                })
                raw_items.extend(items)
                
                # Processa tabelas estruturadas
                for table in extraction.get("tables", []):
                    table_text = table.get("text", "")
                    items = extractor.extract_from_text(table_text, {
                        "filename": extraction.get("filename", ""),
                        "source": "table",
                    })
                    raw_items.extend(items)
            
            normalized_items = normalize_all_items(raw_items)
            progress_bar.progress(45)
            
            # 3. Consolidação (inclui extração automática de carimbo)
            status_text.text("📊 Consolidando e exportando CSVs...")
            master_data = consolidate_and_export(
                extractions,
                normalized_items,
                dirs["extraido"],
            )
            # Add extractions to master_data for electrical structured extraction
            master_data["extractions"] = extractions
            progress_bar.progress(55)
            
            # 4. Indexação
            if model_paths:
                status_text.text("🔍 Indexando memoriais-modelo...")
                style_indexer = index_models(models_dir)
                # Se indexação falhou, cria indexador vazio
                if style_indexer is None:
                    from memorial_maker.rag.index_style import StyleIndexer
                    style_indexer = StyleIndexer()
            else:
                from memorial_maker.rag.index_style import StyleIndexer
                style_indexer = StyleIndexer()
            
            progress_bar.progress(65)
            
            # 5. Geração de seções
            status_text.text("✍️ Gerando seções com LLM...")
            prompts_dir = Path(__file__).parent.parent / "memorial_maker" / "rag" / "prompts"
            generator = SectionGenerator(style_indexer, prompts_dir, memorial_type=memorial_type)
            
            sections = generator.generate_all_sections(master_data, parallel=parallel)
            progress_bar.progress(85)
            
            # 6. Escrita DOCX
            status_text.text("📝 Escrevendo memorial DOCX...")
            output_path = write_memorial_docx(
                sections,
                master_data,
                dirs["memorial"],
                logo_path=logo_path,
                project_name=project_name,
                memorial_type=memorial_type,
            )
            progress_bar.progress(100)
            
            # Armazena resultados
            st.session_state.generated = True
            st.session_state.output_path = output_path
            st.session_state.master_data = master_data
            st.session_state.sections = sections
            
            status_text.text("")
            st.success("✅ Memorial gerado com sucesso!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Erro durante geração: {str(e)}")
            st.exception(e)
            progress_bar.progress(0)


def show_results():
    """Exibe resultados da geração."""
    
    st.markdown("---")
    st.header("📥 3. Resultados")
    
    # Download DOCX
    if st.session_state.output_path:
        output_path = Path(st.session_state.output_path)
        
        if output_path.exists():
            with open(output_path, "rb") as f:
                docx_bytes = f.read()
            
            st.download_button(
                label="📥 Baixar Memorial (DOCX)",
                data=docx_bytes,
                file_name=output_path.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
    
    # Prévia das seções
    with st.expander("👁️ Prévia das Seções", expanded=False):
        if st.session_state.sections:
            sections = st.session_state.sections
            
            section_names = {
                "s1_introducao": "1. Introdução",
                "s2_dados_obra": "2. Dados da Obra",
                "s3_normas": "3. Normas Técnicas",
                "s4_servicos": "4. Serviços Contemplados",
                "s4_1_voz": "4.1. Voz",
                "s4_2_dados": "4.2. Dados",
                "s4_3_video": "4.3. Vídeo",
                "s4_4_intercom": "4.4. Intercomunicação",
                "s4_5_monitoramento": "4.5. Monitoramento",
                "s5_sala_monitoramento": "5. Sala de Monitoramento",
                "s6_passivos_ativos": "6. Elementos Passivos e Ativos",
                "s7_testes_aceitacao": "7. Testes e Aceitação",
            }
            
            for section_id, title in section_names.items():
                content = sections.get(section_id, "")
                if content:
                    st.markdown(f"**{title}**")
                    st.text_area(
                        label=title,
                        value=content,
                        height=150,
                        key=f"preview_{section_id}",
                        disabled=True,
                        label_visibility="collapsed",
                    )
                    st.markdown("---")
    
    # CSVs
    with st.expander("📊 Dados Extraídos (CSVs)", expanded=False):
        if st.session_state.output_path:
            extraido_dir = Path(st.session_state.output_path).parent.parent / "extraido"
            
            csv_files = list(extraido_dir.glob("*.csv"))
            
            for csv_file in csv_files:
                st.markdown(f"**{csv_file.name}**")
                
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao ler {csv_file.name}: {e}")


if __name__ == "__main__":
    main()




