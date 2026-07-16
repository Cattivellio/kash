from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import clear_session_cookie, current_user, set_session_cookie
from .config import (
    KASH_HOST,
    KASH_PORT,
    PAYMENT_METHODS,
    RECORD_KINDS,
    STATIC_DIR,
    SUPPORTED_LOCALES,
    TEMPLATES_DIR,
    TZ,
)
from .database import (
    create_user,
    delete_record,
    get_month_summary,
    get_recent_records,
    get_record_by_id,
    init_db,
    insert_record,
    is_healthy,
    list_records,
    now_iso,
    update_record,
    update_user_prefs,
)
from .i18n import STRINGS, t


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
)
logger = logging.getLogger("kash")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("db ready")
    yield


app = FastAPI(
    title="Kash",
    description="Personal finance tracker",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Helpers ────────────────────────────────────────────────────────────────────


def _ctx(request: Request, user: dict | None = None, **extra):
    locale = user["locale"] if user else "es"
    base = {
        "request": request,
        "locale": locale,
        "t": lambda key, **kw: t(locale, key, **kw),
        "strings": STRINGS.get(locale, STRINGS["es"]),
        "user": user,
        "theme": user["theme"] if user else "light",
    }
    base.update(extra)
    return base


def _today_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")[:16]


def _month_range():
    now = datetime.now()
    return now.year, now.month


# ── Auth middleware (lightweight) ───────────────────────────────────────────────


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


def _require_user(request: Request):
    """Synchronous helper for templates. Returns user dict or None."""
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    from .auth import unsign_user_id
    uid = unsign_user_id(session_cookie)
    if uid is None:
        return None
    from .database import get_user_by_id
    return get_user_by_id(uid)


# ── Pages ──────────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    user = _require_user(request)
    if user is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "onboarding.html",
        _ctx(request, strings=STRINGS["es"]),
    )


@app.post("/onboarding", response_class=HTMLResponse)
async def onboarding_post(
    request: Request,
    name: str = Form(...),
    locale: str = Form("es"),
):
    if locale not in SUPPORTED_LOCALES:
        locale = "es"
    user = create_user(name.strip(), locale)
    resp = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(resp, user["id"])
    return resp


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    year, month = _month_range()
    summary = get_month_summary(user["id"], year, month)
    recent = get_recent_records(user["id"], limit=5)
    return templates.TemplateResponse(
        "dashboard.html",
        _ctx(
            request,
            user,
            summary=summary,
            recent=recent,
            year=year,
            month=month,
            active="dashboard",
        ),
    )


@app.get("/income", response_class=HTMLResponse)
async def income_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    records = list_records(user["id"], kind="income", limit=100)
    return templates.TemplateResponse(
        "income.html",
        _ctx(
            request,
            user,
            records=records,
            active="income",
        ),
    )


@app.post("/income", response_class=HTMLResponse)
async def income_post(
    request: Request,
    name: str = Form(...),
    amount: float = Form(...),
    occurred_at: str = Form(...),
    payment_method: str = Form(...),
    note: str = Form(""),
):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    if payment_method not in PAYMENT_METHODS:
        payment_method = "cash"
    insert_record(
        user["id"],
        kind="income",
        name=name,
        occurred_at=occurred_at,
        amount=amount,
        payment_method=payment_method,
        note=note,
    )
    return RedirectResponse(url="/income", status_code=303)


@app.get("/expenses", response_class=HTMLResponse)
async def expenses_page(request: Request):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    records = list_records(user["id"], kind="expense", limit=100)
    return templates.TemplateResponse(
        "expenses.html",
        _ctx(
            request,
            user,
            records=records,
            active="expenses",
        ),
    )


@app.post("/expenses", response_class=HTMLResponse)
async def expenses_post(
    request: Request,
    name: str = Form(...),
    amount: float = Form(...),
    occurred_at: str = Form(...),
    payment_method: str = Form(...),
    note: str = Form(""),
):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    if payment_method not in PAYMENT_METHODS:
        payment_method = "cash"
    insert_record(
        user["id"],
        kind="expense",
        name=name,
        occurred_at=occurred_at,
        amount=amount,
        payment_method=payment_method,
        note=note,
    )
    return RedirectResponse(url="/expenses", status_code=303)


@app.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    kind: str = Query("all"),
    from_date: str = Query(""),
    to_date: str = Query(""),
    method: str = Query("all"),
):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    k = kind if kind in RECORD_KINDS else None
    m = method if method in PAYMENT_METHODS else None
    fd = from_date or None
    td = to_date or None
    records = list_records(user["id"], kind=k, from_date=fd, to_date=td, limit=500)
    if m:
        records = [r for r in records if r["payment_method"] == m]
    return templates.TemplateResponse(
        "history.html",
        _ctx(
            request,
            user,
            records=records,
            active="history",
            filter_kind=kind,
            filter_from=from_date,
            filter_to=to_date,
            filter_method=method,
        ),
    )


@app.post("/records/{record_id}/delete")
async def record_delete(request: Request, record_id: int):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    delete_record(record_id, user["id"])
    referer = request.headers.get("referer", "/dashboard")
    return RedirectResponse(url=referer, status_code=303)


@app.post("/records/{record_id}/edit")
async def record_edit(
    request: Request,
    record_id: int,
    kind: str = Form(...),
    name: str = Form(...),
    amount: float = Form(...),
    occurred_at: str = Form(...),
    payment_method: str = Form(...),
    note: str = Form(""),
):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    update_record(
        record_id,
        user["id"],
        kind=kind,
        name=name,
        amount=amount,
        occurred_at=occurred_at,
        payment_method=payment_method,
        note=note,
    )
    referer = request.headers.get("referer", "/dashboard")
    return RedirectResponse(url=referer, status_code=303)


@app.post("/preferences")
async def preferences_post(
    request: Request,
    locale: str = Form("es"),
    theme: str = Form("light"),
):
    user = _require_user(request)
    if user is None:
        return RedirectResponse(url="/onboarding", status_code=303)
    if locale not in SUPPORTED_LOCALES:
        locale = "es"
    if theme not in ("light", "dark"):
        theme = "light"
    update_user_prefs(user["id"], locale=locale, theme=theme)
    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer, status_code=303)


@app.get("/signout")
async def signout(request: Request):
    resp = RedirectResponse(url="/onboarding", status_code=303)
    clear_session_cookie(resp)
    return resp


# ── JSON API ───────────────────────────────────────────────────────────────────


@app.get("/api/records")
async def api_records(
    request: Request,
    kind: str = Query("all"),
    limit: int = Query(200, ge=1, le=2000),
):
    user = _require_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="not authenticated")
    k = kind if kind in RECORD_KINDS else None
    records = list_records(user["id"], kind=k, limit=limit)
    return {"records": records}


@app.get("/api/summary")
async def api_summary(request: Request, year: int = Query(...), month: int = Query(...)):
    user = _require_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="not authenticated")
    summary = get_month_summary(user["id"], year, month)
    return summary


@app.get("/api/health", response_model=dict)
async def api_health():
    return {"ok": True, "db": is_healthy(), "now": datetime.now().astimezone()}


@app.exception_handler(404)
async def _not_found(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "not found"})
    return RedirectResponse(url="/", status_code=303)
