from config.models import Competition
from sqlalchemy.orm import Session
from config.schemas import CompetitionModel
from utils.exceptions import validate_wtc_email


def create_competition(user, competition: CompetitionModel, db: Session):

    [validate_wtc_email(email) for email in competition.competitors]

    data = {
        **competition.model_dump(exclude_none=True),
        "creator_id": user.id,
    }

    new_competition = Competition(**data)

    db.add(new_competition)
    db.commit()

    return new_competition


def delete_competition():
    pass


def remove_competitor():
    pass


def add_competitor():
    pass


def get_competition():
    pass


def update_competition():
    pass


def get_competitors():
    pass
