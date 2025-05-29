from services.neo4j import get_session
from collections import defaultdict


def fetch_puzzle_and_pieces(puzzle_id: str):
    """
    Recupera el nodo Puzzle y sus piezas asociadas de Neo4j.
    Devuelve un diccionario con propiedades de puzzle y una lista de diccionarios de piezas.
    """
    with get_session() as session:
        record = session.run(
                """
    MATCH (p:Puzzle {puzzleId: $puzzle_id})
    OPTIONAL MATCH (p)-[:HAS_PIECE]->(piece)
    RETURN p, collect(piece) AS pieces
    """,
            puzzle_id=puzzle_id
        ).single()

        if not record:
            return None, []

        # Extraer propiedades del puzzle
        p_node = record["p"]
        puzzle = {k: p_node[k] for k in p_node.keys()}

        # Extraer lista de piezas
        pieces = []
        for node in record["pieces"]:
            pieces.append({k: node[k] for k in node.keys()})

        return puzzle, pieces


ORIENTATION_HINT = {
    0:   "gira la pieza de forma que la flecha apunte hacia arriba",
    90:  "gira la pieza de forma que la flecha apunte hacia la derecha",
    180: "gira la pieza de forma que la flecha apunte hacia abajo",
    270: "gira la pieza de forma que la flecha apunte hacia la izquierda",
}

def solve_regular(puzzle: dict, pieces: list) -> list:
    """
    Genera instrucciones para armar un puzzle regular, indicando faltantes y posiciones.
    """
    total_expected = puzzle.get("puzzlePieceQty") or len(pieces)
    row_size = puzzle.get("row_size")
    column_size = puzzle.get("column_size") or (total_expected // row_size)

    # Crear mapa de secuencia a pieza
    seq_map = {p['sequenceNumber']: p for p in pieces}
    # Calcular faltantes por ausencia o status
    present = [p for p in pieces if p.get('status') == 'present']
    missing_count = total_expected - len(present)

    instructions = []
    instructions.append(
        f"Rompecabezas regular: {row_size} filas x {column_size} columnas (total {total_expected} piezas, {missing_count} faltantes)."
    )

    # Instrucciones por posición
    for seq in range(1, total_expected + 1):
        piece = seq_map.get(seq)
        row = (seq - 1) // column_size + 1
        col = (seq - 1) % column_size + 1
        if not piece:
            instructions.append(
                f"Pieza {seq}: falta esta pieza en la columna {col}, fila {row}. Continúa con la siguiente posición."
            )
        elif piece.get('status') != 'present':
            instructions.append(
                f"Pieza {seq}: está marcada como faltante en la columna {col}, fila {row}. Continúa con la siguiente."
            )
        else:
            orientation = piece.get('pieceOrientation', 0)
            hint = ORIENTATION_HINT.get(orientation, f"orientación desconocida ({orientation}°)")
            instructions.append(
                f"Pieza {seq}: colócala en la columna {col}, fila {row} y {hint}."
            )

    return instructions


def solve_irregular(puzzle: dict, pieces: list) -> list:
    grouped = defaultdict(list)
    for piece in pieces:
        grouped[piece['group']].append(piece)

    total = puzzle.get("puzzlePieceQty") or len(pieces)
    present = [p for p in pieces if p.get('status') == 'present']
    missing_count = total - len(present)

    instructions = []
    instructions.append(
        f"Rompecabezas irregular dividido en {len(grouped)} grupos (total {total} piezas, {missing_count} faltantes)."
    )

    for group_id, grp in sorted(grouped.items()):
        instructions.append(f"Grupo {group_id} ({len(grp)} piezas):")
        for piece in sorted(grp, key=lambda p: p.get("sequenceNumber", 0)):
            seq = piece['sequenceNumber']
            if piece.get('status') != 'present':
                instructions.append(f"- Pieza {seq} del grupo {group_id}: falta esta pieza.")
            else:
                orient = piece.get('pieceOrientation', 0)
                orient_text = ORIENTATION_HINT.get(orient, f"orientación {orient}°")
                instructions.append(f"- Pieza {seq} del grupo {group_id}: {orient_text}.")

    return instructions


def solve_puzzle(puzzle_id: str) -> list:
    """
    Función principal: devuelve instrucciones detalladas, incluso con piezas faltantes.
    """
    puzzle, pieces = fetch_puzzle_and_pieces(puzzle_id)
    if not puzzle:
        raise ValueError("Puzzle no encontrado.")
    if not pieces:
        raise ValueError("No hay piezas asociadas a este puzzle.")

    if puzzle.get("puzzleTypeIsRegular"):
        return solve_regular(puzzle, pieces)
    else:
        return solve_irregular(puzzle, pieces)