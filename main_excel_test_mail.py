"""
Main script - GỬI MAIL TEST (gửi cho chính mình).

Quy trình giống main_excel_send.py nhưng:
- Tất cả email đều gửi cho SENDER_EMAIL (chính bạn)
- Nội dung email ghi rõ: "Email thật cần gửi: xxx@yyy.com"
- Đính kèm hóa đơn PDF

Mục đích: Kiểm tra nội dung email + hóa đơn trước khi gửi thật.

Cách chạy:
    python main_excel_test_mail.py
"""

import os
import smtplib
from email.message import EmailMessage

from invoice_agents.master_agent_excel import MasterAgentExcel
from invoice_agents import config
from invoice_agents.utils import log


def main():
    log("=" * 70)
    log("🚀 MASTER AGENT EXCEL - TEST MAIL (GỬI CHO CHÍNH MÌNH)")
    log("=" * 70)
    log("📋 Quy trình:")
    log("  1. Đọc file Excel")
    log("  2. Tìm hóa đơn trên EasyInvoice")
    log("  3. Tải PDF và đổi tên theo khách hàng")
    log("  4. 📧 GỬI MAIL CHO CHÍNH MÌNH (không gửi cho khách)")
    log("=" * 70)
    log(f"📄 File Excel: {config.EXCEL_FILE}")
    log(f"📧 Email nhận test: {config.SENDER_EMAIL}")
    log("=" * 70)

    if not config.email_configured():
        log("❌ Chưa cấu hình SENDER_EMAIL/SENDER_PASSWORD trong .env")
        return

    log(f"\n💡 Tất cả email sẽ gửi đến: {config.SENDER_EMAIL}")
    log("💡 Nội dung email sẽ ghi rõ email thật cần gửi")

    response = input("\n✋ Tiếp tục? (y/n): ")
    if response.lower() != 'y':
        log("❌ Đã hủy")
        return

    # Chạy pipeline preview (tải PDF nhưng không gửi mail)
    master = MasterAgentExcel()
    result = master.execute_full_pipeline(
        excel_file=None,
        send_email=False,  # Không gửi mail trong pipeline
        output_file=None
    )

    # Gửi mail test cho chính mình
    log("\n" + "=" * 70)
    log("📧 BẮT ĐẦU GỬI MAIL TEST CHO CHÍNH MÌNH")
    log("=" * 70)

    sent_count = 0
    failed_count = 0

    for r in result.get("results", []):
        if r["status"] != "SUCCESS" or not r["pdf_path"]:
            log(f"\n⚠️  Bỏ qua {r['pharmacy_name']} (lỗi hoặc không có PDF)")
            continue

        pharmacy_name = r["pharmacy_name"]
        real_email = r["receiver_email"]
        pdf_path = r["pdf_path"]

        log(f"\n📧 Gửi test mail: {pharmacy_name}")
        log(f"  → Email thật: {real_email}")
        log(f"  → Gửi đến: {config.SENDER_EMAIL}")
        log(f"  → PDF: {pdf_path}")

        try:
            msg = EmailMessage()
            msg["Subject"] = f"[TEST] Hóa đơn - {pharmacy_name} → {real_email}"
            msg["From"] = config.SENDER_EMAIL
            msg["To"] = config.SENDER_EMAIL  # Gửi cho chính mình

            msg.set_content(
                f"""[ĐÂY LÀ EMAIL TEST - KHÔNG GỬI CHO KHÁCH]

Thông tin hóa đơn:
- Tên khách hàng: {pharmacy_name}
- Email thật cần gửi: {real_email}
- File PDF: {os.path.basename(pdf_path)}

---
Nếu nội dung và hóa đơn đúng, bạn có thể chạy:
  python main_excel_send.py
để gửi mail thật cho khách hàng.
"""
            )

            # Đính kèm PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(pdf_path),
                )
            else:
                log(f"  ⚠️  File PDF không tồn tại: {pdf_path}")

            # Gửi
            with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as smtp:
                smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                smtp.send_message(msg)

            sent_count += 1
            log(f"  ✅ Đã gửi test mail thành công")

        except Exception as e:
            failed_count += 1
            log(f"  ❌ Lỗi gửi mail: {e}")

    # Thống kê
    log("\n" + "=" * 70)
    log("📊 KẾT QUẢ GỬI MAIL TEST")
    log("=" * 70)
    log(f"✅ Gửi thành công: {sent_count}")
    log(f"❌ Lỗi: {failed_count}")
    log(f"📧 Kiểm tra hộp thư: {config.SENDER_EMAIL}")
    log("=" * 70)
    log("\n💡 Nếu OK, chạy: python main_excel_send.py để gửi thật")
    log("=" * 70)


if __name__ == "__main__":
    main()
