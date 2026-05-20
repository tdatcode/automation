# 🤖 EasyInvoice Automation Bot

Bot tự động hóa các tác vụ trên hệ thống EasyInvoice:
- **Tải hóa đơn PDF** và gửi email cho khách hàng
- **Tạo hóa đơn mới** từ file Excel

## 📁 Cấu trúc dự án

```
botmail/
├── main_excel_preview.py        # Tải PDF + xuất danh sách mail (không gửi)
├── main_excel_test_mail.py      # Tải PDF + gửi mail test cho chính mình
├── main_excel_send.py           # Tải PDF + gửi mail thật cho khách
├── main_create_invoice.py       # Tạo hóa đơn mới trên EasyInvoice
├── invoice_agents/
│   ├── config.py                # Cấu hình chung
│   ├── easyinvoice_agent.py     # Agent tải hóa đơn PDF
│   ├── create_invoice_agent.py  # Agent tạo hóa đơn mới
│   ├── mail_agent.py            # Agent gửi email
│   ├── master_agent_excel.py    # Agent điều phối (tải + gửi mail)
│   └── utils.py                 # Hàm tiện ích
├── excel/                       # File Excel đầu vào (gửi mail)
├── exceltaohoadon/              # File Excel đầu vào (tạo hóa đơn)
├── downloads/                   # PDF đã tải (tự động tạo)
├── emailgui/                    # Danh sách mail output (tự động tạo)
├── chrome-debug.bat             # Mở Chrome với remote debugging
├── test_agents.py               # Test các agent
├── .env.example                 # Mẫu cấu hình
└── requirements.txt             # Dependencies
```

## 🚀 Cài đặt

### 1. Cài Python dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Tạo file `.env`

Copy `.env.example` thành `.env` và điền thông tin:

```env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

## 📧 Chức năng 1: Tải hóa đơn & Gửi mail

### Quy trình

1. Đọc file Excel (`excel/HoaDon.xlsx`) chứa danh sách khách hàng
2. Tìm kiếm từng khách hàng trên EasyInvoice (theo tên)
3. So sánh tổng tiền để chọn đúng hóa đơn
4. Nếu có nhiều kết quả → Chọn hóa đơn có "Hợp lệ" ở cột KQ CQT
5. Tải file PDF hóa đơn
6. Gửi email (hoặc xuất danh sách)

### File Excel cần có các cột

| Cột | Mô tả |
|-----|--------|
| Tên công ty/nhà thuốc/quầy thuốc | Tên khách hàng |
| Địa chỉ gửi hóa đơn | Email nhận |
| Tổng tiền | Số tiền để so sánh |

### Cách chạy

```bash
# Preview (không gửi mail, chỉ tải PDF + xuất Excel)
python main_excel_preview.py

# Gửi mail test cho chính mình (kiểm tra trước)
python main_excel_test_mail.py

# Gửi mail thật cho khách hàng
python main_excel_send.py
```

## 📝 Chức năng 2: Tạo hóa đơn mới

### Quy trình

1. Đọc file Excel (`exceltaohoadon/TaoHoaDon.xlsx`, sheet "Details")
2. Nhóm sản phẩm theo ID hóa đơn (cùng ID = cùng 1 hóa đơn)
3. Với mỗi hóa đơn:
   - Click "Tạo mới"
   - Điền Mã số thuế → Lấy thông tin khách hàng
   - Chọn VAT %
   - Điền từng sản phẩm (tên, số lượng, đơn giá)
   - Lưu dữ liệu

### File Excel cần có các cột (sheet "Details")

| Cột | Mô tả |
|-----|--------|
| ID hóa đơn | Nhóm SP cùng 1 hóa đơn |
| Mã số thuế | MST khách hàng |
| Tên sản phẩm | Tên hàng hóa |
| Giá đơn vị | Đơn giá |
| SL đặt | Số lượng |
| vat | % thuế (0, 5, 8, 10) |

### Cách chạy

```bash
python main_create_invoice.py
```

## 🌐 Kết nối Chrome

Bot hỗ trợ 2 cách:

### Cách 1: Mở Chrome mới (mặc định)
Script tự mở Chrome mới → Bạn đăng nhập → Nhấn ENTER.

### Cách 2: Kết nối Chrome đã mở
Mở Chrome trước với remote debugging:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"
```

Hoặc double-click file `chrome-debug.bat`.

Khi script hỏi "Kết nối vào Chrome đã mở?" → Nhập `y`.

## ⚙️ Cấu hình (.env)

```env
# Email (Gmail SMTP)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password

# EasyInvoice
EASYINVOICE_INDEX_URL=https://0312670722.easyinvoice.com.vn/EInvoice/Index

# File paths
EXCEL_FILE=excel/HoaDon.xlsx
DOWNLOAD_FOLDER=downloads
EXCEL_MAIL_PREVIEW_FILE=emailgui/danh_sach_mail.xlsx
```

## 🧪 Test

```bash
python test_agents.py
```

## 📋 Yêu cầu hệ thống

- Python 3.10+
- Google Chrome
- Windows 10/11
