from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.check_admin import get_current_admin
from database.database import get_db  # твой dependency
from models.block_model import Block
from models.interpretation_model import Interpretation
from models.result_model import ScaleResult, TestResult, UserAnswerSchema
from controllers.result_controller import save_test_results, calculate_and_store_test_result
from models.scale_model import Scale
from models.test_model import Test
from models.user_model import User 

result_routes = APIRouter(dependencies=[Depends(get_current_admin)])

@result_routes.post("/{test_id}/save")
def save_results(test_id: int, user_answers: UserAnswerSchema, db: Session = Depends(get_db)):
    return save_test_results(test_id, user_answers, db)

@result_routes.get("/results/by-user/{user_id}")
def get_all_results_by_user(user_id: int, db: Session = Depends(get_db)):
    test_results = db.query(TestResult).filter(TestResult.userId == user_id).order_by(TestResult.id.desc()).all()
    
    if not test_results:
        raise HTTPException(status_code=404, detail="No results found for this user")

    response = []

    for result in test_results:
        scale_results = db.query(ScaleResult).filter(ScaleResult.testResultId == result.id).all()
        result_data = {
            "testResultId": result.id,
            "testId": result.testId,
            "results": []
        }

        for sr in scale_results:
            scale = db.query(Scale).get(sr.scaleId)
            interpretation = db.query(Interpretation).get(sr.interpretationId)

            result_data["results"].append({
                "scaleName": f"{scale.pole1} ←→ {scale.pole2}" if scale and scale.pole2 else (scale.pole1 if scale else f"Шкала {sr.scaleId}"),
                "normalized": sr.normalized,
                "interpretation": interpretation.text if interpretation else "—"
            })

        response.append(result_data)

    return response

@result_routes.get("/results/latest")
def get_latest_result_for_user(user_id: int, test_id: int, db: Session = Depends(get_db)):
    result = db.query(TestResult).filter(
        TestResult.userId == user_id,
        TestResult.testId == test_id
    ).order_by(TestResult.id.desc()).first()

    if not result:
        raise HTTPException(status_code=404, detail="No results found for this user and test")

    scale_results = db.query(ScaleResult).filter(ScaleResult.testResultId == result.id).all()

    pretty_results = []

    for sr in scale_results:
        scale = db.query(Scale).get(sr.scaleId)
        interpretation = db.query(Interpretation).get(sr.interpretationId)

        pretty_results.append({
            "scaleName": f"{scale.pole1} ←→ {scale.pole2}" if scale and scale.pole2 else (scale.pole1 if scale else f"Шкала {sr.scaleId}"),
            "normalized": sr.normalized,
            "interpretation": interpretation.text if interpretation else "—"
        })

    return {
        "testResultId": result.id,
        "testId": result.testId,
        "results": pretty_results
    }

@result_routes.get("/results/{user_id}")
def get_all_results_by_user(user_id: int, db: Session = Depends(get_db)):
    results = db.query(TestResult).filter(TestResult.userId == user_id).order_by(TestResult.id.desc()).all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found for this user")

    all_scale_results = db.query(ScaleResult).filter(
        ScaleResult.userId == user_id
    ).all()

    all_scales = {s.id: s for s in db.query(Scale).all()}
    all_interpretations = {i.id: i for i in db.query(Interpretation).all()}
    all_tests = {t.id: t for t in db.query(Test).all()}
    all_blocks = {b.id: b for b in db.query(Block).all()}

    response = []

    for result in results:
        scales_for_result = [sr for sr in all_scale_results if sr.testResultId == result.id]
        items = []

        for sr in scales_for_result:
            scale = all_scales.get(sr.scaleId)
            interp = all_interpretations.get(sr.interpretationId)
            block = all_blocks.get(scale.blockId) if scale and scale.blockId else None

            interp_for_scale = [
                i for i in all_interpretations.values()
                if i.scaleId == sr.scaleId and i.level is not None
            ]
            max_level = max((i.level for i in interp_for_scale), default=None)

            items.append({
                "scalePole1": scale.pole1 if scale else f"Шкала {sr.scaleId}",
                "scalePole2": scale.pole2 if scale and scale.pole2 else None,
                "normalized": sr.normalized,
                "interpretation": interp.text if interp else "—",
                "level": interp.level if interp else None,
                "block": block.name if block else None,
                "maxLevel": max_level
            })

        test_title = all_tests.get(result.testId).title if result.testId in all_tests else f"Тест {result.testId}"

        response.append({
            "testResultId": result.id,
            "testTitle": test_title,
            "testId": result.testId,
            "createdAt": result.created_at.isoformat(),
            "results": items
        })

    return response
