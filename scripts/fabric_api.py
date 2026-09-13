"""Call Fabric through its signed-in CLI without exposing access tokens."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = "09cea7db-63ec-41f0-9cf0-872a6dc5c61d"

def api(endpoint, method="get", body=None, audience="fabric"):
    command = [str(ROOT / ".local/fabric-cli-env/Scripts/fab.exe"), "api", endpoint, "-X", method, "-A", audience]
    if body is not None:
        path = ROOT / ".local/fabric-request.json"
        path.write_text(json.dumps(body), encoding="utf-8")
        command += ["-i", str(path)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
    response = json.loads(result.stdout)
    if response["status_code"] not in (200, 201, 202):
        raise RuntimeError(f"Fabric request failed: {response}")
    return response
