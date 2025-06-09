from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db  # твой dependency
from models.interpretation_model import Interpretation
from models.result_model import ScaleResult, TestResult, UserAnswerSchema
from controllers.result_controller import save_test_results, calculate_and_store_test_result
from models.scale_model import Scale 

result_routes = APIRouter()

@result_routes.post("/{test_id}/save")
def save_results(test_id: int, user_answers: UserAnswerSchema, db: Session = Depends(get_db)):
    return save_test_results(test_id, user_answers, db)
'''
@result_routes.get("/{test_id}/calculate")
def get_latest_result(test_id: int, user_id: int, db: Session = Depends(get_db)):
    return calculate_and_store_test_result(test_id, user_id, db)
'''
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

    response = []

    for result in results:
        scales_for_result = [sr for sr in all_scale_results if sr.testResultId == result.id]
        items = []

        for sr in scales_for_result:
            scale = all_scales.get(sr.scaleId)
            interp = all_interpretations.get(sr.interpretationId)

            items.append({
                "scaleName": f"{scale.pole1} ↔ {scale.pole2}" if scale and scale.pole2 else (scale.pole1 if scale else f"Шкала {sr.scaleId}"),
                "normalized": sr.normalized,
                "interpretation": interp.text if interp else "—"
            })

        response.append({
            "testResultId": result.id,
            "testId": result.testId,
            "results": items
        })

    return response