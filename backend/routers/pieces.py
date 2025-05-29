from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
from typing import List
from models.piece import PieceCreate, PieceRead, PieceUpdate
from services.neo4j import get_session

router = APIRouter(prefix="/puzzle/{puzzle_id}/pieces", tags=["Pieces"])


@router.post("/bulk", response_model=List[PieceRead])
def create_pieces_bulk(
    puzzle_id: UUID,
    pieces: List[PieceCreate]
):
    """
    Crea varias piezas en un solo request.
    - Verifica que el Puzzle exista.
    - Crea nodos Piece, relaciones y retorna las piezas creadas.
    """
    created = []
    with get_session() as session:
        # 1) validar que exista el puzzle
        if not session.run(
            "MATCH (p:Puzzle {puzzleId:$id}) RETURN p",
            {"id": str(puzzle_id)}
        ).single():
            raise HTTPException(status_code=404, detail="Puzzle no encontrado")

        # 2) crear cada pieza y relacionarla
        for pc in pieces:
            rec = session.run(
                """
                MATCH (p:Puzzle {puzzleId: $puzzle_id})
                CREATE (piece:Piece {
                  pieceId:          randomUUID(),
                  sequenceNumber:   $sequenceNumber,
                  pieceOrientation: $pieceOrientation,
                  group:            $group,
                  status:           $status
                })
                MERGE (p)-[:HAS_PIECE]->(piece)
                RETURN piece {.*, puzzleId: p.puzzleId} AS piece
                """,
                {**pc.model_dump(), "puzzle_id": str(puzzle_id)}
            ).single()

            created.append(PieceRead(**rec["piece"]))

    return created


@router.get("/", response_model=List[PieceRead])
def list_pieces(
    puzzle_id: UUID = Path(..., description="UUID del puzzle")
):
    """Devuelve todas las piezas de un Puzzle dado."""
    with get_session() as session:
        result = session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzle_id})
                  -[:HAS_PIECE]->(piece:Piece)
            RETURN piece {.*, puzzleId: p.puzzleId} AS piece
            """,
            {"puzzle_id": str(puzzle_id)}
        )
        return [PieceRead(**rec["piece"]) for rec in result]


@router.get("/{piece_id}", response_model=PieceRead)
def get_piece(
    puzzle_id: UUID = Path(...),
    piece_id:  UUID = Path(..., description="UUID de la pieza")
):
    """Lee una pieza por su UUID."""
    with get_session() as session:
        rec = session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzle_id})
                  -[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            RETURN piece {.*, puzzleId: p.puzzleId} AS piece
            """,
            {
                "puzzle_id": str(puzzle_id),
                "piece_id":  str(piece_id)
            }
        ).single()

        if not rec:
            raise HTTPException(status_code=404, detail="Pieza no encontrada")

        return PieceRead(**rec["piece"])


@router.patch("/{piece_id}", response_model=PieceRead)
def update_piece(
    puzzle_id: UUID = Path(...),
    piece_id:  UUID = Path(...),
    payload:   PieceUpdate = ...
):
    """Actualiza orientation, group o status de una pieza."""
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    with get_session() as session:
        rec = session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzle_id})
                  -[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            SET piece += $fields
            RETURN piece {.*, puzzleId: p.puzzleId} AS piece
            """,
            {
                "puzzle_id": str(puzzle_id),
                "piece_id":  str(piece_id),
                "fields":    fields
            }
        ).single()

        if not rec:
            raise HTTPException(status_code=404, detail="Pieza no encontrada")

        return PieceRead(**rec["piece"])


@router.delete("/{piece_id}", status_code=204)
def delete_piece(
    puzzle_id: UUID = Path(...),
    piece_id:  UUID = Path(...)
):
    """Elimina el nodo Piece y sus relaciones."""
    with get_session() as session:
        rec = session.run(
            """
            MATCH (p:Puzzle {puzzleId: $puzzle_id})
                  -[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            DETACH DELETE piece
            RETURN COUNT(piece) AS deleted
            """,
            {
                "puzzle_id": str(puzzle_id),
                "piece_id":  str(piece_id)
            }
        ).single()

        if not rec or rec["deleted"] == 0:
            raise HTTPException(status_code=404, detail="Pieza no encontrada")
    # status_code=204 implica body vacío
    return None