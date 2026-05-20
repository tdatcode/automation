"""
Main script - Xử lý từ Excel - PREVIEW MODE (KHÔNG GỬI MAIL).

Quy trình:
1. Đọc file Excel (Tên khách hàng + Email)
2. Tìm trên EasyInvoice theo tên khách hàng
3. Click icon mắt (Xem) → Tải PDF
4. Đổi tên PDF theo tên khách hàng
5. KHÔNG GỬI EMAIL - Chỉ xuất Excel

Cách chạy:
    python main_excel_preview.py

Cấu hình:
    - KHÔNG CẦN SENDER_EMAIL và SENDER_PASSWORD
    - File Excel mặc định: excel/HoaDon.xlsx (hoặc EXCEL_FILE trong .env)
    - Cột cần thiết:
      * "Tên công ty/nhà thuốc/quầy thuốc" → Tên khách hàng
      * "Địa chỉ gửi hóa đơn" → Email nhận
"""

from invoice_agents.master_agent_excel import MasterAgentExcel
from invoice_agents import config
from invoice_agents.utils import log


def main():
    """Chạy Master Agent Excel với Preview Mode (KHÔNG GỬI MAIL)."""
    
    log("=" * 70)
    log("🚀 MASTER AGENT EXCEL - PREVIEW MODE")
    log("=" * 70)
    log("📋 Quy trình:")
    log("  1. Đọc file Excel")
    log("  2. Tìm hóa đơn trên EasyInvoice")
    log("  3. Tải PDF và đổi tên theo khách hàng")
    log("  4. ⚠️  KHÔNG GỬI MAIL - Chỉ xuất Excel")
    log("=" * 70)
    log(f"📄 File Excel: {config.EXCEL_FILE}")
    log("📄 Cột cần thiết:")
    log("   - 'Tên công ty/nhà thuốc/quầy thuốc' → Tên khách hàng")
    log("   - 'Địa chỉ gửi hóa đơn' → Email nhận")
    log("=" * 70)
    
    log("\n💡 TIP: Đây là chế độ PREVIEW - không gửi email thật")
    log("💡 Kết quả sẽ được xuất ra file Excel để kiểm tra")
    log("💡 Khi sẵn sàng gửi mail thật, dùng: python main_excel_send.py")
    
    response = input("\n✋ Tiếp tục? (y/n): ")
    if response.lower() != 'y':
        log("❌ Đã hủy")
        return
    
    # Khởi tạo và chạy Master Agent Excel (Preview Mode)
    master = MasterAgentExcel()
    result = master.execute_full_pipeline(
        excel_file=None,  # Dùng mặc định từ config
        send_email=False,  # KHÔNG gửi email
        output_file=None   # Dùng mặc định
    )
    
    # Kết quả
    if result.get("success", 0) > 0:
        log("\n🎉 Hoàn thành! Đã xử lý thành công một số đơn hàng.")
        log(f"📄 Kiểm tra file Excel: {config.EXCEL_MAIL_PREVIEW_FILE}")
    else:
        log("\n⚠️  Không có đơn nào được xử lý thành công.")
    
    log("\n" + "=" * 70)
    log("✅ HOÀN TẤT - Kiểm tra file Excel để xem danh sách mail cần gửi")
    log("=" * 70)


if __name__ == "__main__":
    main()
