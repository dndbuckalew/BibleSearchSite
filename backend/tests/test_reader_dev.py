"""Offline application-path tests for edition binding and staged delivery."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
import os
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


# Hosted comparison fixture from Bible Hub's BSB edition.
BSB = "For God so loved the world that He gave His one and only Son, that everyone who believes in Him shall not perish but have eternal life."


def accept(question="John 3:16", **options):
    return handle_query(QueryRequest(question=question, **options)).execution_payload


def bsb_response(edition):
    response = MagicMock(status_code=200)
    response.json.return_value = {
        **({"translation_id": edition} if edition is not None else {}),
        "verses": [{"book_name": "John", "chapter": 3, "verse": 16, "text": BSB}],
    }
    return response


class ReaderContractTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {"BTA_ENABLE_BSB_TEST": "1"}))
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
        if not (os.getenv("BTA_SCRIPTURE_SQLITE_PATH") or os.getenv("BTA_DEV_KJV_OSIS")):
            self.skipTest("Configure a verified local Scripture source")
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

    @unittest.skipUnless(os.getenv("BTA_SCRIPTURE_SQLITE_PATH"), "Verified SQLite bundle required")
    def test_sqlite_editions_and_bound_exploration(self):
        from backend.services.scripture_selection import BES as BES_SELECTION

        with closing(scripture_retrieval.sqlite_connection()) as connection:
            with self.assertRaisesRegex(scripture_retrieval.sqlite3.OperationalError, "readonly"):
                connection.execute("CREATE TABLE write_probe (id INTEGER)")

        with patch.object(scripture_retrieval.requests, "get", side_effect=AssertionError) as remote:
            for option, source, wording, reference in (
                ("local-kjv", "Local KJV dataset", KJV, "John 3:16"),
                ("local-bes", "Local BES dataset", BES, "Juan 3:16"),
            ):
                accepted = accept(scripture_option=option)
                for execution in (accepted, accept(reference, parent_execution=accepted), accepted):
                    result = get_results(ResultsRequest(execution_payload=execution))
                    self.assertEqual(len(result.verses), 1)
                    verse = result.verses[0]
                    self.assertEqual((verse.reference, " ".join(verse.text.split())), (reference, wording))
                    self.assertEqual(result.scripture_provenance["source_label"], source)
                    self.assertEqual(result.scripture_provenance["dataset_revision"],
                                     accepted["resolved_scripture"]["dataset_revision"])
            for reference, count in (("Génesis 1:31-2:2", 3), ("1 Juan 4:7-8", 2), ("Salmos 23:1-3", 3)):
                result = get_results(ResultsRequest(execution_payload=accept(reference, scripture_option="local-bes")))
                self.assertEqual(len(result.verses), count)
            missing = list(stream_results(verify(accept("Juan 3:999", scripture_option="local-bes"))))
            self.assertEqual(json.loads(missing[0])["code"], "missing_passage")
            with self.assertRaisesRegex(scripture_retrieval.ScriptureError, "source_unavailable"):
                scripture_retrieval.retrieve("John 3:16", {**BES_SELECTION, "dataset_revision": "missing"})
            with patch.dict(os.environ, {"BTA_SCRIPTURE_SQLITE_SHA256": "0" * 64}):
                unavailable = list(stream_results(verify(accept(scripture_option="local-bes"))))
                self.assertEqual(json.loads(unavailable[0])["code"], "source_unavailable")
            with patch.object(query_service, "resolve_scripture_with_llm", return_value=["Isaiah 41:10", "Psalm 23:4"]):
                for option, edition in (("local-kjv", "kjv"), ("local-bes", "bes")):
                    payload = accept("What does God say about fear?", scripture_option=option)
                    result = get_results(ResultsRequest(execution_payload=payload))
                    self.assertEqual(result.scripture_provenance["edition_id"], edition)
                    self.assertEqual([(v.chapter, v.verse) for v in result.verses], [(23, 4), (41, 10)])
        remote.assert_not_called()

    def test_external_verification_and_retained_selection(self):
        with patch.object(scripture_retrieval.requests, "get", return_value=bsb_response("bsb")) as remote:
            accepted = accept(scripture_option="test-bsb")
            for followup in (accepted, accept("John 3:16", parent_execution=accepted)):
                result = get_results(ResultsRequest(execution_payload=followup))
                self.assertEqual(result.verses[0].text, BSB)
                self.assertEqual(result.verses[0].reference, "John 3:16")
                self.assertEqual(result.scripture_provenance["source_label"], "Bible-API.com")
                self.assertIsNone(result.scripture_provenance["dataset_revision"])
            self.assertEqual(remote.call_count, 2)
            self.assertTrue(all(call.kwargs["params"] == {"translation": "bsb"} for call in remote.call_args_list))
        for edition in (None, "kjv"):
            with patch.object(scripture_retrieval.requests, "get", return_value=bsb_response(edition)):
                events = list(stream_results(verify(accepted)))
                self.assertEqual(len(events), 1)
                self.assertEqual(json.loads(events[0])["code"], "edition_unverified")

    def test_altered_and_unauthorized_selection(self):
        accepted = accept()
        accepted["resolved_scripture"] = accept(scripture_option="test-bsb")["resolved_scripture"]
        with self.assertRaises(HTTPException):
            verify(accepted)
        with patch.dict(os.environ, {"BTA_ENABLE_BSB_TEST": "0"}), self.assertRaises(HTTPException):
            accept(scripture_option="test-bsb")

    def test_missing_snapshot(self):
        with patch.dict(os.environ, {"BTA_DEV_KJV_OSIS": "", "BTA_SCRIPTURE_SQLITE_PATH": ""}):
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
            patch.object(scripture_retrieval.requests, "get", return_value=bsb_response("bsb")),
            patch("backend.services.ai_reflection_service.generate_ai_reflection", side_effect=reflection),
            ThreadPoolExecutor(max_workers=1) as pool,
        ):
            stream = stream_results(verify(accept(scripture_option="test-bsb")))
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
