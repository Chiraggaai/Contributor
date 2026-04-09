from __future__ import annotations

from app.demo_bootstrap import apply_all_temp_demo_seeds, install_temp_api_db_layout

install_temp_api_db_layout()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    credentials,
    dashboard,
    earnings,
    learning,
    messages,
    payouts,
    preferences,
    profile,
    settings,
    submissions,
    support,
    tasks,
)

apply_all_temp_demo_seeds()

app = FastAPI(
    title="Glimmora Contributor API",
    version="1.0.0",
    description="Unified contributor APIs: profile, dashboard, tasks, submissions, earnings, credentials, settings, messages, learning, and support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(credentials.router)
app.include_router(credentials.public_router)
app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(tasks.router)
app.include_router(submissions.router)
app.include_router(earnings.router)
app.include_router(payouts.router)
app.include_router(preferences.router)
app.include_router(settings.router)
app.include_router(messages.router)
app.include_router(learning.router)
app.include_router(support.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
