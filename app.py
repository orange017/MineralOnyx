from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response
)

from model.stone import db, Stone

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stones.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


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

    stone = Stone.query.get_or_404(
        stone_id
    )

    return render_template(
        "stone.html",
        stone=stone
    )


@app.route("/photo/<int:stone_id>")
def photo(stone_id):

    stone = Stone.query.get_or_404(
        stone_id
    )

    if not stone.photo:
        return "", 404

    blob = stone.photo

    if blob.startswith(b"\x89PNG"):
        mime = "image/png"
    elif blob.startswith(b"\xff\xd8"):
        mime = "image/jpeg"
    elif blob.startswith(b"GIF87a") or blob.startswith(b"GIF89a"):
        mime = "image/gif"
    else:
        mime = "application/octet-stream"

    return Response(
        blob,
        mimetype=mime
    )


@app.route(
    "/new",
    methods=["GET", "POST"]
)
def new():

    if request.method == "POST":

        photo_blob = None

        photo = request.files.get(
            "photo"
        )

        if photo and photo.filename:
            photo_blob = photo.read()

        stone = Stone(
            collection_number=request.form.get(
                "collection_number"
            ),
            sample_name=request.form.get(
                "sample_name"
            ),
            photo=photo_blob,
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

        photo = request.files.get(
            "photo"
        )

        if photo and photo.filename:
            stone.photo = photo.read()

        db.session.commit()

        return redirect(
            url_for(
                "stone",
                stone_id=stone.index
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