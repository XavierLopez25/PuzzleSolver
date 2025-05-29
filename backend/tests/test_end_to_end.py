# tests/test_end_to_end.py

import pytest
from fastapi.testclient import TestClient
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from backend.app import app

client = TestClient(app)

# Variables para compartir datos entre tests
_puzzle = {}
_pieces = []


def test_01_create_puzzle():
    """1) CREATE /puzzles/"""
    payload = {
        "puzzleTypeIsRegular": True,
        "puzzleTheme": "Test Tema",
        "puzzleBrand": "Test Brand",
        "puzzlePieceQty":  3,
        "puzzleMaterial": "Cartón",
        "row_size":       3
    }
    resp = client.post("/puzzles/", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    # guardamos para usar luego
    assert "puzzleId" in data
    for k,v in payload.items():
        assert data[k] == v
    _puzzle.update(data)


def test_02_get_puzzle():
    """2) GET /puzzles/{puzzle_id}"""
    pid = _puzzle["puzzleId"]
    resp = client.get(f"/puzzles/{pid}")
    assert resp.status_code == 200, resp.text
    assert resp.json() == _puzzle


def test_03_list_puzzles():
    """3) GET /puzzles/ debería devolver al menos el que creamos"""
    resp = client.get("/puzzles/")
    assert resp.status_code == 200, resp.text
    arr = resp.json()
    assert any(p["puzzleId"] == _puzzle["puzzleId"] for p in arr)


def test_04_update_puzzle():
    """4) PATCH /puzzles/{puzzle_id}"""
    pid = _puzzle["puzzleId"]
    patch = {"puzzleTheme": "Nuevo Tema"}
    resp = client.patch(f"/puzzles/{pid}", json=patch)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["puzzleTheme"] == "Nuevo Tema"
    # actualizamos nuestro _puzzle
    _puzzle.update(data)


def test_05_bulk_create_pieces():
    """5) POST /puzzle/{puzzle_id}/pieces/bulk"""
    pid = _puzzle["puzzleId"]
    bulk = [
        {"sequenceNumber": 1, "pieceOrientation": 0,   "group": 1},
        {"sequenceNumber": 2, "pieceOrientation": 90,  "group": 1},
        {"sequenceNumber": 3, "pieceOrientation": 180, "group": 1},
    ]
    resp = client.post(f"/puzzle/{pid}/pieces/bulk", json=bulk)
    assert resp.status_code == 200, resp.text
    arr = resp.json()
    assert len(arr) == 3
    # comprobamos que tienen pieceId y puzzleId
    for piece in arr:
        assert "pieceId" in piece
        assert piece["puzzleId"] == pid
    _pieces.extend(arr)


def test_06_list_pieces():
    """6) GET /puzzle/{puzzle_id}/pieces/"""
    pid = _puzzle["puzzleId"]
    resp = client.get(f"/puzzle/{pid}/pieces/")
    assert resp.status_code == 200, resp.text
    arr = resp.json()
    # debe coincidir con nuestras piezas
    ids_created = {p["pieceId"] for p in _pieces}
    ids_listed  = {p["pieceId"] for p in arr}
    assert ids_created == ids_listed


def test_07_get_piece():
    """7) GET /puzzle/{puzzle_id}/pieces/{piece_id}"""
    pid = _puzzle["puzzleId"]
    pid_piece = _pieces[0]["pieceId"]
    resp = client.get(f"/puzzle/{pid}/pieces/{pid_piece}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["pieceId"] == pid_piece
    assert data["sequenceNumber"] == 1


def test_08_update_piece():
    """8) PATCH /puzzle/{puzzle_id}/pieces/{piece_id}"""
    pid = _puzzle["puzzleId"]
    pid_piece = _pieces[1]["pieceId"]
    patch = {"status":"missing", "pieceOrientation":270}
    resp = client.patch(f"/puzzle/{pid}/pieces/{pid_piece}", json=patch)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "missing"
    assert data["pieceOrientation"] == 270


def test_09_delete_piece():
    """9) DELETE /puzzle/{puzzle_id}/pieces/{piece_id}"""
    pid = _puzzle["puzzleId"]
    pid_piece = _pieces[2]["pieceId"]
    resp = client.delete(f"/puzzle/{pid}/pieces/{pid_piece}")
    assert resp.status_code == 204, resp.text
    # ahora GET debe 404
    resp2 = client.get(f"/puzzle/{pid}/pieces/{pid_piece}")
    assert resp2.status_code == 404


def test_10_delete_puzzle():
    """🔟 DELETE /puzzles/{puzzle_id}"""
    pid = _puzzle["puzzleId"]
    resp = client.delete(f"/puzzles/{pid}")
    assert resp.status_code == 204, resp.text
    # GET posterior debe 404
    resp2 = client.get(f"/puzzles/{pid}")
    assert resp2.status_code == 404
