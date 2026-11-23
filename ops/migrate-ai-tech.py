"""Update only domain configuration; preserve live AI images and other settings."""

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path("/root/ai-leads")
private = Path("/root/rexileer-private")
changes = {
    "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,45.95.0.124,ai-leads.rexileer.tech",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://ai-leads.rexileer.tech",
    "ADMIN_BASE_URL": "https://ai-leads.rexileer.tech",
    "ADMIN_LOGS_URL": "https://logs.rexileer.tech/",
    "AI_SITE_URL": "https://ai-leads.rexileer.tech",
}
services = ["web", "bot", "parser_worker", "parser_scheduler", "parser_collector"]
containers = json.loads(
    subprocess.check_output(
        ["docker", "inspect", *["ai-leads-" + s + "-1" for s in services]]
    )
)
overrides = {}
expected = {}
for service, container in zip(services, containers, strict=True):
    env = dict(item.split("=", 1) for item in container["Config"]["Env"])
    revised = {**env, **changes}
    if revised == env:
        continue
    # --no-build must also preserve the exact image currently running.
    image = json.loads(
        subprocess.check_output(
            ["docker", "image", "inspect", container["Config"]["Image"]]
        )
    )[0]
    if image["Id"] != container["Image"]:
        raise RuntimeError(
            "Live image differs from its tag; refuse an unrelated update."
        )
    overrides[service] = {"environment": revised}
    expected[service] = (container["Image"], revised, container["Mounts"])

dotenv = root / ".env"
previous = dotenv.read_text(encoding="utf-8")
updated = previous
for key, value in changes.items():
    pattern = r"(?m)^" + re.escape(key) + r"=.*$"
    if len(re.findall(pattern, updated)) > 1:
        raise RuntimeError("Ambiguous domain configuration; refusing duplicate keys.")
    if re.search(pattern, updated):
        updated = re.sub(pattern, lambda match: key + "=" + value, updated)
    else:
        updated = updated.rstrip("\n") + "\n" + key + "=" + value + "\n"

if updated != previous:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = Path("/root/server-fixes") / ("ai-tech-env-" + stamp)
    backup.mkdir(mode=0o700)
    (backup / "before.env").write_text(previous, encoding="utf-8")
    (backup / "before.env").chmod(0o600)
    dotenv.write_text(updated, encoding="utf-8")

if overrides:
    private.mkdir(mode=0o700, exist_ok=True)
    override = private / "ai-tech-runtime.json"
    with os.fdopen(
        os.open(override, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w"
    ) as destination:
        json.dump({"services": overrides}, destination)
    override.chmod(0o600)
    # Preserve live non-domain environment values, including values differing
    # from this separately maintained project's uncommitted dotenv settings.
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(root / "docker-compose.yml"),
            "-f",
            str(override),
            "up",
            "-d",
            "--no-deps",
            "--no-build",
            "--timeout",
            "60",
            *overrides,
        ],
        cwd=root,
        check=True,
    )
    for service, (image, env, mounts) in expected.items():
        actual = json.loads(
            subprocess.check_output(["docker", "inspect", "ai-leads-" + service + "-1"])
        )[0]
        if (
            actual["Image"] != image
            or dict(item.split("=", 1) for item in actual["Config"]["Env"]) != env
            or actual["Mounts"] != mounts
        ):
            raise RuntimeError("AI runtime changed beyond the requested domains.")
print("AI public domain settings updated; credentials, images and volumes preserved.")
