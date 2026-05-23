"""Shared helpers: logging, text normalize, safe filenames."""

import re
import sys
import unicodedata
from datetime import datetime


def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(line.encode(enc, errors="replace").decode(enc, errors="replace"))


def normalize_text(text) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", str(text))
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def cross_verify(thuocsi_name: str, easyinvoice_name: str) -> bool:
    norm_ts = normalize_text(thuocsi_name)
    norm_ei = normalize_text(easyinvoice_name)
    if norm_ts == norm_ei:
        log("✅ [VERIFY] EXACT MATCH")
        return True
    if norm_ts and norm_ei and (norm_ts in norm_ei or norm_ei in norm_ts):
        log("✅ [VERIFY] PARTIAL MATCH")
        return True
    log(f"❌ [VERIFY] MISMATCH: '{norm_ts}' ≠ '{norm_ei}'")
    return False


def sanitize_filename_component(name: str, max_length: int = 100) -> str:
    """Windows-safe single path segment from a human-readable name."""
    if not name:
        return "unknown"
    invalid = '<>:"/\\|?*\n\r\t'
    parts: list[str] = []
    for c in str(name).strip():
        if c in invalid or ord(c) < 32:
            parts.append("_")
        elif c.isspace():
            parts.append("_")
        else:
            parts.append(c)
    out = "".join(parts)
    out = re.sub(r"_+", "_", out)
    out = out.strip("._") or "unknown"
    if len(out) > max_length:
        out = out[:max_length].rstrip("._")
    return out or "unknown"


def pdf_filename_for_customer(order_id: str, customer_display_name: str) -> str:
    """
    Tạo tên file PDF từ tên khách hàng.
    Format: {customer_name}.pdf
    
    Lưu ý: Chỉ dùng tên khách hàng, không lặp lại
    """
    slug = sanitize_filename_component(customer_display_name)
    return f"{slug}.pdf"
