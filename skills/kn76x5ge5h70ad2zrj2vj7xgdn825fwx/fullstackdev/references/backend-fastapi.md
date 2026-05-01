# Backend (FastAPI/Starlette/Uvicorn)

- Keep routers thin; business logic belongs in service layer.
- Use dependency injection for auth, db session, and settings.
- Validate request/response models strictly.
- Return stable error shapes; avoid leaking internals.
- Add structured logging around critical paths.
