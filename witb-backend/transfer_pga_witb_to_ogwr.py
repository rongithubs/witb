import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def transfer_pga_witb_to_ogwr():
    """
    Transfer WITB equipment data from PGA Tour players to their corresponding OGWR entries.
    Only transfers data for players who exist in both tours and have WITB data in PGA.
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print('❌ DATABASE_URL not found')
        return
    
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("🔄 Starting WITB data transfer from PGA Tour to OGWR players...")
            
            # Find overlapping players with WITB data
            result = await session.execute(text('''
                SELECT 
                    pga.name,
                    pga.id as pga_id,
                    ogwr.id as ogwr_id,
                    COUNT(w.id) as witb_count
                FROM players pga
                JOIN players ogwr ON LOWER(TRIM(pga.name)) = LOWER(TRIM(ogwr.name))
                LEFT JOIN witb_items w ON pga.id = w.player_id
                WHERE pga.tour = 'PGA Tour' 
                AND ogwr.tour = 'OGWR'
                GROUP BY pga.name, pga.id, ogwr.id
                HAVING COUNT(w.id) > 0
                ORDER BY pga.name
            '''))
            
            overlapping_players = result.fetchall()
            print(f"📋 Found {len(overlapping_players)} overlapping players with WITB data")
            
            transferred_count = 0
            total_items_transferred = 0
            
            for player_info in overlapping_players:
                pga_id = player_info.pga_id
                ogwr_id = player_info.ogwr_id
                player_name = player_info.name
                witb_count = player_info.witb_count
                
                print(f"\n🏌️ Processing {player_name} ({witb_count} items)...")
                
                # Check if OGWR player already has WITB items
                result = await session.execute(text('''
                    SELECT COUNT(*) as count
                    FROM witb_items 
                    WHERE player_id = :ogwr_id
                '''), {"ogwr_id": ogwr_id})
                
                existing_count = result.fetchone().count
                
                if existing_count > 0:
                    print(f"  ⚠️ OGWR player already has {existing_count} WITB items, skipping...")
                    continue
                
                # Get all WITB items for the PGA player
                result = await session.execute(text('''
                    SELECT id, category, brand, model, loft, shaft, product_url
                    FROM witb_items 
                    WHERE player_id = :pga_id
                    ORDER BY category
                '''), {"pga_id": pga_id})
                
                witb_items = result.fetchall()
                
                # Transfer each WITB item to the OGWR player
                items_transferred = 0
                for item in witb_items:
                    new_id = str(uuid.uuid4())
                    
                    await session.execute(text('''
                        INSERT INTO witb_items (id, player_id, category, brand, model, loft, shaft, product_url)
                        VALUES (:id, :player_id, :category, :brand, :model, :loft, :shaft, :product_url)
                    '''), {
                        "id": new_id,
                        "player_id": ogwr_id,
                        "category": item.category,
                        "brand": item.brand,
                        "model": item.model,
                        "loft": item.loft,
                        "shaft": item.shaft,
                        "product_url": item.product_url
                    })
                    
                    items_transferred += 1
                
                print(f"  ✅ Transferred {items_transferred} WITB items")
                transferred_count += 1
                total_items_transferred += items_transferred
            
            # Commit all changes
            await session.commit()
            
            print(f"\n🎉 Transfer complete!")
            print(f"📊 Summary:")
            print(f"  - Players processed: {transferred_count}")
            print(f"  - Total WITB items transferred: {total_items_transferred}")
            
            # Verify the transfer
            print(f"\n🔍 Verification:")
            result = await session.execute(text('''
                SELECT 
                    p.name,
                    p.tour,
                    COUNT(w.id) as witb_count
                FROM players p
                LEFT JOIN witb_items w ON p.id = w.player_id
                WHERE p.tour = 'OGWR'
                GROUP BY p.id, p.name, p.tour
                HAVING COUNT(w.id) > 0
                ORDER BY witb_count DESC
                LIMIT 10
            '''))
            
            ogwr_with_witb = result.fetchall()
            print(f"  - OGWR players now with WITB data: {len(ogwr_with_witb)}")
            for player in ogwr_with_witb:
                print(f"    {player.name}: {player.witb_count} items")
                
        except Exception as e:
            print(f"❌ Error during transfer: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    print("🏌️ WITB Data Transfer Script")
    print("=" * 50)
    
    asyncio.run(transfer_pga_witb_to_ogwr())