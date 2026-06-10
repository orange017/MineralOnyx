from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Stone(db.Model):
    __tablename__ = "stones"

    index = db.Column(
        db.Integer,
        primary_key=True
    )

    collection_number = db.Column(
        db.String
    )

    sample_name = db.Column(
        db.String
    )

    photo = db.Column(
        db.LargeBinary
    )

    facts = db.Column(
        db.Text
    )

    source_location = db.Column(
        db.Text
    )

    cost = db.Column(
        db.Float
    )

    estimated_price = db.Column(
        db.Float
    )
