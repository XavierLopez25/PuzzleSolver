from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID, uuid4

from models.puzzle import PuzzleCreate, PuzzleRead, PuzzleUpdate
from services.neo4j import get_session

router = APIRouter(
    prefix="/puzzles",
    tags=["puzzles"]
)

# CREATE Puzzle
@router.post("/", response_model=PuzzleRead)
async def create_puzzle(puzzle: PuzzleCreate):
    query = """
    CREATE (p:Puzzle {
        puzzleId: $puzzleId,
        puzzleTypeIsRegular: $puzzleTypeIsRegular,
        puzzleTheme: $puzzleTheme,
        puzzleBrand: $puzzleBrand,
        puzzlePieceQty: $puzzlePieceQty,
        puzzleMaterial: $puzzleMaterial,
        row_size: $row_size,
        column_size: $column_size
    })
    RETURN p.puzzleId AS puzzleId,
           p.puzzleTypeIsRegular AS puzzleTypeIsRegular,
           p.puzzleTheme AS puzzleTheme,
           p.puzzleBrand AS puzzleBrand,
           p.puzzlePieceQty AS puzzlePieceQty,
           p.puzzleMaterial AS puzzleMaterial,
           p.row_size AS row_size,
           p.column_size AS column_size
    """
    puzzle_id = str(uuid4())  # Generar UUID para el puzzle
    with get_session() as session:
        result = session.run(
            query,
            puzzleId=puzzle_id,
            puzzleTypeIsRegular=puzzle.puzzleTypeIsRegular,
            puzzleTheme=puzzle.puzzleTheme,
            puzzleBrand=puzzle.puzzleBrand,
            puzzlePieceQty=puzzle.puzzlePieceQty,
            puzzleMaterial=puzzle.puzzleMaterial,
            row_size=puzzle.row_size,
            column_size=puzzle.column_size
        )
        record = result.single()
        if not record:
            raise HTTPException(status_code=500, detail="No se pudo crear el puzzle")
        return PuzzleRead(
            puzzleId=record["puzzleId"],
            puzzleTypeIsRegular=record["puzzleTypeIsRegular"],
            puzzleTheme=record["puzzleTheme"],
            puzzleBrand=record["puzzleBrand"],
            puzzlePieceQty=record["puzzlePieceQty"],
            puzzleMaterial=record["puzzleMaterial"],
            row_size=record["row_size"],
            column_size=record["column_size"],
        )

# READ Puzzle por ID
@router.get("/{puzzle_id}", response_model=PuzzleRead)
async def get_puzzle(puzzle_id: UUID):
    query = """
    MATCH (p:Puzzle {puzzleId: $puzzleId})
    RETURN p.puzzleId AS puzzleId,
           p.puzzleTypeIsRegular AS puzzleTypeIsRegular,
           p.puzzleTheme AS puzzleTheme,
           p.puzzleBrand AS puzzleBrand,
           p.puzzlePieceQty AS puzzlePieceQty,
           p.puzzleMaterial AS puzzleMaterial,
           p.row_size AS row_size,
           p.column_size AS column_size
    """
    with get_session() as session:
        result = session.run(query, puzzleId=str(puzzle_id))
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Puzzle no encontrado")
        return PuzzleRead(
            puzzleId=record["puzzleId"],
            puzzleTypeIsRegular=record["puzzleTypeIsRegular"],
            puzzleTheme=record["puzzleTheme"],
            puzzleBrand=record["puzzleBrand"],
            puzzlePieceQty=record["puzzlePieceQty"],
            puzzleMaterial=record["puzzleMaterial"],
            row_size=record["row_size"],
            column_size=record["column_size"],
        )

# LISTAR todos los puzzles
@router.get("/", response_model=List[PuzzleRead])
async def list_puzzles():
    query = """
    MATCH (p:Puzzle)
    RETURN p.puzzleId AS puzzleId,
           p.puzzleTypeIsRegular AS puzzleTypeIsRegular,
           p.puzzleTheme AS puzzleTheme,
           p.puzzleBrand AS puzzleBrand,
           p.puzzlePieceQty AS puzzlePieceQty,
           p.puzzleMaterial AS puzzleMaterial,
           p.row_size AS row_size,
           p.column_size AS column_size
    """
    with get_session() as session:
        result = session.run(query)
        puzzles = []
        for record in result:
            puzzles.append(PuzzleRead(
                puzzleId=record["puzzleId"],
                puzzleTypeIsRegular=record["puzzleTypeIsRegular"],
                puzzleTheme=record["puzzleTheme"],
                puzzleBrand=record["puzzleBrand"],
                puzzlePieceQty=record["puzzlePieceQty"],
                puzzleMaterial=record["puzzleMaterial"],
                row_size=record["row_size"],
                column_size=record["column_size"],
            ))
        return puzzles

# UPDATE Puzzle
@router.put("/{puzzle_id}", response_model=PuzzleRead)
async def update_puzzle(puzzle_id: UUID, puzzle: PuzzleUpdate):
    # Para update parcial, construimos dinámicamente el SET
    set_clauses = []
    params = {"puzzleId": str(puzzle_id)}
    for field, value in puzzle.dict(exclude_unset=True).items():
        set_clauses.append(f"p.{field} = ${field}")
        params[field] = value
    if not set_clauses:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")
    set_query = ", ".join(set_clauses)

    query = f"""
    MATCH (p:Puzzle {{puzzleId: $puzzleId}})
    SET {set_query}
    RETURN p.puzzleId AS puzzleId,
           p.puzzleTypeIsRegular AS puzzleTypeIsRegular,
           p.puzzleTheme AS puzzleTheme,
           p.puzzleBrand AS puzzleBrand,
           p.puzzlePieceQty AS puzzlePieceQty,
           p.puzzleMaterial AS puzzleMaterial,
           p.row_size AS row_size,
           p.column_size AS column_size
    """

    with get_session() as session:
        result = session.run(query, **params)
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Puzzle no encontrado")
        return PuzzleRead(
            puzzleId=record["puzzleId"],
            puzzleTypeIsRegular=record["puzzleTypeIsRegular"],
            puzzleTheme=record["puzzleTheme"],
            puzzleBrand=record["puzzleBrand"],
            puzzlePieceQty=record["puzzlePieceQty"],
            puzzleMaterial=record["puzzleMaterial"],
            row_size=record["row_size"],
            column_size=record["column_size"],
        )

# DELETE Puzzle
@router.delete("/{puzzle_id}")
async def delete_puzzle(puzzle_id: UUID):
    query = """
    MATCH (p:Puzzle {puzzleId: $puzzleId})
    DELETE p
    """
    with get_session() as session:
        session.run(query, puzzleId=str(puzzle_id))
    return {"message": "Puzzle eliminado correctamente"}
