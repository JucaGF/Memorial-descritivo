#!/usr/bin/env python3
"""
Script para preparar imagens de cabeçalho e rodapé com largura total da página.

Este script ESTICA/REDIMENSIONA as imagens horizontalmente para que elas
ocupem exatamente a largura de uma página A4 (21cm), mantendo a altura original.
"""

from PIL import Image
from pathlib import Path


def resize_image_to_full_width(input_path: Path, output_path: Path, target_width_cm: float = 21.0):
    """Redimensiona a imagem proporcionalmente para atingir largura alvo.
    
    MANTÉM A PROPORÇÃO (aspect ratio) da imagem original.
    
    Args:
        input_path: Caminho da imagem original
        output_path: Caminho para salvar imagem processada
        target_width_cm: Largura alvo em centímetros (21cm = A4)
    """
    # Abre imagem original
    img = Image.open(input_path)
    
    # Dimensões originais
    orig_width, orig_height = img.size
    print(f"Imagem original: {orig_width}x{orig_height}px")
    
    # Calcula largura alvo em pixels (assumindo 300 DPI)
    # 1 polegada = 2.54 cm
    # 21 cm = 21/2.54 polegadas = ~8.27 polegadas
    # 8.27 polegadas * 300 DPI = ~2480 pixels
    dpi = 300
    target_width_px = int((target_width_cm / 2.54) * dpi)
    print(f"Largura alvo: {target_width_px}px (para {target_width_cm}cm @ {dpi} DPI)")
    
    # Calcula aspect ratio e nova altura proporcional
    aspect_ratio = orig_height / orig_width
    target_height_px = int(target_width_px * aspect_ratio)
    
    print(f"Aspect ratio: {aspect_ratio:.4f}")
    print(f"✓ Redimensionando proporcionalmente:")
    print(f"  Largura: {orig_width}px → {target_width_px}px")
    print(f"  Altura: {orig_height}px → {target_height_px}px")
    
    # Redimensiona mantendo proporção
    new_img = img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
    
    # Salva com DPI correto
    new_img.save(output_path, dpi=(dpi, dpi))
    print(f"✓ Imagem salva: {output_path}")
    print(f"  Nova dimensão: {new_img.size[0]}x{new_img.size[1]}px\n")


def main():
    """Processa as imagens de cabeçalho e rodapé."""
    assets_dir = Path(__file__).parent / "assets"
    
    print("=" * 60)
    print("Preparando imagens de cabeçalho e rodapé para largura A4")
    print("=" * 60)
    print()
    
    # Processa cabeçalho
    header_input = assets_dir / "header_tecpred.png"
    header_output = assets_dir / "header_tecpred_fullwidth.png"
    
    if header_input.exists():
        print("📄 CABEÇALHO:")
        resize_image_to_full_width(header_input, header_output)
    else:
        print(f"⚠️  Arquivo não encontrado: {header_input}")
    
    # Processa rodapé
    footer_input = assets_dir / "footer_tecpred.png"
    footer_output = assets_dir / "footer_tecpred_fullwidth.png"
    
    if footer_input.exists():
        print("📄 RODAPÉ:")
        resize_image_to_full_width(footer_input, footer_output)
    else:
        print(f"⚠️  Arquivo não encontrado: {footer_input}")
    
    print("=" * 60)
    print("✓ Processamento concluído!")
    print()
    print("Agora atualize o código para usar:")
    print("  - header_tecpred_fullwidth.png")
    print("  - footer_tecpred_fullwidth.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
