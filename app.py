from flask import Flask, render_template, request, redirect, url_for
from flask import Response
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

DB_FILE = "stones.db"
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    q = request.args.get("q", "")

    conn = get_db()

    if q:
        stones = conn.execute(
            """
            SELECT *
            FROM stones
            WHERE collection_number LIKE ?
               OR sample_name LIKE ?
            ORDER BY collection_number
            """,
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    else:
        stones = conn.execute(
            "SELECT * FROM stones ORDER BY collection_number"
        ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        stones=stones,
        query=q
    )


@app.route("/stone/<int:stone_id>")
def stone(stone_id):
    
    conn = get_db()

    stone = conn.execute(
        "SELECT * FROM stones WHERE \"index\"=?",
        (stone_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "stone.html",
        stone=stone
    )


@app.route("/edit/<int:stone_id>", methods=["GET", "POST"])
def edit(stone_id):
    conn = get_db()

    if request.method == "POST":

        photo = request.files.get("photo")

        filename = None

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        if filename:
            conn.execute(
                """
                UPDATE stones
                SET
                    collection_number=?,
                    sample_name=?,
                    photo=?,
                    facts=?,
                    source_location=?,
                    cost=?,
                    estimated_price=?
                WHERE \"index\"=?
                """,
                (
                    request.form["collection_number"],
                    request.form["sample_name"],
                    filename,
                    request.form["facts"],
                    request.form["source_location"],
                    request.form["cost"],
                    request.form["estimated_price"],
                    stone_id
                )
            )
        else:
            conn.execute(
                """
                UPDATE stones
                SET
                    collection_number=?,
                    sample_name=?,
                    facts=?,
                    source_location=?,
                    cost=?,
                    estimated_price=?
                WHERE \"index\"=?
                """,
                (
                    request.form["collection_number"],
                    request.form["sample_name"],
                    request.form["facts"],
                    request.form["source_location"],
                    request.form["cost"],
                    request.form["estimated_price"],
                    stone_id
                )
            )

        conn.commit()

        return redirect(
            url_for("stone", stone_id=stone_id)
        )

    stone = conn.execute(
        "SELECT * FROM stones WHERE \"index\"=?",
        (stone_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        stone=stone
    )


@app.route("/new", methods=["GET", "POST"])
def new():

    conn = get_db()

    if request.method == "POST":

        conn.execute(
            """
            INSERT INTO stones(
                collection_number,
                sample_name,
                photo,
                facts,
                source_location,
                cost,
                estimated_price
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                request.form["collection_number"],
                request.form["sample_name"],
                "",
                request.form["facts"],
                request.form["source_location"],
                request.form["cost"],
                request.form["estimated_price"]
            )
        )

        conn.commit()

        return redirect("/")

    return render_template("edit.html", stone=None)


@app.route("/delete/<int:stone_id>")
def delete(stone_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM stones WHERE \"index\"=?",
        (stone_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/photo/<int:stone_id>")
def photo(stone_id):
    conn = sqlite3.connect("stones.db")

    row = conn.execute(
        "SELECT photo FROM stones WHERE \"index\"=?",
        (stone_id,)
    ).fetchone()

    conn.close()

    if row is None or row[0] is None:
        return "", 404

    return Response(
        row[0],
        mimetype="image/jpeg"
    )

if __name__ == "__main__":
    app.run(debug=True)