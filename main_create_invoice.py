"""
Main script - TẠO HÓA ĐƠN TỰ ĐỘNG trên EasyInvoice.

Quy trình:
1. Đọc file Excel từ thư mục exceltaohoadon/ (sheet "Details")
2. Nhóm sản phẩm theo ID hóa đơn
3. Mở trang EasyInvoice, đăng nhập
4. Với mỗi hóa đơn: Tạo mới → Điền MST → Lấy thông tin → Chọn VAT → Điền SP → Lưu

Cách chạy:
    python main_create_invoice.py
"""

import os
from typing import List, Dict, Any

import pandas as pd
from playwright.sync_api import sync_playwright

from invoice_agents import config
from invoice_agents.create_invoice_agent import CreateInvoiceAgent
from invoice_agents.utils import log


def read_invoices_from_excel(excel_path: str) -> List[Dict[str, Any]]:
    """Đọc file Excel (sheet 'Details') và nhóm sản phẩm theo ID hóa đơn."""
    log(f"📋 Đọc file Excel: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, sheet_name="Details", dtype={"Mã số thuế": str})
        log(f"  ✓ Đọc sheet 'Details': {len(df)} dòng")
    except Exception:
        df = pd.read_excel(excel_path, dtype={"Mã số thuế": str})
        log(f"  ✓ Đọc sheet mặc định: {len(df)} dòng")
    
    # Đọc sheet Summary để lấy Tổng tiền theo ID hóa đơn
    total_amount_map = {}
    try:
        df_summary = pd.read_excel(excel_path, sheet_name="Summary")
        for _, row in df_summary.iterrows():
            inv_id = row.get("ID hóa đơn")
            total = row.get("Tổng tiền")
            if not pd.isna(inv_id) and not pd.isna(total):
                total_amount_map[str(int(inv_id))] = float(str(total).replace(",", "").replace(".", "").strip())
        log(f"  ✓ Đọc sheet 'Summary': {len(total_amount_map)} tổng tiền")
    except Exception as e:
        log(f"  ⚠️  Không đọc được sheet Summary: {e}")
    
    invoices = {}
    
    for idx, row in df.iterrows():
        invoice_id = row.get("ID hóa đơn")
        tax_code = row.get("Mã số thuế")
        product_name = row.get("Tên sản phẩm")
        price = row.get("Giá đơn vị")
        quantity = row.get("SL đặt")
        vat = row.get("vat")
        
        if pd.isna(invoice_id) or pd.isna(tax_code) or pd.isna(product_name):
            continue
        
        invoice_id = str(int(invoice_id))
        # MST: giữ nguyên dạng text, không chuyển sang số (giữ số 0 ở đầu)
        tax_code_raw = str(tax_code).strip()
        if tax_code_raw.endswith(".0"):
            tax_code = tax_code_raw[:-2]  # Bỏ .0 nhưng giữ nguyên chuỗi
        else:
            tax_code = tax_code_raw
        product_name = str(product_name).strip()
        
        try:
            price = float(str(price).replace(",", "").replace(".", "").strip())
        except (ValueError, TypeError):
            price = 0
        
        try:
            quantity = int(float(str(quantity).strip()))
        except (ValueError, TypeError):
            quantity = 1
        
        try:
            vat = int(float(str(vat).replace("%", "").strip()))
        except (ValueError, TypeError):
            vat = 10
        
        if invoice_id not in invoices:
            invoices[invoice_id] = {
                "invoice_id": invoice_id,
                "tax_code": tax_code,
                "vat": vat,
                "total_amount": total_amount_map.get(invoice_id),
                "products": []
            }
        
        invoices[invoice_id]["products"].append({
            "name": product_name,
            "quantity": quantity,
            "price": price,
        })
    
    result = list(invoices.values())
    log(f"✅ Tổng cộng {len(result)} hóa đơn cần tạo")
    for i, inv in enumerate(result):
        log(f"  [{i+1}] MST: {inv['tax_code']} | VAT: {inv['vat']}% | {len(inv['products'])} SP")
    
    return result


def main():
    log("=" * 70)
    log("🚀 BOT TẠO HÓA ĐƠN TỰ ĐỘNG - EasyInvoice")
    log("=" * 70)
    
    config.ensure_dirs()
    
    # Bước 1: Đọc file Excel (sheet "Details")
    log("\n📋 Bước 1: Đọc file Excel")
    excel_path = config.EXCEL_FILE
    log(f"  ✓ File: {excel_path} (sheet 'Details')")
    
    invoices = read_invoices_from_excel(excel_path)
    
    if not invoices:
        log("❌ Không có hóa đơn nào để tạo")
        return
    
    # Tóm tắt
    log(f"\n📊 Tóm tắt: {len(invoices)} hóa đơn")
    for i, inv in enumerate(invoices, 1):
        log(f"  [{i}] MST: {inv['tax_code']} | VAT: {inv['vat']}% | {len(inv['products'])} SP")
        for p in inv["products"]:
            log(f"      - {p['name']} x{p['quantity']} @ {p['price']:,.0f}")
    
    log("=" * 70)
    response = input("\n✋ Tiếp tục tạo hóa đơn? (y/n): ")
    if response.lower() != 'y':
        log("❌ Đã hủy")
        return
    
    # Bước 2: Mở Chrome
    log("\n🌐 Bước 2: Kết nối Chrome")
    
    with sync_playwright() as p:
        browser = None
        page = None
        
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            log("  ✅ Đã kết nối vào Chrome")
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                page = context.new_page()
            else:
                context = browser.new_context(accept_downloads=True)
                page = context.new_page()
        except Exception:
            log("  ❌ Không tìm thấy Chrome đang chạy với remote debugging.")
            log("")
            log("  👉 Hãy đóng Chrome hiện tại, rồi mở lại bằng cách:")
            log("     Double-click file 'chrome-debug.bat'")
            log("     Hoặc chạy lệnh:")
            log('     "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
            log("")
            input("  ✋ Nhấn ENTER sau khi đã mở Chrome")
            
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                log("  ✅ Đã kết nối vào Chrome")
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    page = context.new_page()
                else:
                    context = browser.new_context(accept_downloads=True)
                    page = context.new_page()
            except Exception as e:
                log(f"  ❌ Vẫn không kết nối được: {e}")
                return
        
        # Bước 3: Mở trang EasyInvoice
        log("\n📝 Bước 3: Mở trang EasyInvoice")
        page.goto(config.EASYINVOICE_INDEX_URL)
        page.wait_for_timeout(3000)
        
        # Kiểm tra đăng nhập
        if "login" in page.url.lower():
            log("  ⚠️  Chưa đăng nhập! Vui lòng đăng nhập.")
            input("  ✋ ENTER khi đã đăng nhập EasyInvoice")
        else:
            log("  ✅ Đã đăng nhập sẵn!")
        
        input("  ✋ Nhấn ENTER để bắt đầu tạo hóa đơn")
        
        # Bước 4: Tạo từng hóa đơn
        log("\n📝 Bước 4: Tạo hóa đơn")
        log("=" * 70)
        
        agent = CreateInvoiceAgent(page)
        stats = {"total": len(invoices), "success": 0, "failed": 0}
        
        for i, invoice in enumerate(invoices, 1):
            log(f"\n{'=' * 70}")
            log(f"📦 HÓA ĐƠN {i}/{len(invoices)} - MST: {invoice['tax_code']}")
            log(f"{'=' * 70}")
            
            result = agent.create_invoice(invoice)
            
            if result["success"]:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            # Chờ giữa các hóa đơn
            if i < len(invoices):
                log(f"\n⏳ Chờ 3s trước hóa đơn tiếp theo...")
                page.wait_for_timeout(3000)
        
        # Thống kê
        log("\n" + "=" * 70)
        log("📊 KẾT QUẢ")
        log("=" * 70)
        log(f"  Tổng: {stats['total']}")
        log(f"  ✅ Thành công: {stats['success']}")
        log(f"  ❌ Lỗi: {stats['failed']}")
        log("=" * 70)
        log("\n💡 Chrome vẫn mở để bạn kiểm tra kết quả.")
        log("✅ HOÀN TẤT!")


if __name__ == "__main__":
    main()
