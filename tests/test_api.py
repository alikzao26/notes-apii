import pytest


# ── helpers ───────────────────────────────────────────────────────────────────

def create_note(client, title="Test note", content="Some content", tags=None):
    payload = {"title": title, "content": content}
    if tags:
        payload["tags"] = tags
    return client.post("/api/notes", json=payload)


# ── health ────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# ── create ────────────────────────────────────────────────────────────────────

def test_create_note_basic(client):
    r = create_note(client, title="Hello", content="World")
    assert r.status_code == 201
    data = r.get_json()
    assert data["title"] == "Hello"
    assert data["content"] == "World"
    assert data["id"] is not None
    assert data["created_at"] is not None


def test_create_note_with_tags(client):
    r = create_note(client, title="Tagged", tags=["python", "flask"])
    assert r.status_code == 201
    tag_names = [t["name"] for t in r.get_json()["tags"]]
    assert "python" in tag_names
    assert "flask" in tag_names


def test_create_note_missing_title(client):
    r = client.post("/api/notes", json={"content": "no title"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_create_note_empty_body(client):
    r = client.post("/api/notes", json={})
    assert r.status_code == 400


# ── list ──────────────────────────────────────────────────────────────────────

def test_list_notes_empty(client):
    r = client.get("/api/notes")
    assert r.status_code == 200
    data = r.get_json()
    assert data["notes"] == []
    assert data["total"] == 0


def test_list_notes_returns_all(client):
    create_note(client, title="Note 1")
    create_note(client, title="Note 2")
    r = client.get("/api/notes")
    assert r.get_json()["total"] == 2


def test_list_notes_pagination(client):
    for i in range(5):
        create_note(client, title=f"Note {i}")
    r = client.get("/api/notes?page=1&per_page=3")
    data = r.get_json()
    assert len(data["notes"]) == 3
    assert data["total"] == 5
    assert data["pages"] == 2


def test_list_notes_search(client):
    create_note(client, title="Python tips", content="Use list comprehensions")
    create_note(client, title="Cooking recipes", content="Bake at 180")
    r = client.get("/api/notes?q=python")
    data = r.get_json()
    assert data["total"] == 1
    assert data["notes"][0]["title"] == "Python tips"


def test_list_notes_filter_by_tag(client):
    create_note(client, title="Tagged", tags=["work"])
    create_note(client, title="Untagged")
    r = client.get("/api/notes?tag=work")
    data = r.get_json()
    assert data["total"] == 1
    assert data["notes"][0]["title"] == "Tagged"


# ── get single ────────────────────────────────────────────────────────────────

def test_get_note_by_id(client):
    note_id = create_note(client, title="Find me").get_json()["id"]
    r = client.get(f"/api/notes/{note_id}")
    assert r.status_code == 200
    assert r.get_json()["title"] == "Find me"


def test_get_note_not_found(client):
    r = client.get("/api/notes/99999")
    assert r.status_code == 404


# ── update ────────────────────────────────────────────────────────────────────

def test_update_note_title(client):
    note_id = create_note(client, title="Old title").get_json()["id"]
    r = client.put(f"/api/notes/{note_id}", json={"title": "New title"})
    assert r.status_code == 200
    assert r.get_json()["title"] == "New title"


def test_update_note_content(client):
    note_id = create_note(client, content="old").get_json()["id"]
    r = client.put(f"/api/notes/{note_id}", json={"content": "new content"})
    assert r.status_code == 200
    assert r.get_json()["content"] == "new content"


def test_update_note_tags(client):
    note_id = create_note(client, tags=["a"]).get_json()["id"]
    r = client.put(f"/api/notes/{note_id}", json={"tags": ["b", "c"]})
    tag_names = [t["name"] for t in r.get_json()["tags"]]
    assert "b" in tag_names
    assert "c" in tag_names
    assert "a" not in tag_names


def test_update_note_empty_title_rejected(client):
    note_id = create_note(client).get_json()["id"]
    r = client.put(f"/api/notes/{note_id}", json={"title": "  "})
    assert r.status_code == 400


def test_update_note_not_found(client):
    r = client.put("/api/notes/99999", json={"title": "x"})
    assert r.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_note(client):
    note_id = create_note(client).get_json()["id"]
    r = client.delete(f"/api/notes/{note_id}")
    assert r.status_code == 200
    assert client.get(f"/api/notes/{note_id}").status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/api/notes/99999")
    assert r.status_code == 404


# ── tags ──────────────────────────────────────────────────────────────────────

def test_list_tags(client):
    create_note(client, tags=["alpha", "beta"])
    r = client.get("/api/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.get_json()]
    assert "alpha" in names
    assert "beta" in names


def test_tags_deduplicated(client):
    create_note(client, tags=["dup"])
    create_note(client, tags=["dup"])
    r = client.get("/api/tags")
    assert len([t for t in r.get_json() if t["name"] == "dup"]) == 1
