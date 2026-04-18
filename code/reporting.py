from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1 << 16)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def verify_pdf_readability(pdf_paths: list[Path], out_path: Path) -> None:
    import fitz  # type: ignore[import-untyped]

    lines = ["pdf_path,page_count,width,height,status"]
    for p in pdf_paths:
        doc = fitz.open(p)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.3, 1.3))
        status = "ok" if pix.width >= 700 and pix.height >= 500 else "review_needed"
        lines.append(f"{p},{doc.page_count},{pix.width},{pix.height},{status}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
