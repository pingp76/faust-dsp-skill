from pathlib import Path
import importlib.util
import os
import tempfile
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

    def test_base_env_prepends_venv_bin_when_available(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            py = cache / "venv" / "bin" / "python"
            py.parent.mkdir(parents=True)
            py.touch()
            old = module.os.environ.get("FAUST_DSP_SKILL_CACHE")
            try:
                module.os.environ["FAUST_DSP_SKILL_CACHE"] = str(cache)
                env = module.base_env()
                self.assertEqual(env["VIRTUAL_ENV"], str(cache / "venv"))
                self.assertEqual(env["TMPDIR"], str(cache / "tmp"))
                self.assertTrue((cache / "tmp").is_dir())
                self.assertEqual(env["PATH"].split(os.pathsep)[0], str(py.parent))
            finally:
                if old is None:
                    module.os.environ.pop("FAUST_DSP_SKILL_CACHE", None)
                else:
                    module.os.environ["FAUST_DSP_SKILL_CACHE"] = old

    def test_base_env_adds_cpp_wrapper_for_homebrew_faust_headers(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache = root / "cache"
            brew = root / "homebrew"
            bin_dir = brew / "bin"
            include_dir = brew / "include"
            (include_dir / "faust" / "gui").mkdir(parents=True)
            (include_dir / "faust" / "gui" / "MapUI.h").touch()
            bin_dir.mkdir(parents=True)
            gpp = bin_dir / "g++"
            faust = bin_dir / "faust"
            gpp.write_text("#!/bin/sh\n", encoding="utf-8")
            faust.write_text("#!/bin/sh\n", encoding="utf-8")
            gpp.chmod(0o755)
            faust.chmod(0o755)
            old_cache = module.os.environ.get("FAUST_DSP_SKILL_CACHE")
            old_path = module.os.environ.get("PATH")
            try:
                module.os.environ["FAUST_DSP_SKILL_CACHE"] = str(cache)
                module.os.environ["PATH"] = str(bin_dir)
                env = module.base_env()
            finally:
                if old_cache is None:
                    module.os.environ.pop("FAUST_DSP_SKILL_CACHE", None)
                else:
                    module.os.environ["FAUST_DSP_SKILL_CACHE"] = old_cache
                if old_path is None:
                    module.os.environ.pop("PATH", None)
                else:
                    module.os.environ["PATH"] = old_path

            wrapper = cache / "bin" / "g++"
            self.assertTrue(wrapper.exists())
            self.assertIn(f"-I{include_dir.resolve()}", wrapper.read_text(encoding="utf-8"))
            self.assertEqual(env["PATH"].split(os.pathsep)[0], str(cache / "bin"))

    def test_analyze_resolves_relative_dsp_before_switching_to_upstream_cwd(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            cache = root / "cache"
            work = root / "work"
            work.mkdir()
            dsp = work / "tone.dsp"
            dsp.write_text("process = _;", encoding="utf-8")
            py = cache / "venv" / "bin" / "python"
            py.parent.mkdir(parents=True)
            py.touch()

            captured = {}
            old_cache = module.os.environ.get("FAUST_DSP_SKILL_CACHE")
            old_cwd = Path.cwd()
            try:
                module.os.environ["FAUST_DSP_SKILL_CACHE"] = str(cache)
                os.chdir(work)
                module.ensure_repo = lambda update=False: None
                module.ensure_venv = lambda: None

                def fake_run(cmd, cwd=None, env=None):
                    captured["cmd"] = cmd
                    captured["cwd"] = cwd
                    captured["env"] = env

                module.run = fake_run
                args = module.argparse.Namespace(
                    dsp="tone.dsp",
                    runtime="cpp",
                    skip_python_deps=False,
                    input_source=None,
                    input_freq=None,
                    input_file=None,
                )
                module.analyze(args)
            finally:
                os.chdir(old_cwd)
                if old_cache is None:
                    module.os.environ.pop("FAUST_DSP_SKILL_CACHE", None)
                else:
                    module.os.environ["FAUST_DSP_SKILL_CACHE"] = old_cache

            self.assertEqual(captured["cwd"], cache / "faust-mcp")
            self.assertEqual(captured["cmd"][0], str(py))
            self.assertIn(str(dsp.resolve()), captured["cmd"])
            self.assertIn(str(cache / "tmp"), captured["cmd"])
            self.assertEqual(captured["env"]["PATH"].split(os.pathsep)[0], str(py.parent))


if __name__ == "__main__":
    unittest.main()
