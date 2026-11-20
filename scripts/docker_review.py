"""Run independent Olist aggregates in DeepAnalyze's Docker executor."""
import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "vendor/DeepAnalyze/demo/chat_v2/backend_app"
IMAGE = "python:3.11-slim"


def verify(reverse_periods=False, *, baseline_month="2018-07", target_month="2018-08", driver_row=None):
    (ROOT / "artifacts/phase2").mkdir(parents=True, exist_ok=True)
    for directory in (
        Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "Programs/DockerDesktop/resources/bin",
        Path(r"C:\Program Files\Docker\Docker\resources\bin"),
    ):
        if (directory / "docker.exe").is_file():
            os.environ["PATH"] = str(directory) + os.pathsep + os.environ["PATH"]
            break

    # Each invocation has its own environment and mount. No credentials are copied.
    with TemporaryDirectory(prefix="docker-review-", dir=ROOT / "artifacts/phase2") as directory:
        session = "review-" + uuid4().hex
        workspace = Path(directory) / session
        raw = workspace / "data/raw/olist"
        raw.mkdir(parents=True)
        for table in ("orders", "order_items", "products"):
            name = f"olist_{table}_dataset.csv"
            shutil.copyfile(ROOT / "data/raw/olist" / name, raw / name)
        package = workspace / "commercelens_eval"
        package.mkdir()
        shutil.copyfile(ROOT / "commercelens_eval/baseline.py", package / "baseline.py")
        shutil.copyfile(ROOT / "scripts/sales_drivers.py", workspace / "sales_drivers.py")
        script = workspace / "verify.py"
        script.write_text(
            "import json\nfrom commercelens_eval.baseline import oracle\nfrom sales_drivers import decompose\n"
            f"rows = oracle(reverse_periods={reverse_periods!r}, "
            f"baseline_month={baseline_month!r}, target_month={target_month!r})\n"
            f"driver_row = {driver_row!r}\n"
            "print(json.dumps({'rows': rows, 'drivers': decompose(driver_row) if driver_row else None}, default=str))\n",
            encoding="utf-8",
        )
        os.environ.update(
            DEEPANALYZE_WORKSPACE_BASE=directory,
            DEEPANALYZE_EXECUTION_MODE="docker",
            DEEPANALYZE_DOCKER_IMAGE=IMAGE,
            DEEPANALYZE_DOCKER_AUTO_BUILD="false",
            DEEPANALYZE_DOCKER_NETWORK_MODE="none",
            DEEPANALYZE_ALLOW_UNSAFE_LOCAL_EXECUTION="false",
        )
        # Load the upstream executor without booting its web app.
        for name, path in (("review_backend", BASE), ("review_backend.services", BASE / "services")):
            module = ModuleType(name)
            module.__path__ = [str(path)]
            sys.modules[name] = module
        executor = importlib.import_module("review_backend.services.docker_executor")
        try:
            output = executor.execute_python_in_docker(str(script), str(workspace), 25, session)
            result = json.loads(output)
            inspected = subprocess.check_output(
                ["docker", "inspect", executor._container_name_for_session(session)], text=True, timeout=15
            )
            details = json.loads(inspected)[0]
            if details["HostConfig"]["NetworkMode"] != "none":
                raise RuntimeError("Review container must be disconnected from the network")
            return {**result, "container_id": details["Id"], "image_id": details["Image"],
                    "network": "none", "executor": "DeepAnalyze chat_v2"}
        finally:
            executor.release_session_container(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reverse-periods", action="store_true")
    parser.add_argument("--baseline-month", default="2018-07")
    parser.add_argument("--target-month", default="2018-08")
    parser.add_argument("--driver-row", type=json.loads)
    args = parser.parse_args()
    if args.driver_row is not None and (
        not isinstance(args.driver_row, list) or len(args.driver_row) != 4
        or any(type(value) not in (int, float) for value in args.driver_row)
    ):
        parser.error("Expected four numeric driver inputs")
    print(json.dumps(verify(args.reverse_periods, baseline_month=args.baseline_month,
                            target_month=args.target_month, driver_row=args.driver_row)))
