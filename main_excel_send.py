"""
Main script - Xử lý từ Excel - GỬI MAIL THẬT.

Quy trình:
1. Đọc file Excel (Tên khách hàng + Email)
2. Tìm trên EasyInvoice theo tên khách hàng
3. Click icon mắt (Xem) → Tải PDF
4. Đổi tên PDF theo tên khách hàng
5. GỬI EMAIL với PDF đính kèm

Cách chạy:
    python main_excel_send.py

Cấu hình:
    - CẦN SENDER_EMAIL và SENDER_PASSWORD trong .env
    - File Excel mặc định: excel/HoaDon.xlsx (hoặc EXCEL_FILE trong .env)
    - Cột cần thiết:
      * "Tên công ty/nhà thuốc/quầy thuốc" → Tên khách hàng
      * "Địa chỉ gửi hóa đơn" → Email nhận
"""

from invoice_agents.master_agent_excel import MasterAgentExcel
from invoice_agents import config
from invoice_agents.utils import log


def main():
    """Chạy Master Agent Excel với Production Mode (GỬI MAIL THẬT)."""
    
    log("=" * 70)
    log("🚀 MASTER AGENT EXCEL - PRODUCTION MODE")
    log("=" * 70)
    log("📋 Quy trình:")
    log("  1. Đọc file Excel")
    log("  2. Tìm hóa đơn trên EasyInvoice")
    log("  3. Tải PDF và đổi tên theo khách hàng")
    log("  4. ⚠️  GỬI EMAIL THẬT với PDF đính kèm")
    log("=" * 70)
    log(f"📄 File Excel: {config.EXCEL_FILE}")
    log("📄 Cột cần thiết:")
    log("   - 'Tên công ty/nhà thuốc/quầy thuốc' → Tên khách hàng")
    log("   - 'Địa chỉ gửi hóa đơn' → Email nhận")
    log("=" * 70)
    
    # Kiểm tra cấu hình email
    if not config.email_configured():
        log("\n❌ CẢNH BÁO: Chưa cấu hình SENDER_EMAIL/SENDER_PASSWORD trong .env")
        log("   Vui lòng cấu hình email trước khi gửi mail thật.")
        log("   Hoặc dùng: python main_excel_preview.py để test trước")
        return
    
    log(f"\n📧 Email gửi đi: {config.SENDER_EMAIL}")
    log("\n⚠️  CẢNH BÁO: Chế độ này sẽ GỬI EMAIL THẬT!")
    log("⚠️  Đảm bảo bạn đã chạy Preview Mode và kiểm tra kỹ trước!")
    
    response = input("\n✋ Xác nhận gửi email thật? (yes/no): ")
    if response.lower() != 'yes':
        log("❌ Đã hủy")
        log("💡 TIP: Chạy python main_excel_preview.py để test trước")
        return
    
    # Khởi tạo và chạy Master Agent Excel (Production Mode)
    master = MasterAgentExcel()
    result = master.execute_full_pipeline(
        excel_file=None,  # Dùng mặc định từ config
        send_email=True,  # GỬI EMAIL THẬT
        output_file=None
    )
    
    # Kết quả
    if result.get("success", 0) > 0:
        log("\n🎉 Hoàn thành! Đã gửi email thành công cho một số đơn hàng.")
    else:
        log("\n⚠️  Không có đơn nào được gửi email thành công.")
    
    log("\n" + "=" * 70)
    log("✅ HOÀN TẤT")
    log("=" * 70)


if __name__ == "__main__":
    main()
