from datetime import datetime, timedelta
from typing import List
from pydantic import EmailStr
from config.models import Competition, association_table, User
from sqlalchemy.orm import Session
from sqlalchemy import insert
from config.schemas import CompetitionModel
from utils.exceptions import validate_wtc_email
from uuid import UUID
from services.users import get_users_by_email
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
    competitions = db.query(Competition).join(User).filter(Competition.creator_id == user.id).all()
    print([user.users for user in competitions])
    if competitions is None:
        raise HTTPError(status_code=400, detail="Competitions not found")
    return competitions


def delete_competition(user, competition_id: UUID, db: Session):
    deleted_competition = db.query(Competition).filter(Competition.creator_id == user.id,
                                                       Competition.id == competition_id).delete()
    if deleted_competition is None:
        raise HTTPError(status_code=400, detail="Competition not found.")
    return deleted_competition


def remove_competitor():
    pass


def leave_competition():
    pass


def add_competitor():
    pass


def add_competitors(competition_id: UUID, competitors: List[EmailStr]):
    pass


def get_competition():
    pass


def update_competition():
    pass


def get_competitors():
    pass
