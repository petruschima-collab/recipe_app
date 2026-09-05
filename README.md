# Recipe API

A RESTful Recipe API built with **FastAPI, PostgreSQL, and asynchronous SQLAlchemy 2.0**.

## Features

* Recipe creation and management
* Category support
* Pydantic request and response validation
* Async database operations
* PostgreSQL database integration
* RESTful CRUD endpoints
* Interactive Swagger documentation

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy 2.0
* AsyncSession
* asyncpg
* Pydantic
* Uvicorn

## Architecture

```text
Client
  ↓
FastAPI
  ↓
Routers
  ↓
Services
  ↓
Repositories
  ↓
Async SQLAlchemy
  ↓
PostgreSQL
```

## Run the Project

```powershell
python -m uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Current Status

**Stage 1 — Basic Recipe CRUD completed.**
