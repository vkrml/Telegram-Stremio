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

app = FastAPI(
    title="Telegram Web VOD",
    description="Netflix-style Media Portal powered by Telegram Multi-Token bots",
    version=__version__
)

# --- Middleware Setup ---
app.add_middleware(SessionMiddleware, secret_key="NETFLIX_STYLE_SECRET_KEY")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.mount("/static", StaticFiles(directory="Backend/fastapi/static"), name="static")
except:
    pass

# --- ROUTER INTEGRATION ---
app.include_router(public_router) # The Public Netflix UI
app.include_router(stream_router) # The Multi-Token Engine

# --- AUTH ROUTES ---
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return await login_page(request)

@app.post("/login", response_class=HTMLResponse)
async def login_post_route(request: Request, username: str = Form(...), password: str = Form(...)):
    return await login_post(request, username, password)

@app.get("/logout")
async def logout_route(request: Request):
    return await logout(request)

# --- PROTECTED ADMIN ROUTES ---
@app.get("/admin", response_class=HTMLResponse)
async def root(request: Request, _: bool = Depends(require_auth)):
    return await dashboard_page(request, _)

@app.get("/media/manage", response_class=HTMLResponse)
async def media_management(request: Request, media_type: str = "movie", _: bool = Depends(require_auth)):
    return await media_management_page(request, media_type, _)

@app.get("/media/edit", response_class=HTMLResponse)
async def edit_media(request: Request, tmdb_id: int, db_index: int, media_type: str, _: bool = Depends(require_auth)):
    return await edit_media_page(request, tmdb_id, db_index, media_type, _)

@app.exception_handler(401)
async def auth_exception_handler(request: Request, exc):
    return RedirectResponse(url="/login", status_code=302)
