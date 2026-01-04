from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from Backend.config import Telegram
from Backend import db
import PTN

router = APIRouter(tags=["Public UI"])
templates = Jinja2Templates(directory="Backend/fastapi/templates")

def format_info(filename, quality, size):
    try:
        p = PTN.parse(filename)
        return f"{quality} • {size} • {p.get('codec', '')}"
    except:
        return f"{quality} • {size}"

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    movies = await db.sort_movies([("updated_on", "desc")], 1, 20)
    series = await db.sort_tv_shows([("updated_on", "desc")], 1, 20)
    hero = movies['movies'][0] if movies['movies'] else None
    return templates.TemplateResponse("index.html", {
        "request": request, "hero": hero, "movies": movies['movies'], "series": series['tv_shows']
    })

@router.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = Query("")):
    res = await db.search_documents(q, 1, 40)
    return templates.TemplateResponse("search.html", {"request": request, "results": res['results'], "query": q})

@router.get("/watch/{m_type}/{tmdb_id}/{db_idx}")
async def watch(request: Request, m_type: str, tmdb_id: int, db_idx: int):
    media = await db.get_document(m_type, tmdb_id, db_idx)
    if not media: raise HTTPException(404)
    streams = []
    if m_type == "movie":
        for q in media.get("telegram", []):
            streams.append({"label": format_info(q.get('name'), q.get('quality'), q.get('size')), 
                            "url": f"{Telegram.BASE_URL}/dl/{q.get('id')}/video.mkv"})
    return templates.TemplateResponse("player.html", {"request": request, "media": media, "m_type": m_type, "streams": streams, "base": Telegram.BASE_URL})
