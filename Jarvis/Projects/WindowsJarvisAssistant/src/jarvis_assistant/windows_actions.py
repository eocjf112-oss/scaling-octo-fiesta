from __future__ import annotations

import html
import os
import platform
import re
import shutil
import subprocess
import webbrowser
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
from xml.sax.saxutils import escape

from jarvis_assistant.config import JarvisConfig


@dataclass(frozen=True)
class ActionResult:
    action: str
    success: bool
    message: str
    path: Path | None = None


def run_windows_action(command: str, config: JarvisConfig) -> ActionResult:
    normalized = command.lower()
    if _has_any(normalized, ("excel", "엑셀", "xlsx")):
        return create_excel_document(config, command)
    if _has_any(normalized, ("word", "워드", "docx")):
        return create_word_document(config, command)
    if _has_any(normalized, ("pdf", "피디에프")):
        return create_pdf_document(config, command)
    if _has_any(normalized, ("search file", "file search", "파일 검색", "찾아", "검색")):
        return search_files(config, _extract_query(command))
    if _has_any(normalized, ("organize", "정리", "분류")):
        return organize_files(config)
    if _has_any(normalized, ("internet", "web", "browser", "인터넷", "웹", "구글")):
        return internet_search(_extract_query(command))
    if _has_any(normalized, ("run ", "launch", "open program", "프로그램 실행", "실행")):
        return launch_program(_extract_query(command))
    return ActionResult(
        action="help",
        success=True,
        message="\n".join(
            [
                "Jarvis Windows 자동화 기능",
                "- 엑셀 생성: Jarvis.bat excel \"월간 계획\"",
                "- 워드 생성: Jarvis.bat word \"회의록\"",
                "- PDF 생성: Jarvis.bat pdf \"보고서\"",
                "- 파일 검색: Jarvis.bat search \"계획\"",
                "- 파일 정리: Jarvis.bat organize",
                "- 프로그램 실행: Jarvis.bat run notepad",
                "- 인터넷 검색: Jarvis.bat web \"Windows 자동화\"",
            ]
        ),
    )


def create_excel_document(config: JarvisConfig, title: str) -> ActionResult:
    output = _generated_dir(config) / f"{_safe_name(title, 'jarvis_excel')}.xlsx"
    rows = [
        ["Jarvis Excel 문서", title],
        ["생성 시간", datetime.now().isoformat(timespec="seconds")],
        ["상태", "API 없이 로컬에서 생성됨"],
    ]
    _write_xlsx(output, rows)
    return ActionResult("excel", True, f"엑셀 파일을 생성했습니다: {output}", output)


def create_word_document(config: JarvisConfig, title: str) -> ActionResult:
    output = _generated_dir(config) / f"{_safe_name(title, 'jarvis_word')}.docx"
    paragraphs = [
        "Jarvis Word 문서",
        f"제목: {title}",
        f"생성 시간: {datetime.now().isoformat(timespec='seconds')}",
        "이 문서는 API 없이 Jarvis 로컬 기능으로 생성되었습니다.",
    ]
    _write_docx(output, paragraphs)
    return ActionResult("word", True, f"워드 파일을 생성했습니다: {output}", output)


def create_pdf_document(config: JarvisConfig, title: str) -> ActionResult:
    output = _generated_dir(config) / f"{_safe_name(title, 'jarvis_pdf')}.pdf"
    lines = [
        "Jarvis PDF Document",
        f"Title: {_latin_pdf_text(title)}",
        f"Created: {datetime.now().isoformat(timespec='seconds')}",
        "Generated locally without external AI APIs.",
    ]
    _write_pdf(output, lines)
    return ActionResult("pdf", True, f"PDF 파일을 생성했습니다: {output}", output)


