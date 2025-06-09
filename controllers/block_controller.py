from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

#from collections import defaultdict
#from typing import List

from models.block_model import Block, BlockSchema
from models.state_model import State

def get_all_blocks(db: Session):
    blocks = db.query(Block).all()
    if not blocks:
        raise HTTPException(status_code=404, detail="No blocks found")
    return blocks

def add_block(test_id: int, block: Block, db: Session):

    new_block = Block(
        testId=test_id,
        name=block.name,
        instructions=block.instructions,
        numberOfQuestions = block.numberOfQuestions,
        questionsType = block.questionsType,
        numberOfAnswers = block.numberOfAnswers,
    )

    if block.order:
        new_block.order = block.order
    else:
        last_block = db.query(Block).filter(Block.testId == test_id).order_by(Block.order.desc()).first()
        if last_block:
            new_block.order = last_block.order + 1
        else:
            new_block.order = 1

    if block.hasTimeLimit:
        new_block.hasTimeLimit = block.hasTimeLimit
        new_block.timeLimit = block.timeLimit
    
    if block.randomizeQuestions:
        new_block.randomizeQuestions = block.randomizeQuestions

    if block.randomizeAnswers:
        new_block.randomizeAnswers = block.randomizeAnswers    

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block


def add_blocks_batch(
    test_id: int,
    blocks: List[Block],
    db: Session
):
    if not blocks:
        raise HTTPException(status_code=400, detail="No blocks provided")

    created_blocks = []

    # Определим последний order
    last_block = db.query(Block).filter(Block.testId == test_id).order_by(Block.order.desc()).first()
    current_order = last_block.order if last_block else 0

    for block in blocks:
        new_block = Block(
            testId=test_id,
            name=block.name,
            instructions=block.instructions,
            numberOfQuestions=block.numberOfQuestions,
            questionsType=block.questionsType,
            numberOfAnswers=block.numberOfAnswers,
        )

        # Логика порядка
        if block.order:
            new_block.order = block.order
        else:
            current_order += 1
            new_block.order = current_order

        # Остальные поля
        if block.hasTimeLimit:
            new_block.hasTimeLimit = True
            new_block.timeLimit = block.timeLimit

        if block.randomizeQuestions:
            new_block.randomizeQuestions = True

        if block.randomizeAnswers:
            new_block.randomizeAnswers = True

        db.add(new_block)
        created_blocks.append(new_block)

    db.commit()

    for b in created_blocks:
        db.refresh(b)

    return {
        "message": f"{len(created_blocks)} blocks successfully created",
        "blocks": [b.id for b in created_blocks]
    }

def get_block(test_id: int, block_id: int, db: Session):
    block = db.query(Block).filter(Block.testId == test_id, Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

def get_all_blocks_by_test(test_id: int, db: Session):
    blocks = db.query(Block).filter(Block.testId == test_id).order_by(Block.id).all()
    if not blocks:
        raise HTTPException(status_code=404, detail="No blocks found")
    return blocks

def update_block(test_id: int, block_id: int, block_data: BlockSchema, db: Session):
    existing_block = db.query(Block).filter(
        Block.testId == test_id,
        Block.id == block_id
    ).first()

    if not existing_block:
        raise HTTPException(status_code=404, detail="Block not found")

    # Обновляем вручную нужные поля
    for field, value in block_data.dict().items():
        setattr(existing_block, field, value)

    db.commit()
    db.refresh(existing_block)
    return existing_block


def delete_block(test_id: int, block_id: int, db: Session):
    block = db.query(Block).filter(Block.testId == test_id, Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    db.delete(block)
    db.commit()
    return {"message": "Block deleted successfully"}