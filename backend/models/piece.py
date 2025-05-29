# Archivo: backend/models/piece.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Modelo base con los campos comunes de una pieza de puzzle
class PieceBase(BaseModel):
    sequenceNumber: int        # Número secuencial que indica la posición de la pieza
    pieceOrientation: int      # Orientación de la pieza en grados (ejemplo: 90°)
    group: int                 # Grupo al que pertenece la pieza (ejemplo: grupo 3)
    status: Optional[str] = 'present' # 'present' | 'missing'

# Modelo usado para crear una nueva pieza
class PieceCreate(PieceBase):
    """Datos necesarios al crear una Piece."""
    pass

# Modelo usado para actualizar una pieza existente
class PieceUpdate(BaseModel):
    pieceOrientation: Optional[int]  = None # Permite actualizar la orientación
    group: Optional[int]       = None        # Permite actualizar el grupo
    status: Optional[str] = None # 'present' | 'missing'


# Modelo usado para leer una pieza (incluye el ID único)
class PieceRead(PieceBase):
    pieceId: UUID  # Identificador único de la pieza
    puzzleId: str  # ID del puzzle al que pertenece la pieza
