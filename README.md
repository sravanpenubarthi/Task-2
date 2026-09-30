# Product Management API

A CRUD REST API for managing products, built with **FastAPI**, **SQLAlchemy 2.0** and **Pydantic v2**, storing data in **SQLite** (zero setup).

## Project structure

```
product_api/
├── app/
│   ├── main.py              # app, lifespan, global error handlers
│   ├── config.py            # env-based configuration (DATABASE_URL)
│   ├── database.py          # engine, session, get_db dependency
│   ├── models.py            # SQLAlchemy model (Product)
│   ├── schemas.py           # Pydantic request/response schemas + validation rules
│   ├── crud.py              # database operations (no HTTP concerns)
│   ├── exceptions.py        # domain errors -> HTTP status mapping
│   └── routers/products.py  # route definitions
├── tests/test_products.py   # pytest tests (in-memory SQLite)
├── schema.sql               # database schema (reference)
├── postman_collection.json  # importable Postman collection with test scripts
└── requirements.txt
```

Layering: **router -> crud -> model**. Routers handle HTTP, `crud` handles data, `schemas` handle validation.

## Setup & run

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- The `products` table and `products.db` file are created automatically on startup.
- To use a different database file: `export DATABASE_URL="sqlite:///./other.db"`

## Run tests

```bash
pytest -q
```

Tests use an in-memory database, so your real `products.db` is never touched.

## Test with Postman

1. Start the server.
2. Import `postman_collection.json` (the `base_url` variable defaults to `http://127.0.0.1:8000`).
3. Run the collection with the Collection Runner. Each request has test scripts and the run starts and ends with an empty database.

## Database schema

Table `products` (see `schema.sql`):

| Column       | Type         | Constraints                     |
|--------------|--------------|---------------------------------|
| product_id   | INTEGER      | PRIMARY KEY (unique, client-supplied) |
| product_name | VARCHAR(100) | NOT NULL                        |
| category     | VARCHAR(100) | NOT NULL, indexed               |
| price        | FLOAT        | NOT NULL, CHECK (price > 0)     |
| quantity     | INTEGER      | NOT NULL, CHECK (quantity > 0)  |

## API reference

| Method | Path                     | Description                                         | Success | Errors   |
|--------|--------------------------|-----------------------------------------------------|---------|----------|
| POST   | `/products`              | Create a product                                    | 201     | 409, 422 |
| GET    | `/products`              | List products (`category`, `skip`, `limit`)         | 200     | 422      |
| GET    | `/products/{product_id}` | Get a product by ID                                 | 200     | 404, 422 |
| PUT    | `/products/{product_id}` | Update a product (all fields required)              | 200     | 404, 422 |
| DELETE | `/products/{product_id}` | Delete a product                                    | 200     | 404, 422 |
| GET    | `/health`                | Liveness check                                      | 200     |          |

Search by category (bonus): `GET /products?category=Electronics` (case-insensitive).

## Validation rules

- `product_id` must be unique and greater than 0
- `price` and `quantity` must be greater than 0
- `product_name` and `category` must be non-empty (whitespace is trimmed, max 100 chars)

## Error format

All errors use one consistent shape:

```json
{ "error": { "code": "product_not_found", "message": "Product with ID 99 not found." } }
```

| Status | Code                   | When                                  |
|--------|------------------------|---------------------------------------|
| 404    | `product_not_found`    | Product ID does not exist             |
| 409    | `duplicate_product_id` | POST with an ID that already exists   |
| 422    | `validation_error`     | Invalid input; includes a `details` list with the field and message |
| 500    | `internal_error`       | Unexpected server error               |

## Example requests (curl)

```bash
# Create
curl -X POST http://127.0.0.1:8000/products -H "Content-Type: application/json" \
  -d '{"product_id": 1, "product_name": "Laptop", "category": "Electronics", "price": 55000, "quantity": 10}'

# List all / filter by category
curl http://127.0.0.1:8000/products
curl "http://127.0.0.1:8000/products?category=Electronics"

# Get one
curl http://127.0.0.1:8000/products/1

# Update (product_id comes from the URL)
curl -X PUT http://127.0.0.1:8000/products/1 -H "Content-Type: application/json" \
  -d '{"product_name": "Gaming Laptop", "category": "Electronics", "price": 80000, "quantity": 5}'

# Delete
curl -X DELETE http://127.0.0.1:8000/products/1
```

## Concepts covered

FastAPI, CRUD, Pydantic validation, SQLite + SQLAlchemy, path & query parameters, exception handling, dependency injection, automated testing.
