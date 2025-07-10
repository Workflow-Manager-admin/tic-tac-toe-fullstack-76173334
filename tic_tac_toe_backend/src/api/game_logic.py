import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union
from .models import Player, GameResult, MoveRequest, GameSummary, GameStateResponse

# --- SESSION STORAGE (in-memory for now) ---
sessions: Dict[str, dict] = {}
history: List[dict] = []

def _empty_board():
    return [[None for _ in range(3)] for _ in range(3)]

def _check_winner(board: List[List[Optional[str]]]) -> GameResult:
    # Rows and columns
    for i in range(3):
        if board[i][0] and all(board[i][j] == board[i][0] for j in range(3)):
            winner = str(board[i][0]).lower()
            return GameResult(winner + "_wins")
        if board[0][i] and all(board[j][i] == board[0][i] for j in range(3)):
            winner = str(board[0][i]).lower()
            return GameResult(winner + "_wins")
    # Diagonals
    if board[0][0] and all(board[d][d] == board[0][0] for d in range(3)):
        winner = str(board[0][0]).lower()
        return GameResult(winner + "_wins")
    if board[0][2] and all(board[d][2-d] == board[0][2] for d in range(3)):
        winner = str(board[0][2]).lower()
        return GameResult(winner + "_wins")
    # Draw or in progress
    filled = True
    for row in board:
        for cell in row:
            if not cell:
                filled = False
                break
        if not filled:
            break
    if filled:
        return GameResult.DRAW
    return GameResult.IN_PROGRESS

# PUBLIC_INTERFACE
def create_session(player_name: Optional[str]) -> dict:
    """Create a game session and return the session data."""
    session_id = str(uuid.uuid4())
    session = {
        "created": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "players": [(player_name or "Player X")] if player_name else [],
        "player_slots": [Player.X.value, Player.O.value],
        "player_names": {},
        "board": _empty_board(),
        "current_player": Player.X.value,
        "result": GameResult.IN_PROGRESS.value
    }
    if player_name:
        session["player_names"][Player.X.value] = player_name
    sessions[session_id] = session
    return session

# PUBLIC_INTERFACE
def join_session(session_id: str, player_name: Optional[str]) -> Union[dict, None]:
    """Join an existing session if a slot is available."""
    session = sessions.get(session_id)
    if not session or len(session["player_names"]) >= 2:
        return None
    if Player.O.value not in session["player_names"]:
        session["player_names"][Player.O.value] = player_name or f"Player O"
        session["players"].append(session["player_names"][Player.O.value])
        return session
    elif Player.X.value not in session["player_names"]:
        session["player_names"][Player.X.value] = player_name or f"Player X"
        session["players"].append(session["player_names"][Player.X.value])
        return session
    return None

# PUBLIC_INTERFACE
def get_game_state(session_id: str) -> Optional[GameStateResponse]:
    """Return the current game state for UI display."""
    session = sessions.get(session_id)
    if not session:
        return None
    return GameStateResponse(
        board=session["board"],
        current_player=Player(session["current_player"]),
        players=list(session["player_names"].values()),
        result=GameResult(session["result"])
    )

# PUBLIC_INTERFACE
def make_move(move_req: MoveRequest) -> Optional[dict]:
    """Apply a player's move; returns dict with board, next_player, result, error."""
    session = sessions.get(move_req.session_id)
    if not session:
        return None
    row = move_req.row
    col = move_req.col
    player = move_req.player.value
    board = session["board"]

    if session["result"] != GameResult.IN_PROGRESS.value:
        return {"error": "Game already finished", "board": board, "result": session["result"]}

    if board[row][col]:
        return {"error": "Cell already taken", "board": board, "result": session["result"]}

    if player != session["current_player"]:
        return {"error": "Not your turn", "board": board, "result": session["result"]}

    board[row][col] = player
    winner = _check_winner(board)
    session["result"] = winner.value
    if winner == GameResult.IN_PROGRESS:
        session["current_player"] = Player.O.value if player == Player.X.value else Player.X.value
        next_player = session["current_player"]
    else:
        # Record history and end game
        game_summary = GameSummary(
            session_id=move_req.session_id,
            created=session["created"],
            players=list(session["player_names"].values()),
            result=winner
        )
        history.append(game_summary.model_dump())
        next_player = None

    return {
        "board": board,
        "next_player": next_player,
        "result": winner.value
    }

# PUBLIC_INTERFACE
def list_game_history() -> List[GameSummary]:
    """Return a list of completed games (history)."""
    return [GameSummary(**rec) for rec in history]

