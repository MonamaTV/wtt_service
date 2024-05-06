from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from pydantic import EmailStr
from config.models import Competition, association_table, User, CompetitionUserMapping, Score
from sqlalchemy.orm import Session
from sqlalchemy import insert, or_
from config.schemas import CompetitionModel
from utils.exceptions import validate_wtc_email
from uuid import UUID
from services.users import get_users_by_email, get_user_by_email
from utils.exceptions import HTTPError


def create_competition(user, competition: CompetitionModel, db: Session):
    if len(competition.competitors) == 0:
        raise HTTPError(status_code=400, detail="At least add one peer.")

    [validate_wtc_email(email) for email in competition.competitors]

    data = {
        **competition.model_dump(exclude_none=True),
        "creator_id": user.id,
        "expires_in": datetime.utcnow() + timedelta(days=5)
    }

    del data["competitors"]

    new_competition = Competition(**data)

    users = get_users_by_email(competition.competitors, db)
    if len(users) == 0:
        raise HTTPError(status_code=400, detail="Peer(s) not found.")

    db.add(new_competition)

    db.commit()
    print([{"user_id": user.id, "competition_id": new_competition.id}
           for user in users])
    # Add the competitors now after creating a competition...
    db.execute(insert(association_table),
               [{"user_id": user.id, "competition_id": new_competition.id}
                for user in users])
    db.commit()

    return new_competition


def get_competitions(user, db: Session):
    competitions = (db.query(Competition).join(CompetitionUserMapping)
                    .filter(or_(Competition.creator_id == user.id, CompetitionUserMapping.user_id == user.id)).all())
    print([user.users for user in competitions])
    print([u.user for u in competitions])
    if competitions is None:
        raise HTTPError(status_code=400, detail="Competitions not found.")
    return competitions


def delete_competition(user, competition_id: UUID, db: Session):
    deleted_competition = (db.query(Competition).filter(Competition.creator_id == user.id,
                                                        Competition.id == competition_id).delete())

    db.commit()
    if deleted_competition is None:
        raise HTTPError(status_code=400, detail="Competition not found.")
    return deleted_competition


def remove_competitor(current_user, user_id, competition_id, db: Session):
    removed = (db.query(CompetitionUserMapping).join(Competition)
               .filter(CompetitionUserMapping.user_id == user_id,
                       Competition.id == competition_id,
                       Competition.creator_id == current_user.id)).delete()
    if removed is None:
        raise HTTPError(status_code=400, detail="Peer is not in the competition.")

    return removed


def leave_competition(user, competition_id: UUID, db: Session):
    deleted = (db.query(CompetitionUserMapping)
               .filter(CompetitionUserMapping.user_id == user.id,
                       CompetitionUserMapping.competition_id == competition_id).delete())

    db.commit()
    if deleted is None:
        raise HTTPError(status_code=400, detail=f"User not in competition: {competition_id}")
    return deleted


def add_competitor(curr_user, email: EmailStr, competition_id: UUID, db: Session):
    user = get_user_by_email(email, db)
    if user is None:
        raise HTTPError(status_code=400, detail=f"User not found")

    competitor = CompetitionUserMapping(user_id=user.id, competition_id=competition_id)
    db.add(competitor)
    db.commit()
    return competitor


def add_competitors(competition_id: UUID, competitors: List[EmailStr]):
    pass


def get_competition(user, competition_id: UUID, db: Session):
    competition = (db.query(Competition).join(User)
                   .join(Competition.id == competition_id, Competition.creator_id == user.id).first())

    if competition is None:
        raise HTTPError(status_code=400, detail="Competition not found.")

    return competition


def get_competitors(_, competition_id: UUID, db: Session):
    competitors = db.query(User).join(Competition).filter(Competition.id == competition_id).all()
    if competitors is None:
        raise HTTPError(status_code=400, detail="Competition has no competitors.")
    return competitors


def update_competition():
    pass


def user_in_competition(curr_user, competition_id: UUID, db: Session):
    user = db.query(CompetitionUserMapping).join(Competition).filter(CompetitionUserMapping.user_id == curr_user.id,
                                                                     CompetitionUserMapping.competition_id == competition_id,
                                                                     Competition.expires_in > datetime.now()).first()
    if user is None:
        raise HTTPException(detail="Competing in this competition is no longer valid.", status_code=400)

    if user.score_id is not None:
        raise HTTPException(detail="User has already participated in the competition.", status_code=400)

    return user


def competition_details(current_user, competition_id: UUID, db: Session):
    details = (db.query(CompetitionUserMapping).join(Competition).join(User)
               .filter(CompetitionUserMapping.competition_id == competition_id)).all()

    if details is None:
        raise HTTPException(detail="No competition info at the moment.", status_code=400)

    unpacked = ([{"user": detail.user, "score": detail.score, "competition_id": detail.competition_id}
                 for detail in details])

    return unpacked


def competition_information(current_user, competition_id: UUID, db: Session):
    information = db.query(Competition).join(User).filter(Competition.id == competition_id).first()

    if information is None:
        raise HTTPException(detail="No competition info at the moment.", status_code=400)

    print(information.user)

    return information
