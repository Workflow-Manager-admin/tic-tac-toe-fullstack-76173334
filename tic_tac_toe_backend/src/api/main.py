from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    CreateSessionRequest,
    CreateSessionResponse,
    JoinSessionRequest,
    JoinSessionResponse,
    MoveRequest,
    MoveResponse,
    GameStateResponse,
    GameHistoryResponse,
    ErrorResponse,
    Player,
    GameResult,
)
from . import game_logic

tags_metadata = [
    {
        "name": "Session",
        "description": "Create and join Tic Tac Toe game sessions.",
    },
    {
        "name": "Gameplay",
        "description": "Play moves, get current game state.",
    },
    {
        "name": "History",
        "description": "View game history and previous results.",
    },
]

app = FastAPI(
    title="Tic Tac Toe Backend API",
    description="API for gameplay, session, and game history for Tic Tac Toe game.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Health Check", tags=["Session"])
def health_check():
    """Health check endpoint.
    Returns:
        dict: Service health message
    """
    return {"message": "Healthy"}

#--- SESSION ENDPOINTS ---

# PUBLIC_INTERFACE
@app.post("/session/create", response_model=CreateSessionResponse, tags=["Session"], summary="Create a new game session", responses={400: {"model": ErrorResponse}})
def create_game_session(req: CreateSessionRequest):
    """Create a Tic Tac Toe game session.

    Args:
        req (CreateSessionRequest): Player name optional.

    Returns:
        CreateSessionResponse: Session ID and assigned player.
    """
    session = game_logic.create_session(req.player_name)
    return CreateSessionResponse(
        session_id=session["session_id"],
        player=Player.X if req.player_name else Player.X
    )

# PUBLIC_INTERFACE
@app.post("/session/join", response_model=JoinSessionResponse, tags=["Session"], summary="Join a game session", responses={400: {"model": ErrorResponse}})
def join_game_session(req: JoinSessionRequest):
    """Join a game session by providing session ID.

    Args:
        req (JoinSessionRequest): Session details.

    Returns:
        JoinSessionResponse: Session and assigned player.
    """
    session = game_logic.join_session(req.session_id, req.player_name)
    if not session:
        raise HTTPException(status_code=400, detail="Unable to join session: Does not exist or full.")
    assigned_player = Player.O if Player.O.value in session["player_names"] and session["player_names"][Player.O.value] == req.player_name else Player.X
    return JoinSessionResponse(session_id=req.session_id, player=assigned_player)

#--- GAMEPLAY ENDPOINTS ---

# PUBLIC_INTERFACE
@app.post("/game/move", response_model=MoveResponse, tags=["Gameplay"], summary="Make a move", responses={400: {"model": ErrorResponse}})
def make_move(move_req: MoveRequest):
    """Play a move on the current session's board.

    Args:
        move_req (MoveRequest)

    Returns:
        MoveResponse | ErrorResponse
    """
    move_result = game_logic.make_move(move_req)
    if not move_result:
        raise HTTPException(status_code=400, detail="Session not found.")
    if move_result.get("error"):
        raise HTTPException(status_code=400, detail=move_result["error"])
    return MoveResponse(
        board=move_result["board"],
        next_player=move_result.get("next_player"),
        result=GameResult(move_result["result"])
    )

# PUBLIC_INTERFACE
@app.get("/game/state/{session_id}", response_model=GameStateResponse, tags=["Gameplay"], summary="Get game state", responses={404: {"model": ErrorResponse}})
def get_game_state(session_id: str):
    """Get current game state for the session."""
    state = game_logic.get_game_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return state

#--- HISTORY ENDPOINTS ---

# PUBLIC_INTERFACE
@app.get("/history", response_model=GameHistoryResponse, tags=["History"], summary="Get game history")
def get_game_history():
    """List summaries of completed games."""
    all_games = game_logic.list_game_history()
    return GameHistoryResponse(games=all_games)

