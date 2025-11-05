"""Utilitários de Computer Vision."""

import cv2
import numpy as np
from typing import Tuple, Optional


def preprocess_image(
    image: np.ndarray,
    blur_kernel: int = 5,
    threshold_block: int = 11,
    threshold_c: int = 2,
) -> np.ndarray:
    """Preprocessa imagem para OCR."""
    
    # Grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Blur para reduzir ruído
    blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
    
    # Threshold adaptativo
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        threshold_block,
        threshold_c,
    )
    
    return thresh


def deskew_image(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """Corrige inclinação da imagem."""
    
    coords = np.column_stack(np.where(image > 0))
    if len(coords) == 0:
        return image, 0.0
    
    angle = cv2.minAreaRect(coords)[-1]
    
    # Corrige ângulo
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Rotaciona
    if abs(angle) > 0.5:  # Só rotaciona se necessário
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rotated, angle
    
    return image, 0.0


def extract_roi(
    image: np.ndarray,
    x_start: float,
    y_start: float,
    x_end: float = 1.0,
    y_end: float = 1.0,
) -> np.ndarray:
    """Extrai ROI (região de interesse) da imagem.
    
    Args:
        image: Imagem original
        x_start: Início X (proporção 0-1)
        y_start: Início Y (proporção 0-1)
        x_end: Fim X (proporção 0-1)
        y_end: Fim Y (proporção 0-1)
    """
    h, w = image.shape[:2]
    
    x1 = int(w * x_start)
    y1 = int(h * y_start)
    x2 = int(w * x_end)
    y2 = int(h * y_end)
    
    return image[y1:y2, x1:x2]


def detect_tables(image: np.ndarray) -> list:
    """Detecta tabelas na imagem usando linhas horizontais/verticais."""
    
    # Preprocessa
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Detecta linhas horizontais
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Detecta linhas verticais
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # Combina
    table_mask = cv2.add(horizontal, vertical)
    
    # Encontra contornos
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtra contornos por área
    tables = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > 5000:  # Área mínima para ser considerada tabela
            tables.append((x, y, w, h))
    
    return tables


def enhance_for_ocr(image: np.ndarray) -> np.ndarray:
    """Melhora imagem especificamente para OCR."""
    
    # Preprocessa
    processed = preprocess_image(image)
    
    # Dilata levemente para conectar letras quebradas
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(processed, kernel, iterations=1)
    
    # Remove ruído pequeno
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
    
    return cleaned






