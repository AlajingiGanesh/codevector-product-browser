# CodeVector Product Browser

Interview-ready FastAPI and MySQL solution for browsing about 200,000 products with cursor-based pagination.

The core backend goal is correctness under changing data without using `OFFSET`. The bonus frontend is a lightweight Next.js dashboard that consumes the API with infinite scrolling.

## Tech Stack

- Backend: Python 3.12, FastAPI
- ORM: SQLAlchemy 2.x
- Validation: Pydantic 2.x
- Database: MySQL 8
- Deployment: Render
- Bonus frontend: Next.js, Tailwind CSS, Framer Motion

## Project Structure

```text
backend/
  app/
    api/routers/        # FastAPI route handlers
    core/               # config, database, logging, cursor helpers
    models/             # SQLAlchemy models and indexes
    repositories/       # database query logic
    schemas/            # Pydantic response models
    services/           # business logic and pagination rules
  scripts/
    seed_products.py    # 200,000 product batch seeder
  tests/
frontend/
  app/                  # Next.js app router page
  components/           # dashboard UI components
  lib/api.ts            # API client
```

## Quick Start

1. Start MySQL 8:

```bash
docker compose up -d
```

2. Configure the backend:

```bash
cd backend
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Create tables and seed 200,000 rows:

```bash
python scripts/seed_products.py --count 200000 --batch-size 5000 --reset
```

4. Run the API:

```bash
uvicorn app.main:app --reload
```

5. Call the endpoint:

```bash
curl "http://localhost:8000/api/products?limit=25"
```

## API

### `GET /api/products`

Query parameters:

- `limit`: page size, default `25`, max `100`
- `category`: optional category filter
- `cursor`: opaque cursor returned by the previous response

Response:

```json
{
  "data": [],
  "next_cursor": "eyJ1cGRhdGVkX2F0IjoiMjAyNi0wMS0wMlQwMzowNDo...",
  "has_more": true
}
```

The cursor is Base64 URL-safe JSON containing:

```json
{
  "updated_at": "2026-01-02T03:04:05.123456",
  "id": 123
}
```

Clients should treat it as opaque and never build it manually.

## Database Design

The `products` table stores:

- `id BIGINT PRIMARY KEY AUTO_INCREMENT`
- `name VARCHAR(255)`
- `category VARCHAR(64)`
- `price DECIMAL(10,2)`
- `created_at DATETIME(6)`
- `updated_at DATETIME(6)`

`DECIMAL(10,2)` is used for price because money should not be stored as binary floating point.

`DATETIME(6)` preserves microseconds, which reduces timestamp ties. `id` is still included in the ordering so pagination remains deterministic when two rows have the same `updated_at`.

## Cursor Pagination

Products are always ordered by:

```sql
ORDER BY updated_at DESC, id DESC
```

For the first request, the API returns the newest products.

For the next request, the cursor contains the last product from the previous page. If the last product had:

```text
updated_at = 2026-01-02 03:04:05.123456
id = 123
```

the next page uses:

```sql
WHERE
  updated_at < '2026-01-02 03:04:05.123456'
  OR (updated_at = '2026-01-02 03:04:05.123456' AND id < 123)
ORDER BY updated_at DESC, id DESC
LIMIT 26;
```

The API fetches `limit + 1` rows. If one extra row exists, `has_more` is `true`; only `limit` rows are returned.

## Why OFFSET Fails

Offset pagination asks the database to skip a number of rows:

```sql
SELECT * FROM products
ORDER BY updated_at DESC, id DESC
LIMIT 25 OFFSET 25;
```

This is fragile while users browse changing data.

Example:

1. Page 1 returns `[P100, P99]`.
2. A new product `P101` is inserted at the top.
3. Page 2 with `OFFSET 2` now skips `[P101, P100]`.
4. The user sees `[P99, P98]`.

`P99` is duplicated because the insert shifted the row positions. Similar shifts can cause missed rows.

Cursor pagination does not count positions. It anchors the next query after the last seen sort key:

```sql
WHERE (updated_at, id) is strictly older than the last seen row
```

After `[P100, P99]`, the next page asks for rows older than `P99`. A newly inserted `P101` does not change that boundary, so the next page correctly starts at `P98`.

## Indexing Strategy

```python
Index("ix_products_updated_at_id", "updated_at", "id")
Index("ix_products_category_updated_at_id", "category", "updated_at", "id")
```

### `ix_products_updated_at_id`

Supports browsing all products by newest first:

```sql
ORDER BY updated_at DESC, id DESC
```

MySQL 8 can scan this B-tree backward for descending order. The same index helps the cursor predicate find rows older than the cursor without scanning the full table.

### `ix_products_category_updated_at_id`

Supports category browsing:

```sql
WHERE category = 'Books'
ORDER BY updated_at DESC, id DESC
```

`category` comes first because it is an equality filter. After MySQL narrows to one category, `updated_at, id` are already in the order needed for fast pagination.

## Performance Notes

- No `OFFSET`, so deep pages do not become slower because of skipped rows.
- Page size is capped at `100` to protect the API and database.
- The repository only fetches `limit + 1` rows.
- Connection pooling uses `pool_pre_ping` to avoid stale MySQL connections.
- The seed script inserts batches of `5,000` rows by default instead of inserting one row at a time.

## Running Tests

```bash
cd backend
pytest
```

## Bonus Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

The UI includes:

- Dark mode
- Category filters
- Product cards
- Infinite scrolling
- Loading skeletons
- Framer Motion transitions

## Render Deployment

This repo includes `render.yaml` for the backend web service.

Render does not provide MySQL as its default managed database. Use a MySQL 8 provider such as Aiven, PlanetScale-compatible MySQL, AWS RDS, or another managed MySQL host, then set:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/DATABASE
```

Recommended production settings:

```text
ENVIRONMENT=production
AUTO_CREATE_TABLES=false
CORS_ORIGINS=https://your-frontend-domain.com
```

For a real production system, table creation should be handled by migrations. `AUTO_CREATE_TABLES` exists only to simplify local demos.

## Interview Talking Points

- Cursor pagination is also called keyset pagination.
- The sort order must be deterministic, so `id` breaks ties after `updated_at`.
- The cursor uses the exact same columns as the `ORDER BY`.
- The query asks for rows strictly after the last seen row in sort order.
- `limit + 1` avoids running a separate count query.
- Composite indexes match the filter and order patterns.
- Offset pagination becomes both slower and less correct as data grows.

## Future Improvements

- Add Alembic migrations instead of optional `create_all`.
- Add write endpoints with optimistic locking.
- Add request IDs and structured JSON logs.
- Add read replicas for high traffic browsing.
- Add cache headers or CDN caching for category landing pages.
- Define stricter snapshot semantics if rows are frequently updated while a user is paging. A stateless cursor cannot perfectly reproduce a historical snapshot if the ordering column itself changes between requests.

## AI Usage Disclosure

This solution was generated with AI assistance and reviewed for architecture, correctness, and interview explainability. The implementation favors straightforward Python, explicit SQLAlchemy queries, and documented tradeoffs so a developer can understand and defend each decision.

