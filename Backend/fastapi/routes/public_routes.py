from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from Backend.config import Telegram
from Backend import db
import PTN

router = APIRouter(tags=["Public Web UI"])
templates = Jinja2Templates(directory="Backend/fastapi/templates")

# --- Helper Logic from your original file ---
def format_stream_details(filename: str, quality: str, size: str):
    try:
        parsed = PTN.parse(filename)
    except:
        return f"Quality: {quality} | Size: {size}"
    
    info = []
    if parsed.get("codec"): info.append(parsed.get("codec"))
    if parsed.get("audio"): info.append(parsed.get("audio"))
    return f"{quality} | {size} | {' '.join(info)}"

# --- Routes ---

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Fetch data for Netflix rows
    latest_movies = await db.sort_movies([("updated_on", "desc")], 1, 20)
    latest_series = await db.sort_tv_shows([("updated_on", "desc")], 1, 20)
    top_rated = await db.sort_movies([("rating", "desc")], 1, 20)
    
    hero = latest_movies['movies'][0] if latest_movies['movies'] else None
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "hero": hero,
        "sections": [
            {"title": "Recently Added Movies", "items": latest_movies['movies'], "type": "movie"},
            {"title": "Recently Added Series", "items": latest_series['tv_shows'], "type": "tv"},
            {"title": "Top Rated", "items": top_rated['movies'], "type": "movie"}
        ]
    })

@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, query: str = Query("")):
    results = await db.search_documents(query=query, page=1, page_size=40)
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": query,
        "results": results.get("results", [])
    })

@router.get("/watch/{media_type}/{tmdb_id}/{db_index}", response_class=HTMLResponse)
async def player_page(request: Request, media_type: str, tmdb_id: int, db_index: int):
    media = await db.get_document(media_type, tmdb_id, db_index)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Process stream info for UI
    streams = []
    if media_type == "movie":
        for q in media.get("telegram", []):
            streams.append({
                "label": format_stream_details(q.get('name'), q.get('quality'), q.get('size')),
                "url": f"{Telegram.BASE_URL}/dl/{q.get('id')}/video.mkv"
            })

    return templates.TemplateResponse("player.html", {
        "request": request,
        "media": media,
        "media_type": media_type,
        "streams": streams,
        "base_url": Telegram.BASE_URL
    })
