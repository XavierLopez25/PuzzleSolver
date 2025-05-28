# Archivo: backend/models/piece.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Modelo base que contiene los atributos comunes de una pieza (Piece)
class PieceBase(BaseModel):
    sequenceNumber: int  
    pieceOrientation: int  
    group: int  

# Modelo utilizado al crear una nueva pieza (hereda todos los campos de PieceBase)
class PieceCreate(PieceBase):
    """Datos necesarios al crear una Piece."""
    pass  

# Modelo utilizado para actualizar parcialmente una pieza existente
class PieceUpdate(BaseModel):
    pieceOrientation: Optional[int]  # Se puede actualizar la orientación de la pieza
    group: Optional[int]  # Se puede actualizar el grupo al que pertenece

# Modelo utilizado para leer o devolver los datos de una pieza
class PieceRead(PieceBase):
    pieceId: UUID  
