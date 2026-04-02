from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from app.core.database import Base, engine
from app.routers import auth, users, records, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="""
A role-based finance dashboard backend.

## Roles
| Role     | Permissions                                      |
|----------|--------------------------------------------------|
| viewer   | View records, view summary & recent activity     |
| analyst  | All viewer rights + category breakdown & trends  |
| admin    | Full access including create/update/delete/users |

## Auth
All protected routes require: `Authorization: Bearer <token>`
Get a token via `/auth/login`.
    """,
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "details": errors}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail, "details": None}
        )
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "details": None}
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Finance Dashboard API is running", "docs": "/docs"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi