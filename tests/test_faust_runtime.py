from pathlib import Path
import importlib.util
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skill" / "faust-dsp" / "scripts" / "faust_runtime.py"


def load_module():
    spec = importlib.util.spec_from_file_location("faust_runtime", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FaustRuntimeTests(unittest.TestCase):
    def test_cache_root_can_be_overridden(self):
        module = load_module()
        tmp = Path("/tmp/faust-dsp-skill-test")
        old = module.os.environ.get("FAUST_DSP_SKILL_CACHE")
        try:
            module.os.environ["FAUST_DSP_SKILL_CACHE"] = str(tmp)
            self.assertEqual(module.cache_root(), tmp)
            self.assertEqual(module.repo_dir(), tmp / "faust-mcp")
        finally:
            if old is None:
                module.os.environ.pop("FAUST_DSP_SKILL_CACHE", None)
            else:
                module.os.environ["FAUST_DSP_SKILL_CACHE"] = old

    def test_runtime_command_browser(self):
        module = load_module()
        tmp = Path("/tmp/faust-dsp-skill-test")
        old = module.os.environ.get("FAUST_DSP_SKILL_CACHE")
        try:
            module.os.environ["FAUST_DSP_SKILL_CACHE"] = str(tmp)
            cmd, port, env = module.runtime_command("browser")
            self.assertEqual(cmd[-1], "faust_browser_server.py")
            self.assertEqual(port, 8010)
            self.assertEqual(env["MCP_TRANSPORT"], "sse")
        finally:
            if old is None:
                module.os.environ.pop("FAUST_DSP_SKILL_CACHE", None)
            else:
                module.os.environ["FAUST_DSP_SKILL_CACHE"] = old

    def test_runtime_command_rejects_unknown(self):
        module = load_module()
        with self.assertRaisesRegex(ValueError, "unknown runtime kind"):
            module.runtime_command("bad")


if __name__ == "__main__":
    unittest.main()
