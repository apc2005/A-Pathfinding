import heapq
import math
import asyncio
import time as _time
from pyscript import window, document

# --- CONFIGURACIÓN ---
ROWS, COLS = 10, 10
MOVIMIENTOS = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]

class State:
    def __init__(self):
        self.grid = [[0]*COLS for _ in range(ROWS)]
        self.start = [0, 0]
        self.end = [ROWS-1, COLS-1]
        self.is_running = False

state = State()

# --- UTILIDADES ---
def get_cell_el(r, c):
    return document.getElementById(f"c_{r}_{c}")

def heuristica(a, b):
    # Distancia Euclidiana
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

class Node:
    def __init__(self, pos, parent=None, g=0, h=0):
        self.pos = pos
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h
    def __lt__(self, other): return self.f < other.f

# --- LÓGICA CORE ---
def render_grid():
    for r in range(ROWS):
        for c in range(COLS):
            el = get_cell_el(r, c)
            el.className = "cell"
            el.textContent = ""
            if [r,c] == state.start:
                el.classList.add("cell-start")
                el.textContent = "▶"
            elif [r,c] == state.end:
                el.classList.add("cell-end")
                el.textContent = "✕"
            elif state.grid[r][c] == 1:
                el.classList.add("cell-wall")

async def run_astar():
    if state.is_running: return
    state.is_running = True
    
    window._setStatus("run", "Calculando ruta óptima...")
    render_grid()
    
    t0 = _time.time()
    camino, visitados = astar_algo(state.start, state.end)
    t1 = _time.time()
    
    # Animación de exploración
    for (r,c) in visitados:
        if [r,c] not in [state.start, state.end]:
            get_cell_el(r,c).classList.add("cell-visited")
            await asyncio.sleep(0.01)
    
    if not camino:
        window._setStatus("err", "No hay camino posible.")
        state.is_running = False
        return

    # Animación de camino final
    coste = 0
    for i in range(1, len(camino)):
        r,c = camino[i]
        pr, pc = camino[i-1]
        coste += math.sqrt(2) if r!=pr and c!=pc else 1.0
        
        if [r,c] != state.end:
            el = get_cell_el(r,c)
            el.classList.remove("cell-visited")
            el.classList.add("cell-path")
        await asyncio.sleep(0.04)

    ms = (t1-t0)*1000
    window._setStats(f"{len(camino)}", f"{len(visitados)}", f"{coste:.2f}", f"{ms:.2f}ms")
    window._setStatus("ok", "¡Ruta encontrada!")
    state.is_running = False

def astar_algo(inicio, meta):
    # Implementación estándar de A*
    start_node = Node(tuple(inicio), h=heuristica(inicio, meta))
    frontier = [start_node]
    reached = {tuple(inicio): start_node}
    visited = []

    while frontier:
        current = heapq.heappop(frontier)
        if list(current.pos) == list(meta):
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1], visited
        
        visited.append(current.pos)
        
        for dr, dc in MOVIMIENTOS:
            nr, nc = current.pos[0]+dr, current.pos[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and state.grid[nr][nc] == 0:
                new_g = current.g + (1.41 if dr!=0 and dc!=0 else 1)
                new_node = Node((nr,nc), current, new_g, heuristica((nr,nc), meta))
                
                if (nr,nc) not in reached or new_g < reached[(nr,nc)].g:
                    reached[(nr,nc)] = new_node
                    heapq.heappush(frontier, new_node)
    return None, visited

# --- EXPOSICIÓN A JS ---
window._runAstar = run_astar
window._applyTool = lambda r, c: apply_tool_logic(r, c)
window._resetAll = lambda: reset_logic()

def apply_tool_logic(r, c):
    tool = window._getTool()
    if tool == "start": state.start = [r,c]
    elif tool == "end": state.end = [r,c]
    elif tool == "wall": 
        if [r,c] not in [state.start, state.end]: state.grid[r][c] = 1
    elif tool == "erase": state.grid[r][c] = 0
    render_grid()

def reset_logic():
    state.grid = [[0]*COLS for _ in range(ROWS)]
    render_grid()
    window._setStatus("idle", "Mapa reiniciado.")

render_grid()
document.getElementById("loading-overlay").style.display = "none"