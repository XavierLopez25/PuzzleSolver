# PuzzleSolver

Puzzle Solver with Neo4J and Streamlit.

### Entities for models:

#### Puzzle

- id: tipoIdxd
- puzzleTypeIsRegular: boolean
- puzzleTheme: string
- puzzleBrand: string
- puzzlePieceQty: int
- puzzleMaterial: string
- row_size? (opcional): (solo para regulares)

#### Piece

- pieceId: tipo id xdd
- sequenceNumber: int (ejemplo: 1).
- pieceOrientation: int (ejemplo: 90°).
- group: int (ej: si es irregular, 3. si es el caracol o un rompecabezas convencional 1).

## Install all the dependencies (make sure to be in the PuzzleSolver/ folder):

```bash
pip install -r requirements.txt
```

## .env configurations

Put a .env file in the `backend` folder with the following:

```bash
NEO4J_URI=URI
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD
```

## How to run the API?

- Navigate to the `backend` folder and run this command:

```bash
uvicorn app:app --reload
```

## How to run the client?

-- Navigate to the `frontend` folder and run this command:

```bash
streamlit run .\streamlit_app.py
```
