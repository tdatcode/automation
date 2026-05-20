"""
Script test các AI Agents riêng lẻ.

Dùng để kiểm tra từng agent hoạt động đúng không trước khi chạy toàn bộ pipeline.
"""

from invoice_agents import config
from invoice_agents.utils import log


def test_imports():
    """Test import các agents."""
    log("🧪 Test 1: Import các agents")
    try:
        from invoice_agents import (
            MasterAgentExcel,
            EasyInvoiceAgent,
            MailAgent
        )
        log("✅ Import thành công tất cả agents")
        log(f"  - MasterAgentExcel: {MasterAgentExcel}")
        log(f"  - EasyInvoiceAgent: {EasyInvoiceAgent}")
        log(f"  - MailAgent: {MailAgent}")
        return True
    except Exception as e:
        log(f"❌ Lỗi import: {e}")
        return False


def test_config():
    """Test cấu hình."""
    log("\n🧪 Test 2: Kiểm tra cấu hình")
    try:
        log(f"  - THUOCSI_LOGIN_URL: {config.THUOCSI_LOGIN_URL}")
        log(f"  - EASYINVOICE_INDEX_URL: {config.EASYINVOICE_INDEX_URL}")
        log(f"  - DOWNLOAD_FOLDER: {config.DOWNLOAD_FOLDER}")
        log(f"  - EMAIL_DOMAIN: {config.EMAIL_DOMAIN}")
        
        if config.email_configured():
            log(f"  - Email đã cấu hình: ✅")
            log(f"  - SENDER_EMAIL: {config.SENDER_EMAIL}")
        else:
            log(f"  - Email chưa cấu hình: ⚠️")
        
        log("✅ Cấu hình OK")
        return True
    except Exception as e:
        log(f"❌ Lỗi cấu hình: {e}")
        return False


def test_mail_agent():
    """Test MailAgent (không gửi thật)."""
    log("\n🧪 Test 3: MailAgent - Tạo địa chỉ routing")
    try:
        from invoice_agents import MailAgent
        
        agent = MailAgent()
        
        # Test tạo email routing
        test_order_id = "TEST123"
        email = agent.generate_routing_email(test_order_id)
        
        log(f"  - Order ID: {test_order_id}")
        log(f"  - Email routing: {email}")
        
        expected = f"{test_order_id}.{config.EMAIL_DOMAIN}"
        if email == expected:
            log("✅ MailAgent hoạt động đúng")
            return True
        else:
            log(f"❌ Email không đúng. Mong đợi: {expected}, Nhận được: {email}")
            return False
            
    except Exception as e:
        log(f"❌ Lỗi MailAgent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test các hàm utils."""
    log("\n🧪 Test 4: Utils - Verify tên khách hàng")
    try:
        from invoice_agents.utils import cross_verify, normalize_text, sanitize_filename_component
        
        # Test normalize
        text1 = "Nhà Thuốc ABC"
        text2 = "nha thuoc abc"
        norm1 = normalize_text(text1)
        norm2 = normalize_text(text2)
        log(f"  - Normalize '{text1}' → '{norm1}'")
        log(f"  - Normalize '{text2}' → '{norm2}'")
        
        # Test cross verify
        result = cross_verify("Nhà Thuốc ABC", "nha thuoc abc")
        log(f"  - Cross verify 'Nhà Thuốc ABC' vs 'nha thuoc abc': {result}")
        
        # Test sanitize filename
        filename = sanitize_filename_component("Nhà Thuốc ABC/XYZ")
        log(f"  - Sanitize 'Nhà Thuốc ABC/XYZ' → '{filename}'")
        
        log("✅ Utils hoạt động đúng")
        return True
        
    except Exception as e:
        log(f"❌ Lỗi Utils: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_master_agent_init():
    """Test khởi tạo MasterAgentExcel."""
    log("\n🧪 Test 5: Khởi tạo MasterAgentExcel")
    try:
        from invoice_agents import MasterAgentExcel
        
        # Test MasterAgentExcel
        master = MasterAgentExcel()
        log(f"  - MasterAgentExcel name: {master.name}")
        log(f"  - EasyInvoiceAgent: {master.easyinvoice_agent}")
        log(f"  - MailAgent: {master.mail_agent}")
        
        log("✅ MasterAgentExcel khởi tạo thành công")
        return True
        
    except Exception as e:
        log(f"❌ Lỗi khởi tạo: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Chạy tất cả tests."""
    log("=" * 70)
    log("🧪 BẮT ĐẦU TEST CÁC AI AGENTS")
    log("=" * 70)
    
    results = []
    
    results.append(("Import Agents", test_imports()))
    results.append(("Config", test_config()))
    results.append(("MailAgent", test_mail_agent()))
    results.append(("Utils", test_utils()))
    results.append(("MasterAgent Init", test_master_agent_init()))
    
    # Tổng kết
    log("\n" + "=" * 70)
    log("📊 KẾT QUẢ TEST")
    log("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"{status} - {name}")
    
    log("=" * 70)
    log(f"Tổng kết: {passed}/{total} tests passed")
    
    if passed == total:
        log("🎉 TẤT CẢ TESTS ĐỀU PASS!")
    else:
        log("⚠️  MỘT SỐ TESTS FAILED - Vui lòng kiểm tra lại")
    
    log("=" * 70)


if __name__ == "__main__":
    main()
