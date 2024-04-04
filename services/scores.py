from config.schemas import ScoreModel
from sqlalchemy.orm import Session
from config.models import Score
from utils.exceptions import HTTPError


def create_score(user, score: ScoreModel, db: Session):
    score_with_user_id = {**score.model_dump(exclude_none=True), "user_id": user.id}
    new_score = Score(**score_with_user_id)
    db.add(new_score)
    db.commit()

    return new_score


def get_scores_by_user(user, db: Session):
    scores = db.query(Score).filter(Score.user_id == user.id).all()
    if scores is None:
        raise HTTPError(status_code=404, detail="Could not find users scores")
    return scores
