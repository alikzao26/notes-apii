# 📝 Notes API

A RESTful API service for managing notes with tags, built with Flask and SQLAlchemy.  
Supports full CRUD, search, tag filtering, pagination, and Docker deployment.

---

## Tech Stack

- **Python 3.11** + **Flask 3.0**
- **SQLAlchemy** ORM + **SQLite** (dev) / **PostgreSQL** (prod)
- **pytest** for testing
- **Docker** + **docker-compose** for containerization
- Deployed on **[Render](https://render.com)**

---

## Project Structure

```
notes-api/
├── app/
│   ├── __init__.py      # app factory
│   ├── database.py      # SQLAlchemy instance
│   ├── models.py        # Note, Tag models
│   └── routes.py        # all API endpoints
├── tests/
│   ├── conftest.py      # pytest fixtures
│   └── test_api.py      # unit tests (25 tests)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── run.py               # app entry point
```

---

## Local Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/YOUR_USERNAME/notes-api.git
cd notes-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum
```

### 4. Run the development server

```bash
python run.py
```

The API will be available at `http://localhost:5000`.

---

## Running with Docker

```bash
# Build and start both web + postgres
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop
docker-compose down
```

---

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Verbose output
pytest -v
```

---

## API Reference

Base URL (local): `http://localhost:5000/api`  
Base URL (production): `https://notes-api.onrender.com/api`

### Endpoints

| Method   | URL                | Description                        |
|----------|--------------------|------------------------------------|
| `GET`    | `/health`          | Health check                       |
| `GET`    | `/notes`           | List all notes (search, filter, paginate) |
| `GET`    | `/notes/<id>`      | Get a single note                  |
| `POST`   | `/notes`           | Create a new note                  |
| `PUT`    | `/notes/<id>`      | Update a note                      |
| `DELETE` | `/notes/<id>`      | Delete a note                      |
| `GET`    | `/tags`            | List all tags                      |

### Query Parameters for `GET /notes`

| Parameter  | Type    | Default      | Description                            |
|------------|---------|--------------|----------------------------------------|
| `q`        | string  | —            | Search in title and content            |
| `tag`      | string  | —            | Filter by tag name                     |
| `sort`     | string  | `created_at` | Sort field: `created_at`, `updated_at`, `title` |
| `order`    | string  | `desc`       | `asc` or `desc`                        |
| `page`     | integer | `1`          | Page number                            |
| `per_page` | integer | `10`         | Items per page (max 100)               |

---

## curl Examples

### Health check
```bash
curl http://localhost:5000/api/health
```

### Get all notes
```bash
curl http://localhost:5000/api/notes
```

### Get all notes (with pagination)
```bash
curl "http://localhost:5000/api/notes?page=1&per_page=5"
```

### Search notes
```bash
curl "http://localhost:5000/api/notes?q=flask&sort=title&order=asc"
```

### Filter notes by tag
```bash
curl "http://localhost:5000/api/notes?tag=python"
```

### Get a single note
```bash
curl http://localhost:5000/api/notes/1
```

### Create a note
```bash
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "My first note", "content": "Hello, Notes API!", "tags": ["python", "flask"]}'
```

### Update a note
```bash
curl -X PUT http://localhost:5000/api/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "tags": ["updated"]}'
```

### Delete a note
```bash
curl -X DELETE http://localhost:5000/api/notes/1
```

### List all tags
```bash
curl http://localhost:5000/api/tags
```

---

## Example Response

`GET /api/notes`

```json
{
  "notes": [
    {
      "id": 1,
      "title": "My first note",
      "content": "Hello, Notes API!",
      "tags": [
        {"id": 1, "name": "python"},
        {"id": 2, "name": "flask"}
      ],
      "created_at": "2025-06-15T10:30:00.000000",
      "updated_at": "2025-06-15T10:30:00.000000"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

---

## Deploy to Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → connect your repo.
3. Set these values:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. Add environment variables in the Render dashboard:
   - `SECRET_KEY` — any long random string
   - `DATABASE_URL` — Render PostgreSQL connection string (add a PostgreSQL service)
5. Deploy. Your API will be live at `https://<your-app-name>.onrender.com`.

---

## Environment Variables

| Variable        | Required | Description                          |
|-----------------|----------|--------------------------------------|
| `SECRET_KEY`    | Yes      | Flask secret key                     |
| `DATABASE_URL`  | No       | DB connection string (default SQLite)|

---

## License

MIT
