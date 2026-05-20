"""
Mail Agent - AI Agent nhỏ để xử lý gửi email.

Nhiệm vụ:
1. Tạo địa chỉ email routing theo format ThuocSi
2. Soạn nội dung email
3. Đính kèm file PDF hóa đơn
4. Gửi email qua Gmail SMTP
"""

import os
from email.message import EmailMessage
import smtplib
from typing import Dict, Any

from invoice_agents import config
from invoice_agents.utils import log


class MailAgent:
    """AI Agent chuyên xử lý gửi email."""
    
    def __init__(self):
        self.name = "MailAgent"
        log(f"🤖 [{self.name}] Khởi tạo agent")
    
    def execute_task(
        self,
        pdf_path: str,
        order_id: str,
        customer_name: str
    ) -> Dict[str, Any]:
        """
        Thực thi nhiệm vụ chính: gửi email với hóa đơn đính kèm.
        
        Args:
            pdf_path: Đường dẫn file PDF
            order_id: Mã đơn hàng
            customer_name: Tên khách hàng
            
        Returns:
            Dict với keys: success, receiver_email, error
        """
        log(f"🎯 [{self.name}] Bắt đầu gửi email cho Order {order_id}")
        
        try:
            # Bước 1: Tạo địa chỉ email routing
            receiver_email = self.generate_routing_email(order_id)
            
            # Bước 2: Kiểm tra cấu hình email
            if not self._check_email_config():
                return {
                    "success": False,
                    "receiver_email": receiver_email,
                    "error": "Chưa cấu hình SENDER_EMAIL/SENDER_PASSWORD"
                }
            
            # Bước 3: Gửi email
            success = self.send_email_with_attachment(
                pdf_path=pdf_path,
                order_id=order_id,
                customer_name=customer_name,
                receiver_email=receiver_email
            )
            
            if success:
                return {
                    "success": True,
                    "receiver_email": receiver_email,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "receiver_email": receiver_email,
                    "error": "Gửi email thất bại"
                }
                
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi: {e}")
            return {
                "success": False,
                "receiver_email": "",
                "error": str(e)
            }
    
    def generate_routing_email(self, order_id: str) -> str:
        """
        Tạo địa chỉ email routing theo format ThuocSi.
        Format: <Order_ID>.<domain>@hoadon.thuocsi.vn
        """
        email = f"{order_id}.{config.EMAIL_DOMAIN}"
        log(f"📧 [{self.name}] Email routing: {email}")
        return email
    
    def _check_email_config(self) -> bool:
        """Kiểm tra xem đã cấu hình email chưa."""
        if not config.email_configured():
            log(f"❌ [{self.name}] Chưa cấu hình SENDER_EMAIL/SENDER_PASSWORD trong .env")
            return False
        return True
    
    def send_email_with_attachment(
        self,
        pdf_path: str,
        order_id: str,
        customer_name: str,
        receiver_email: str
    ) -> bool:
        """
        Gửi email với file PDF đính kèm.
        
        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        log(f"📬 [{self.name}] Gửi email đến: {receiver_email}")
        
        try:
            # Tạo email message
            msg = EmailMessage()
            msg["Subject"] = f"Hóa đơn điện tử - Đơn hàng {order_id}"
            msg["From"] = config.SENDER_EMAIL
            msg["To"] = receiver_email

            # Nội dung email
            msg.set_content(
                f"""
Kính gửi Quý khách {customer_name},

Công ty xin gửi hóa đơn điện tử đính kèm.

Quý khách vui lòng kiểm tra file PDF trong email này.

Trân trọng.

---
Công ty Lucky Star
Đơn hàng: {order_id}
"""
            )

            # Đính kèm file PDF
            with open(pdf_path, "rb") as f:
                file_data = f.read()

            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path),
            )

            # Gửi qua Gmail SMTP
            with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as smtp:
                smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                smtp.send_message(msg)
            
            log(f"✅ [{self.name}] Đã gửi email thành công")
            return True
            
        except Exception as e:
            log(f"❌ [{self.name}] Lỗi gửi email: {e}")
            return False


# ============================================================================
# Legacy functions - giữ lại để tương thích với code cũ
# ============================================================================

def generate_email_address(order_id: str) -> str:
    """Legacy function - sử dụng MailAgent thay thế."""
    agent = MailAgent()
    return agent.generate_routing_email(order_id)


def send_email(
    pdf_path: str,
    order_id: str,
    pharmacy_name: str,
    receiver_email: str,
) -> bool:
    """Legacy function - sử dụng MailAgent thay thế."""
    agent = MailAgent()
    result = agent.send_email_with_attachment(
        pdf_path=pdf_path,
        order_id=order_id,
        customer_name=pharmacy_name,
        receiver_email=receiver_email
    )
    return result
