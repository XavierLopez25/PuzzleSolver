# Archivo: backend/models/puzzle.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Modelo base que contiene los atributos comunes de un Puzzle
class PuzzleBase(BaseModel):
    name: str  
    description: Optional[str] = None  

# Modelo utilizado al crear un nuevo Puzzle (hereda de PuzzleBase)
class PuzzleCreate(PuzzleBase):
    """Datos necesarios al crear un Puzzle."""
    pass  # No se agregan campos adicionales, solo se reutilizan los de PuzzleBase

# Modelo utilizado para actualizar un Puzzle existente
class PuzzleUpdate(BaseModel):
    name: Optional[str]  
    description: Optional[str] 

# Modelo utilizado para leer o devolver un Puzzle
class PuzzleRead(PuzzleBase):
    puzzleId: UUID  
