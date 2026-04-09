"""Create temp_api_db/ (SQLite + dashboard JSON) and apply in-memory demo seeds.

Delete the entire ``temp_api_db`` directory while the server is stopped to wipe file-backed
state; restart the app to recreate it. See temp_api_db/RESET.txt.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def install_temp_api_db_layout() -> None:
    """Ensure temp folder, RESET instructions, dashboard.json copy, and seeded task SQLite."""
    root = _repo_root()
    tmp = root / "temp_api_db"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "RESET.txt").write_text(
        "temp_api_db — temporary demo storage\n"
        "====================================\n"
        "1) Stop uvicorn (Ctrl+C).\n"
        "2) Delete this entire folder (temp_api_db).\n"
        "3) Start uvicorn again — files and DB are recreated.\n\n"
        "What lives here:\n"
        "  dashboard.json              — GET /api/contributor/me, /dashboard, /notifications\n"
        "  contributor_tasks.sqlite    — GET /api/contributor/tasks, workroom, timeline, …\n\n"
        "Also re-seeded on every process start (in RAM):\n"
        "  credentials, earnings, payouts prefs, profile, submissions, messages, learning, support, settings extras.\n",
        encoding="utf-8",
    )
    dash_dst = tmp / "dashboard.json"
    if not dash_dst.is_file():
        src = root / "data" / "DELETE_ME_TEMP_DASHBOARD_API_DATA.json"
        if src.is_file():
            shutil.copyfile(src, dash_dst)
    from app.db.persistence import get_db_path
    from app.db.seed import ensure_seeded_database

    ensure_seeded_database(get_db_path())


def apply_all_temp_demo_seeds() -> None:
    """Populate in-memory stores (idempotent). Reset task service so it reloads SQLite."""
    from app.services import (
        credentials_store,
        dashboard_store,
        earnings_data,
        learning_store,
        messages_store,
        profile_store,
        submission_store,
        support_store,
    )
    from app.services.contributor_tasks import reset_task_service_singleton
    from app.schemas.settings import AccountSummary, NotificationPreferences
    from app.settings_state import state

    credentials_store.apply_temp_demo_seed()
    earnings_data.apply_temp_demo_seed()
    learning_store.apply_temp_demo_seed()
    submission_store.apply_temp_demo_seed()
    profile_store.apply_temp_demo_seed()
    messages_store.store.apply_temp_demo_seed()
    support_store.apply_temp_demo_seed()
    state.account_summary = AccountSummary(
        display_name="Demo Settings User",
        email="demo.settings@example.com",
        phone="+1-555-0199",
    )
    state.notification_preferences = NotificationPreferences(
        task_assignments=True,
        review_decisions=True,
        sla_reminders=False,
        payout_updates=True,
        learning=True,
    )
    state.language = "en"
    state.timezone = "Europe/London"
    state.quiet_hours_start = "22:00"
    state.quiet_hours_end = "07:00"
    dashboard_store.apply_e2e_dashboard_alignment()
    reset_task_service_singleton()
