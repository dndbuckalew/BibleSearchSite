"""Offline application-path tests for edition binding and staged delivery."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
from threading import Event
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("OPENAI_API_KEY", "offline-test")

from fastapi import HTTPException
from backend.api.query import handle_query
from backend.api.results import get_results, stream_results
from backend.models.query_models import QueryRequest, ResultsRequest
from backend.services import query_service, scripture_retrieval
from backend.services.scripture_selection import verify

KJV = "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."
# Offline John 3:16 sample from eBible.org (spabes).
BES = "Porque de tal manera amó Dios al mundo, que dio a su Hijo único, para que todo el que cree en él no se pierda, sino que tenga vida eterna."


def accept(question="John 3:16", **options):
    return handle_query(QueryRequest(question=question, **options)).execution_payload


def bes_response(edition):
    response = MagicMock(status_code=200)
    response.json.return_value = {
        **({"translation_id": edition} if edition is not None else {}),
        "verses": [{"book_name": "Juan", "chapter": 3, "verse": 16, "text": BES}],
    }
    return response


class ReaderContractTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {"BTA_ENABLE_BES_TEST": "1"}))
        for name, result in {
            "classify_reaffirmation_intent": None,
            "build_commentary": None,
            "generate_ai_summary": "",
            "generate_free_context": "Context fixture.",
            "generate_context_exploration": "",
        }.items():
            self.enterContext(patch.object(query_service, name, return_value=result))
        self.enterContext(patch.object(query_service.QueryService, "_build_theme_interaction_result",
                                      return_value=MagicMock(central_conclusion="Summary fixture.", supporting_movements=[])))
        self.enterContext(patch("backend.services.ai_reflection_service.generate_ai_reflection",
                                return_value="Reflection fixture."))

    def test_real_local_default_explicit_and_missing(self):
        if not os.getenv("BTA_DEV_KJV_OSIS"):
            self.skipTest("Set BTA_DEV_KJV_OSIS to run the pinned KJV integration test")
        with patch.object(scripture_retrieval.requests, "get", side_effect=AssertionError) as remote:
            for options in ({}, {"translation": "KJV"}, {"scripture_option": "local-kjv"}):
                request = ResultsRequest(execution_payload=accept(**options))
                result = get_results(request)
                self.assertEqual(" ".join(result.verses[0].text.split()), KJV)
                self.assertEqual(result.scripture_provenance["source_label"], "Local KJV dataset")
                self.assertTrue(result.scripture_provenance["dataset_revision"])
            events = list(stream_results(verify(accept("John 3:999"))))
            self.assertEqual(json.loads(events[-1])["code"], "missing_passage")
        remote.assert_not_called()

    def test_external_verification_and_retained_selection(self):
        with patch.object(scripture_retrieval.requests, "get", return_value=bes_response("bes")) as remote:
            accepted = accept(scripture_option="test-bes")
            for followup in (accepted, accept("Juan 3:16", parent_execution=accepted)):
                result = get_results(ResultsRequest(execution_payload=followup))
                self.assertEqual(result.verses[0].text, BES)
                self.assertEqual(result.verses[0].reference, "Juan 3:16")
                self.assertEqual(result.scripture_provenance["source_label"], "Bible-API.com")
                self.assertIsNone(result.scripture_provenance["dataset_revision"])
            self.assertEqual(remote.call_count, 2)
            self.assertTrue(all(call.kwargs["params"] == {"translation": "bes"} for call in remote.call_args_list))
        for edition in (None, "kjv"):
            with patch.object(scripture_retrieval.requests, "get", return_value=bes_response(edition)):
                events = list(stream_results(verify(accepted)))
                self.assertEqual(len(events), 1)
                self.assertEqual(json.loads(events[0])["code"], "edition_unverified")

    def test_altered_and_unauthorized_selection(self):
        accepted = accept()
        accepted["resolved_scripture"] = accept(scripture_option="test-bes")["resolved_scripture"]
        with self.assertRaises(HTTPException):
            verify(accepted)
        with patch.dict(os.environ, {"BTA_ENABLE_BES_TEST": "0"}), self.assertRaises(HTTPException):
            accept(scripture_option="test-bes")

    def test_missing_snapshot(self):
        with patch.dict(os.environ, {"BTA_DEV_KJV_OSIS": ""}):
            events = list(stream_results(verify(accept())))
        self.assertEqual(json.loads(events[0])["code"], "source_unavailable")

    def test_upstream_hold_and_partial_failure(self):
        entered, release = Event(), Event()

        def reflection(_):
            entered.set()
            if not release.wait(4):
                raise TimeoutError("Test did not release Reflection")
            raise RuntimeError("Controlled failure")

        with (
            patch.object(scripture_retrieval.requests, "get", return_value=bes_response("bes")),
            patch("backend.services.ai_reflection_service.generate_ai_reflection", side_effect=reflection),
            ThreadPoolExecutor(max_workers=1) as pool,
        ):
            stream = stream_results(verify(accept(scripture_option="test-bes")))
            try:
                for section in ("scripture", "summary", "context"):
                    row = json.loads(next(stream))
                    self.assertEqual((row["section"], row["success"]), (section, True))
                pending = pool.submit(next, stream)
                self.assertTrue(entered.wait(2))
                self.assertFalse(pending.done())
            finally:
                release.set()
            self.assertEqual(json.loads(pending.result(timeout=3)),
                             {"event": "failure", "section": "reflection", "code": "section_failed"})


if __name__ == "__main__":
    unittest.main()
