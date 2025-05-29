import streamlit as st
import requests
from collections import defaultdict
import re

API_BASE = "http://localhost:8000"  # Asegúrate que esté corriendo el backend con Uvicorn

st.set_page_config(page_title="PuzzleSolver", layout="centered")
st.title("🧩 PuzzleSolver")

# Navegación por pestañas
tabs = st.tabs(["Crear Puzzle", "Agregar Piezas", "Resolver Puzzle"])

with tabs[0]:
    st.header("Crear nuevo Puzzle")

    tipo = st.radio("Tipo de puzzle", ["Regular", "Irregular"]) == "Regular"
    theme = st.text_input("Tema")
    brand = st.text_input("Marca")
    qty = st.number_input("Cantidad de piezas", min_value=1, step=1)
    material = st.text_input("Material")

    if tipo:
        row_size = st.number_input("Tamaño de fila", min_value=1)
    else:
        row_size = None

    if st.button("Crear Puzzle"):
        payload = {
            "puzzleTypeIsRegular": tipo,
            "puzzleTheme": theme,
            "puzzleBrand": brand,
            "puzzlePieceQty": int(qty),
            "puzzleMaterial": material,
            "row_size": int(row_size) if row_size else None,
        }

        resp = requests.post(f"{API_BASE}/puzzles/", json=payload)
        if resp.status_code == 200:
            puzzle = resp.json()
            st.success(f"Puzzle creado con ID: {puzzle['puzzleId']}")
            st.session_state["puzzle_id"] = puzzle["puzzleId"]
        else:
            st.error(f"Error al crear puzzle: {resp.text}")

with tabs[1]:
    st.header("Agregar piezas al puzzle")

    pid = st.text_input("Puzzle ID", st.session_state.get("puzzle_id", ""))
    n_piezas = st.number_input("¿Cuántas piezas agregarás?", min_value=1, step=1)

    piece_inputs = []
    for i in range(n_piezas):
        seq = i + 1  # Secuencia empieza en 1
        st.markdown(f"### Pieza {i + 1}")
        st.write(f"Secuencia **{seq}**")   # ← sólo para mostrar, no es editable
        ori = st.selectbox(f"Orientación", [0, 90, 180, 270], key=f"ori_{i}")
        group = st.number_input(f"Grupo", key=f"group_{i}", min_value=1)
        status = st.selectbox(f"Estatus", ["present", "missing"], key=f"status_{i}")
        piece_inputs.append({
            "sequenceNumber": int(seq),
            "pieceOrientation": ori,
            "group": int(group),
            "status": status
        })

    if st.button("Enviar piezas"):
        resp = requests.post(f"{API_BASE}/puzzle/{pid}/pieces/bulk", json=piece_inputs)
        if resp.status_code == 200:
            st.success("¡Piezas agregadas correctamente!")
        else:
            st.error(f"Error: {resp.text}")

with tabs[2]:
    st.header("Resolver un puzzle")

    pid = st.text_input("ID del puzzle a resolver", st.session_state.get("puzzle_id", ""))

    if st.button("Resolver"):
        resp = requests.get(f"{API_BASE}/solver/{pid}")
        if resp.status_code == 200:
            st.session_state.instrucciones = resp.json()
        else:
            st.error(f"Error al resolver: {resp.text}")
            st.session_state.instrucciones = None

    instrucciones = st.session_state.get("instrucciones")

    if instrucciones:
        st.subheader("Instrucciones")
        resumen = instrucciones[0]
        st.markdown(f"🧩 {resumen}")

        is_regular = resumen.lower().startswith("rompecabezas regular")

        if is_regular:
            # Agrupar por fila
            fila_map = defaultdict(list)
            for line in instrucciones[1:]:
                match = re.search(r"fila (\d+)", line)
                if match:
                    fila = match.group(1)
                    fila_map[fila].append(line)

            for fila, lines in sorted(fila_map.items(), key=lambda x: int(x[0])):
                checked = st.checkbox(f"✅ Marcar fila {fila} como resuelta", key=f"fila_{fila}")
                label = f"Fila {fila}" + (" ✅" if checked else "")
                with st.expander(label, expanded=not checked):
                    for l in lines:
                        icon = "🟡" if "falta esta pieza" in l or "marcada como faltante" in l else "🧩"
                        st.markdown(f"{icon} {l}")

        if not is_regular:
            #––> Agrupación por grupo sin regex
            grupo_map    = defaultdict(list)
            grupo_orden  = []
            grupo_actual = None

            # Recorremos cada línea (sin el resumen)
            for line in instrucciones[1:]:
                text = line.strip()
                # Si empieza con "Grupo ", es un título
                if text.startswith("Grupo "):
                    grupo_actual = text               # ej. "Grupo 1 (5 piezas):"
                    grupo_orden.append(grupo_actual)
                    grupo_map[grupo_actual] = []      # inicializamos lista
                # Si ya tenemos un grupo en curso, lo añadimos
                elif grupo_actual is not None:
                    grupo_map[grupo_actual].append(text)

            def emoji_grupo(idx):
                numerados = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
                letras     = ["🅰️","🅱️","🆎","🆑","🆒","🆓","🆔","🆕","🆖","🆗"]
                return numerados[idx] if idx < len(numerados) else letras[(idx-len(numerados))%len(letras)]

            for idx, grupo in enumerate(grupo_orden):
                checked = st.checkbox(f"✅ Marcar {grupo} como resuelto", key=f"grupo_{idx}")
                emoji   = emoji_grupo(idx)
                label   = f"{emoji} {grupo}" + (" ✅" if checked else "")
                with st.expander(label, expanded=not checked):
                    for instr in grupo_map[grupo]:
                        icon = "🟡" if "falta esta pieza" in instr else "🧩"
                        st.markdown(f"{icon} {instr}")
