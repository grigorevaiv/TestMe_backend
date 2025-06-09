from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db

from models.block_model import BlockSchema

from controllers.block_controller import (
    add_block,
    get_block,
    get_all_blocks_by_test,
    update_block,
    delete_block,
    get_all_blocks,
    add_blocks_batch,
)

block_routes = APIRouter()

@block_routes.get("/blocks/all")
def getAllBlocks(db: Session = Depends(get_db)):
    """
    Retrieve all blocks from the database.
    """
    try:
        return get_all_blocks(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@block_routes.post("/{test_id}/blocks")
def addBlock(test_id: int, block: BlockSchema, db: Session = Depends(get_db)):
    return add_block(test_id, block, db)

@block_routes.post("/blocks/batch/{test_id}")
def addBlocksBatch(test_id: int, blocks: List[BlockSchema], db: Session = Depends(get_db)):
    """
    Add multiple blocks to a test in a single request.
    """
    return add_blocks_batch(test_id, blocks, db)

@block_routes.get("/{test_id}/blocks/{block_id}")
def getBlock(test_id: int, block_id: int, db: Session = Depends(get_db)):
    return get_block(test_id, block_id, db)

@block_routes.get("/{test_id}/blocks")
def getAllBlocksByTest(test_id: int, db: Session = Depends(get_db)):
    return get_all_blocks_by_test(test_id, db)

@block_routes.put("/{test_id}/blocks/{block_id}")
def updateBlock(test_id: int, block_id: int, block: BlockSchema, db: Session = Depends(get_db)):
    return update_block(test_id, block_id, block, db)

@block_routes.delete("/{test_id}/blocks/{block_id}")
def deleteBlock(test_id: int, block_id: int, db: Session = Depends(get_db)):
    return delete_block(test_id, block_id, db)