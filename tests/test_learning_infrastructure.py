import asyncio
import tempfile
import unittest
from pathlib import Path


class LearningInfrastructureTests(unittest.TestCase):
    def test_markdown_memory_provider_contract_and_learning_queue(self):
        from nano_hermes.agent.memory_providers.markdown import MarkdownMemoryProvider

        with tempfile.TemporaryDirectory() as tmp:
            provider = MarkdownMemoryProvider(Path(tmp))
            entry_id = provider.add_entry("user", "User prefers concise technical replies.", {"source": "test"})
            self.assertTrue(entry_id)
            self.assertIn("concise technical", provider.read_user())
            self.assertEqual(provider.search_memory("concise", limit=1)[0]["target"], "user")
            provider.replace_entry("user", "concise technical", "terse technical")
            self.assertIn("terse technical", provider.read_user())
            event_id = provider.append_learning_event({"kind": "memory_add", "content": "Project uses pytest."})
            pending = provider.read_learning_events()
            self.assertEqual(pending[0]["id"], event_id)
            provider.update_learning_event(event_id, "applied", "verified")
            self.assertEqual(provider.read_learning_events(status="applied")[0]["reason"], "verified")

    def test_sqlite_memory_provider_searches_entries(self):
        from nano_hermes.agent.memory_providers.sqlite import SQLiteMemoryProvider

        with tempfile.TemporaryDirectory() as tmp:
            provider = SQLiteMemoryProvider(Path(tmp))
            provider.add_entry("memory", "Run tests with scripts/run_tests.sh", {"tags": ["testing"]})
            results = provider.search_memory("run_tests", limit=5)
            self.assertEqual(results[0]["target"], "memory")
            self.assertIn("scripts/run_tests.sh", results[0]["content"])

    def test_session_database_recent_and_search(self):
        from nano_hermes.session.database import SessionDatabase

        with tempfile.TemporaryDirectory() as tmp:
            db = SessionDatabase(Path(tmp) / "sessions.db")
            db.append_message("s1", role="user", content="We fixed the OAuth redirect bug", title="OAuth work")
            db.append_message("s1", role="assistant", content="Changed callback URL validation")
            self.assertEqual(db.recent(limit=1)[0]["id"], "s1")
            results = db.search("OAuth redirect", limit=5)
            self.assertEqual(results[0]["session_id"], "s1")

    def test_skill_index_validation_and_search(self):
        from nano_hermes.agent.skill_index import SkillIndex
        from nano_hermes.agent.skill_validator import SkillValidator

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "github-review"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: github-review\ndescription: Review GitHub pull requests\nmetadata:\n  nanohermes:\n    tags: [github, review]\n    triggers: [pull request, PR review]\n---\n# GitHub Review\nUse gh pr diff before reviewing.\n",
                encoding="utf-8",
            )
            index = SkillIndex(root)
            results = index.search("review pull request", limit=3)
            self.assertEqual(results[0]["name"], "github-review")
            report = SkillValidator().validate(skill_dir / "SKILL.md")
            self.assertTrue(report.valid, report.errors)

    def test_tools_manage_memory_skills_and_sessions(self):
        from nano_hermes.agent.tools.memory import MemoryTool
        from nano_hermes.agent.tools.session_search import SessionSearchTool
        from nano_hermes.agent.tools.skills import SkillsTool
        from nano_hermes.session.database import SessionDatabase

        async def run_case():
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                mem = MemoryTool(root)
                await mem.execute(action="add", target="user", content="User likes examples")
                self.assertIn("examples", await mem.execute(action="read", target="user"))

                skills = SkillsTool(root)
                created = await skills.execute(
                    action="create",
                    name="example-skill",
                    content="---\nname: example-skill\ndescription: Example skill\n---\n# Example\nDo the thing.\n",
                )
                self.assertIn("created", created.lower())
                self.assertIn("example-skill", await skills.execute(action="search", query="example"))

                db = SessionDatabase(root / "memory" / "sessions.db")
                db.append_message("s1", role="user", content="OAuth prior work")
                search = SessionSearchTool(root, database=db)
                self.assertIn("OAuth", await search.execute(action="search", query="OAuth"))

        asyncio.run(run_case())

    def test_context_includes_enforcement_policies(self):
        from nano_hermes.agent.context import ContextBuilder

        with tempfile.TemporaryDirectory() as tmp:
            prompt = ContextBuilder(Path(tmp)).build_system_prompt()
            self.assertIn("# Enforcement Policy", prompt)
            self.assertIn("# Learning Policy", prompt)
            self.assertIn("# Verification Policy", prompt)


if __name__ == "__main__":
    unittest.main()
