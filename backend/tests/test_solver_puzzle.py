import os, sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import core.solver as solver

@pytest.fixture
def regular_puzzle_dict():
    return {
        "puzzleTypeIsRegular": True,
        "puzzlePieceQty": 6,
        "row_size": 2,
        "column_size": 3,
    }

@pytest.fixture
def regular_pieces_all_present():
    orients = [0, 90, 180, 270, 0, 90]
    return [
        {"sequenceNumber": i, "pieceOrientation": o, "group": 1, "status": "present"}
        for i, o in zip(range(1, 7), orients)
    ]

@pytest.fixture
def regular_pieces_with_missing():
    # Faltan las piezas 2 y 5
    return [
        {"sequenceNumber": 1, "pieceOrientation": 0,   "group": 1, "status": "present"},
        {"sequenceNumber": 3, "pieceOrientation": 180, "group": 1, "status": "present"},
        {"sequenceNumber": 4, "pieceOrientation": 270, "group": 1, "status": "present"},
        {"sequenceNumber": 6, "pieceOrientation": 90,  "group": 1, "status": "present"},
    ]

def test_solve_regular_all_present(regular_puzzle_dict, regular_pieces_all_present):
    instr = solver.solve_regular(regular_puzzle_dict, regular_pieces_all_present)
    # Resumen correcto
    assert instr[0] == "Rompecabezas regular: 2 filas x 3 columnas (total 6 piezas, 0 faltantes)."
    # Verifica la primera y última instrucción
    assert instr[1] == "Pieza 1: colócala en (1, 1) con orientación 0°."
    assert instr[2] == "Pieza 2: colócala en (1, 2) con orientación 90°."
    assert instr[-1] == "Pieza 6: colócala en (2, 3) con orientación 90°."

def test_solve_regular_with_missing(regular_puzzle_dict, regular_pieces_with_missing):
    instr = solver.solve_regular(regular_puzzle_dict, regular_pieces_with_missing)
    # Debe contar 2 faltantes
    assert "(total 6 piezas, 2 faltantes)" in instr[0]
    # Piezas 2 y 5 deben aparecer como faltantes en la lista
    assert any("Pieza 2: falta esta pieza" in line for line in instr)
    assert any("Pieza 5: falta esta pieza" in line for line in instr)

def test_solve_irregular_simple():
    puzzle = {"puzzleTypeIsRegular": False, "puzzlePieceQty": 3}
    pieces = [
        {"sequenceNumber":1, "pieceOrientation":0,   "group":1, "status":"present"},
        {"sequenceNumber":2, "pieceOrientation":90,  "group":1, "status":"missing"},
        {"sequenceNumber":3, "pieceOrientation":180, "group":2, "status":"present"},
    ]
    instr = solver.solve_irregular(puzzle, pieces)
    # Resumen inicial
    assert "dividido en 2 grupos (total 3 piezas, 1 faltantes)." in instr[0]
    # Grupo 1
    idx1 = instr.index("Grupo 1:")
    assert instr[idx1 + 1] == "  - Pieza 1: orientación 0°"
    assert instr[idx1 + 2] == "  - Pieza 2: falta esta pieza."
    # Grupo 2
    idx2 = instr.index("Grupo 2:")
    assert instr[idx2 + 1] == "  - Pieza 3: orientación 180°"

def test_solve_puzzle_regular(monkeypatch, regular_puzzle_dict, regular_pieces_all_present):
    # Simular fetch
    monkeypatch.setattr(solver, "fetch_puzzle_and_pieces",
                        lambda pid: (regular_puzzle_dict, regular_pieces_all_present))
    result = solver.solve_puzzle("dummy-id")
    # Debe delegar a solve_regular
    assert result == solver.solve_regular(regular_puzzle_dict, regular_pieces_all_present)

def test_solve_puzzle_irregular(monkeypatch):
    puzzle = {"puzzleTypeIsRegular": False, "puzzlePieceQty": 2}
    pieces = [
        {"sequenceNumber":1,"pieceOrientation":0,"group":1,"status":"present"},
        {"sequenceNumber":2,"pieceOrientation":90,"group":1,"status":"present"},
    ]
    monkeypatch.setattr(solver, "fetch_puzzle_and_pieces", lambda pid: (puzzle, pieces))
    result = solver.solve_puzzle("x")
    assert result == solver.solve_irregular(puzzle, pieces)

@pytest.mark.parametrize("fetch_return", [
    (None, []),
    ({}, []),
])
def test_solve_puzzle_not_found(fetch_return, monkeypatch):
    monkeypatch.setattr(solver, "fetch_puzzle_and_pieces", lambda pid: fetch_return)
    with pytest.raises(ValueError):
        solver.solve_puzzle("id")