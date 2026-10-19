"""Run on the VPS only; secrets stay outside checkout and build context."""

import base64
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

root = Path("/root/rexileer-private")
root.mkdir(mode=0o700, exist_ok=True)
root.chmod(0o700)
(root / "bootstrap").mkdir(mode=0o700, exist_ok=True)
env = root / "desk.env"


def existing_volume_files(volume, pattern):
    result = subprocess.run(
        ["docker", "volume", "inspect", "-f", "{{.Mountpoint}}", volume],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and any(Path(result.stdout.strip()).glob(pattern))


if not env.exists():
    if existing_volume_files("rexileer-dev_desk_data", "desk.sqlite3"):
        raise RuntimeError(
            "Existing Desk database has no private configuration. Restore the original key file explicitly."
        )
    with os.fdopen(
        os.open(env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
    ) as file:
        file.write(
            "DESK_SECRET_KEY="
            + secrets.token_urlsafe(64)
            + "\nDESK_OWNER_USERNAME=owner\n"
        )
env.chmod(0o600)
document_env = root / "document.env"
if not document_env.exists():
    if existing_volume_files(
        "rexileer-dev_desk_documents", "*.fernet"
    ) or existing_volume_files("rexileer-dev_desk_data", "desk.sqlite3"):
        raise RuntimeError(
            "Existing encrypted files have no key file. Restore the original document key; do not rotate silently."
        )
    with os.fdopen(
        os.open(document_env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
    ) as file:
        file.write(
            "DESK_DOCUMENT_KEY="
            + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")
            + "\n"
        )
document_env.chmod(0o600)
running = subprocess.run(
    ["docker", "inspect", "-f", "{{.State.Running}}", "rexileer-desk"],
    capture_output=True,
    text=True,
)
if running.returncode == 0 and running.stdout.strip() == "true":
    subprocess.run(
        [
            "docker",
            "exec",
            "rexileer-desk",
            "python",
            "manage.py",
            "desk_backup",
            "backup",
            f"/app/desk-db/backups/deploy-{time.time_ns()}.desk",
        ],
        check=True,
    )
print("Private Desk configuration ready; existing keys and owner retained.")
network_name = "rexileer-dev_desk_private"
network = subprocess.run(
    ["docker", "network", "inspect", network_name], capture_output=True, text=True
)
if network.returncode == 0:
    current = json.loads(network.stdout)[0]
    if current.get("Internal"):
        names = {v["Name"] for v in current.get("Containers", {}).values()}
        if names - {"rexileer-desk"}:
            raise RuntimeError(
                "Desk network contains an unrelated endpoint; refusing to change it."
            )
        # Internal bridge suppresses published ports. Replace only this owned
        # container/network, after backup; named data/blob volumes are retained.
        if "rexileer-desk" in names:
            subprocess.run(
                ["docker", "rm", "-f", "rexileer-desk"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        subprocess.run(
            ["docker", "network", "rm", network_name],
            check=True,
            stdout=subprocess.DEVNULL,
        )
