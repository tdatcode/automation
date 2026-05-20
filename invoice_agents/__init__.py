"""
Invoice automation: AI Agents architecture - Excel Mode.

Kiến trúc đơn giản:
- MasterAgentExcel: Agent lớn điều phối (Excel + EasyInvoice + Mail)
- EasyInvoiceAgent: Agent nhỏ lấy hóa đơn PDF
- MailAgent: Agent nhỏ gửi email

Chỉ cần Excel + EasyInvoice - KHÔNG CẦN ThuocSi!
"""

from invoice_agents.master_agent_excel import MasterAgentExcel
from invoice_agents.easyinvoice_agent import EasyInvoiceAgent
from invoice_agents.mail_agent import MailAgent

__all__ = [
    "MasterAgentExcel",
    "EasyInvoiceAgent",
    "MailAgent",
]
