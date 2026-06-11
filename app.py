from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response
)
from markdown import markdown
from werkzeug.utils import secure_filename
import os
import uuid
from itertools import count
from pathlib import Path
from model.stone import db, Stone

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stones.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

UPLOAD_DIR = Path(app.static_folder) / "uploads"
ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}

def upload_photo(request):
    photo = request.files.get("photo")
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower().lstrip(".")
        if ext in ALLOWED_EXTENSIONS:
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            new_filename = f"{uuid.uuid4()}.{ext}"
            filepath = UPLOAD_DIR / new_filename
            photo.save(filepath)
            return new_filename


@app.route("/")
def index():

    q = request.args.get(
        "q",
        ""
    ).strip()

    query = Stone.query

    if q:
        query = query.filter(
            (Stone.collection_number.contains(q))
            |
            (Stone.sample_name.contains(q))
        )

    stones = query.order_by(
        Stone.collection_number
    ).all()

    return render_template(
        "index.html",
        stones=stones,
        query=q
    )


@app.route("/stone/<int:stone_id>")
def stone(stone_id):

    stone = Stone.query.get_or_404(stone_id)

    facts_html = markdown(
        stone.facts or "",
        extensions=[
            "tables",
            "fenced_code"
        ]
    )

    return render_template(
        "stone.html",
        stone=stone,
        facts_html=facts_html
    )


@app.route(
    "/new",
    methods=["GET", "POST"]
)
def new():

    if request.method == "POST":

        stone = Stone(
            collection_number=request.form.get(
                "collection_number"
            ),
            sample_name=request.form.get(
                "sample_name"
            ),
            photo=upload_photo(request),
            facts=request.form.get(
                "facts"
            ),
            source_location=request.form.get(
                "source_location"
            ),
            cost=request.form.get(
                "cost"
            ) or None,
            estimated_price=request.form.get(
                "estimated_price"
            ) or None
        )

        db.session.add(stone)
        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        stone=None
    )


@app.route(
    "/edit/<int:stone_id>",
    methods=["GET", "POST"]
)
def edit(stone_id):

    stone = Stone.query.get_or_404(
        stone_id
    )

    if request.method == "POST":

        stone.collection_number = (
            request.form.get(
                "collection_number"
            )
        )

        stone.sample_name = (
            request.form.get(
                "sample_name"
            )
        )

        stone.photo = (
            upload_photo(request)
        )

        stone.facts = (
            request.form.get(
                "facts"
            )
        )

        stone.source_location = (
            request.form.get(
                "source_location"
            )
        )

        stone.cost = (
            request.form.get(
                "cost"
            ) or None
        )

        stone.estimated_price = (
            request.form.get(
                "estimated_price"
            ) or None
        )

        db.session.commit()

        return redirect(
            url_for(
                "stone",
                stone_id=stone.id
            )
        )

    return render_template(
        "edit.html",
        stone=stone
    )


@app.route(
    "/delete/<int:stone_id>"
)
def delete(stone_id):

    stone = Stone.query.get_or_404(
        stone_id
    )

    db.session.delete(stone)
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(
        debug=True
    )