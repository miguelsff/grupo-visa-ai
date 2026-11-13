import json
import os
import subprocess
import sys
import time
from pathlib import Path

from ocd_ingesta.cli import ingestion_lock
from tests.conftest import FIXTURES
from tests.test_clients import openai_server


def environment(tmp_path, url):
    return os.environ | {
        "ATLASSIAN_BASE_URL": "https://grupo-visai.atlassian.net",
        "ATLASSIAN_EMAIL": "test@example.test",
        "ATLASSIAN_API_TOKEN": "test-only-token",
        "OPENAI_API_KEY": "test-only-key",
        "OPENAI_BASE_URL": url,
        "QDRANT_URL": os.environ["QDRANT_TEST_URL"],
        "INGESTA_STATE_DIR": str(tmp_path),
        "TEST_FIXTURES": str(FIXTURES),
        "PYTHONPATH": str(Path(__file__).parent / "cron_support"),
        "TZ": "America/Lima",
    }


def test_process_lock_released_after_process_exit(tmp_path):
    command = [
        sys.executable,
        "-c",
        (
            "from ocd_ingesta.cli import ingestion_lock; from pathlib import Path; "
            f"\nwith ingestion_lock(Path({str(tmp_path)!r})): print('acquired')"
        ),
    ]
    with ingestion_lock(tmp_path):
        blocked = subprocess.run(command, capture_output=True, text=True, timeout=10)
        assert blocked.returncode != 0
        assert "Ya existe una ingesta" in blocked.stderr
    available = subprocess.run(command, capture_output=True, text=True, timeout=10)
    assert available.returncode == 0


def test_manual_cli_failure_preserves_published_alias(qdrant, tmp_path):
    with openai_server() as (url, _):
        env = environment(tmp_path, url)
        completed = subprocess.run(
            ["ocd-ingestar"], env=env, capture_output=True, text=True, timeout=60
        )
        assert completed.returncode == 0, completed.stderr
    active = qdrant.target()
    assert active is not None
    with openai_server(fail=True) as (url, _):
        failed = subprocess.run(
            ["ocd-ingestar"],
            env=environment(tmp_path, url),
            capture_output=True,
            text=True,
            timeout=30,
        )
    assert failed.returncode == 1
    assert "test-only" not in failed.stderr
    assert qdrant.target() == active
    assert qdrant.collections() == {active}


def test_supercronic_invokes_same_cli_in_lima(qdrant, tmp_path):
    assert Path("crontab").read_text().strip() == "0 3 * * * ocd-ingestar"
    # Supercronic admite seis campos con segundos. Solo la prueba cambia el horario.
    temporary_cron = tmp_path / "test.cron"
    temporary_cron.write_text("*/2 * * * * * ocd-ingestar\n")
    with openai_server() as (url, _):
        process = subprocess.Popen(
            ["supercronic", str(temporary_cron)],
            env=environment(tmp_path, url),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                if qdrant.target():
                    break
                time.sleep(0.2)
            assert qdrant.target() is not None
            state = json.loads((tmp_path / "publication.json").read_text())
            assert state["pending"] is None
            # La zona del contenedor y la del proceso están fijadas explícitamente.
            zone = subprocess.check_output(
                ["date", "+%Z %z"], env=environment(tmp_path, url), text=True
            ).strip()
            assert zone == "-05 -0500"
        finally:
            process.terminate()
            output, _ = process.communicate(timeout=15)
        assert "Carga publicada" in output
        assert "test-only" not in output