def search_files(config: JarvisConfig, query: str) -> ActionResult:
    root = config.workspace_root.resolve()
    query = query.strip() or "*"
    matches: list[Path] = []
    for path in root.rglob("*"):
        if len(matches) >= 30:
            break
        if path.is_file() and query.lower() in path.name.lower():
            matches.append(path)

    if not matches:
        return ActionResult("search", True, f"'{query}'와 일치하는 파일을 찾지 못했습니다.")

    message = "\n".join(["파일 검색 결과:", *[f"- {path}" for path in matches]])
    return ActionResult("search", True, message)


def organize_files(config: JarvisConfig) -> ActionResult:
    source = (config.workspace_root / "Downloads").resolve()
    if not source.exists():
        source.mkdir(parents=True, exist_ok=True)
        return ActionResult("organize", True, f"정리할 Downloads 폴더를 생성했습니다: {source}")

    moved = 0
    for path in source.iterdir():
        if not path.is_file():
            continue
        category = _category_for_suffix(path.suffix)
        target_dir = source / category
        target_dir.mkdir(exist_ok=True)
        shutil.move(str(path), str(target_dir / path.name))
        moved += 1

    return ActionResult("organize", True, f"Downloads 폴더 파일 {moved}개를 확장자 기준으로 정리했습니다: {source}")


def launch_program(program: str) -> ActionResult:
    program = program.strip() or "notepad"
    if platform.system().lower() == "windows":
        subprocess.Popen(program, shell=True)
        return ActionResult("run", True, f"프로그램 실행 요청을 보냈습니다: {program}")
    return ActionResult("run", True, f"현재 OS는 Windows가 아니므로 실행하지 않았습니다. Windows에서는 실행됩니다: {program}")


def internet_search(query: str) -> ActionResult:
    query = query.strip() or "Jarvis Windows automation"
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    opened = webbrowser.open(url)
    status = "브라우저를 열었습니다" if opened else "브라우저를 열 수 없어 URL만 반환합니다"
    return ActionResult("web", True, f"{status}: {url}")


def _generated_dir(config: JarvisConfig) -> Path:
    directory = config.workspace_root / "Documents" / "Generated"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _extract_query(command: str) -> str:
    cleaned = re.sub(
        r"^(excel|엑셀|word|워드|pdf|피디에프|search|검색|find|찾아|organize|정리|run|실행|web|인터넷|구글)\s*",
        "",
        command.strip(),
        flags=re.IGNORECASE,
    )
    return cleaned.strip().strip('"')


def _safe_name(value: str, fallback: str) -> str:
    value = _extract_query(value) or fallback
    cleaned = re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", value).strip("._")
    return (cleaned or fallback)[:80]


def _has_any(value: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in value for keyword in keywords)


def _category_for_suffix(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in {".doc", ".docx", ".txt", ".pdf", ".md", ".rtf"}:
        return "Documents"
    if suffix in {".xls", ".xlsx", ".csv"}:
        return "Spreadsheets"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return "Images"
    if suffix in {".zip", ".7z", ".rar", ".tar", ".gz"}:
        return "Archives"
    return "Others"


def _write_xlsx(path: Path, rows: list[list[str]]) -> None:
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            cell_ref = f"{chr(64 + col_index)}{row_index}"
            cells.append(
                f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Jarvis" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>',
        )


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{escape(paragraph)}</w:t></w:r></w:p>" for paragraph in paragraphs
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "word/document.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}</w:body></w:document>",
        )


def _write_pdf(path: Path, lines: list[str]) -> None:
    text = "\\n".join(_latin_pdf_text(line) for line in lines)
    stream = f"BT /F1 12 Tf 72 720 Td ({_escape_pdf_text(text)}) Tj ET"
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream.encode('latin-1'))} >> stream\n{stream}\nendstream endobj\n",
    ]
    content = "%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(content.encode("latin-1")))
        content += obj
    xref_position = len(content.encode("latin-1"))
    content += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets:
        content += f"{offset:010d} 00000 n \n"
    content += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF\n"
    )
    path.write_bytes(content.encode("latin-1"))


def _latin_pdf_text(value: str) -> str:
    return value.encode("latin-1", errors="replace").decode("latin-1")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
