from config.schemas import ScoreModel
from sqlalchemy.orm import Session
from config.models import Score, User
from utils.exceptions import HTTPError
from datetime import datetime
from sqlalchemy.sql import func


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
    del score_with_details["errors"]
    new_score = Score(**score_with_details)
    db.add(new_score)
    db.commit()

    return new_score


def get_sort(sorter):
    if sorter == 1:
        return Score.played_at
    elif sorter == 2:
        return Score.accuracy
    else:
        return Score.wpm


def get_scores_by_user(user, query, db: Session):
    scores_user = (db.query(Score).join(User)
                   .filter(User.id == user.id)
                   .order_by(get_sort(query["sort"]))
                   .limit(query["limit"])
                   .all())
    print([score.user for score in scores_user])
    some = calculate_leaderboard(db)
    for user in some:
        print("User", user[0], user[1])
    if scores_user is None:
        raise HTTPError(status_code=404, detail="Could not find users scores")
    return scores_user


def calculate_leaderboard(db: Session):
    results = db.query(Score, func.avg(Score.wpm).label("average")).join(User).all()
    return results
