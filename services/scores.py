from config.schemas import ScoreModel
from sqlalchemy.orm import Session
from config.models import Score
from utils.exceptions import HTTPError
from datetime import datetime


def create_score(user, score: ScoreModel, db: Session):
    # Calculations
    wpm = score.characters / 5 / (score.duration / 60)
    correct = score.characters - score.errors
    accuracy = round((correct / score.characters) * 100)

    score_with_details = {
        **score.model_dump(exclude_none=True, ),
        "user_id": user.id,
        "played_at": datetime.now(),
        "wpm": wpm,
        "accuracy": accuracy
    }
    print(score_with_details)
    del score_with_details["errors"]
    new_score = Score(**score_with_details)
    db.add(new_score)
    db.commit()

    return new_score


def get_scores_by_user(user, db: Session):
    scores = db.query(Score).filter(Score.user_id == user.id).all()
    if scores is None:
        raise HTTPError(status_code=404, detail="Could not find users scores")
    return scores
