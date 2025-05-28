# @router.post("/bulk", response_model=List[PieceRead])
# def create_pieces_bulk(puzzle_id: str, pieces: List[PieceCreate]):
#     """
#     Crea varias piezas en un solo request.
#     - Verifica que el Puzzle exista.
#     - Crea nodos Piece y relaciones (Puzzle)-[:HAS_PIECE]->(Piece).
#     """
#     ...
#
# @router.get("/", response_model=List[PieceRead])
# def list_pieces(puzzle_id: str):
#     """Devuelve todas las piezas de un Puzzle dado."""
#     ...
#
# @router.get("/{piece_id}", response_model=PieceRead)
# def get_piece(puzzle_id: str, piece_id: int):
#     """Lee una pieza por su ID secuencial."""
#     ...
#
# @router.patch("/{piece_id}", response_model=PieceRead)
# def update_piece(puzzle_id: str, piece_id: int, payload: PieceUpdate):
#     """Actualiza orientation, group o status de una pieza."""
#     ...
#
# @router.delete("/{piece_id}", status_code=204)
# def delete_piece(puzzle_id: str, piece_id: int):
#     """Elimina el nodo Piece y sus relaciones."""
#     ...