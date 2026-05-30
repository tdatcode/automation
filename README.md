# 🤖 EasyInvoice Auto - Tự động hóa toàn diện

[![Version](https://img.shields.io/badge/version-1.1-blue.svg)](https://github.com/tdatcode/automation)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Ứng dụng GUI tự động hóa 3 tác vụ trên hệ thống EasyInvoice:
- 📥 **Tải hóa đơn PDF** - Tìm theo MST, tải và đổi tên tự động
- 📝 **Tạo hóa đơn mới** - Tạo hóa đơn từ file Excel
- 📧 **Gửi email** - Gửi PDF qua email với chế độ TEST/REAL

---

## ✨ Tính năng nổi bật

### 🎯 3 Chức năng chính

#### 1. 📥 Tải PDF
- Tìm hóa đơn theo **Mã số thuế (MST)**
- Tải PDF từ EasyInvoice
- Đổi tên tự động theo tên khách hàng
- Lưu vào thư mục `downloads/`

#### 2. 📝 Tạo hóa đơn
- Đọc thông tin từ Excel (Sheet: Details)
- Tự động điền MST, sản phẩm, VAT
- Tự động điều chỉnh thuế nếu sai lệch
- Lưu dữ liệu trên EasyInvoice

#### 3. 📧 Gửi email (MỚI v1.1)
- **🧪 TEST Mode**: Gửi cho chính mình để kiểm tra
  - Email có thông tin khách hàng (Tên, MST, Email thật)
  - Có PDF hóa đơn đính kèm
  - An toàn, không gửi cho khách hàng
- **📧 REAL Mode**: Gửi thật cho khách hàng
  - Email chính thức
  - Gửi đến địa chỉ trong Excel

### 🚀 Tự động hóa hoàn toàn

- ✅ Tự động cài Chromium (lần đầu)
- ✅ Tự động mở Chrome với debug mode
- ✅ Tự động lưu đăng nhập EasyInvoice
- ✅ Popup xác nhận rõ ràng
- ✅ Nút "Dừng lại" để dừng giữa chừng
- ✅ Progress bar + Log real-time
- ✅ Thân thiện với non-IT

---

## 📸 Giao diện

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 EasyInvoice Auto - Tự động hóa toàn diện                │
├─────────────────────────────────────────────────────────────┤
│  [📥 Tải PDF]  [📝 Tạo hóa đơn]  [📧 Gửi email]            │
├─────────────────────────────────────────────────────────────┤
│  📁 Chọn file Excel                                         │
│  [File path........................] [📂 Chọn file]         │
│                                                             │
│  📧 Cấu hình Email (chỉ tab Gửi email)                      │
│  Email: [your@gmail.com]                                    │
│  Pass:  [****************]                                  │
│                                                             │
│  📊 Tiến độ                                                 │
│  [████████████████████████████████]                         │
│  Sẵn sàng                                                   │
│                                                             │
│  📝 Log                                                     │
│  [Log messages here....................]                    │
│                                                             │
│  [▶️ Bắt đầu]  [⏹️ Dừng lại]                               │
│                                                             │
│  (Tab Gửi email có 2 nút)                                  │
│  [🧪 TEST - Gửi cho chính mình]                            │
│  [📧 THẬT - Gửi cho khách hàng]                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.10+ (nếu chạy từ source)
- Google Chrome
- Kết nối internet (lần đầu)

### Cách 1: Dùng file EXE (Khuyến nghị cho non-IT)

1. **Tải file**
   ```
   Tải EasyInvoiceAuto.zip từ GitHub Releases
   ```

2. **Giải nén**
   ```
   Giải nén vào thư mục bất kỳ
   ```

3. **Chạy**
   ```
   Double-click EasyInvoiceAuto.exe
   ```

4. **Lần đầu chạy**
   - Cần internet để tải Chromium (~100MB)
   - Mất 5-10 phút
   - Lần sau không cần nữa

### Cách 2: Chạy từ source code

1. **Clone repository**
   ```bash
   git clone https://github.com/tdatcode/automation.git
   cd automation/botmail
   ```

2. **Cài đặt dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Tạo file .env**
   ```bash
   cp .env.example .env
   ```
   
   Sửa file `.env`:
   ```env
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   EASYINVOICE_INDEX_URL=https://your-mst.easyinvoice.com.vn/EInvoice/Index
   ```

4. **Chạy ứng dụng**
   ```bash
   python gui_app.py
   ```

---

## 📊 File Excel

### Sheet "Summary" (cho Tải PDF và Gửi email)

| Cột | Bắt buộc | Mô tả |
|-----|----------|-------|
| **Tên công ty/nhà thuốc/quầy thuốc** | ✅ | Tên khách hàng (dùng để đặt tên file PDF) |
| **Mã số thuế** | ✅ | MST để tìm kiếm (format TEXT, giữ số 0 ở đầu) |
| **Địa chỉ gửi hóa đơn** | ✅ | Email nhận hóa đơn |
| **Tổng tiền** | ⚪ | Số tiền để so sánh (optional) |

⚠️ **Lưu ý**: Cột "Mã số thuế" phải format TEXT để giữ số 0 ở đầu!

### Sheet "Details" (cho Tạo hóa đơn)

| Cột | Mô tả |
|-----|--------|
| **ID hóa đơn** | Nhóm sản phẩm cùng 1 hóa đơn |
| **Mã số thuế** | MST khách hàng |
| **Tên sản phẩm** | Tên hàng hóa |
| **Giá đơn vị** | Đơn giá |
| **SL đặt** | Số lượng |
| **vat** | % thuế (0, 5, 8, 10) |

---

## 📧 Cấu hình Email (Gmail)

### Bước 1: Tạo App Password

1. Vào https://myaccount.google.com/apppasswords
2. Chọn "Mail" → "Windows Computer"
3. Copy mật khẩu 16 ký tự
4. Dán vào ô "Mật khẩu" trong GUI

### Bước 2: Điền vào GUI

- **Email gửi**: your@gmail.com
- **Mật khẩu**: Mật khẩu 16 ký tự (App Password)

---

## 🎯 Hướng dẫn sử dụng

### Tab 1: 📥 Tải PDF

1. Chọn file Excel (Sheet: Summary)
2. Click "▶️ Bắt đầu tải PDF"
3. Chrome tự động mở
4. Đăng nhập EasyInvoice (nếu chưa)
5. Click OK để bắt đầu
6. Chờ xử lý
7. File PDF lưu trong `downloads/`

### Tab 2: 📝 Tạo hóa đơn

1. Chọn file Excel (Sheet: Details)
2. Click "▶️ Bắt đầu tạo hóa đơn"
3. Chrome tự động mở
4. Đăng nhập EasyInvoice (nếu chưa)
5. Click OK để bắt đầu
6. Chờ xử lý
7. Hóa đơn được tạo trên EasyInvoice

### Tab 3: 📧 Gửi email

#### 🧪 TEST Mode (Khuyến nghị làm trước)

1. Chọn file Excel (Sheet: Summary)
2. Điền Email + Mật khẩu
3. Click **"🧪 TEST - Gửi cho chính mình"**
4. Chrome tự động mở
5. Đăng nhập EasyInvoice (nếu chưa)
6. Click OK để bắt đầu
7. Kiểm tra hộp thư của BẠN
8. Xem email có đúng không:
   - Thông tin khách hàng đúng?
   - PDF đúng hóa đơn?
   - Nội dung email OK?

#### 📧 REAL Mode (Sau khi TEST OK)

1. Nếu TEST OK → Click **"📧 THẬT - Gửi cho khách hàng"**
2. Xác nhận popup (⚠️ Cảnh báo)
3. Chờ xử lý
4. Email gửi đến khách hàng

---

## 🧪 Email TEST vs REAL

### 🧪 Email TEST

**Gửi đến**: Email của bạn (không phải khách hàng)

**Tiêu đề**: `🧪 TEST - Hóa đơn điện tử - Nhà thuốc ABC`

**Nội dung**:
```
🧪 ĐÂY LÀ EMAIL TEST - KHÔNG GỬI CHO KHÁCH HÀNG

Email này được gửi để kiểm tra trước khi gửi thật.

---
THÔNG TIN KHÁCH HÀNG:
- Tên: Nhà thuốc ABC
- MST: 0312670722
- Email thật: nhathuocabc@gmail.com

---
NỘI DUNG EMAIL THẬT SẼ NHƯ SAU:

Kính gửi Quý khách Nhà thuốc ABC,

Công ty xin gửi hóa đơn điện tử đính kèm.

Quý khách vui lòng kiểm tra file PDF trong email này.

Trân trọng.

---
Công ty Lucky Star
```

**Đính kèm**: Nhà_thuốc_ABC.pdf

### 📧 Email REAL

**Gửi đến**: Email khách hàng (trong Excel)

**Tiêu đề**: `Hóa đơn điện tử - Nhà thuốc ABC`

**Nội dung**:
```
Kính gửi Quý khách Nhà thuốc ABC,

Công ty xin gửi hóa đơn điện tử đính kèm.

Quý khách vui lòng kiểm tra file PDF trong email này.

Trân trọng.

---
Công ty Lucky Star
```

**Đính kèm**: Nhà_thuốc_ABC.pdf

---

## 🔧 Build EXE (cho developer)

### Bước 1: Cài PyInstaller

```bash
pip install pyinstaller
```

### Bước 2: Build

```bash
python build_exe.py
```

### Bước 3: Tạo package

```bash
create_package.bat
```

### Bước 4: Nén ZIP

```bash
# Windows
Compress-Archive -Path "EasyInvoiceAuto_v1.0" -DestinationPath "EasyInvoiceAuto.zip"
```

---

## 📁 Cấu trúc dự án

```
botmail/
├── gui_app.py                    # GUI chính
├── invoice_agents/               # Backend logic
│   ├── config.py
│   ├── easyinvoice_agent.py
│   ├── create_invoice_agent.py
│   ├── mail_agent.py
│   ├── master_agent_excel.py
│   └── utils.py
├── excel/
│   └── HoaDon.xlsx              # File Excel mẫu
├── downloads/                    # Thư mục lưu PDF
├── dist/
│   └── EasyInvoiceAuto.exe      # File EXE
├── build_exe.py                  # Script build
├── create_package.bat            # Script tạo package
├── requirements.txt              # Dependencies
├── .env.example                  # Mẫu cấu hình
└── README.md                     # File này
```

---

## ⚠️ Lưu ý quan trọng

### Mã số thuế (MST)

**MST phải là TEXT trong Excel** để giữ số 0 ở đầu:

1. Chọn cột "Mã số thuế"
2. Chuột phải → Format Cells → Chọn "Text"
3. Nhập MST (ví dụ: `0312670722`)

Nếu để dạng Number, Excel sẽ tự động xóa số 0 ở đầu → Sai MST!

### Email Gmail

- Phải dùng **App Password**, không phải mật khẩu Gmail thường
- Gmail giới hạn ~500 email/ngày
- Nếu gửi nhiều, nên chia nhỏ batch

### Chrome Debug Mode

- Ứng dụng tự động mở Chrome với debug mode
- Đăng nhập EasyInvoice sẽ được lưu lại
- Lần sau không cần đăng nhập lại

### Antivirus

- Antivirus có thể cảnh báo file EXE (false positive)
- Thêm vào whitelist nếu cần

---

## 🐛 Xử lý lỗi

### Lỗi: "Không tìm thấy Chrome"

**Giải pháp**: Cài đặt Google Chrome từ https://www.google.com/chrome/

### Lỗi: "Không kết nối được Chrome"

**Giải pháp**: 
1. Đóng tất cả cửa sổ Chrome
2. Chạy lại ứng dụng
3. Chrome sẽ tự động mở với debug mode

### Lỗi: "Chưa đăng nhập EasyInvoice"

**Giải pháp**:
1. Đăng nhập trong Chrome khi popup hiện ra
2. Click OK sau khi đăng nhập xong

### Lỗi: "Không gửi được email"

**Giải pháp**:
1. Kiểm tra Email + App Password đúng chưa
2. Kiểm tra kết nối internet
3. Thử gửi TEST trước

---

## 🔄 Changelog

### v1.1 (30/05/2026)

**Tính năng mới**:
- ✅ Thêm chế độ TEST email (gửi cho chính mình)
- ✅ Thêm chế độ REAL email (gửi cho khách hàng)
- ✅ Email TEST có thông tin khách hàng đầy đủ
- ✅ Popup xác nhận rõ ràng cho từng chế độ

**Cải tiến**:
- ✅ Giao diện Tab 3 gọn gàng hơn
- ✅ An toàn hơn, tránh gửi nhầm email

### v1.0 (23/05/2026)

**Tính năng**:
- ✅ GUI 3 tab đầy đủ
- ✅ Tải PDF theo MST
- ✅ Tạo hóa đơn từ Excel
- ✅ Gửi email với PDF đính kèm
- ✅ Tự động hóa hoàn toàn
- ✅ Nút Dừng lại

---

## 📞 Hỗ trợ

### Liên hệ

- **GitHub**: https://github.com/tdatcode/automation
- **Issues**: https://github.com/tdatcode/automation/issues

### Báo lỗi

Nếu gặp lỗi, vui lòng tạo issue trên GitHub với thông tin:
- Mô tả lỗi
- Các bước tái hiện
- Screenshot (nếu có)
- File log (nếu có)

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🙏 Đóng góp

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Star History

Nếu project này hữu ích, hãy cho một ⭐ trên GitHub!

---

**Made with ❤️ by tdatcode**
