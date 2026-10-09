import base64
import binascii
import json
import tempfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .acquisition import acquire_data
from .analysis import run_analysis
from .integrity import verify_integrity
from .report import REPORT_DIR, generate_report
from .validation import validate_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def process_upload(filename, content, categories):
    if not categories.get("call_records") and not categories.get("signal_data"):
        raise ValueError("Authorize call records, signal data, or both.")

    safe_name = Path(filename).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in {".csv", ".json"}:
        raise ValueError("Only CSV and JSON evidence files are supported.")
    if not content:
        raise ValueError("The selected evidence file is empty.")

    requisition = {
        "call_records": bool(categories.get("call_records")),
        "signal_data": bool(categories.get("signal_data")),
    }
    consent = {
        "status": "GRANTED",
        "timestamp": datetime.now().astimezone().isoformat(),
        "purpose": "Forensic call and signal analysis",
    }

    with tempfile.TemporaryDirectory(prefix="call-signal-") as temporary_dir:
        source_path = Path(temporary_dir) / safe_name
        source_path.write_bytes(content)
        evidence = acquire_data(requisition, source_path)

    if evidence is None:
        raise RuntimeError("Evidence acquisition failed.")

    validation = validate_data(evidence, requisition)
    if validation is None:
        raise ValueError("Evidence validation failed; no analysis was performed.")

    integrity = verify_integrity(evidence)
    if integrity is None:
        raise ValueError("Integrity verification failed; no analysis was performed.")

    results = run_analysis(validation["data"], requisition)
    if results is None:
        raise RuntimeError("Forensic analysis failed.")

    report = generate_report(
        consent, requisition, evidence, validation, integrity, results
    )
    if report is None:
        raise RuntimeError("Report generation failed.")

    records = validation["data"].copy()
    records["timestamp"] = records["timestamp"].astype(str)
    records = records.astype(object).where(records.notna(), None)

    return {
        "status": "complete",
        "consent": consent,
        "requisition": requisition,
        "evidence": {
            "filename": evidence["filename"],
            "size_bytes": evidence["size_bytes"],
            "sha256": integrity["hash"],
            "records": validation["records"],
            "duplicates": validation["duplicates"],
        },
        "analysis": results,
        "report": Path(report["report_path"]).name,
        "rows": records.to_dict(orient="records"),
    }


class TrackerHandler(BaseHTTPRequestHandler):
    server_version = "CallSignalTracker/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json({"status": "ready", "app": "Call & Signal Forensic Tracker"})
            return

        if parsed.path.startswith("/api/reports/"):
            report_name = Path(unquote(parsed.path.removeprefix("/api/reports/"))).name
            report_path = (REPORT_DIR / report_name).resolve()
            if report_path.parent != REPORT_DIR.resolve() or not report_path.is_file():
                self._send_json({"error": "Report not found."}, status=404)
                return
            self._send_bytes(
                report_path.read_bytes(),
                "text/plain; charset=utf-8",
                headers={"Content-Disposition": f'attachment; filename="{report_name}"'},
            )
            return

        requested = "index.html" if parsed.path == "/" else parsed.path.lstrip("/")
        static_path = (FRONTEND_DIR / requested).resolve()
        if static_path != FRONTEND_DIR.resolve() and FRONTEND_DIR.resolve() not in static_path.parents:
            self._send_json({"error": "Not found."}, status=404)
            return
        if not static_path.is_file():
            self._send_json({"error": "Not found."}, status=404)
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
        }.get(static_path.suffix, "application/octet-stream")
        self._send_bytes(static_path.read_bytes(), content_type)

    def do_POST(self):
        if urlparse(self.path).path != "/api/analyze":
            self._send_json({"error": "Not found."}, status=404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Invalid content length."}, status=400)
            return
        if content_length <= 0 or content_length > MAX_UPLOAD_BYTES * 2:
            self._send_json({"error": "Upload must be between 1 byte and 25 MB."}, status=413)
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
            if payload.get("consent") is not True:
                raise ValueError("Explicit consent is required to continue.")
            content = base64.b64decode(payload["content_base64"], validate=True)
            if len(content) > MAX_UPLOAD_BYTES:
                raise ValueError("Upload exceeds the 25 MB limit.")
            result = process_upload(payload["filename"], content, payload["categories"])
        except (json.JSONDecodeError, KeyError, TypeError, binascii.Error) as error:
            self._send_json({"error": f"Invalid request: {error}"}, status=400)
            return
        except ValueError as error:
            self._send_json({"error": str(error)}, status=422)
            return
        except Exception as error:
            self._send_json({"error": f"Pipeline error: {error}"}, status=500)
            return

        self._send_json(result)

    def _send_json(self, payload, status=200):
        self._send_bytes(
            json.dumps(payload, allow_nan=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status=status,
        )

    def _send_bytes(self, content, content_type, status=200, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {format_string % args}")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), TrackerHandler)
    print("Call & Signal Forensic Tracker ready at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down tracker server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()