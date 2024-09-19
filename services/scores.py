from config.schemas import ScoreModel
from sqlalchemy.orm import Session
from config.models import Score, User, CompetitionUserMapping, CompetitionUsers
from services.competitions import user_in_competition
from utils.exceptions import HTTPError
from datetime import datetime
from sqlalchemy.sql import func
from uuid import UUID


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
                   .offset((query["page"] - 1) * query["limit"])
                   .limit(query["limit"])
                   .all())
    print([score.user for score in scores_user])

    if scores_user is None:
        raise HTTPError(status_code=404, detail="Could not find users scores")
    return scores_user


def calculate_leaderboard(db: Session):
    results = (db.query(Score, func.avg(Score.wpm).label("average"),
                        func.avg(Score.accuracy).label("acc"))
               .join(User)
               .group_by(User.id)
               .all())
    new_results = [
        {"user": score.user, "accuracy": accuracy, "wpm": wpm, "score": score}
        for score, accuracy, wpm in results
    ]
    return new_results


def add_competition_score(user, competition_id: UUID, score_id, db: Session):

    if user_in_competition(user, competition_id, db) is None:
        print("In here")
        raise HTTPError(status_code=400, detail="No longer active to participate")

    score = db.query(CompetitionUsers).filter(CompetitionUsers.competition_id == competition_id,
                                              CompetitionUsers.user_id == user.id).first()
    if score is None:
        raise HTTPError(status_code=404, detail="User is not in competition.")

    setattr(score, "score_id", score_id)

    score_with_details = {
        "user_id": user.id,
        "competition_id": competition_id,
        "score_id": score_id,
    }
    new_score = CompetitionUserMapping(**score_with_details)
    db.add(new_score)
    db.commit()

    return score
