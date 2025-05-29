from fastapi import APIRouter, HTTPException, Path
from typing import List
from core.solver import solve_puzzle

router = APIRouter(
    prefix="/solver",
    tags=["Solver"]
)

@router.get("/{puzzle_id}", response_model=List[str])
async def get_solution(
    puzzle_id: str = Path(..., description="UUID del puzzle")
):
    """
    Devuelve una serie de instrucciones detalladas para armar el puzzle,
    indicando piezas faltantes y posiciones.
    """
    try:
        instructions = solve_puzzle(puzzle_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return instructions