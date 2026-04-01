"""Export endpoint — CSV, JSON, PDF for grids and portfolios."""

import csv
import io
import json
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class ExportGrid(BaseModel):
    numbers: list[int]
    stars: list[int] | None = None
    total_score: float
    method: str | None = None


class ExportRequest(BaseModel):
    title: str = "Export Loto Ultime"
    grids: list[ExportGrid]


@router.post("/csv")
# noinspection PyUnusedLocal
async def export_csv(body: ExportRequest) -> StreamingResponse:
    """Export grids as CSV."""
    logger.info("export_requested", format="csv", grid_count=len(body.grids))
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["#", "Numéros", "Étoiles", "Score", "Méthode"])
    for i, g in enumerate(body.grids, 1):
        nums = " - ".join(str(n) for n in g.numbers)
        stars = " - ".join(str(s) for s in g.stars) if g.stars else ""
        writer.writerow([i, nums, stars, f"{g.total_score:.4f}", g.method or ""])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=loto_ultime_{datetime.now():%Y%m%d_%H%M}.csv"},
    )


@router.post("/json")
async def export_json(body: ExportRequest) -> StreamingResponse:
    """Export grids as JSON."""
    logger.info("export_requested", format="json", grid_count=len(body.grids))
    data = {
        "title": body.title,
        "exported_at": datetime.now().isoformat(),
        "count": len(body.grids),
        "grids": [g.model_dump() for g in body.grids],
    }
    content = json.dumps(data, ensure_ascii=False, indent=2)
    return StreamingResponse(
        iter([content]),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=loto_ultime_{datetime.now():%Y%m%d_%H%M}.json"},
    )


@router.post("/pdf")
async def export_pdf(body: ExportRequest) -> StreamingResponse:
    """Export grids as a simple PDF document."""
    logger.info("export_requested", format="pdf", grid_count=len(body.grids))
    buf = _generate_pdf(body)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=loto_ultime_{datetime.now():%Y%m%d_%H%M}.pdf"},
    )


def _generate_pdf(body: ExportRequest) -> io.BytesIO:
    """Generate a minimal PDF without external dependencies."""
    buf = io.BytesIO()
    lines: list[str] = []
    lines.append(body.title)
    lines.append(f"Exporté le {datetime.now():%d/%m/%Y à %H:%M}")
    lines.append("")
    for i, g in enumerate(body.grids, 1):
        nums = " - ".join(str(n) for n in g.numbers)
        stars_str = ""
        if g.stars:
            stars_str = f"  |  Étoiles: {' - '.join(str(s) for s in g.stars)}"
        method_str = f"  ({g.method})" if g.method else ""
        lines.append(f"Grille {i}: {nums}{stars_str}  —  Score: {g.total_score:.4f}{method_str}")

    # Minimal PDF structure
    text = "\n".join(lines)
    objects: list[bytes] = []
    offsets: list[int] = []

    def add_obj(content: bytes) -> int:
        idx = len(objects) + 1
        offsets.append(buf.tell())
        obj = f"{idx} 0 obj\n".encode() + content + b"\nendobj\n"
        buf.write(obj)
        objects.append(obj)
        return idx

    buf.write(b"%PDF-1.4\n")

    # Catalog
    catalog_id = add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Pages
    pages_id = add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # Stream content
    stream_lines = [f"BT /F1 10 Tf 50 750 Td 12 TL"]
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines.append(f"({safe}) '")
    stream_lines.append("ET")
    stream_content = "\n".join(stream_lines).encode("latin-1", errors="replace")
    stream_obj = f"<< /Length {len(stream_content)} >>\nstream\n".encode() + stream_content + b"\nendstream"
    stream_id = add_obj(stream_obj)
    # Page
    page_obj = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {stream_id} 0 R /Resources << /Font << /F1 {stream_id + 1} 0 R >> >> >>".encode()
    # We need to fix: page should be object 3; let's rewrite properly
    # Actually the objects are created sequentially, page is object 3 only if we add in order.
    # Let me restructure:

    buf.seek(0)
    buf.truncate()

    buf.write(b"%PDF-1.4\n")
    pos = [buf.tell()]

    def write_obj(n: int, content: bytes) -> None:
        pos.append(buf.tell())
        buf.write(f"{n} 0 obj\n".encode() + content + b"\nendobj\n")

    # 1: Catalog
    write_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    # 2: Pages
    write_obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # 4: Font
    write_obj(4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    # 5: Stream
    stream_lines2 = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines2.append(f"({safe}) '")
    stream_lines2.append("ET")
    stream_data = "\n".join(stream_lines2).encode("latin-1", errors="replace")
    write_obj(5, f"<< /Length {len(stream_data)} >>\nstream\n".encode() + stream_data + b"\nendstream")
    # 3: Page
    write_obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 5 0 R /Resources << /Font << /F1 4 0 R >> >> >>")

    # XRef
    xref_pos = buf.tell()
    buf.write(b"xref\n")
    buf.write(f"0 6\n".encode())
    buf.write(b"0000000000 65535 f \n")
    for i in range(1, 6):
        buf.write(f"{pos[i]:010d} 00000 n \n".encode())

    buf.write(b"trailer\n")
    buf.write(f"<< /Size 6 /Root 1 0 R >>\n".encode())
    buf.write(b"startxref\n")
    buf.write(f"{xref_pos}\n".encode())
    buf.write(b"%%EOF\n")

    buf.seek(0)
    return buf
