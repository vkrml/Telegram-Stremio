import uvicorn
from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from Backend import __version__
from Backend.fastapi.security.credentials import require_auth
from Backend.fastapi.routes.stream_routes import router as stream_router
from Backend.fastapi.routes.public_routes import router as public_router
from Backend.fastapi.routes.template_routes import (
    login_page, login_post, logout, set_theme, dashboard_page,
    media_management_page, edit_media_page, public_status_page
)
from Backend.fastapi.routes.api_routes import (
    list_media_api, delete_media_api, update_media_api,
    delete_movie_quality_api, delete_tv_quality_api,
    delete_tv_episode_api, delete_tv_season_api
)

# Initialize FastAPI
app = FastAPI(
    title="Telegram Web VOD",
    description="Netflix-style Media Portal powered by Telegram",
    version=__version__
)

# --- Middleware ---
# For Admin Authentication sessions
app.add_middleware(
    SessionMiddleware, 
    secret_key="f6d2e3b9a0f43d9a2e6a56b2d3175cd9c05bbfe31d95ed2a7306b57cb1a8b6f0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for CSS/JS
try:
    app.mount("/static", StaticFiles(directory="Backend/fastapi/static"), name="static")
except:
    pass

# --- ROUTER INTEGRATION ---

# 1. Public Netflix UI (Home, Search, Watch)
app.include_router(public_router)

# 2. Streaming Engine (Direct Download/Stream Logic)
app.include_router(stream_router)


# --- Authentication & Dashboard Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return await login_page(request)

@app.post("/login", response_class=HTMLResponse)
async def login_post_route(request: Request, username: str = Form(...), password: str = Form(...)):
    return await login_post(request, username, password)

@app.get("/logout")
async def logout_route(request: Request):
    return await logout(request)

# --- Protected Admin Routes ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, _: bool = Depends(require_auth)):
    return await dashboard_page(request, _)

@app.get("/media/manage", response_class=HTMLResponse)
async def media_management(request: Request, media_type: str = "movie", _: bool = Depends(require_auth)):
    return await media_management_page(request, media_type, _)

@app.get("/media/edit", response_class=HTMLResponse)
async def edit_media(request: Request, tmdb_id: int, db_index: int, media_type: str, _: bool = Depends(require_auth)):
    return await edit_media_page(request, tmdb_id, db_index, media_type, _)


# --- Management APIs ---

@app.get("/api/media/list")
async def list_media(
    media_type: str = Query("movie", regex="^(movie|tv)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    search: str = Query("", max_length=100),
    _: bool = Depends(require_auth)
):
    return await list_media_api(media_type, page, page_size, search)

@app.delete("/api/media/delete")
async def delete_media(tmdb_id: int, db_index: int, media_type: str, _: bool = Depends(require_auth)):
    return await delete_media_api(tmdb_id, db_index, media_type)

@app.put("/api/media/update")
async def update_media(request: Request, tmdb_id: int, db_index: int, media_type: str, _: bool = Depends(require_auth)):
    return await update_media_api(request, tmdb_id, db_index, media_type)

@app.delete("/api/media/delete-quality")
async def delete_movie_quality(tmdb_id: int, db_index: int, id: str, _: bool = Depends(require_auth)):
    return await delete_movie_quality_api(tmdb_id, db_index, id)

# --- Error Handlers ---
@app.exception_handler(401)
async def auth_exception_handler(request: Request, exc):
    return RedirectResponse(url="/login", status_code=302)
