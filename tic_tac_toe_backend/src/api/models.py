from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# --- ENUMS AND CONSTANTS ---

class Player(str, Enum):
    X = "X"
    O = "O"

class GameResult(str, Enum):
    IN_PROGRESS = "in_progress"
    X_WINS = "x_wins"
    O_WINS = "o_wins"
    DRAW = "draw"

# --- DATA MODELS ---

# PUBLIC_INTERFACE
class CreateSessionRequest(BaseModel):
    """Request model to create a new game session (optionally with player name)."""
    player_name: Optional[str] = Field(None, description="Name of the player creating the session")

# PUBLIC_INTERFACE
class CreateSessionResponse(BaseModel):
    """Response with session ID and assigned player."""
    session_id: str = Field(..., description="Unique session identifier")
    player: Player = Field(..., description="Assigned player (X or O)")

# PUBLIC_INTERFACE
class JoinSessionRequest(BaseModel):
    """Request to join an existing session with ID."""
    session_id: str = Field(..., description="Session the player wants to join")
    player_name: Optional[str] = Field(None, description="Name of the player joining")

# PUBLIC_INTERFACE
class JoinSessionResponse(BaseModel):
    """Response confirming session join and assigned player."""
    session_id: str
    player: Player

# PUBLIC_INTERFACE
class MoveRequest(BaseModel):
    """Request to perform a move on the board."""
    session_id: str = Field(..., description="Game session to play in")
    player: Player = Field(..., description="Player making the move")
    row: int = Field(..., ge=0, le=2, description="Row index (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column index (0-2)")

# PUBLIC_INTERFACE
class MoveResponse(BaseModel):
    """Response after a move is applied."""
    board: List[List[Optional[Player]]] = Field(..., description="Updated game board")
    next_player: Optional[Player] = Field(None, description="The next player to move (if game not over)")
    result: GameResult = Field(..., description="Current result/state after move")

# PUBLIC_INTERFACE
class GameStateResponse(BaseModel):
    """Represents the full game state for a session."""
    board: List[List[Optional[Player]]] = Field(..., description="Game board (3x3, X or O)")
    current_player: Player = Field(..., description="Next player who should play")
    players: List[str] = Field(..., description="Names or identifiers of players")
    result: GameResult = Field(..., description="Current game result (in_progress, win, draw)")

# PUBLIC_INTERFACE
class GameSummary(BaseModel):
    """Short summary for listing in game history."""
    session_id: str
    created: str  # ISO8601 string
    players: List[str]
    result: GameResult

# PUBLIC_INTERFACE
class GameHistoryResponse(BaseModel):
    """Response containing a list of recent or finished games."""
    games: List[GameSummary]

# PUBLIC_INTERFACE
class ErrorResponse(BaseModel):
    """API error response model."""
    detail: str

