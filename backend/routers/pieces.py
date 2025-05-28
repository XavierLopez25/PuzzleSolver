from fastapi import APIRouter, HTTPException
from typing import List
from models.piece import PieceCreate, PieceRead, PieceUpdate
from services.neo4j import get_session

router = APIRouter(prefix="/pieces", tags=["Pieces"])


@router.post("/bulk", response_model=List[PieceRead])
def create_pieces_bulk(puzzle_id: str, pieces: List[PieceCreate]):
    """
    Crea varias piezas en un solo request.
    - Verifica que el Puzzle exista.
    - Crea nodos Piece y relaciones (Puzzle)-[:HAS_PIECE]->(Piece).
    """
    created_pieces = []
    with get_session() as session:
        puzzle_exists = session.run(
            "MATCH (p:Puzzle {puzzleId: $puzzle_id}) RETURN p",
            puzzle_id=puzzle_id
        ).single()

        if not puzzle_exists:
            raise HTTPException(status_code=404, detail="Puzzle no encontrado.")

        for piece in pieces:
            result = session.run("""
                MATCH (p:Puzzle {puzzleId: $puzzle_id})
                CREATE (piece:Piece {
                    pieceId: randomUUID(),
                    sequenceNumber: $sequenceNumber,
                    pieceOrientation: $pieceOrientation,
                    group: $group
                })
                RETURN piece
            """, puzzle_id=puzzle_id, **piece.dict()).single()

            created_pieces.append(PieceRead(**dict(result["piece"])))

    return created_pieces


@router.get("/", response_model=List[PieceRead])
def list_pieces(puzzle_id: str):
    """Devuelve todas las piezas de un Puzzle dado."""
    with get_session() as session:
        result = session.run("""
            MATCH (p:Puzzle {puzzleId: $puzzle_id})-[:HAS_PIECE]->(piece:Piece)
            RETURN piece
        """, puzzle_id=puzzle_id)

        return [
            PieceRead(**dict(record["piece"]))
            for record in result
        ]


@router.get("/{piece_id}", response_model=PieceRead)
def get_piece(puzzle_id: str, piece_id: str):
    """Lee una pieza por su ID."""
    with get_session() as session:
        result = session.run("""
            MATCH (p:Puzzle {puzzleId: $puzzle_id})-[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            RETURN piece
        """, puzzle_id=puzzle_id, piece_id=piece_id).single()

        if not result:
            raise HTTPException(status_code=404, detail="Pieza no encontrada.")

        return PieceRead(**dict(result["piece"]))


@router.patch("/{piece_id}", response_model=PieceRead)
def update_piece(puzzle_id: str, piece_id: str, payload: PieceUpdate):
    """Actualiza orientation, group o status de una pieza."""
    with get_session() as session:
        result = session.run("""
            MATCH (p:Puzzle {puzzleId: $puzzle_id})-[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            SET piece += $fields
            RETURN piece
        """, puzzle_id=puzzle_id, piece_id=piece_id, fields=payload.dict(exclude_unset=True)).single()

        if not result:
            raise HTTPException(status_code=404, detail="Pieza no encontrada.")

        return PieceRead(**dict(result["piece"]))


@router.delete("/{piece_id}", status_code=204)
def delete_piece(puzzle_id: str, piece_id: str):
    """Elimina el nodo Piece y sus relaciones."""
    with get_session() as session:
        result = session.run("""
            MATCH (p:Puzzle {puzzleId: $puzzle_id})-[:HAS_PIECE]->(piece:Piece {pieceId: $piece_id})
            DETACH DELETE piece
            RETURN COUNT(piece) AS deleted
        """, puzzle_id=puzzle_id, piece_id=piece_id).single()

        if result["deleted"] == 0:
            raise HTTPException(status_code=404, detail="Pieza no encontrada.")