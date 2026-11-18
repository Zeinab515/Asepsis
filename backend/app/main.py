from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api import agent, analytics, auth, imports, ml, reports
from app.db.session import init_db_and_views


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite/PostgreSQL schema and views on startup
    try:
        init_db_and_views()
    except Exception as e:
        print(f"Warning initializing DB views: {e}")
    yield


app = FastAPI(
    title="Asepsis API — Clinical Analytics & Decision Support",
    description="Deterministic REST API platform for hospital hand hygiene compliance analytics and statistical audit decision support.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for API clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Pure REST API Routers
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(imports.router)
app.include_router(ml.router)
app.include_router(reports.router)
app.include_router(agent.router)


@app.get("/", include_in_schema=False)
def root():
    """Root redirects directly to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
def health():
    """Liveness probe for deployment and monitoring."""
    return {"status": "ok"}
