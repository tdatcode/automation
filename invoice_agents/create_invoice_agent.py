"""
Agent tạo hóa đơn trên EasyInvoice.

Quy trình cho mỗi hóa đơn:
1. Click nút "Tạo mới" (#crtInvoice)
2. Điền Mã số thuế (#CusTaxCode) → Click "Lấy thông tin" (#taxFinder)
3. Cuộn xuống bảng sản phẩm
4. Chọn VAT % (#VATRate)
5. Điền từng sản phẩm: Tên (.ui-autocomplete-input), SL (.quantity), Đơn giá (.price)
6. Click "Lưu dữ liệu" (#submitBtn)
"""

from typing import Dict, Any, List, Optional

from playwright.sync_api import Page

from invoice_agents.utils import log


class CreateInvoiceAgent:
    """Agent tự động tạo hóa đơn trên EasyInvoice."""
    
    def __init__(self, page: Page):
        self.page = page
        self.name = "CreateInvoiceAgent"
        log(f"🤖 [{self.name}] Khởi tạo agent")
    
    def create_invoice(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo 1 hóa đơn trên EasyInvoice.
        
        Args:
            invoice: {
                "invoice_id": str,
                "tax_code": str,
                "vat": int (0, 5, 8, 10),
                "total_amount": float (tổng tiền từ Excel Summary),
                "products": [{"name": str, "quantity": int, "price": float}]
            }
        
        Returns:
            {"success": bool, "error": str}
        """
        tax_code = invoice["tax_code"]
        vat = invoice["vat"]
        products = invoice["products"]
        expected_total = invoice.get("total_amount")  # Tổng tiền từ Excel
        
        log(f"🎯 [{self.name}] Tạo hóa đơn: MST={tax_code}, VAT={vat}%, {len(products)} sản phẩm")
        if expected_total:
            log(f"  💰 Tổng tiền Excel: {expected_total:,.0f}")
        
        try:
            # Bước 1: Click nút "Tạo mới" (id="crtInvoice")
            log(f"  → Click nút 'Tạo mới'...")
            create_btn = self.page.locator("#crtInvoice")
            create_btn.click()
            self.page.wait_for_timeout(4000)
            log(f"  ✓ Đã mở form tạo hóa đơn")
            
            # Bước 2: Điền Mã số thuế
            log(f"  → Điền Mã số thuế: {tax_code}")
            tax_input = self.page.locator("#CusTaxCode")
            tax_input.click()
            self.page.wait_for_timeout(500)
            tax_input.fill(tax_code)
            self.page.wait_for_timeout(1000)
            
            # Bước 3: Click nút "Lấy thông tin"
            log(f"  → Click 'Lấy thông tin'...")
            tax_finder_btn = self.page.locator("#taxFinder")
            tax_finder_btn.click()
            self.page.wait_for_timeout(4000)
            log(f"  ✓ Đã lấy thông tin khách hàng")
            
            # Bước 4: Cuộn xuống bảng sản phẩm
            log(f"  → Cuộn xuống bảng sản phẩm...")
            table_section = self.page.locator(".form-group.table-responsive").first
            table_section.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1500)
            log(f"  ✓ Đã cuộn tới bảng sản phẩm")
            
            # Bước 5: Chọn VAT %
            log(f"  → Chọn VAT: {vat}%")
            vat_select = self.page.locator("#VATRate")
            vat_value = str(vat) if vat >= 0 else "-1"
            vat_select.select_option(value=vat_value)
            self.page.wait_for_timeout(1000)
            log(f"  ✓ Đã chọn VAT: {vat}%")
            
            # Bước 6: Điền từng sản phẩm
            for idx, product in enumerate(products):
                log(f"  → Sản phẩm {idx+1}/{len(products)}: {product['name']}")
                self._fill_product_row(idx, product)
                self.page.wait_for_timeout(1500)
            
            # Click ra ngoài để số tiền được cập nhật
            self.page.mouse.click(50, 50)
            self.page.wait_for_timeout(2000)
            
            # Bước 7: Kiểm tra và sửa tổng tiền thuế (nếu cần)
            if expected_total:
                self._adjust_vat_amount(expected_total)
            
            # Bước 8: Click "Lưu dữ liệu"
            log(f"  → Click 'Lưu dữ liệu'...")
            self.page.wait_for_timeout(2000)
            submit_btn = self.page.locator("#submitBtn")
            submit_btn.click()
            self.page.wait_for_timeout(4000)
            
            log(f"✅ [{self.name}] Đã tạo hóa đơn thành công! MST={tax_code}")
            
            return {"success": True, "error": None}
            
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi tạo hóa đơn: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _adjust_vat_amount(self, expected_total: float) -> None:
        """
        So sánh tổng tiền dịch vụ (mAmount) trên web với tổng tiền Excel.
        Nếu khác → Sửa ô "Tổng tiền thuế" (mVATAmount).
        
        Logic:
        1. Đọc mAmount (tổng tiền dịch vụ trên web)
        2. So sánh với tổng tiền Excel
        3. Nếu khác: Tổng tiền thuế mới = Tổng tiền Excel - mTotal (tổng tiền trước thuế)
        4. Sửa mVATAmount
        """
        log(f"  → Kiểm tra tổng tiền...")
        
        try:
            # Chờ số tiền được load xong
            self.page.wait_for_timeout(1500)
            
            # Đọc "Tổng tiền dịch vụ" (mAmount) trên web
            amount_input = self.page.locator("#mAmount").first
            amount_text = amount_input.input_value()
            web_total = self._parse_money(amount_text)
            log(f"    💰 Tổng tiền dịch vụ (web): {web_total:,.0f}")
            log(f"    💰 Tổng tiền (Excel): {expected_total:,.0f}")
            
            # So sánh
            if abs(web_total - expected_total) < 1:
                log(f"    ✅ Tổng tiền khớp!")
                return
            
            # Không bằng → Sửa tổng tiền thuế
            log(f"    ⚠️  Sai lệch! Cần sửa...")
            
            # Đọc "Tổng tiền trước thuế" (mTotal)
            total_input = self.page.locator("#mTotal").first
            total_text = total_input.input_value()
            total_before_vat = self._parse_money(total_text)
            log(f"    💰 Tổng tiền trước thuế (web): {total_before_vat:,.0f}")
            
            # Tính tổng tiền thuế mới = Tổng tiền Excel - Tổng tiền trước thuế
            new_vat_amount = expected_total - total_before_vat
            log(f"    💰 Tổng tiền thuế mới: {expected_total:,.0f} - {total_before_vat:,.0f} = {new_vat_amount:,.0f}")
            
            # Sửa ô "Tổng tiền thuế" (mVATAmount)
            vat_amount_input = self.page.locator("#mVATAmount").first
            vat_amount_input.click()
            self.page.wait_for_timeout(500)
            vat_amount_input.fill("")
            self.page.wait_for_timeout(300)
            vat_amount_input.fill(str(int(new_vat_amount)))
            self.page.wait_for_timeout(1000)
            
            # Click ra ngoài để cập nhật
            self.page.keyboard.press("Tab")
            self.page.wait_for_timeout(1000)
            
            log(f"    ✅ Đã sửa tổng tiền thuế → Tổng dịch vụ = {expected_total:,.0f}")
            
        except Exception as e:
            log(f"    ⚠️  Lỗi kiểm tra tổng tiền: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_money(self, text: str) -> float:
        """Parse số tiền từ text (bỏ dấu chấm/phẩy phân cách)."""
        import re
        text = str(text).replace(".", "").replace(",", "")
        text = re.sub(r'[^\d]', '', text)
        return float(text) if text else 0

    def _fill_product_row(self, row_index: int, product: Dict[str, Any]) -> None:
        """Điền thông tin 1 sản phẩm vào hàng trong bảng."""
        name = product["name"]
        quantity = product["quantity"]
        price = product["price"]
        
        # Lấy bảng sản phẩm (form-group table-responsive)
        table_section = self.page.locator(".form-group.table-responsive").first
        
        # Nếu không phải hàng đầu tiên, thêm hàng mới
        if row_index > 0:
            self._add_new_product_row()
            self.page.wait_for_timeout(2000)
        
        # Điền tên sản phẩm (ô autocomplete BÊN TRONG bảng, cột thứ 4)
        log(f"    → Tên: {name}")
        rows = table_section.locator("tbody tr").all()
        if row_index < len(rows):
            current_row = rows[row_index]
            name_input = current_row.locator("td").nth(3).locator("input.ui-autocomplete-input").first
            name_input.click()
            self.page.wait_for_timeout(500)
            name_input.fill(name)
            self.page.wait_for_timeout(2000)
            
            # Nếu có autocomplete dropdown, chọn item đầu tiên hoặc nhấn ESC
            try:
                autocomplete = self.page.locator(".ui-autocomplete .ui-menu-item").first
                if autocomplete.is_visible(timeout=2000):
                    autocomplete.click()
                    self.page.wait_for_timeout(1000)
                    log(f"    ✓ Chọn từ autocomplete")
                else:
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(500)
            except Exception:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
        
        # Điền số lượng (BÊN TRONG bảng)
        log(f"    → SL: {quantity}")
        qty_inputs = table_section.locator("input.quantity.align-right.textr").all()
        if row_index < len(qty_inputs):
            qty_input = qty_inputs[row_index]
            qty_input.click()
            self.page.wait_for_timeout(500)
            qty_input.fill(str(quantity))
            self.page.wait_for_timeout(800)
        
        # Điền đơn giá (BÊN TRONG bảng)
        log(f"    → Giá: {price:,.0f}")
        price_inputs = table_section.locator("input.price.align-right.textr").all()
        if row_index < len(price_inputs):
            price_input = price_inputs[row_index]
            price_input.click()
            self.page.wait_for_timeout(500)
            price_input.fill(str(int(price)))
            self.page.wait_for_timeout(800)
        
        log(f"    ✓ Đã điền sản phẩm {row_index+1}")
    
    def _add_new_product_row(self) -> None:
        """Thêm hàng sản phẩm mới trong bảng."""
        log(f"    → Thêm hàng mới...")
        try:
            add_selectors = [
                'button:has-text("Thêm")',
                'a:has-text("Thêm")',
                'button:has(i.fa-plus)',
                'a:has(i.fa-plus)',
                '#addRow',
                '.add-row',
            ]
            
            for selector in add_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        self.page.wait_for_timeout(1500)
                        log(f"    ✓ Đã thêm hàng mới")
                        return
                except Exception:
                    continue
            
            log(f"    ⚠️  Không tìm thấy nút thêm hàng")
        except Exception as e:
            log(f"    ⚠️  Lỗi thêm hàng: {e}")
