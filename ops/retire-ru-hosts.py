"""Archive obsolete .ru renewal jobs and disable old vhosts without deleting history."""

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

enabled = Path("/etc/nginx/sites-enabled")
names = [
    "rexileer.conf",
    "rexileer-ssl.conf",
    "desk.rexileer.ru.conf",
    "ai-leads.rexileer.ru.conf",
    "logs.rexileer.ru.conf",
]
links = {}
for name in names:
    path = enabled / name
    if path.is_symlink():
        target = path.resolve()
        if target.parent != Path("/etc/nginx/sites-available"):
            raise RuntimeError(
                "Unexpected legacy vhost target; refusing to disable it."
            )
        links[path] = target
    elif path.exists():
        raise RuntimeError(
            "Legacy enabled vhost is not a symlink; refusing to replace it."
        )
backup = Path("/root/server-fixes") / (
    "retired-ru-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
)
if links:
    backup.mkdir(mode=0o700)
    (backup / "vhost-links.txt").write_text(
        "\n".join(str(path) + " -> " + str(target) for path, target in links.items())
    )
    try:
        for path in links:
            path.unlink()
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
    except BaseException:
        for path, target in links.items():
            if not path.exists():
                path.symlink_to(target)
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        raise
for cert in [
    "rexileer.ru",
    "desk.rexileer.ru",
    "ai-leads.rexileer.ru",
    "logs.rexileer.ru",
]:
    path = Path("/etc/letsencrypt/renewal") / (cert + ".conf")
    if path.is_file():
        backup.mkdir(mode=0o700, exist_ok=True)
        shutil.move(str(path), str(backup / path.name))
print(
    "Obsolete .ru vhosts disabled and renewal jobs archived; certificates/history retained."
)
