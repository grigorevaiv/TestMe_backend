from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.interpretation_model import Interpretation
from models.invitation_model import Invitation
from models.norm_model import Norm
from models.result_model import ScaleResult, TestResult, TestResultSchema, UserAnswerSchema, UserAnswer
from models.block_model import Block
from models.question_model import Question
from models.answer_model import Answer
from models.scale_model import Scale
from models.weight_model import Weight

def save_test_results(test_id: int, user_answers: UserAnswerSchema, db: Session):
    if user_answers.userId is None:
        raise HTTPException(status_code=400, detail="Missing userId in request body")
    
    if not user_answers.token:
        raise HTTPException(status_code=400, detail="Missing token in request body")

    invitation = db.query(Invitation).filter(Invitation.token == user_answers.token).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if invitation.used:
        raise HTTPException(status_code=400, detail="Invitation already used")

    invitation.used = True
    db.commit()

    result = TestResult(testId=test_id, userId=user_answers.userId, created_at=datetime.now())
    db.add(result)
    db.flush()

    user_answers_to_save = []

    for question_id, answers in user_answers.answers.items():
        for answer_id in answers:
            user_answers_to_save.append(
                UserAnswer(
                    testResultId=result.id,
                    questionId=int(question_id),
                    answerId=int(answer_id)
                )
            )

    db.add_all(user_answers_to_save)
    db.commit()
    final_result = calculate_and_store_test_result(
        test_id=test_id,
        user_id=user_answers.userId,
        db=db
    )


    return {"testSaved": "ok", "resultId": result.id, "finalResult": final_result}

def calculate_and_store_test_result(test_id: int, user_id: int, db: Session):
    result = (
        db.query(TestResult)
        .filter(TestResult.testId == test_id, TestResult.userId == user_id)
        .order_by(TestResult.id.desc())
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="No results found for this test and user")

    user_answers = db.query(UserAnswer).filter(UserAnswer.testResultId == result.id).all()
    answer_ids = [ua.answerId for ua in user_answers]

    weights = db.query(Weight).filter(Weight.answerId.in_(answer_ids)).all()

    scale_scores = defaultdict(int)
    for w in weights:
        scale_scores[w.scaleId] += w.value

    norms = db.query(Norm).filter(Norm.scaleId.in_(scale_scores.keys())).all()
    norm_map = {norm.scaleId: norm for norm in norms}

    db.query(ScaleResult).filter(ScaleResult.testResultId == result.id).delete()
    db.flush()

    pretty_results = []

    for scale_id, raw_score in scale_scores.items():
        norm = norm_map.get(scale_id)
        normalized = None

        if norm and norm.type == "sten":
            normalized = round(5 + 2 * (raw_score - norm.mean) / norm.stdDev)
            normalized = max(1, min(10, normalized))

        interpretation = None
        if normalized is not None:
            interpretations = db.query(Interpretation).filter(
                Interpretation.scaleId == scale_id
            ).all()

            if len(interpretations) == 1:
                interpretation = interpretations[0]
            else:
                interpretation = select_interpretation_by_levels(interpretations, normalized)

        scale_result = ScaleResult(
            testResultId=result.id,
            testId=result.testId,
            userId=result.userId,
            scaleId=scale_id,
            normalized=normalized,
            interpretationId=interpretation.id if interpretation else None
        )
        db.add(scale_result)

        scale = db.query(Scale).get(scale_id)

        pretty_results.append({
            "scaleName": f"{scale.pole1} ←→ {scale.pole2}" if scale and scale.pole2 else (scale.pole1 if scale else f"Шкала {scale_id}"),
            "raw": raw_score,
            "normalized": normalized,
            "interpretation": interpretation.text if interpretation else "—"
        })

    db.commit()

    return {
        "testResultId": result.id,
        "results": pretty_results
    }


def select_interpretation_by_levels(interpretations, normalized: int):
    levels = sorted(set(i.level for i in interpretations))
    count = len(levels)

    if count == 0:
        return None

    step = 9 / count

    index = min(int((normalized - 1) / step), count - 1)

    target_level = levels[index]

    return next((i for i in interpretations if i.level == target_level), None)


from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import HTTPException

from collections import defaultdict

def read_test_results(test_id: int, db: Session):
    results_ids = db.query(TestResult).filter(TestResult.testId == test_id).all()
    if not results_ids:
        raise HTTPException(status_code=404, detail="No results found for this test")

    result_ids = [r.id for r in results_ids]

    user_answers = db.query(UserAnswer).filter(UserAnswer.testResultId.in_(result_ids)).all()

    blocks = db.query(Block).filter(Block.testId == test_id).all()
    block_ids = [b.id for b in blocks]

    questions = db.query(Question).filter(Question.blockId.in_(block_ids)).all()
    question_ids = [q.id for q in questions]

    answers = db.query(Answer).filter(Answer.questionId.in_(question_ids)).all()

    answer_to_question = {a.id: a.questionId for a in answers}
    frequencies = defaultdict(lambda: defaultdict(int))
    for answer in answers:
        frequencies[answer.questionId][answer.id] = 0

    for ua in user_answers:
        answer_id = ua.answerId
        question_id = answer_to_question.get(answer_id)
        if question_id:
            frequencies[question_id][answer_id] += 1

    return frequencies
