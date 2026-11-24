"""Offline cleanup regressions. Providers and transport are blocked or mocked."""
import ast
from contextlib import ExitStack, redirect_stdout
import io
import logging
import os
from pathlib import Path
import subprocess
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "72ac927f7672eda93c53a238eb80cc20ddc39c85"
ACCEPTED_CLEANUP = "c07929136719fd2686fb27c881ed8e211fa464ea"
CANARY = "OFFLINE_PRIVATE_CANARY"

# Imports create clients but cannot send requests; never read a real credential.
with patch.dict(os.environ, {"OPENAI_API_KEY": "offline-fixture"}), redirect_stdout(io.StringIO()):
    from backend.services import query_service as current
    from backend.core.vocabulary import nql_scripture_vocabulary as vocabulary
    from backend.services import ai_client, ai_reflection_service


def baseline_source(path, revision=BASELINE):
    return subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT).decode("utf-8")


def baseline_conductor():
    module = types.ModuleType("baseline_query_service")
    module.__file__ = str(ROOT / "backend/services/query_service.py")
    with redirect_stdout(io.StringIO()):
        exec(compile(baseline_source("backend/services/query_service.py"), module.__file__, "exec"), module.__dict__)
    return module


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch("socket.socket.connect", side_effect=AssertionError("Network forbidden")))
        self.stack.enter_context(patch.object(ai_client.client.chat.completions, "create", side_effect=AssertionError("Provider forbidden")))
        self.stack.enter_context(patch.object(current, "classify_reaffirmation_intent", return_value=None))
        self.output = self.stack.enter_context(redirect_stdout(io.StringIO()))

    def execute(self, module, *, summary_failure=False, fallback=False):
        calls = []
        verse = module.VerseItem(reference="John 3:16", text="Offline Scripture fixture.", testament="NT", book_order=43)
        service = module.QueryService()

        def record(name, result=None):
            def run(*args, **kwargs):
                calls.append(name)
                return result
            return run

        def theme(**kwargs):
            calls.append("meaning")
            if summary_failure:
                raise ValueError("offline summary failure")
            return types.SimpleNamespace(central_conclusion="Offline summary.", supporting_movements=["Offline movement."])

        def exploration(*, verses, supporting_movements):
            calls.append("exploration")
            self.assertEqual(verses, [verse])
            self.assertEqual(supporting_movements, [] if summary_failure else ["Offline movement."])
            return "Offline exploration."

        with ExitStack() as stack:
            for name, replacement in {
                "resolve_scripture_with_llm": record("selector", [] if fallback else ["John 3:16"]),
                "resolve_nql_topics": record("fallback", ["John 3:16"]),
                "classify_reaffirmation_intent": record("classifier", {"intent": "GENERAL_EXPLORATION"}),
                "generate_intent_reaffirmation": record("opening", "Offline opening."),
                "build_commentary": record("commentary", None),
                "generate_ai_summary": record("legacy_summary", None),
                "generate_free_context": record("context", "Offline context."),
                "generate_context_exploration": exploration,
            }.items():
                stack.enter_context(patch.object(module, name, replacement))
            stack.enter_context(patch.object(service, "fetch_scripture_items", side_effect=record("scripture", [verse])))
            stack.enter_context(patch.object(service, "_format_commentary_result_as_string", return_value="Offline commentary."))
            stack.enter_context(patch.object(service, "_build_theme_interaction_result", side_effect=theme))
            stack.enter_context(patch.object(ai_reflection_service, "generate_ai_reflection", side_effect=record("reflection", "Offline reflection.")))
            result = service.process_query({"question": "An ordinary offline question", "translation": "kjv", "want_commentary": True})
        return result, calls

    def test_reproduces_baseline_unbound_expansion_and_preserves_viable_processing(self):
        with self.assertRaises(UnboundLocalError):
            self.execute(baseline_conductor(), summary_failure=True)
        result, calls = self.execute(current, summary_failure=True)
        self.assertEqual(len(result.verses), 1)
        self.assertEqual(result.summary, "")
        self.assertEqual(result.context, "Offline context.")
        self.assertEqual(result.context_exploration, "Offline exploration.")
        self.assertEqual(result.reflection, "")
        self.assertEqual(calls, ["selector", "scripture", "classifier", "opening", "commentary", "legacy_summary", "meaning", "context", "exploration"])

    def test_successful_response_and_service_order_match_baseline(self):
        before, before_calls = self.execute(baseline_conductor())
        after, after_calls = self.execute(current)
        self.assertEqual(after.model_dump(), before.model_dump())
        self.assertEqual(after_calls, before_calls)
        self.assertIn("reflection", after_calls)

    def test_selector_exception_logs_fixed_warning_without_content_or_traceback(self):
        with patch.object(ai_client, "call_ai_model", side_effect=ValueError(CANARY)), self.assertLogs(vocabulary.logger, logging.WARNING) as captured:
            self.assertEqual(vocabulary.resolve_scripture_with_llm(CANARY), [])
        self.assertEqual(len(captured.records), 1)
        record = captured.records[0]
        self.assertEqual(record.getMessage(), "Scripture reference selection failed.")
        self.assertIsNone(record.exc_info)
        self.assertIsNone(record.stack_info)
        self.assertNotIn(CANARY, " ".join(captured.output) + self.output.getvalue())

    def test_selector_failure_still_reaches_existing_registry_fallback(self):
        real_selector = vocabulary.resolve_scripture_with_llm
        with patch.object(ai_client, "call_ai_model", side_effect=ValueError(CANARY)), self.assertLogs(vocabulary.logger, logging.WARNING):
            self.assertEqual(real_selector("What does the Bible say about fear?"), [])
        # Exercise the actual conductor's unchanged empty-selection branch.
        result, calls = self.execute(current, fallback=True)
        self.assertEqual(calls[:3], ["selector", "fallback", "scripture"])
        self.assertEqual(len(result.verses), 1)
        self.assertTrue(vocabulary.resolve_nql_topics("fear"))

    def test_selector_parsing_and_conditional_diagnostics_do_not_print_content(self):
        for response in ['["John 3:16", "Romans 8:28"]', 'John 3:16, Romans 8:28', None]:
            with self.subTest(shape="empty" if response is None else "references"), patch.object(ai_client, "call_ai_model", return_value=response):
                result = vocabulary.resolve_scripture_with_llm(CANARY)
                self.assertEqual(result, [] if response is None else ["John 3:16", "Romans 8:28"])
        vocabulary.resolve_concepts_dynamic(CANARY)
        # Exercise the otherwise dormant raw-output branch without repairing its import.
        from backend.services import ai_summary_service
        with patch.object(ai_summary_service, "call_openai_model", return_value='["fear"]', create=True):
            self.assertEqual(vocabulary.map_query_to_concepts_llm(CANARY), ["fear"])
        self.assertNotIn(CANARY, self.output.getvalue())
        self.assertEqual(self.output.getvalue(), "")

    def test_governance_and_empty_retrieval_contracts_are_unchanged(self):
        from fastapi import HTTPException
        for module in [baseline_conductor(), current]:
            service = module.QueryService()
            with self.assertRaises(HTTPException) as short:
                service.process_query({"question": "a"})
            self.assertEqual(short.exception.status_code, 400)
            with patch.object(module, "detect_tier0", return_value=types.SimpleNamespace(crisis_type="SUICIDAL_INTENT", confidence=1)), patch.object(module, "resolve_scripture_with_llm", side_effect=AssertionError("Must stop before provider")):
                result = service.process_query({"question": "Offline safety fixture"})
                self.assertEqual(result.escalation_level, "hard_stop")
                self.assertEqual(result.verses, [])
            with patch.object(module, "resolve_scripture_with_llm", return_value=["John 3:16"]), patch.object(service, "fetch_scripture_items", return_value=[]):
                with self.assertRaises(HTTPException) as empty:
                    service.process_query({"question": "Offline lookup"})
                self.assertEqual(empty.exception.status_code, 422)

    def test_only_approved_statement_changes_affect_backend_behavior(self):
        # Compare ASTs after normalizing only this work package's permitted edits.
        class Normalize(ast.NodeTransformer):
            def visit_Expr(self, node):
                if isinstance(node.value, ast.Call):
                    fn = node.value.func
                    if isinstance(fn, ast.Name) and fn.id == "print":
                        return None
                    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id == "logger" and fn.attr == "warning":
                        return None
                return self.generic_visit(node)

            def visit_Import(self, node):
                if [a.name for a in node.names] == ["logging"]:
                    return None
                return node

            def visit_Assign(self, node):
                if any(isinstance(t, ast.Name) and t.id in {"logger", "key"} for t in node.targets):
                    return None
                return self.generic_visit(node)

            def visit_AnnAssign(self, node):
                if isinstance(node.target, ast.Name) and node.target.id == "expansion" and isinstance(node.value, ast.List) and not node.value.elts:
                    return None
                return self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                node.name = None
                return self.generic_visit(node)

            def visit_If(self, node):
                if isinstance(node.test, ast.Name) and node.test.id == "key":
                    return None
                return self.generic_visit(node)

        for path in ["backend/core/vocabulary/nql_scripture_vocabulary.py", "backend/main.py", "backend/api/results.py", "backend/services/query_service.py"]:
            expected = baseline_source(path)
            if path == "backend/main.py":
                # V6.5.4.2 removes only the donation router import and registration.
                for line in (
                    "from backend.routes.donation_routes import router as donation_router",
                    "app.include_router(donation_router)",
                ):
                    self.assertEqual(expected.count(line + "\n"), 1)
                    expected = expected.replace(line + "\n", "", 1)
            before = Normalize().visit(ast.parse(expected))
            # Results and orchestration were intentionally changed by V6.5.3.
            # Keep the historical scope assertion anchored to the accepted cleanup.
            if path in {"backend/api/results.py", "backend/services/query_service.py"}:
                source = baseline_source(path, ACCEPTED_CLEANUP)
            else:
                source = (ROOT / path).read_text(encoding="utf-8")
            after = Normalize().visit(ast.parse(source))
            self.assertEqual(ast.dump(before), ast.dump(after), path)


if __name__ == "__main__":
    unittest.main()
