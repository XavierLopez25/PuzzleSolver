# 3ra persona: backend/routers/puzzles.py
# ---------------------------------------
# from fastapi import APIRouter, HTTPException, Depends
# from typing import List
# from backend.models.puzzle import PuzzleCreate, PuzzleRead, PuzzleUpdate
# from backend.services.neo4j import get_session
#
# router = APIRouter(
#     prefix="/puzzles",
#     tags=["puzzles"]
# )
#
# @router.post("/", response_model=PuzzleRead)
# def create_puzzle(payload: PuzzleCreate):
#     """Crea un nuevo Puzzle con sus propiedades básicas."""
#     ...
#
# @router.get("/", response_model=List[PuzzleRead])
# def list_puzzles():
#     """Lista todos los Puzzles existentes."""
#     ...
#
# @router.get("/{puzzle_id}", response_model=PuzzleRead)
# def get_puzzle(puzzle_id: str):
#     """Obtiene un Puzzle por su UUID."""
#     ...
#
# @router.patch("/{puzzle_id}", response_model=PuzzleRead)
# def update_puzzle(puzzle_id: str, payload: PuzzleUpdate):
#     """Modifica propiedades de un Puzzle (tema, row_size, etc.)."""
#     ...
#
# @router.delete("/{puzzle_id}", status_code=204)
# def delete_puzzle(puzzle_id: str):
#     """Elimina el nodo Puzzle y sus relaciones."""
#     ...