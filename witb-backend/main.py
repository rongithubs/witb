from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from schemas import WITBItem, WITBItemBase
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import models, schemas
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi import Request
import traceback
from fastapi.middleware.cors import CORSMiddleware
from typing import List
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




async def get_db():
    async with SessionLocal() as session:
        yield session

@app.post("/players/", response_model=schemas.Player)
async def create_player(player: schemas.PlayerCreate, db: AsyncSession = Depends(get_db)):
    new_player = models.Player(**player.dict())
    db.add(new_player)
    try:
        await db.commit()
        await db.refresh(new_player)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Player already exists")
    return new_player

@app.get("/players", response_model=List[schemas.Player])
async def get_players(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Player).options(selectinload(models.Player.witb_items))
    )
    return result.scalars().all()

@app.get("/players/{player_id}", response_model=schemas.Player)
async def get_player(player_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Player)
        .where(models.Player.id == player_id)
        .options(selectinload(models.Player.witb_items))
    )
    player = result.scalars().first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/players/{player_id}/witb_items/", response_model=schemas.WITBItem)
async def add_witb_item(
    player_id: str,
    item: schemas.WITBItemBase,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(models.Player).where(models.Player.id == player_id))
        player = result.scalars().first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        db_item = models.WITBItem(**item.dict(), player_id=player.id)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    except Exception as e:
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
