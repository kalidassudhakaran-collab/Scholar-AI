from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404

WEB_ROOT = Path(settings.BASE_DIR).parent / "web"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/x-icon",
}


def _safe_path(*parts: str) -> Path:
    base = WEB_ROOT.resolve()
    target = (WEB_ROOT.joinpath(*parts)).resolve()
    if not str(target).startswith(str(base)):
        raise Http404("Not found")
    return target


def serve_web_file(request, filepath: str):
    path = _safe_path(filepath)
    if not path.is_file():
        raise Http404("Not found")
    content_type = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
    resp = FileResponse(open(path, "rb"), content_type=content_type)
    # Avoid stale UI when iterating quickly in dev.
    if settings.DEBUG and path.suffix.lower() in (".js", ".css", ".html"):
        resp["Cache-Control"] = "no-store, max-age=0"
        resp["Pragma"] = "no-cache"
        resp["Expires"] = "0"
    return resp


def serve_page(request, page: str = "index.html"):
    if page == "":
        page = "index.html"
    if not page.endswith(".html"):
        page = f"{page}.html"
    return serve_web_file(request, page)


def serve_css(request, filepath: str):
    return serve_web_file(request, f"css/{filepath}")


def serve_js(request, filepath: str):
    return serve_web_file(request, f"js/{filepath}")
