from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List
import traceback
import models, schemas
from database import SessionLocal, engine
from brand_urls import get_brand_url
import sys
import os
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scraper'))
from tournament_scraper import simple_tournament_scraper

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Create all tables for local development
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("Database tables created successfully")
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




async def get_db():
    async with SessionLocal() as session:
        yield session

def enrich_witb_items_with_urls(items):
    """Add brand URLs to WITB items that don't have specific product URLs"""
    for item in items:
        if not item.product_url and item.brand:
            item.product_url = get_brand_url(item.brand)
    return items

@app.post("/players/", response_model=schemas.Player)
async def create_player(player: schemas.PlayerCreate, db: AsyncSession = Depends(get_db)):
    new_player = models.Player(**player.model_dump())
    db.add(new_player)
    try:
        await db.commit()
        await db.refresh(new_player)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Player already exists")
    return new_player

@app.get("/players", response_model=schemas.PaginatedPlayersResponse)
async def get_players(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total_result = await db.execute(select(func.count(models.Player.id)))
    total = total_result.scalar()
    
    # Get paginated players
    result = await db.execute(
        select(models.Player)
        .options(selectinload(models.Player.witb_items))
        .offset(offset)
        .limit(per_page)
    )
    players = result.scalars().all()
    
    # Enrich WITB items with brand URLs
    for player in players:
        enrich_witb_items_with_urls(player.witb_items)
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    return schemas.PaginatedPlayersResponse(
        items=players,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@app.get("/players/search")
async def search_player(name: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Player).where(models.Player.name.ilike(name.strip()))
    )
    player = result.scalars().first()
    return {"exists": bool(player)}


@app.get("/players/{player_id}", response_model=schemas.Player)
async def get_player(player_id: str, db: AsyncSession = Depends(get_db)):
    try:
        # Convert string to UUID
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid player ID format")
    
    result = await db.execute(
        select(models.Player)
        .where(models.Player.id == player_uuid)
        .options(selectinload(models.Player.witb_items))
    )
    player = result.scalars().first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Enrich WITB items with brand URLs
    enrich_witb_items_with_urls(player.witb_items)
    
    return player

@app.post("/players/{player_id}/witb_items/", response_model=schemas.WITBItem)
async def add_witb_item(
    player_id: str,
    item: schemas.WITBItemCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Convert string to UUID
        try:
            player_uuid = uuid.UUID(player_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid player ID format")
            
        result = await db.execute(select(models.Player).where(models.Player.id == player_uuid))
        player = result.scalars().first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        db_item = models.WITBItem(**item.model_dump(), player_id=player.id)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    except Exception as e:
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/tournament-winner")
async def get_tournament_winner():
    """Get the latest PGA tournament winner using cost-efficient scraping + Supabase storage"""
    try:
        winner_data = await simple_tournament_scraper.scrape_and_store_winner()
        return winner_data
    except Exception as e:
        print(f"Error fetching tournament winner: {e}")
        return {
            "winner": "Tournament data unavailable",
            "tournament": "Please try again later", 
            "date": "",
            "score": ""
        }

@app.get("/tournament-winner/debug")
async def debug_tournament_winner():
    """Debug endpoint to see raw scraped data"""
    try:
        # For debugging, let's try a simpler approach with ESPN or Golf.com
        from scrapingbee import ScrapingBeeClient
        import os
        
        # Get API key
        api_key = os.getenv("SCRAPINGBEE_API_KEY", "")
        if not api_key:
            scraper_env_path = os.path.join(os.path.dirname(__file__), "..", "scraper", ".env")
            if os.path.exists(scraper_env_path):
                with open(scraper_env_path, 'r') as f:
                    for line in f:
                        if line.startswith("SCRAPINGBEE_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
        
        if not api_key:
            return {"error": "No API key found"}
            
        client = ScrapingBeeClient(api_key=api_key)
        
        # Try ESPN PGA page which usually has recent results
        response = client.get(
            "https://www.espn.com/golf/leaderboard",
            params={'render_js': True, 'wait': 3000}
        )
        
        if response.status_code == 200:
            html_snippet = response.content.decode('utf-8')[:2000]  # First 2000 chars
            return {
                "status": "success",
                "url": "https://www.espn.com/golf/leaderboard", 
                "status_code": response.status_code,
                "html_preview": html_snippet
            }
        else:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "error": "Could not fetch data"
            }
            
    except Exception as e:
        return {"error": str(e)}
