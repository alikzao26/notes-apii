from datetime import datetime, timezone
from .database import db

# Association table for Note <-> Tag many-to-many
note_tags = db.Table(
    "note_tags",
    db.Column("note_id", db.Integer, db.ForeignKey("notes.id"), primary_key=True),
    db.Column("tag_id",  db.Integer, db.ForeignKey("tags.id"),  primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Note(db.Model):
    __tablename__ = "notes"

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(256), nullable=False)
    content    = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    tags = db.relationship("Tag", secondary=note_tags, backref="notes", lazy="select")

    def to_dict(self):
        return {
            "id":         self.id,
            "title":      self.title,
            "content":    self.content,
            "tags":       [t.to_dict() for t in self.tags],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
