import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.query_models import ResultsRequest, QueryResponse
from backend.services.query_service import QueryService
from backend.services.scripture_selection import verify

router = APIRouter()
query_service = QueryService()


@router.post("/api/results", response_model=QueryResponse)
def get_results(req: ResultsRequest):
    payload = verify(req.execution_payload)
    return query_service.process_query(payload, payload["resolved_scripture"])


def encode(event, **data):
    return json.dumps({"event": event, **data}, ensure_ascii=False) + "\n"


def stream_results(payload):
    stages = query_service.result_stages(payload, payload["resolved_scripture"])
    current = "scripture"
    sections = ("scripture", "summary", "context", "reflection")
    incomplete = []
    try:
        while True:
            section, data = next(stages)
            issue = bool(data.get("scripture_issues")) or not data.get(section if section != "scripture" else "verses")
            if issue:
                incomplete.append(section)
            yield encode("section", section=section, data=data, success=not issue)
            index = sections.index(section) + 1
            current = sections[index] if index < len(sections) else section
    except StopIteration as finished:
        response = finished.value
        yield encode("complete", success=not incomplete and response.escalation_level is None,
                     escalation=response.summary if response.escalation_level else None)
    except HTTPException as error:
        code = error.detail.get("code") if isinstance(error.detail, dict) else "request_failed"
        yield encode("failure", section=current, code=code)
    except Exception:
        yield encode("failure", section=current, code="section_failed")
    finally:
        stages.close()


@router.post("/api/results/stream")
def get_stream(req: ResultsRequest):
    payload = verify(req.execution_payload)
    return StreamingResponse(stream_results(payload), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
