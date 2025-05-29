from fastapi import APIRouter, HTTPException, Path
from typing import List
from uuid import UUID, uuid4

from models.puzzle import PuzzleCreate, PuzzleRead, PuzzleUpdate
from services.neo4j import get_session

router = APIRouter(
    prefix="/puzzles",
    tags=["puzzles"]
)

@router.post("/", response_model=PuzzleRead)
def create_puzzle(payload: PuzzleCreate):
    """
    Crea un nuevo Puzzle.
    - Genera UUID
    - Inserta nodo con propiedades (sin column_size)
    """
    pid = str(uuid4())
    with get_session() as session:
        rec = session.run(
            """
            CREATE (p:Puzzle {
              puzzleId:            $puzzleId,
              puzzleTypeIsRegular: $puzzleTypeIsRegular,
              puzzleTheme:         $puzzleTheme,
              puzzleBrand:         $puzzleBrand,
              puzzlePieceQty:      $puzzlePieceQty,
              puzzleMaterial:      $puzzleMaterial,
              row_size:            $row_size
            })
            RETURN p {.*, puzzleId: p.puzzleId} AS p
            """,
            {**payload.model_dump(), "puzzleId": pid}
        ).single()

        if not rec:
            raise HTTPException(status_code=500, detail="No se pudo crear el puzzle")

        return PuzzleRead(**rec["p"])


@router.get("/{puzzle_id}", response_model=PuzzleRead)
def get_puzzle(
    puzzle_id: UUID = Path(..., description="UUID del puzzle")
):
    """Recupera un Puzzle por su UUID."""
    with get_session() as session:
        rec = session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzleId})
            RETURN p {.*, puzzleId: p.puzzleId} AS p
            """,
            {"puzzleId": str(puzzle_id)}
        ).single()

        if not rec:
            raise HTTPException(status_code=404, detail="Puzzle no encontrado")

        return PuzzleRead(**rec["p"])


@router.get("/", response_model=List[PuzzleRead])
def list_puzzles():
    """Lista todos los puzzles con sus propiedades correctamente tipadas."""
    with get_session() as session:
        result = session.run(
            """
            MATCH (p:Puzzle)
            WHERE p.puzzleId IS NOT NULL
            RETURN
              p.puzzleId            AS puzzleId,
              p.puzzleTypeIsRegular AS puzzleTypeIsRegular,
              p.puzzleTheme         AS puzzleTheme,
              p.puzzleBrand         AS puzzleBrand,
              p.puzzlePieceQty      AS puzzlePieceQty,
              p.puzzleMaterial      AS puzzleMaterial,
              p.row_size            AS row_size
            """
        )
        return [PuzzleRead(**record) for record in result]

@router.patch("/{puzzle_id}", response_model=PuzzleRead)
def update_puzzle(
    puzzle_id: UUID = Path(...),
    payload:   PuzzleUpdate = ...
):
    """Actualización parcial de un Puzzle."""
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    # Construye dinámicamente el SET
    set_str = ", ".join(f"p.{k} = ${k}" for k in fields)
    params  = {"puzzleId": str(puzzle_id), **fields}

    with get_session() as session:
        rec = session.run(
            f"""
            MATCH (p:Puzzle {{puzzleId: $puzzleId}})
            SET {set_str}
            RETURN p {{.*, puzzleId: p.puzzleId}} AS p
            """,
            params
        ).single()

        if not rec:
            raise HTTPException(status_code=404, detail="Puzzle no encontrado")

        return PuzzleRead(**rec["p"])


@router.delete("/{puzzle_id}", status_code=204)
def delete_puzzle(
    puzzle_id: UUID = Path(...)
):
    """Elimina un Puzzle y sus relaciones."""
    with get_session() as session:
        session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzleId})
            DETACH DELETE p
            """,
            {"puzzleId": str(puzzle_id)}
        )
    return None