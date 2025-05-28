# Archivo: backend/models/puzzle.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Modelo base que contiene los atributos comunes de un Puzzle
class PuzzleBase(BaseModel):
    puzzleTypeIsRegular: bool  # Indica si el rompecabezas es regular
    puzzleTheme: str  # Tema del rompecabezas (ej. "Paisajes", "Animales", etc.)
    puzzleBrand: str  # Marca del rompecabezas
    puzzlePieceQty: int  # Cantidad total de piezas del rompecabezas
    puzzleMaterial: str  # Material del rompecabezas (ej. "Cartón", "Madera", etc.)
    row_size: Optional[int] = None  # Solo para puzzles regulares (número de piezas por fila)
    column_size: Optional[int] = None  # Solo para puzzles regulares (número de columnas)


# Modelo utilizado al crear un nuevo Puzzle
class PuzzleCreate(PuzzleBase):
    """Datos necesarios al crear un Puzzle."""
    pass

# Modelo utilizado para actualizar un Puzzle existente (campos opcionales)
class PuzzleUpdate(BaseModel):
    puzzleTypeIsRegular: Optional[bool]
    puzzleTheme: Optional[str]
    puzzleBrand: Optional[str]
    puzzlePieceQty: Optional[int]
    puzzleMaterial: Optional[str]
    row_size: Optional[int]

# Modelo utilizado para leer o devolver un Puzzle (incluye el ID)
class PuzzleRead(PuzzleBase):
    puzzleId: UUID  # Identificador único del Puzzle