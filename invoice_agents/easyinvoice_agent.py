"""
EasyInvoice Agent - AI Agent nhỏ để xử lý hóa đơn từ EasyInvoice.

Nhiệm vụ:
1. Tìm kiếm hóa đơn theo Mã số thuế (MST)
2. Đọc cột "Tên khách hàng" từ bảng
3. Click icon mắt (Xem) để mở chi tiết hóa đơn
4. Tải file PDF hóa đơn
5. Đổi tên file PDF theo tên khách hàng
"""

import os
from typing import Optional, Dict, Any

from playwright.sync_api import Page

from invoice_agents import config
from invoice_agents.utils import log, pdf_filename_for_customer


class EasyInvoiceAgent:
    """AI Agent chuyên xử lý hóa đơn từ EasyInvoice."""
    
    def __init__(self, page: Page):
        self.page = page
        self.name = "EasyInvoiceAgent"
        log(f"🤖 [{self.name}] Khởi tạo agent")
    
    def execute_task(self, order_id: str, customer_name: str, customer_tax_code: str, total_amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Thực thi nhiệm vụ chính: tìm và tải hóa đơn.
        
        Args:
            order_id: ID đơn hàng
            customer_name: Tên khách hàng (dùng để đặt tên file PDF)
            customer_tax_code: Mã số thuế (MST) để tìm kiếm
            total_amount: Tổng tiền để so sánh (optional)
        
        Returns:
            Dict với keys: success, pdf_path, customer_name, error
        """
        log(f"🎯 [{self.name}] Bắt đầu xử lý Order {order_id}")
        log(f"  🏢 MST: {customer_tax_code}")
        if total_amount:
            log(f"  💰 Tổng tiền cần tìm: {total_amount:,.0f} VNĐ")
        
        try:
            # Bước 1: Tìm kiếm hóa đơn theo MST
            self.search_invoice_by_tax_code(customer_tax_code)
            
            # Bước 2: Tìm hàng phù hợp (so sánh tổng tiền + KQ CQT)
            row_index = self.find_matching_invoice_row(customer_name, total_amount)
            
            if row_index is None:
                return {
                    "success": False,
                    "pdf_path": None,
                    "customer_name": customer_name,
                    "error": "Không tìm thấy hóa đơn phù hợp"
                }
            
            # Bước 3: Click icon mắt và tải PDF
            pdf_path = self.view_and_download_invoice(order_id, customer_name, row_index)
            
            if pdf_path:
                return {
                    "success": True,
                    "pdf_path": pdf_path,
                    "customer_name": customer_name,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "pdf_path": None,
                    "customer_name": customer_name,
                    "error": "Không tải được PDF"
                }
                
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "pdf_path": None,
                "customer_name": customer_name,
                "error": str(e)
            }
    
    def search_invoice_by_tax_code(self, tax_code: str) -> None:
        """
        Tìm kiếm hóa đơn theo Mã số thuế (MST).
        Dán MST vào ô "Mã số thuế" (id=CodeTax) và click nút "Tìm kiếm".
        """
        log(f"🔍 [{self.name}] Tìm kiếm theo MST: {tax_code}")

        try:
            # Ô "Mã số thuế": id=CodeTax
            tax_code_input = self.page.locator('#CodeTax')
            
            if not tax_code_input.is_visible(timeout=5000):
                log(f"❌ [{self.name}] Không tìm thấy ô 'Mã số thuế' (#CodeTax)")
                return

            log(f"  ✓ Tìm thấy ô 'Mã số thuế' (#CodeTax)")
            
            # Xóa nội dung cũ
            log(f"  → Xóa nội dung cũ...")
            tax_code_input.click()
            self.page.wait_for_timeout(500)
            tax_code_input.fill("", timeout=3000)
            self.page.wait_for_timeout(500)
            
            # Dán MST mới (chuyển sang string để giữ số 0 ở đầu)
            log(f"  → Dán MST mới: {tax_code}")
            tax_code_input.fill(str(tax_code), timeout=5000)
            self.page.wait_for_timeout(1000)
            log(f"  ✓ Đã dán MST: {tax_code}")
            
            # Click nút "Tìm kiếm"
            clicked = False
            try:
                btn = self.page.locator('button:has-text("Tìm kiếm")').first
                if btn.is_visible(timeout=3000):
                    log(f"  → Click nút 'Tìm kiếm'...")
                    btn.click()
                    clicked = True
                    log(f"  ✓ Đã click nút 'Tìm kiếm'")
            except Exception:
                pass
            
            if not clicked:
                log(f"  ⚠️  Không tìm thấy nút, thử Enter")
                tax_code_input.press("Enter")
            
            # Chờ kết quả tải
            log(f"  → Chờ kết quả tải...")
            self.page.wait_for_timeout(3000)
            log(f"✅ [{self.name}] Đã tìm kiếm MST: {tax_code}")
                
        except Exception as e:
            log(f"⚠️  [{self.name}] Lỗi tìm kiếm: {e}")
            import traceback
            traceback.print_exc()
                
        except Exception as e:
            log(f"⚠️  [{self.name}] Lỗi tìm kiếm: {e}")
            import traceback
            traceback.print_exc()
    
    def find_matching_invoice_row(self, customer_name: str, total_amount: Optional[float] = None) -> Optional[int]:
        """
        Tìm hàng hóa đơn phù hợp trong bảng kết quả.
        
        Logic:
        1. Tìm tất cả các hàng trong bảng kết quả chính
        2. Nếu có total_amount, so sánh với cột "Tổng tiền" trên web
        3. Nếu có ≥2 hàng trùng → Chỉ lấy hàng có "Hợp lệ" ở cột "KQ CQT"
        4. Trả về index của hàng phù hợp (0-based)
        
        Cấu trúc bảng EasyInvoice:
        STT(0) | Số(1) | Ikey(2) | Mã KH(3) | Tên khách hàng(4) | KH xem(5) | 
        Ngày tạo(6) | ?(7) | Tổng tiền(8) | Trạng thái(9) | Người PH(10) | 
        Mã CQT(11) | KQ CQT(12) | Xem(13) | Sửa(14) | Xóa(15) | Gửi mail(16)
        
        Returns:
            Index của hàng phù hợp, hoặc None nếu không tìm thấy
        """
        log(f"🔎 [{self.name}] Tìm hàng phù hợp trong bảng kết quả")
        
        try:
            # Chờ bảng tải xong
            self.page.wait_for_timeout(2000)
            
            # Đọc tất cả các hàng trong tbody (bảng kết quả chính)
            rows = self.page.locator("table tbody tr").all()
            log(f"  ✓ Tìm thấy {len(rows)} hàng trong bảng")
            
            if len(rows) == 0:
                log(f"❌ [{self.name}] Không có hàng nào trong bảng kết quả")
                return None
            
            matching_rows = []
            
            for row_idx, row in enumerate(rows):
                try:
                    cells = row.locator("td").all()
                    
                    if len(cells) < 13:
                        continue
                    
                    # Đọc tên khách hàng (cột 4) - chỉ để log
                    name = (cells[4].text_content() or "").strip()
                    log(f"  → Hàng {row_idx}: Tên='{name}'")
                    
                    # Vì đã tìm kiếm theo tên rồi, kết quả bảng chỉ có hàng khớp
                    # Không cần so sánh tên nữa, chỉ cần so sánh tổng tiền + KQ CQT
                    
                    # Đọc tổng tiền (cột 8 - "Tổng tiền")
                    amount = None
                    try:
                        amount_text = (cells[8].text_content() or "").strip()
                        amount = self._parse_amount(amount_text)
                        log(f"    💰 Tổng tiền web: {amount:,.0f}" if amount else "    💰 Tổng tiền: N/A")
                    except Exception:
                        pass
                    
                    # Đọc KQ CQT (cột 12 - "KQ CQT")
                    kq_cqt = ""
                    try:
                        kq_cqt = (cells[12].text_content() or "").strip()
                        log(f"    📋 KQ CQT: '{kq_cqt}'")
                    except Exception:
                        pass
                    
                    # So sánh tổng tiền (nếu có)
                    amount_match = True
                    if total_amount and amount:
                        diff_percent = abs(amount - total_amount) / total_amount * 100
                        amount_match = diff_percent < 1.0
                        log(f"    {'✅' if amount_match else '❌'} So sánh tổng tiền: Excel={total_amount:,.0f} vs Web={amount:,.0f} ({diff_percent:.2f}% sai lệch)")
                    
                    if amount_match:
                        matching_rows.append({
                            "index": row_idx,
                            "name": name,
                            "amount": amount,
                            "kq_cqt": kq_cqt
                        })
                        
                except Exception as e:
                    log(f"  ⚠️  Lỗi đọc hàng {row_idx}: {e}")
                    continue
            
            # Xử lý kết quả
            if len(matching_rows) == 0:
                log(f"❌ [{self.name}] Không tìm thấy hàng nào phù hợp")
                return None
            elif len(matching_rows) == 1:
                log(f"✅ [{self.name}] Tìm thấy 1 hàng phù hợp: hàng {matching_rows[0]['index']}")
                return matching_rows[0]["index"]
            else:
                # Có ≥2 hàng trùng → Chỉ lấy hàng có "Hợp lệ"
                log(f"⚠️  [{self.name}] Tìm thấy {len(matching_rows)} hàng trùng khớp")
                for row in matching_rows:
                    if row["kq_cqt"] and "hợp lệ" in row["kq_cqt"].lower():
                        log(f"✅ [{self.name}] Chọn hàng {row['index']} (có 'Hợp lệ' ở KQ CQT)")
                        return row["index"]
                
                # Nếu không có hàng nào "Hợp lệ" → Lấy hàng đầu tiên
                log(f"⚠️  [{self.name}] Không có hàng nào 'Hợp lệ', lấy hàng đầu tiên: {matching_rows[0]['index']}")
                return matching_rows[0]["index"]
                
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi tìm hàng phù hợp: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _normalize_name(self, name: str) -> str:
        """Chuẩn hóa tên để so sánh."""
        import unicodedata
        import re
        
        # Loại bỏ dấu tiếng Việt
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Chuyển thành chữ thường, loại bỏ ký tự đặc biệt
        name = re.sub(r'[^a-z0-9\s]', '', name.lower())
        
        # Loại bỏ khoảng trắng thừa
        name = ' '.join(name.split())
        
        return name
    
    def _parse_amount(self, amount_text: str) -> Optional[float]:
        """Parse số tiền từ text.
        
        Web dùng dấu chấm phân cách hàng nghìn: 175.000
        Excel dùng dấu phẩy phân cách hàng nghìn: 175,000
        Cả hai đều = 175000
        """
        try:
            import re
            # Loại bỏ dấu chấm và dấu phẩy (đều là phân cách hàng nghìn)
            amount_text = amount_text.replace('.', '').replace(',', '')
            # Loại bỏ ký tự không phải số
            amount_text = re.sub(r'[^\d]', '', amount_text)
            if amount_text:
                return float(amount_text)
        except Exception:
            pass
        return None
    
    def extract_customer_name(self) -> Optional[str]:
        """Đọc tên khách hàng từ cột 'Tên khách hàng' trong bảng."""
        log(f"📖 [{self.name}] Đọc tên khách hàng từ bảng")


        try:
            header_cells = self.page.locator("thead th").all()
            col_idx = None
            for i, th in enumerate(header_cells):
                txt = (th.text_content() or "").lower()
                if "tên khách" in txt or "khách hàng" in txt:
                    col_idx = i
                    log(f"  ✓ Tìm thấy cột 'Tên khách hàng' tại vị trí {i}")
                    break
            
            if col_idx is not None:
                cell = self.page.locator("tbody tr").first.locator("td").nth(col_idx)
                name = cell.text_content()
                if name:
                    name = name.strip()
                    if name:
                        log(f"✅ [{self.name}] Tên khách hàng: {name}")
                        return name
        except Exception as e:
            log(f"⚠️  [{self.name}] Không đọc được tên khách: {e}")
        return None
    
    def view_and_download_invoice(self, order_id: str, customer_name: str, row_index: int) -> Optional[str]:
        """
        Click icon mắt (Xem) ở hàng chỉ định để mở chi tiết hóa đơn và tải PDF.
        Đổi tên file PDF theo tên khách hàng.
        
        Args:
            order_id: ID đơn hàng
            customer_name: Tên khách hàng
            row_index: Index của hàng cần click (0-based)
        """
        log(f"👁️  [{self.name}] Mở chi tiết và tải hóa đơn - Hàng {row_index}")

        try:
            # Bước 1: Click icon mắt (Xem) ở cột 13 của hàng chỉ định
            log(f"  → Tìm hàng {row_index}...")
            self.page.wait_for_timeout(1000)
            
            row = self.page.locator("table tbody tr").nth(row_index)
            cells = row.locator("td").all()
            
            clicked = False
            
            # Click trực tiếp vào icon mắt trong cột 13 (cột Xem)
            if len(cells) > 13:
                try:
                    view_cell = cells[13]
                    eye_icon = view_cell.locator("i.fa-eye").first
                    if eye_icon.is_visible(timeout=3000):
                        log(f"  → Click icon mắt (cột 13)...")
                        eye_icon.click()
                        clicked = True
                        log(f"  ✓ Đã click icon mắt ở hàng {row_index}")
                except Exception:
                    pass
            
            # Fallback: tìm icon mắt trong toàn hàng
            if not clicked:
                # Tìm nút Xem trong hàng này (icon mắt: class="fa fa-eye")
                view_selectors = [
                    'i.fa-eye',           # Icon mắt chính xác
                    'a:has(i.fa-eye)',    # Link chứa icon mắt
                    '[title="Xem"]',
                    'button:has-text("Xem")',
                    'a:has-text("Xem")',
                ]
                
                for selector in view_selectors:
                    try:
                        btn = row.locator(selector).first
                        if btn.is_visible(timeout=3000):
                            log(f"  → Click '{selector}'...")
                            btn.click()
                            clicked = True
                            log(f"  ✓ Đã click nút Xem ở hàng {row_index}")
                            break
                    except Exception:
                        continue
            
            if not clicked:
                log(f"⚠️  [{self.name}] Không tìm thấy icon mắt, thử click vào hàng")
                row.click()
            
            # Chờ modal mở
            log(f"  → Chờ modal mở...")
            self.page.wait_for_timeout(3000)
            
            # Bước 2: Tải PDF
            log(f"📥 [{self.name}] Tải file PDF...")
            try:
                # Thử tìm nút "Tải hóa đơn" trước
                try:
                    download_btn = self.page.locator("text=Tải hóa đơn").first
                    if download_btn.is_visible(timeout=5000):
                        log(f"  → Click 'Tải hóa đơn'...")
                        download_btn.click()
                        self.page.wait_for_timeout(1000)
                except Exception:
                    log(f"  ⚠️  Không tìm thấy nút 'Tải hóa đơn', thử trực tiếp 'Tải tệp PDF'")
                
                # Click "Tải tệp PDF"
                log(f"  → Click 'Tải tệp PDF'...")
                with self.page.expect_download(timeout=30000) as download_info:
                    pdf_btn = self.page.locator("text=Tải tệp PDF").first
                    pdf_btn.click()
                
                download = download_info.value
                
                # Bước 3: Đổi tên file theo tên khách hàng
                pdf_name = pdf_filename_for_customer(order_id, customer_name)
                pdf_path = os.path.join(config.DOWNLOAD_FOLDER, pdf_name)
                download.save_as(pdf_path)
                
                log(f"✅ [{self.name}] Đã lưu PDF: {pdf_path}")
                
            except Exception as e:
                log(f"❌ [{self.name}] Lỗi tải PDF: {e}")
                import traceback
                traceback.print_exc()
                return None
            
            # Bước 4: Đóng popup bằng cách click vào phần trống bên ngoài
            log(f"🔙 [{self.name}] Đóng chi tiết hóa đơn")
            try:
                # Chờ một chút để download hoàn tất
                self.page.wait_for_timeout(1000)
                
                # Cách 1: Click vào phần trống bên ngoài modal (góc trên trái)
                log(f"  → Click vào phần trống...")
                self.page.mouse.click(50, 50)
                self.page.wait_for_timeout(1500)
                log(f"  ✓ Đã click vào phần trống")
                
                # Cách 2: Nếu vẫn còn modal, thử click overlay
                try:
                    overlay = self.page.locator(".modal-backdrop, .overlay, [class*='backdrop']").first
                    if overlay.is_visible(timeout=2000):
                        log(f"  → Click vào overlay...")
                        overlay.click()
                        self.page.wait_for_timeout(1000)
                        log(f"  ✓ Đã click vào overlay")
                except Exception:
                    pass
                
                # Cách 3: Thử nhấn ESC
                log(f"  → Nhấn ESC...")
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(1000)
                
                log(f"✅ [{self.name}] Đã đóng chi tiết, sẵn sàng xử lý đơn tiếp theo")
                
            except Exception as e:
                log(f"⚠️  [{self.name}] Lỗi khi đóng chi tiết: {e}")
                log(f"  → Thử reload trang để reset")
                try:
                    self.page.reload()
                    self.page.wait_for_timeout(3000)
                    log(f"  ✓ Đã reload trang")
                except Exception:
                    pass
            
            return pdf_path
            
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi tải PDF: {e}")
            import traceback
            traceback.print_exc()
            return None


# ============================================================================
# Legacy functions - giữ lại để tương thích với code cũ
# ============================================================================

def search_easyinvoice(page_ei: Page, pharmacy_name: str) -> None:
    """Legacy function - sử dụng EasyInvoiceAgent thay thế."""
    agent = EasyInvoiceAgent(page_ei)
    agent.search_invoice(pharmacy_name)


def extract_customer_name_from_easyinvoice(page_ei: Page) -> Optional[str]:
    """Legacy function - sử dụng EasyInvoiceAgent thay thế."""
    agent = EasyInvoiceAgent(page_ei)
    return agent.extract_customer_name()


def download_pdf_from_open_detail(
    page_ei: Page,
    order_id: str,
    customer_label: str,
) -> Optional[str]:
    """Legacy function - khi detail đã mở sẵn."""
    log(f"📥 [EasyInvoiceAgent] DOWNLOAD (detail đã mở) — Order {order_id}")
    try:
        agent = EasyInvoiceAgent(page_ei)
        ei_name = agent.extract_customer_name()
        file_label = ei_name or customer_label
        try:
            page_ei.click("text=Tải hóa đơn")
            page_ei.wait_for_timeout(1000)
        except Exception:
            pass
        with page_ei.expect_download() as download_info:
            page_ei.click("text=Tải tệp PDF")
        download = download_info.value
        pdf_name = pdf_filename_for_customer(order_id, file_label)
        pdf_path = os.path.join(config.DOWNLOAD_FOLDER, pdf_name)
        download.save_as(pdf_path)
        log(f"✅ PDF saved: {pdf_path}")
        return pdf_path
    except Exception as e:
        log(f"❌ Download error: {e}")
        return None


def auto_view_and_download(
    page_ei: Page,
    order_id: str,
    customer_label: str,
    tax_code: str = "",
) -> Optional[str]:
    """
    Legacy function - sử dụng EasyInvoiceAgent thay thế.
    
    DEPRECATED: Hàm này chỉ để tương thích với code cũ.
    Nên sử dụng EasyInvoiceAgent.execute_task() trực tiếp.
    """
    agent = EasyInvoiceAgent(page_ei)
    # Nếu không có tax_code, dùng customer_label làm fallback
    if not tax_code:
        tax_code = customer_label
    result = agent.execute_task(order_id, customer_label, tax_code)
    return result.get("pdf_path")
