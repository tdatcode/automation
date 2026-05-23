# 🤖 EasyInvoice Automation Bot

Bot tự động hóa các tác vụ trên hệ thống EasyInvoice:
- **Tải hóa đơn PDF** và gửi email cho khách hàng (tìm theo Mã số thuế)
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
│   ├── easyinvoice_agent.py     # Agent tải hóa đơn PDF (tìm theo MST)
│   ├── create_invoice_agent.py  # Agent tạo hóa đơn mới
│   ├── mail_agent.py            # Agent gửi email
│   ├── master_agent_excel.py    # Agent điều phối (tải + gửi mail)
│   └── utils.py                 # Hàm tiện ích
├── excel/
│   └── HoaDon.xlsx             # File Excel chung (2 sheet)
├── downloads/                   # PDF đã tải (tự động tạo)
├── emailgui/                    # Danh sách mail output (tự động tạo)
├── chrome-debug.bat             # Mở Chrome với remote debugging
├── test_agents.py               # Test các agent
├── .env.example                 # Mẫu cấu hình
└── requirements.txt             # Dependencies
```

## 📊 File Excel

Cả 2 tác vụ dùng **cùng 1 file Excel** (`excel/HoaDon.xlsx`) với 2 sheet:

| Sheet | Tác vụ | Mô tả |
|-------|--------|--------|
| **Summary** | Gửi mail | Thông tin khách hàng + email + MST |
| **Details** | Tạo hóa đơn | Chi tiết sản phẩm từng đơn |

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

1. Đọc file Excel (`excel/HoaDon.xlsx`, sheet "Summary") chứa danh sách khách hàng
2. **Tìm kiếm từng khách hàng trên EasyInvoice theo Mã số thuế (MST)**
3. So sánh tổng tiền để chọn đúng hóa đơn
4. Nếu có nhiều kết quả → Chọn hóa đơn có "Hợp lệ" ở cột KQ CQT
5. Tải file PDF hóa đơn (đặt tên theo tên khách hàng)
6. Gửi email (hoặc xuất danh sách)

### File Excel cần có các cột (sheet "Summary")

| Cột | Bắt buộc | Mô tả |
|-----|----------|-------|
| **Tên công ty/nhà thuốc/quầy thuốc** | ✅ | Tên khách hàng (dùng để đặt tên file PDF) |
| **Mã số thuế** | ✅ | MST để tìm kiếm trên EasyInvoice |
| **Địa chỉ gửi hóa đơn** | ✅ | Email nhận hóa đơn |
| **Tổng tiền** | ⚪ | Số tiền để so sánh (optional) |

### ⚠️ Lưu ý quan trọng về Mã số thuế

**MST phải là TEXT trong Excel** để giữ số 0 ở đầu:

1. Chọn cột "Mã số thuế"
2. Chuột phải → Format Cells → Chọn "Text"
3. Nhập MST (ví dụ: `0312670722`)

Nếu để dạng Number, Excel sẽ tự động xóa số 0 ở đầu → Sai MST!

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

1. Đọc file Excel (`excel/HoaDon.xlsx`, sheet "Details")
2. Nhóm sản phẩm theo ID hóa đơn (cùng ID = cùng 1 hóa đơn)
3. Với mỗi hóa đơn:
   - Click "Tạo mới"
   - Điền Mã số thuế → Lấy thông tin khách hàng
   - Chọn VAT %
   - Điền từng sản phẩm (tên, số lượng, đơn giá)
   - So sánh tổng tiền với Excel, tự động điều chỉnh thuế nếu sai lệch
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

Bot kết nối vào Chrome đang chạy với remote debugging:

### Cách mở Chrome debug mode:

**Cách 1: Double-click file `chrome-debug.bat`**

**Cách 2: Chạy lệnh PowerShell:**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**Lưu ý:**
- Đóng tất cả cửa sổ Chrome trước khi chạy
- Chrome sẽ mở với remote debugging port 9222
- Đăng nhập vào EasyInvoice trước khi chạy bot
- Bot sẽ tự động kết nối vào Chrome đang mở

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

## 🔄 Changelog

### v2.0 - Cập nhật tìm kiếm theo MST (2026-05-23)

**Thay đổi chính:**
- ✅ Tìm hóa đơn theo **Mã số thuế (MST)** thay vì tên khách hàng (chính xác hơn)
- ✅ Sửa lỗi tên file PDF bị lặp (từ `Tên_Tên.pdf` → `Tên.pdf`)
- ✅ Đảm bảo MST được đọc dạng text (giữ số 0 ở đầu)
- ✅ Tự động điều chỉnh thuế khi tạo hóa đơn nếu tổng tiền sai lệch

**File thay đổi:**
- `invoice_agents/easyinvoice_agent.py` - Đổi tìm kiếm theo MST
- `invoice_agents/utils.py` - Sửa tên file PDF
- `invoice_agents/master_agent_excel.py` - Đọc MST dạng text

## 📞 Hỗ trợ

Nếu gặp lỗi, kiểm tra:
1. Chrome đã mở với remote debugging port 9222 chưa?
2. Đã đăng nhập EasyInvoice chưa?
3. File Excel có đúng format không?
4. Cột "Mã số thuế" có format Text không?
5. File `.env` đã cấu hình đúng chưa?

## 📄 License

MIT License
