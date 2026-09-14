from flask import Blueprint, jsonify, request
from .database import db
from .models import Note, Tag

notes_bp = Blueprint("notes", __name__)


def _get_or_create_tag(name: str) -> Tag:
    tag = Tag.query.filter_by(name=name.strip().lower()).first()
    if not tag:
        tag = Tag(name=name.strip().lower())
        db.session.add(tag)
    return tag


# ── GET /api/notes ────────────────────────────────────────────────────────────
@notes_bp.get("/notes")
def list_notes():
    q        = request.args.get("q", "").strip()
    tag_name = request.args.get("tag", "").strip().lower()
    sort     = request.args.get("sort", "created_at")
    order    = request.args.get("order", "desc")
    page     = request.args.get("page", 1,  type=int)
    per_page = request.args.get("per_page", 10, type=int)
    per_page = min(per_page, 100)

    query = Note.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Note.title.ilike(like), Note.content.ilike(like))
        )

    if tag_name:
        query = query.join(Note.tags).filter(Tag.name == tag_name)

    allowed_sort = {"created_at", "updated_at", "title"}
    sort = sort if sort in allowed_sort else "created_at"
    sort_col = getattr(Note, sort)
    query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "notes":    [n.to_dict() for n in pagination.items],
        "total":    pagination.total,
        "page":     pagination.page,
        "per_page": pagination.per_page,
        "pages":    pagination.pages,
    })


# ── GET /api/notes/<id> ───────────────────────────────────────────────────────
@notes_bp.get("/notes/<int:note_id>")
def get_note(note_id):
    note = db.get_or_404(Note, note_id)
    return jsonify(note.to_dict())


# ── POST /api/notes ───────────────────────────────────────────────────────────
@notes_bp.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    note = Note(
        title   = title,
        content = (data.get("content") or "").strip(),
    )

    for tag_name in data.get("tags", []):
        note.tags.append(_get_or_create_tag(tag_name))

    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


# ── PUT /api/notes/<id> ───────────────────────────────────────────────────────
@notes_bp.put("/notes/<int:note_id>")
def update_note(note_id):
    note = db.get_or_404(Note, note_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        note.title = title

    if "content" in data:
        note.content = data["content"].strip()

    if "tags" in data:
        note.tags = [_get_or_create_tag(t) for t in data["tags"]]

    db.session.commit()
    return jsonify(note.to_dict())


# ── DELETE /api/notes/<id> ────────────────────────────────────────────────────
@notes_bp.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = db.get_or_404(Note, note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": f"Note {note_id} deleted"}), 200


# ── GET /api/tags ─────────────────────────────────────────────────────────────
@notes_bp.get("/tags")
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([t.to_dict() for t in tags])


# ── health ────────────────────────────────────────────────────────────────────
@notes_bp.get("/health")
def health():
    return jsonify({"status": "ok"})
