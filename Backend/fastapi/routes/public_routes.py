from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.templating import Jinja2Templates
from Backend import db
from Backend.config import Telegram
import random

router = APIRouter()
templates = Jinja2Templates(directory="Backend/fastapi/templates")

@router.get("/", response_class=HTMLResponse)
async def public_home(request: Request):
    # Fetch latest movies for the grid
    latest_movies_data = await db.sort_movies([("updated_on", "desc")], 1, 24)
    latest_movies = latest_movies_data.get("movies", [])
    
    # Fetch random "Featured" content (Hero Section)
    featured = None
    if latest_movies:
        featured = random.choice(latest_movies)
        
    return templates.TemplateResponse("home.html", {
        "request": request,
        "featured": featured,
        "latest_movies": latest_movies,
        "title": "Links4U Archive"
    })

@router.get("/search", response_class=HTMLResponse)
async def public_search(request: Request, q: str = Query("", max_length=100)):
    results = []
    if q:
        search_res = await db.search_documents(q, 1, 50)
        results = search_res.get("results", [])
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results
    })

@router.get("/view/{media_type}/{tmdb_id}", response_class=HTMLResponse)
async def public_view(request: Request, media_type: str, tmdb_id: int, db_index: int = Query(None)):
    # If db_index isn't provided, we might need to search or assume current (logic simplifed to search all)
    # The home/search page links should include db_index ideally. 
    # If not provided, we iterate to find it.
    
    media_data = None
    
    if db_index:
        media_data = await db.get_media_details(tmdb_id, db_index)
    else:
        # Fallback: Find which DB it lives in
        for idx in range(1, db.current_db_index + 1):
             media_data = await db.get_media_details(tmdb_id, idx)
             if media_data:
                 break
    
    if not media_data:
         raise HTTPException(status_code=404, detail="Media not found in archive")

    # Format data for the view
    return templates.TemplateResponse("view.html", {
        "request": request,
        "media": media_data,
        "media_type": media_type,
        "base_url": Telegram.BASE_URL
    })
