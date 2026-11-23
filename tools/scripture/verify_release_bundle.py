"""Verify the pinned deployable SQLite catalog and smoke-test local retrieval."""
from contextlib import closing
from hashlib import file_digest
import json
import os
from pathlib import Path
import sqlite3

CATALOG = Path(__file__).with_name("release-catalog.json")


def verify_bundle(path, checksum):
    expected = json.loads(CATALOG.read_text(encoding="utf-8"))
    with path.open("rb") as bundle:
        if file_digest(bundle, "sha256").hexdigest() != checksum:
            raise ValueError("Scripture bundle SHA-256 mismatch")
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("Scripture bundle failed SQLite integrity_check")
        snapshots = db.execute("SELECT edition, revision FROM snapshot").fetchall()
        if sorted(snapshots) != sorted(expected.items()):
            raise ValueError("Scripture snapshot editions or revisions differ from the approved catalog")
    return expected


def verify_retrieval(expected):
    from backend.api.query import handle_query, scripture_options
    from backend.api.results import stream_results
    from backend.models.query_models import QueryRequest
    from backend.services.scripture_selection import verify

    catalog = scripture_options()
    editions = sorted(
        (option["edition_id"], option["dataset_revision"])
        for option in catalog["options"]
        if option["source_id"] == "local"
    )
    if catalog["default"] != "local-kjv" or editions != sorted(expected.items()):
        raise ValueError("Served Scripture catalog or its default differs from the approved catalog")

    reference = "John 3:16"
    decision = handle_query(QueryRequest(question=reference))
    with closing(stream_results(verify(decision.execution_payload))) as results:
        first = json.loads(next(results))
    if first.get("section") != "scripture" or not first.get("success"):
        raise ValueError("Default KJV Scripture lookup failed")
    data = first["data"]
    verses = data["verses"]
    provenance = data["scripture_provenance"]
    if (len(verses) != 1 or verses[0]["reference"] != reference
            or "only begotten Son" not in verses[0]["text"]
            or (provenance["source_id"], provenance["edition_id"], provenance["dataset_revision"])
            != ("local", "kjv", expected["kjv"])):
        raise ValueError("Unexpected verse or provenance from the local KJV lookup")
    print(json.dumps({"editions": len(editions), "default": catalog["default"],
                      "reference": reference, "provenance": provenance}))


if __name__ == "__main__":
    path = Path(os.environ["BTA_SCRIPTURE_SQLITE_PATH"])
    verify_retrieval(verify_bundle(path, os.environ["BTA_SCRIPTURE_SQLITE_SHA256"]))
