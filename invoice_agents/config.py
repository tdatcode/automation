"""Central config: URLs, paths, credentials from environment."""

import os

from dotenv import load_dotenv

load_dotenv()

# Paths (relative to cwd when running scripts from project root)
EXCEL_FILE = os.getenv("EXCEL_FILE", "excel/HoaDon.xlsx")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "downloads")
LOG_FILE = os.getenv("LOG_FILE", "logs/result.xlsx")
PREVIEW_FILE = os.getenv("PREVIEW_FILE", "excel/danh_sach_mail_can_gui_thuocsi.xlsx")
# Thư mục chứa các email sẽ gửi (preview mode)
EMAIL_GUI_FOLDER = os.getenv("EMAIL_GUI_FOLDER", "emailgui")
# File Excel danh sách mail cần gửi
EXCEL_MAIL_PREVIEW_FILE = os.getenv(
    "EXCEL_MAIL_PREVIEW_FILE", "emailgui/danh_sach_mail.xlsx"
)

# Web
THUOCSI_LOGIN_URL = os.getenv(
    "THUOCSI_LOGIN_URL", "https://sellercenter.thuocsi.vn/login"
)
EASYINVOICE_INDEX_URL = os.getenv(
    "EASYINVOICE_INDEX_URL",
    "https://0312670722.easyinvoice.com.vn/EInvoice/Index",
)

# Email (Gmail SMTP)
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "Z2I4OQEM8D@hoadon.thuocsi.vn")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

# Pipeline
PIPELINE_LIMIT = os.getenv("PIPELINE_LIMIT")  # optional max invoices (int string)


def ensure_dirs():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(EMAIL_GUI_FOLDER, exist_ok=True)
    for p in (LOG_FILE, PREVIEW_FILE, EXCEL_MAIL_PREVIEW_FILE):
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)


def email_configured() -> bool:
    return bool(SENDER_EMAIL and SENDER_PASSWORD)
