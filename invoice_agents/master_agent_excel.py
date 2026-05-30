"""
Master Agent Excel - AI Agent lớn xử lý từ file Excel.

Quy trình đơn giản:
1. Đọc file Excel (Tên khách hàng + Email)
2. Tìm trên EasyInvoice theo tên khách hàng
3. Click icon mắt (Xem) → Tải PDF
4. Đổi tên PDF theo tên khách hàng
5. Gửi email (hoặc xuất Excel nếu Preview)

Không cần ThuocSi - Chỉ cần Excel + EasyInvoice
"""

import os
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page, sync_playwright
import pandas as pd

from invoice_agents import config
from invoice_agents.easyinvoice_agent import EasyInvoiceAgent
from invoice_agents.mail_agent import MailAgent
from invoice_agents.utils import log


class MasterAgentExcel:
    """
    AI Agent lớn - xử lý từ file Excel.
    
    Chứa 2 AI Agents nhỏ:
    - EasyInvoiceAgent: Tìm và tải hóa đơn PDF
    - MailAgent: Gửi email
    
    Không cần ThuocSiAgent nữa!
    """
    
    def __init__(self):
        self.name = "MasterAgentExcel"
        self.easyinvoice_agent: Optional[EasyInvoiceAgent] = None
        self.mail_agent: Optional[MailAgent] = None
        log(f"🤖🤖 [{self.name}] Khởi tạo Master Agent Excel")
    
    def execute_full_pipeline(
        self,
        excel_file: Optional[str] = None,
        send_email: bool = True,
        output_file: Optional[str] = None,
        skip_confirmation: bool = False,  # Thêm tham số này cho GUI
        test_mode: bool = False  # Thêm tham số test_mode
    ) -> Dict[str, Any]:
        """
        Thực thi toàn bộ quy trình từ Excel.
        
        Args:
            excel_file: Đường dẫn file Excel (None = dùng mặc định)
            send_email: True = gửi email, False = chỉ xuất Excel
            output_file: File Excel output nếu send_email=False
            skip_confirmation: True = bỏ qua input() cho GUI
            test_mode: True = gửi cho chính mình (test), False = gửi cho khách hàng
            
        Returns:
            Dict với thống kê kết quả
        """
        if test_mode:
            mode_text = "🧪 TEST MODE - GỬI CHO CHÍNH MÌNH"
        elif send_email:
            mode_text = "📧 GỬI EMAIL THẬT"
        else:
            mode_text = "PREVIEW (KHÔNG GỬI EMAIL)"
        
        log(f"🚀 [{self.name}] BẮT ĐẦU QUY TRÌNH - {mode_text}")
        log("=" * 70)
        
        config.ensure_dirs()
        
        # Kiểm tra email config nếu cần gửi mail
        if send_email and not config.email_configured():
            log(f"❌ [{self.name}] Chưa cấu hình SENDER_EMAIL/SENDER_PASSWORD")
            return {"success": False, "error": "Email not configured"}
        
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "results": [],
            "preview_rows": []
        }
        
        # Đọc Excel
        excel_path = excel_file or config.EXCEL_FILE
        invoices = self._load_invoices_from_excel(excel_path)
        
        if not invoices:
            log(f"❌ [{self.name}] Không có dòng nào trong Excel")
            return stats
        
        stats["total"] = len(invoices)
        log(f"\n✅ [{self.name}] Sẽ xử lý {len(invoices)} đơn hàng")
        
        with sync_playwright() as p:
            # Kết nối vào Chrome đang chạy (port 9222)
            # Nếu chưa có, hướng dẫn người dùng mở Chrome
            log(f"\n📍 [{self.name}] Kết nối Chrome...")
            
            browser = None
            page_easyinvoice = None
            
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                log("✅ Đã kết nối vào Chrome")
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    page_easyinvoice = context.new_page()
                else:
                    context = browser.new_context(accept_downloads=True)
                    page_easyinvoice = context.new_page()
            except Exception:
                log("❌ Không tìm thấy Chrome đang chạy với remote debugging.")
                log("")
                log("👉 Hãy đóng Chrome hiện tại, rồi mở lại bằng cách:")
                log("   Double-click file 'chrome-debug.bat'")
                log("   Hoặc chạy lệnh:")
                log('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
                log("")
                input("✋ Nhấn ENTER sau khi đã mở Chrome")
                
                try:
                    browser = p.chromium.connect_over_cdp("http://localhost:9222")
                    log("✅ Đã kết nối vào Chrome")
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                        page_easyinvoice = context.new_page()
                    else:
                        context = browser.new_context(accept_downloads=True)
                        page_easyinvoice = context.new_page()
                except Exception as e:
                    log(f"❌ Vẫn không kết nối được: {e}")
                    return stats
            try:
                # Khởi tạo agents
                self.easyinvoice_agent = EasyInvoiceAgent(page_easyinvoice)
                self.mail_agent = MailAgent()
                
                # Mở EasyInvoice
                log(f"\n📍 [{self.name}] Mở EasyInvoice...")
                page_easyinvoice.goto(config.EASYINVOICE_INDEX_URL)
                page_easyinvoice.wait_for_timeout(3000)
                
                # Kiểm tra đăng nhập
                if "login" in page_easyinvoice.url.lower():
                    log("⚠️  Chưa đăng nhập! Vui lòng đăng nhập.")
                    if not skip_confirmation:
                        input("✋ ENTER khi đã đăng nhập EasyInvoice")
                    else:
                        # GUI mode: Sẽ hiển thị popup yêu cầu xác nhận
                        log("⏳ Vui lòng đăng nhập EasyInvoice trong Chrome...")
                        log("💡 Sau khi đăng nhập xong, click OK trong popup")
                else:
                    log("✅ Đã đăng nhập sẵn!")
                    if not skip_confirmation:
                        input("✋ ENTER để bắt đầu xử lý")
                    else:
                        # GUI mode: Sẽ hiển thị popup xác nhận
                        log("💡 Click OK để bắt đầu xử lý...")
                
                # Xử lý từng đơn
                for i, invoice in enumerate(invoices, 1):
                    log(f"\n{'=' * 70}")
                    log(f"📦 [{self.name}] ĐƠN {i}/{len(invoices)} - {invoice['pharmacy_name']}")
                    log(f"{'=' * 70}")
                    
                    result = self._process_single_invoice(
                        invoice,
                        page_easyinvoice,
                        send_email,
                        test_mode  # Truyền test_mode
                    )
                    
                    stats["results"].append(result)
                    
                    # Thống kê
                    if result["status"] == "SUCCESS":
                        stats["success"] += 1
                        if not send_email:
                            stats["preview_rows"].append({
                                "Dia_chi_email_nhan": result["receiver_email"],
                                "Ten_nha_thuoc": result["pharmacy_name"],
                                "Trang_thai": "Sẵn sàng gửi"
                            })
                    else:
                        stats["failed"] += 1
                        if not send_email:
                            stats["preview_rows"].append({
                                "Dia_chi_email_nhan": result.get("receiver_email", ""),
                                "Ten_nha_thuoc": result["pharmacy_name"],
                                "Trang_thai": f"Lỗi: {result['error']}"
                            })
                    
                    # Chờ giữa các đơn để tránh xử lý đồng loạt
                    if i < len(invoices):
                        wait_time = 3
                        log(f"\n⏳ Chờ {wait_time}s trước khi xử lý đơn tiếp theo...")
                        page_easyinvoice.wait_for_timeout(wait_time * 1000)
                
            finally:
                # Không đóng Chrome - để người dùng tiếp tục sử dụng
                pass
        
        # Xuất Excel nếu preview mode
        if not send_email:
            output_path = output_file or config.EXCEL_MAIL_PREVIEW_FILE
            self._export_to_excel(stats["preview_rows"], output_path)
            self._print_statistics(stats, send_email, output_path)
        else:
            self._print_statistics(stats, send_email)
        
        return stats
    
    def _load_invoices_from_excel(self, excel_path: str) -> List[Dict[str, Any]]:
        """
        Đọc file Excel và lấy danh sách đơn hàng.
        
        Cột cần thiết:
        - "Tên công ty/nhà thuốc/quầy thuốc" → Tên khách hàng
        - "Mã số thuế" → MST để tìm kiếm (dạng text, giữ số 0 ở đầu)
        - "Địa chỉ gửi hóa đơn" → Email nhận
        - "Tổng tiền" → Tổng tiền để so sánh (optional)
        """
        log(f"📋 [{self.name}] Đọc file Excel: {excel_path}")
        
        try:
            # Đọc Excel với dtype để giữ MST dạng text
            df = pd.read_excel(
                excel_path, 
                sheet_name="Summary",
                dtype={"Mã số thuế": str}  # Đọc MST dạng text để giữ số 0 ở đầu
            )
            log(f"  ✓ Đọc sheet 'Summary': {len(df)} dòng")
            log(f"  ✓ Các cột: {df.columns.tolist()}")
            
            # Kiểm tra các cột cần thiết
            required_cols = ["Tên công ty/nhà thuốc/quầy thuốc", "Mã số thuế", "Địa chỉ gửi hóa đơn"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                log(f"❌ [{self.name}] Thiếu các cột: {missing_cols}")
                return []
            
            # Kiểm tra cột "Tổng tiền"
            has_total_amount = "Tổng tiền" in df.columns
            if has_total_amount:
                log(f"  ✓ Có cột 'Tổng tiền' - sẽ so sánh với web")
            else:
                log(f"  ⚠️  Không có cột 'Tổng tiền' - bỏ qua so sánh")
            
            invoices = []
            for idx, row in df.iterrows():
                # Bỏ qua dòng đầu tiên (header thứ 2 hoặc dòng trống)
                if idx == 0:
                    continue
                
                # Lấy email
                email = row.get("Địa chỉ gửi hóa đơn")
                if pd.isna(email) or str(email).strip() == "":
                    log(f"  ⚠️  Dòng {idx}: Không có email, bỏ qua")
                    continue
                
                # Lấy tên khách hàng
                pharmacy_name = row.get("Tên công ty/nhà thuốc/quầy thuốc")
                if pd.isna(pharmacy_name) or str(pharmacy_name).strip() == "":
                    log(f"  ⚠️  Dòng {idx}: Không có tên khách hàng, bỏ qua")
                    continue
                
                # Lấy MST (giữ dạng text để không mất số 0 ở đầu)
                tax_code = row.get("Mã số thuế")
                if pd.isna(tax_code) or str(tax_code).strip() == "" or str(tax_code).strip().lower() == "nan":
                    log(f"  ⚠️  Dòng {idx}: Không có MST, bỏ qua")
                    continue
                
                # Chuyển MST thành chuỗi, loại bỏ phần .0 nếu có (nhưng giữ số 0 ở đầu)
                tax_code_str = str(tax_code).strip()
                # Nếu MST kết thúc bằng .0 (do Excel tự động format), loại bỏ phần .0
                if tax_code_str.endswith('.0'):
                    tax_code_str = tax_code_str[:-2]
                
                # Lấy tổng tiền (nếu có)
                total_amount = None
                if has_total_amount:
                    amount_val = row.get("Tổng tiền")
                    if not pd.isna(amount_val):
                        try:
                            total_amount = float(amount_val)
                        except Exception:
                            pass
                
                invoices.append({
                    "row_index": idx,
                    "pharmacy_name": str(pharmacy_name).strip(),
                    "tax_code": tax_code_str,
                    "receiver_email": str(email).strip(),
                    "total_amount": total_amount
                })
                
                if total_amount:
                    log(f"  ✓ Dòng {idx}: {pharmacy_name} (MST: {tax_code_str}) → {email} (Tổng: {total_amount:,.0f})")
                else:
                    log(f"  ✓ Dòng {idx}: {pharmacy_name} (MST: {tax_code_str}) → {email}")
            
            log(f"✅ [{self.name}] Tổng cộng {len(invoices)} đơn hợp lệ")
            return invoices
            
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi đọc Excel: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _process_single_invoice(
        self,
        invoice: Dict[str, Any],
        page_easyinvoice: Page,
        send_email: bool,
        test_mode: bool = False  # Thêm tham số test_mode
    ) -> Dict[str, Any]:
        """
        Xử lý 1 đơn hàng: tìm trên EasyInvoice, tải PDF, gửi email (hoặc preview).
        
        Args:
            test_mode: True = gửi cho chính mình, False = gửi cho khách hàng
        """
        pharmacy_name = invoice["pharmacy_name"]
        tax_code = invoice["tax_code"]
        receiver_email = invoice["receiver_email"]
        total_amount = invoice.get("total_amount")
        
        result = {
            "pharmacy_name": pharmacy_name,
            "receiver_email": receiver_email,
            "status": "PENDING",
            "pdf_path": "",
            "email_sent": False,
            "error": ""
        }
        
        try:
            # Bước 1: Tìm và tải PDF từ EasyInvoice
            log(f"🔍 [{self.name}] Tìm hóa đơn cho: {pharmacy_name}")
            log(f"  🏢 MST: {tax_code}")
            if total_amount:
                log(f"  💰 Tổng tiền: {total_amount:,.0f} VNĐ")
            
            # Sử dụng tên khách hàng làm order_id (vì không có order_id từ Excel)
            ei_result = self.easyinvoice_agent.execute_task(
                order_id=pharmacy_name,  # Dùng tên làm order_id
                customer_name=pharmacy_name,
                customer_tax_code=tax_code,  # Truyền MST để tìm kiếm
                total_amount=total_amount
            )
            
            if not ei_result["success"]:
                result["status"] = "ERROR"
                result["error"] = ei_result.get("error", "Lỗi EasyInvoice")
                log(f"❌ [{self.name}] Lỗi EasyInvoice: {result['error']}")
                return result
            
            result["pdf_path"] = ei_result["pdf_path"]
            log(f"✅ [{self.name}] Đã tải PDF: {result['pdf_path']}")
            
            # Bước 2: Gửi email hoặc preview
            if send_email:
                # Xác định email nhận
                if test_mode:
                    # TEST MODE: Gửi cho chính mình
                    actual_receiver = config.SENDER_EMAIL
                    log(f"🧪 [{self.name}] TEST MODE - Gửi cho chính mình: {actual_receiver}")
                    log(f"   (Email thật của khách hàng: {receiver_email})")
                else:
                    # REAL MODE: Gửi cho khách hàng
                    actual_receiver = receiver_email
                    log(f"📧 [{self.name}] Gửi email đến: {actual_receiver}")
                
                # Tạo email message
                from email.message import EmailMessage
                import smtplib
                
                msg = EmailMessage()
                
                # Tiêu đề email
                if test_mode:
                    msg["Subject"] = f"🧪 TEST - Hóa đơn điện tử - {pharmacy_name}"
                else:
                    msg["Subject"] = f"Hóa đơn điện tử - {pharmacy_name}"
                
                msg["From"] = config.SENDER_EMAIL
                msg["To"] = actual_receiver
                
                # Nội dung email
                email_body = f"""
Kính gửi Quý khách {pharmacy_name},

Công ty xin gửi hóa đơn điện tử đính kèm.

Quý khách vui lòng kiểm tra file PDF trong email này.

Trân trọng.

---
Công ty Lucky Star
"""
                
                # Thêm thông tin test nếu là test mode
                if test_mode:
                    email_body = f"""
🧪 ĐÂY LÀ EMAIL TEST - KHÔNG GỬI CHO KHÁCH HÀNG

Email này được gửi để kiểm tra trước khi gửi thật.

---
THÔNG TIN KHÁCH HÀNG:
- Tên: {pharmacy_name}
- MST: {tax_code}
- Email thật: {receiver_email}

---
NỘI DUNG EMAIL THẬT SẼ NHƯ SAU:

{email_body}
"""
                
                msg.set_content(email_body)
                
                # Đính kèm PDF
                with open(ei_result["pdf_path"], "rb") as f:
                    file_data = f.read()
                
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(ei_result["pdf_path"]),
                )
                
                # Gửi qua SMTP
                try:
                    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as smtp:
                        smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                        smtp.send_message(msg)
                    
                    result["status"] = "SUCCESS"
                    result["email_sent"] = True
                    
                    if test_mode:
                        log(f"✅ [{self.name}] Đã gửi email TEST thành công đến: {actual_receiver}")
                    else:
                        log(f"✅ [{self.name}] Đã gửi email thành công đến: {actual_receiver}")
                    
                except Exception as e:
                    result["status"] = "MAIL_ERROR"
                    result["error"] = f"Lỗi gửi email: {str(e)}"
                    log(f"❌ [{self.name}] {result['error']}")
            else:
                # Preview mode - không gửi email
                result["status"] = "SUCCESS"
                log(f"✅ [{self.name}] PREVIEW - Không gửi email")
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            log(f"❌ [{self.name}] Lỗi xử lý đơn: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def _export_to_excel(self, preview_rows: List[Dict[str, Any]], output_path: str) -> None:
        """Xuất danh sách mail ra Excel (preview mode)."""
        log(f"\n💾 [{self.name}] Xuất Excel...")
        
        if not preview_rows:
            log(f"⚠️  [{self.name}] Không có dòng nào để xuất")
            df = pd.DataFrame(columns=["Dia_chi_email_nhan", "Ten_nha_thuoc", "Trang_thai"])
            df.to_excel(output_path, index=False)
            log(f"📄 Đã tạo file rỗng: {output_path}")
            return
        
        df = pd.DataFrame(preview_rows)
        df = df[["Dia_chi_email_nhan", "Ten_nha_thuoc", "Trang_thai"]]
        df.to_excel(output_path, index=False)
        
        log(f"✅ [{self.name}] Đã xuất {len(df)} dòng vào: {output_path}")
        log("\n" + "=" * 70)
        log("📊 PREVIEW DANH SÁCH MAIL CẦN GỬI:")
        log("=" * 70)
        print(df.to_string(index=False))
        log("=" * 70)
    
    def _print_statistics(
        self,
        stats: Dict[str, Any],
        send_email: bool,
        output_path: Optional[str] = None
    ) -> None:
        """In thống kê kết quả."""
        mode_text = "GỬI EMAIL" if send_email else "PREVIEW MODE"
        
        log("\n" + "=" * 70)
        log(f"📊 [{self.name}] THỐNG KÊ KẾT QUẢ ({mode_text})")
        log("=" * 70)
        log(f"Tổng số đơn:        {stats['total']}")
        log(f"✅ Thành công:      {stats['success']}")
        log(f"❌ Lỗi:             {stats['failed']}")
        log("=" * 70)
        
        if not send_email and output_path:
            log(f"📄 File Excel: {output_path}")
            log("=" * 70)
        
        # In chi tiết các đơn thành công
        if stats['success'] > 0:
            log("\n✅ CÁC ĐƠN THÀNH CÔNG:")
            for r in stats['results']:
                if r['status'] == 'SUCCESS':
                    log(f"  • {r['pharmacy_name']}")
                    log(f"    → Email: {r['receiver_email']}")
                    if send_email:
                        log(f"    → Đã gửi: ✅")
        
        # In chi tiết các đơn lỗi
        if stats['failed'] > 0:
            log("\n❌ CÁC ĐƠN LỖI:")
            for r in stats['results']:
                if r['status'] != 'SUCCESS':
                    log(f"  • {r['pharmacy_name']}: {r['error']}")
        
        log("\n" + "=" * 70)
        if not send_email:
            log("💡 TIP: Kiểm tra file Excel để xem danh sách đầy đủ")
            log("💡 Khi sẵn sàng gửi mail thật, dùng: python main_excel_send.py")
        log("=" * 70)
