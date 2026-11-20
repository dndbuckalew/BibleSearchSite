"""Loopback-only browser fixture server for the V6.5.3 dev acceptance run."""
from contextlib import asynccontextmanager
from threading import Event
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.tests.test_reader_dev import ReaderContractTests, bsb_response
from backend.api import query, results
from backend.services import ai_reflection_service, scripture_retrieval

release = Event()
waiting = Event()
fail = Event()
outage = Event()
read_local = scripture_retrieval.local_verses
provider_calls = []


def reflection(_):
    waiting.set()
    if not release.wait(15):
        raise TimeoutError("Fixture Reflection was not released")
    if fail.is_set():
        raise RuntimeError("Fixture Reflection failure")
    return "Reflection fixture."


def scripture_get(_url, **kwargs):
    if kwargs.get("params") != {"translation": "bsb"}:
        raise AssertionError("Unexpected hosted Scripture request")
    provider_calls.append("bsb")
    return bsb_response("bsb")


def local_verses(reference, selection):
    if outage.is_set():
        raise scripture_retrieval.ScriptureError("source_unavailable")
    return read_local(reference, selection)


@asynccontextmanager
async def lifespan(_app):
    suite = ReaderContractTests()
    suite.setUp()
    try:
        with (
            patch.object(ai_reflection_service, "generate_ai_reflection", side_effect=reflection),
            patch.object(scripture_retrieval.requests, "get", side_effect=scripture_get),
            patch.object(scripture_retrieval, "local_verses", side_effect=local_verses),
        ):
            yield
    finally:
        suite.doCleanups()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:43271"],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(query.router)
app.include_router(results.router)


@app.post("/fixture/reset")
def reset():
    release.clear()
    waiting.clear()
    fail.clear()
    outage.clear()
    provider_calls.clear()


@app.post("/fixture/release")
def unblock(failure: bool = False):
    if failure:
        fail.set()
    release.set()


@app.post("/fixture/outage")
def set_outage(active: bool):
    if active:
        outage.set()
    else:
        outage.clear()


@app.get("/fixture/status")
def status():
    return {"reflection_waiting": waiting.is_set(), "provider_fixture_calls": len(provider_calls)}
