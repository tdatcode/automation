"""
EasyInvoice Auto - GUI Application (FULL VERSION)
Ứng dụng GUI đầy đủ với 3 chức năng:
1. Tải PDF + Đổi tên (theo MST)
2. Tạo hóa đơn mới
3. Gửi email

KHÔNG CẦN:
- Cài Python
- Chạy server
- Chạy chrome-debug.bat

CHỈ CẦN:
- Double-click EXE
- Đăng nhập EasyInvoice (lần đầu)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import subprocess
import time
from pathlib import Path

# Thêm đường dẫn để import
sys.path.insert(0, str(Path(__file__).parent))

from invoice_agents.master_agent_excel import MasterAgentExcel
from invoice_agents.create_invoice_agent import CreateInvoiceAgent
from invoice_agents import config
from playwright.sync_api import sync_playwright
import pandas as pd


class EasyInvoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyInvoice Auto - Tự động hóa toàn diện")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Variables
        self.excel_file = tk.StringVar()
        self.is_running = False
        self.should_stop = False  # Flag để dừng xử lý
        self.chrome_process = None  # Lưu process Chrome
        
        # Kiểm tra và cài đặt Playwright (lần đầu)
        self.check_playwright_installation()
        
        # Setup UI
        self.setup_ui()
        
        # Đóng Chrome khi thoát app
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def check_playwright_installation(self):
        """Kiểm tra và cài đặt Playwright Chromium (lần đầu)"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                # Thử khởi tạo browser để kiểm tra
                try:
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                except Exception:
                    # Chưa cài Chromium → Cài tự động
                    messagebox.showinfo(
                        "Cài đặt lần đầu",
                        "Lần đầu sử dụng, ứng dụng cần tải Chromium (~100MB).\n\n"
                        "Quá trình này mất 5-10 phút.\n\n"
                        "Click OK để bắt đầu..."
                    )
                    
                    # Hiển thị loading window
                    loading = tk.Toplevel(self.root)
                    loading.title("Đang cài đặt...")
                    loading.geometry("400x150")
                    loading.resizable(False, False)
                    
                    tk.Label(
                        loading,
                        text="⏳ Đang tải Chromium...",
                        font=("Arial", 14, "bold")
                    ).pack(pady=20)
                    
                    progress = ttk.Progressbar(loading, mode='indeterminate')
                    progress.pack(fill=tk.X, padx=20, pady=10)
                    progress.start(10)
                    
                    tk.Label(
                        loading,
                        text="Vui lòng chờ 5-10 phút...",
                        font=("Arial", 10)
                    ).pack(pady=10)
                    
                    loading.update()
                    
                    # Cài Chromium
                    subprocess.run(["playwright", "install", "chromium"], check=True)
                    
                    progress.stop()
                    loading.destroy()
                    
                    messagebox.showinfo("Hoàn thành", "Cài đặt thành công!\n\nBây giờ bạn có thể sử dụng ứng dụng.")
        except Exception as e:
            messagebox.showerror("Lỗi cài đặt", f"Không thể cài đặt Playwright:\n\n{str(e)}")
    
    def start_chrome_debug(self):
        """Tự động mở Chrome với debug mode"""
        try:
            # Tìm Chrome executable
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                messagebox.showerror(
                    "Lỗi",
                    "Không tìm thấy Google Chrome!\n\n"
                    "Vui lòng cài đặt Chrome từ:\n"
                    "https://www.google.com/chrome/"
                )
                return False
            
            # Kiểm tra xem Chrome debug đã chạy chưa
            try:
                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp("http://localhost:9222")
                    browser.close()
                    return True  # Đã chạy rồi
            except Exception:
                pass  # Chưa chạy → Mở mới
            
            # Mở Chrome với debug mode
            self.chrome_process = subprocess.Popen([
                chrome_exe,
                "--remote-debugging-port=9222",
                "--user-data-dir=" + os.path.expanduser("~/.easyinvoice_chrome_profile")
            ])
            
            # Chờ Chrome khởi động
            time.sleep(3)
            
            # Kiểm tra kết nối
            max_retries = 10
            for i in range(max_retries):
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.connect_over_cdp("http://localhost:9222")
                        browser.close()
                        return True
                except Exception:
                    if i < max_retries - 1:
                        time.sleep(1)
                    else:
                        messagebox.showerror(
                            "Lỗi",
                            "Không thể kết nối Chrome!\n\n"
                            "Vui lòng thử lại."
                        )
                        return False
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Chrome:\n\n{str(e)}")
            return False
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if messagebox.askokcancel("Thoát", "Bạn có muốn thoát ứng dụng?"):
            # Không đóng Chrome - để người dùng tiếp tục dùng
            self.root.destroy()
        
    def setup_ui(self):
        """Tạo giao diện với 3 tab"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#667eea", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 EasyInvoice Auto - Tự động hóa toàn diện",
            font=("Arial", 18, "bold"),
            bg="#667eea",
            fg="white"
        )
        title_label.pack(pady=25)
        
        # Main content với Notebook (tabs)
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Tải PDF
        self.tab_download = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_download, text="📥 Tải PDF")
        self.setup_download_tab()
        
        # Tab 2: Tạo hóa đơn
        self.tab_create = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_create, text="📝 Tạo hóa đơn")
        self.setup_create_tab()
        
        # Tab 3: Gửi email
        self.tab_email = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_email, text="📧 Gửi email")
        self.setup_email_tab()
    
    def setup_download_tab(self):
        """Tab 1: Tải PDF + Đổi tên"""
        main_frame = self.tab_download
        
        # File selection
        file_frame = tk.LabelFrame(main_frame, text="📁 Chọn file Excel (Sheet: Summary)", font=("Arial", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_file = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.download_file, font=("Arial", 10), state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="📂 Chọn file",
            command=lambda: self.browse_file(self.download_file),
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Info
        info_frame = tk.LabelFrame(main_frame, text="ℹ️ Thông tin", font=("Arial", 10, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """✅ Tìm hóa đơn theo Mã số thuế (MST)
✅ Tải PDF từ EasyInvoice
✅ Đổi tên tự động theo tên khách hàng
✅ Lưu vào thư mục: downloads/
❌ Không gửi email"""
        info_label = tk.Label(info_frame, text=info_text, font=("Arial", 9), justify=tk.LEFT, fg="#666")
        info_label.pack(anchor=tk.W)
        
        # Progress
        progress_frame = tk.LabelFrame(main_frame, text="📊 Tiến độ", font=("Arial", 10, "bold"), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.download_progress.pack(fill=tk.X, pady=(0, 5))
        
        self.download_status = tk.Label(progress_frame, text="Sẵn sàng", font=("Arial", 9), fg="#28a745")
        self.download_status.pack(anchor=tk.W)
        
        # Log
        log_frame = tk.LabelFrame(main_frame, text="📝 Log", font=("Arial", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.download_log = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 8),
            bg="#f8f9fa",
            fg="#333",
            height=8,
            state=tk.DISABLED
        )
        self.download_log.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.download_start_btn = tk.Button(
            button_frame,
            text="▶️ Bắt đầu tải PDF",
            command=self.start_download,
            bg="#28a745",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.download_start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.download_stop_btn = tk.Button(
            button_frame,
            text="⏹️ Dừng lại",
            command=self.stop_download,
            bg="#dc3545",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.download_stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def setup_create_tab(self):
        """Tab 2: Tạo hóa đơn mới"""
        main_frame = self.tab_create
        
        # File selection
        file_frame = tk.LabelFrame(main_frame, text="📁 Chọn file Excel (Sheet: Details)", font=("Arial", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_file = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.create_file, font=("Arial", 10), state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="📂 Chọn file",
            command=lambda: self.browse_file(self.create_file),
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Info
        info_frame = tk.LabelFrame(main_frame, text="ℹ️ Thông tin", font=("Arial", 10, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """✅ Tạo hóa đơn mới trên EasyInvoice
✅ Tự động điền MST, sản phẩm, VAT
✅ Tự động điều chỉnh thuế nếu sai lệch
📋 Cần: ID hóa đơn, MST, Tên SP, SL, Giá, VAT"""
        info_label = tk.Label(info_frame, text=info_text, font=("Arial", 9), justify=tk.LEFT, fg="#666")
        info_label.pack(anchor=tk.W)
        
        # Progress
        progress_frame = tk.LabelFrame(main_frame, text="📊 Tiến độ", font=("Arial", 10, "bold"), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.create_progress.pack(fill=tk.X, pady=(0, 5))
        
        self.create_status = tk.Label(progress_frame, text="Sẵn sàng", font=("Arial", 9), fg="#28a745")
        self.create_status.pack(anchor=tk.W)
        
        # Log
        log_frame = tk.LabelFrame(main_frame, text="📝 Log", font=("Arial", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.create_log = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 8),
            bg="#f8f9fa",
            fg="#333",
            height=8,
            state=tk.DISABLED
        )
        self.create_log.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.create_start_btn = tk.Button(
            button_frame,
            text="▶️ Bắt đầu tạo hóa đơn",
            command=self.start_create,
            bg="#007bff",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.create_start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.create_stop_btn = tk.Button(
            button_frame,
            text="⏹️ Dừng lại",
            command=self.stop_create,
            bg="#dc3545",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.create_stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def setup_email_tab(self):
        """Tab 3: Gửi email"""
        main_frame = self.tab_email
        
        # File selection
        file_frame = tk.LabelFrame(main_frame, text="📁 Chọn file Excel (Sheet: Summary)", font=("Arial", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.email_file = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.email_file, font=("Arial", 10), state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="📂 Chọn file",
            command=lambda: self.browse_file(self.email_file),
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Email config
        config_frame = tk.LabelFrame(main_frame, text="📧 Cấu hình Email", font=("Arial", 10, "bold"), padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sender email
        tk.Label(config_frame, text="Email gửi:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sender_email = tk.Entry(config_frame, font=("Arial", 9), width=40)
        self.sender_email.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.sender_email.insert(0, config.SENDER_EMAIL)
        
        # Sender password
        tk.Label(config_frame, text="Mật khẩu:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sender_password = tk.Entry(config_frame, font=("Arial", 9), width=40, show="*")
        self.sender_password.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.sender_password.insert(0, config.SENDER_PASSWORD)
        
        # Progress
        progress_frame = tk.LabelFrame(main_frame, text="📊 Tiến độ", font=("Arial", 10, "bold"), padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.email_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.email_progress.pack(fill=tk.X, pady=(0, 5))
        
        self.email_status = tk.Label(progress_frame, text="Sẵn sàng", font=("Arial", 9), fg="#28a745")
        self.email_status.pack(anchor=tk.W)
        
        # Log
        log_frame = tk.LabelFrame(main_frame, text="📝 Log", font=("Arial", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.email_log = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 8),
            bg="#f8f9fa",
            fg="#333",
            height=4,
            state=tk.DISABLED
        )
        self.email_log.pack(fill=tk.X)
        
        # Buttons - 2 hàng
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Hàng 1: Test + Real
        action_frame = tk.Frame(button_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.email_test_btn = tk.Button(
            action_frame,
            text="🧪 TEST - Gửi cho chính mình",
            command=self.start_email_test,
            bg="#ffc107",
            fg="black",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.email_test_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.email_real_btn = tk.Button(
            action_frame,
            text="📧 THẬT - Gửi cho khách hàng",
            command=self.start_email_real,
            bg="#dc3545",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.email_real_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Hàng 2: Stop
        stop_frame = tk.Frame(button_frame)
        stop_frame.pack(fill=tk.X)
        
        self.email_stop_btn = tk.Button(
            stop_frame,
            text="⏹️ Dừng lại",
            command=self.stop_email,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            state=tk.DISABLED
        )
        self.email_stop_btn.pack(fill=tk.X)
        
    def browse_file(self, var):
        """Chọn file Excel"""
        filename = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def log(self, log_widget, message):
        """Thêm log vào text box"""
        log_widget.config(state=tk.NORMAL)
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END)
        log_widget.config(state=tk.DISABLED)
        self.root.update()
    
    def update_status(self, status_widget, message, color="#667eea"):
        """Cập nhật status"""
        status_widget.config(text=message, fg=color)
        self.root.update()
    
    # ========== TAB 1: TẢI PDF ==========
    
    def start_download(self):
        """Bắt đầu tải PDF"""
        if not self.download_file.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not os.path.exists(self.download_file.get()):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        
        if not messagebox.askyesno("Xác nhận", "Bắt đầu tải PDF?\n\nChrome sẽ tự động mở và xử lý hóa đơn."):
            return
        
        self.should_stop = False  # Reset flag
        self.download_start_btn.config(state=tk.DISABLED)
        self.download_stop_btn.config(state=tk.NORMAL)
        self.download_progress.start(10)
        self.update_status(self.download_status, "Đang xử lý...", "#667eea")
        
        self.download_log.config(state=tk.NORMAL)
        self.download_log.delete(1.0, tk.END)
        self.download_log.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.process_download, daemon=True)
        thread.start()
    
    def stop_download(self):
        """Dừng tải PDF"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng?\n\nĐơn hàng đang xử lý sẽ hoàn thành, các đơn sau sẽ bỏ qua."):
            self.should_stop = True
            self.log(self.download_log, "\n⏹️ Đang dừng... (Chờ đơn hiện tại hoàn thành)")
            self.update_status(self.download_status, "Đang dừng...", "#ffc107")
            self.download_stop_btn.config(state=tk.DISABLED)
    
    def process_download(self):
        """Xử lý tải PDF (thread)"""
        try:
            self.log(self.download_log, "=" * 50)
            self.log(self.download_log, "🚀 BẮT ĐẦU TẢI PDF")
            self.log(self.download_log, "=" * 50)
            self.log(self.download_log, f"📄 File: {os.path.basename(self.download_file.get())}")
            self.log(self.download_log, "")
            
            # Tự động mở Chrome debug mode
            self.log(self.download_log, "🌐 Đang mở Chrome...")
            if not self.start_chrome_debug():
                return
            self.log(self.download_log, "✅ Chrome đã sẵn sàng")
            self.log(self.download_log, "")
            
            # Khởi tạo master agent
            master = MasterAgentExcel()
            
            # Kết nối và kiểm tra đăng nhập
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                contexts = browser.contexts
                if contexts:
                    page = contexts[0].new_page()
                else:
                    page = browser.new_context().new_page()
                
                # Mở EasyInvoice
                page.goto(config.EASYINVOICE_INDEX_URL)
                page.wait_for_timeout(3000)
                
                # Kiểm tra đăng nhập
                if "login" in page.url.lower():
                    self.log(self.download_log, "⚠️  Chưa đăng nhập EasyInvoice")
                    self.log(self.download_log, "💡 Vui lòng đăng nhập trong Chrome")
                    
                    # Hiển thị popup yêu cầu đăng nhập
                    messagebox.showinfo(
                        "Đăng nhập EasyInvoice",
                        "Vui lòng đăng nhập EasyInvoice trong Chrome.\n\n"
                        "Sau khi đăng nhập xong, click OK để tiếp tục."
                    )
                    
                    self.log(self.download_log, "✅ Đã xác nhận đăng nhập")
                else:
                    self.log(self.download_log, "✅ Đã đăng nhập sẵn!")
                    
                    # Hiển thị popup xác nhận bắt đầu
                    if not messagebox.askyesno(
                        "Sẵn sàng",
                        "Đã đăng nhập EasyInvoice.\n\n"
                        "Bắt đầu xử lý ngay?"
                    ):
                        self.log(self.download_log, "❌ Đã hủy")
                        return
                    
                    self.log(self.download_log, "🚀 Bắt đầu xử lý...")
                
                page.close()
            
            # Xử lý
            result = master.execute_full_pipeline(
                excel_file=self.download_file.get(),
                send_email=False,
                output_file=None,
                skip_confirmation=True  # Bỏ qua input() cho GUI
            )
            
            self.log(self.download_log, "")
            self.log(self.download_log, "=" * 50)
            self.log(self.download_log, "✅ HOÀN THÀNH!")
            self.log(self.download_log, "=" * 50)
            self.log(self.download_log, f"📊 Tổng số: {result.get('total', 0)}")
            self.log(self.download_log, f"✅ Thành công: {result.get('success', 0)}")
            self.log(self.download_log, f"❌ Lỗi: {result.get('failed', 0)}")
            self.log(self.download_log, f"📁 File PDF: {config.DOWNLOAD_FOLDER}")
            self.log(self.download_log, "=" * 50)
            
            self.download_progress.stop()
            self.update_status(self.download_status, "Hoàn thành!", "#28a745")
            
            messagebox.showinfo(
                "Hoàn thành",
                f"Đã tải xong!\n\nTổng: {result.get('total', 0)}\nThành công: {result.get('success', 0)}\nLỗi: {result.get('failed', 0)}"
            )
            
        except Exception as e:
            self.log(self.download_log, f"\n❌ LỖI: {str(e)}")
            self.download_progress.stop()
            self.update_status(self.download_status, "Lỗi!", "#dc3545")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n\n{str(e)}")
        
        finally:
            self.download_start_btn.config(state=tk.NORMAL)
            self.download_stop_btn.config(state=tk.DISABLED)
    
    # ========== TAB 2: TẠO HÓA ĐƠN ==========
    
    def start_create(self):
        """Bắt đầu tạo hóa đơn"""
        if not self.create_file.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not os.path.exists(self.create_file.get()):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        
        if not messagebox.askyesno("Xác nhận", "Bắt đầu tạo hóa đơn?\n\nChrome sẽ tự động mở và tạo hóa đơn."):
            return
        
        self.should_stop = False  # Reset flag
        self.create_start_btn.config(state=tk.DISABLED)
        self.create_stop_btn.config(state=tk.NORMAL)
        self.create_progress.start(10)
        self.update_status(self.create_status, "Đang xử lý...", "#667eea")
        
        self.create_log.config(state=tk.NORMAL)
        self.create_log.delete(1.0, tk.END)
        self.create_log.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.process_create, daemon=True)
        thread.start()
    
    def stop_create(self):
        """Dừng tạo hóa đơn"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng?\n\nHóa đơn đang tạo sẽ hoàn thành, các hóa đơn sau sẽ bỏ qua."):
            self.should_stop = True
            self.log(self.create_log, "\n⏹️ Đang dừng... (Chờ hóa đơn hiện tại hoàn thành)")
            self.update_status(self.create_status, "Đang dừng...", "#ffc107")
            self.create_stop_btn.config(state=tk.DISABLED)
    
    def process_create(self):
        """Xử lý tạo hóa đơn (thread)"""
        try:
            self.log(self.create_log, "=" * 50)
            self.log(self.create_log, "🚀 BẮT ĐẦU TẠO HÓA ĐƠN")
            self.log(self.create_log, "=" * 50)
            self.log(self.create_log, f"📄 File: {os.path.basename(self.create_file.get())}")
            self.log(self.create_log, "")
            
            # Tự động mở Chrome debug mode
            self.log(self.create_log, "🌐 Đang mở Chrome...")
            if not self.start_chrome_debug():
                return
            self.log(self.create_log, "✅ Chrome đã sẵn sàng")
            self.log(self.create_log, "")
            
            # Đọc Excel
            invoices = self.read_invoices_from_excel(self.create_file.get())
            
            if not invoices:
                self.log(self.create_log, "❌ Không có hóa đơn nào để tạo")
                return
            
            self.log(self.create_log, f"📊 Tổng: {len(invoices)} hóa đơn")
            self.log(self.create_log, "")
            
            # Kết nối Chrome
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                self.log(self.create_log, "✅ Đã kết nối Chrome")
                
                contexts = browser.contexts
                if contexts:
                    page = contexts[0].new_page()
                else:
                    page = browser.new_context().new_page()
                
                # Mở EasyInvoice
                page.goto(config.EASYINVOICE_INDEX_URL)
                page.wait_for_timeout(3000)
                
                # Kiểm tra đăng nhập
                if "login" in page.url.lower():
                    self.log(self.create_log, "⚠️  Chưa đăng nhập EasyInvoice")
                    self.log(self.create_log, "💡 Vui lòng đăng nhập trong Chrome")
                    
                    # Hiển thị popup yêu cầu đăng nhập
                    messagebox.showinfo(
                        "Đăng nhập EasyInvoice",
                        "Vui lòng đăng nhập EasyInvoice trong Chrome.\n\n"
                        "Sau khi đăng nhập xong, click OK để tiếp tục."
                    )
                    
                    self.log(self.create_log, "✅ Đã xác nhận đăng nhập")
                else:
                    self.log(self.create_log, "✅ Đã đăng nhập sẵn!")
                    
                    # Hiển thị popup xác nhận bắt đầu
                    if not messagebox.askyesno(
                        "Sẵn sàng",
                        "Đã đăng nhập EasyInvoice.\n\n"
                        "Bắt đầu tạo hóa đơn ngay?"
                    ):
                        self.log(self.create_log, "❌ Đã hủy")
                        return
                    
                    self.log(self.create_log, "🚀 Bắt đầu tạo hóa đơn...")
                
                self.log(self.create_log, "")
                
                # Tạo từng hóa đơn
                agent = CreateInvoiceAgent(page)
                stats = {"total": len(invoices), "success": 0, "failed": 0}
                
                for i, invoice in enumerate(invoices, 1):
                    self.log(self.create_log, f"\n📦 [{i}/{len(invoices)}] MST: {invoice['tax_code']}")
                    
                    result = agent.create_invoice(invoice)
                    
                    if result["success"]:
                        stats["success"] += 1
                        self.log(self.create_log, "✅ Thành công")
                    else:
                        stats["failed"] += 1
                        self.log(self.create_log, f"❌ Lỗi: {result['error']}")
                    
                    if i < len(invoices):
                        page.wait_for_timeout(3000)
                
                # Kết quả
                self.log(self.create_log, "")
                self.log(self.create_log, "=" * 50)
                self.log(self.create_log, "✅ HOÀN THÀNH!")
                self.log(self.create_log, "=" * 50)
                self.log(self.create_log, f"📊 Tổng: {stats['total']}")
                self.log(self.create_log, f"✅ Thành công: {stats['success']}")
                self.log(self.create_log, f"❌ Lỗi: {stats['failed']}")
                self.log(self.create_log, "=" * 50)
                
                self.create_progress.stop()
                self.update_status(self.create_status, "Hoàn thành!", "#28a745")
                
                messagebox.showinfo(
                    "Hoàn thành",
                    f"Đã tạo xong!\n\nTổng: {stats['total']}\nThành công: {stats['success']}\nLỗi: {stats['failed']}"
                )
                
        except Exception as e:
            self.log(self.create_log, f"\n❌ LỖI: {str(e)}")
            self.create_progress.stop()
            self.update_status(self.create_status, "Lỗi!", "#dc3545")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n\n{str(e)}")
        
        finally:
            self.create_start_btn.config(state=tk.NORMAL)
            self.create_stop_btn.config(state=tk.DISABLED)
    
    def read_invoices_from_excel(self, excel_path):
        """Đọc file Excel (sheet Details) và nhóm sản phẩm theo ID hóa đơn"""
        try:
            df = pd.read_excel(excel_path, sheet_name="Details", dtype={"Mã số thuế": str})
        except Exception:
            df = pd.read_excel(excel_path, dtype={"Mã số thuế": str})
        
        # Đọc sheet Summary để lấy Tổng tiền
        total_amount_map = {}
        try:
            df_summary = pd.read_excel(excel_path, sheet_name="Summary")
            for _, row in df_summary.iterrows():
                inv_id = row.get("ID hóa đơn")
                total = row.get("Tổng tiền")
                if not pd.isna(inv_id) and not pd.isna(total):
                    total_amount_map[str(int(inv_id))] = float(str(total).replace(",", "").replace(".", "").strip())
        except Exception:
            pass
        
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
            tax_code_raw = str(tax_code).strip()
            if tax_code_raw.endswith(".0"):
                tax_code = tax_code_raw[:-2]
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
        
        return list(invoices.values())
    
    # ========== TAB 3: GỬI EMAIL ==========
    
    def start_email_test(self):
        """Bắt đầu gửi email TEST (cho chính mình)"""
        if not self.email_file.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not os.path.exists(self.email_file.get()):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        
        # Kiểm tra email config
        sender_email = self.sender_email.get().strip()
        sender_password = self.sender_password.get().strip()
        
        if not sender_email or not sender_password:
            messagebox.showerror("Lỗi", "Vui lòng điền Email và Mật khẩu!")
            return
        
        if not messagebox.askyesno("🧪 TEST MODE", 
            "Gửi email TEST cho chính mình?\n\n"
            "• Email sẽ gửi đến: " + sender_email + "\n"
            "• Nội dung: Giống email thật\n"
            "• PDF: Hóa đơn tương ứng\n\n"
            "Dùng để kiểm tra trước khi gửi thật!"):
            return
        
        # Cập nhật config
        config.SENDER_EMAIL = sender_email
        config.SENDER_PASSWORD = sender_password
        
        self.should_stop = False  # Reset flag
        self.email_test_btn.config(state=tk.DISABLED)
        self.email_real_btn.config(state=tk.DISABLED)
        self.email_stop_btn.config(state=tk.NORMAL)
        self.email_progress.start(10)
        self.update_status(self.email_status, "🧪 TEST - Đang gửi...", "#ffc107")
        
        self.email_log.config(state=tk.NORMAL)
        self.email_log.delete(1.0, tk.END)
        self.email_log.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=lambda: self.process_email(test_mode=True), daemon=True)
        thread.start()
    
    def start_email_real(self):
        """Bắt đầu gửi email THẬT (cho khách hàng)"""
        if not self.email_file.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file Excel!")
            return
        
        if not os.path.exists(self.email_file.get()):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
        
        # Kiểm tra email config
        sender_email = self.sender_email.get().strip()
        sender_password = self.sender_password.get().strip()
        
        if not sender_email or not sender_password:
            messagebox.showerror("Lỗi", "Vui lòng điền Email và Mật khẩu!")
            return
        
        if not messagebox.askyesno("⚠️ XÁC NHẬN", 
            "Bắt đầu GỬI EMAIL THẬT?\n\n"
            "• Email sẽ gửi đến KHÁCH HÀNG\n"
            "• Địa chỉ: Trong cột 'Địa chỉ gửi hóa đơn'\n"
            "• Không thể hoàn tác!\n\n"
            "⚠️ Đã test kỹ chưa?"):
            return
        
        # Cập nhật config
        config.SENDER_EMAIL = sender_email
        config.SENDER_PASSWORD = sender_password
        
        self.should_stop = False  # Reset flag
        self.email_test_btn.config(state=tk.DISABLED)
        self.email_real_btn.config(state=tk.DISABLED)
        self.email_stop_btn.config(state=tk.NORMAL)
        self.email_progress.start(10)
        self.update_status(self.email_status, "📧 THẬT - Đang gửi...", "#dc3545")
        
        self.email_log.config(state=tk.NORMAL)
        self.email_log.delete(1.0, tk.END)
        self.email_log.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=lambda: self.process_email(test_mode=False), daemon=True)
        thread.start()
    
    def stop_email(self):
        """Dừng gửi email"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng?\n\nEmail đang gửi sẽ hoàn thành, các email sau sẽ bỏ qua."):
            self.should_stop = True
            self.log(self.email_log, "\n⏹️ Đang dừng... (Chờ email hiện tại gửi xong)")
            self.update_status(self.email_status, "Đang dừng...", "#ffc107")
            self.email_stop_btn.config(state=tk.DISABLED)
    
    def process_email(self, test_mode=False):
        """Xử lý gửi email (thread)"""
        try:
            mode_text = "🧪 TEST MODE - GỬI CHO CHÍNH MÌNH" if test_mode else "📧 REAL MODE - GỬI CHO KHÁCH HÀNG"
            
            self.log(self.email_log, "=" * 50)
            self.log(self.email_log, f"🚀 BẮT ĐẦU GỬI EMAIL")
            self.log(self.email_log, mode_text)
            self.log(self.email_log, "=" * 50)
            self.log(self.email_log, f"📄 File: {os.path.basename(self.email_file.get())}")
            self.log(self.email_log, f"📧 Email gửi: {config.SENDER_EMAIL}")
            
            if test_mode:
                self.log(self.email_log, f"🧪 Email nhận: {config.SENDER_EMAIL} (chính mình)")
            else:
                self.log(self.email_log, f"📧 Email nhận: Theo Excel (khách hàng)")
            
            self.log(self.email_log, "")
            
            # Tự động mở Chrome debug mode
            self.log(self.email_log, "🌐 Đang mở Chrome...")
            if not self.start_chrome_debug():
                return
            self.log(self.email_log, "✅ Chrome đã sẵn sàng")
            self.log(self.email_log, "")
            
            # Khởi tạo master agent
            master = MasterAgentExcel()
            
            # Kết nối và kiểm tra đăng nhập
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                contexts = browser.contexts
                if contexts:
                    page = contexts[0].new_page()
                else:
                    page = browser.new_context().new_page()
                
                # Mở EasyInvoice
                page.goto(config.EASYINVOICE_INDEX_URL)
                page.wait_for_timeout(3000)
                
                # Kiểm tra đăng nhập
                if "login" in page.url.lower():
                    self.log(self.email_log, "⚠️  Chưa đăng nhập EasyInvoice")
                    self.log(self.email_log, "💡 Vui lòng đăng nhập trong Chrome")
                    
                    # Hiển thị popup yêu cầu đăng nhập
                    messagebox.showinfo(
                        "Đăng nhập EasyInvoice",
                        "Vui lòng đăng nhập EasyInvoice trong Chrome.\n\n"
                        "Sau khi đăng nhập xong, click OK để tiếp tục."
                    )
                    
                    self.log(self.email_log, "✅ Đã xác nhận đăng nhập")
                else:
                    self.log(self.email_log, "✅ Đã đăng nhập sẵn!")
                    
                    # Hiển thị popup xác nhận bắt đầu
                    confirm_msg = "Đã đăng nhập EasyInvoice.\n\n"
                    if test_mode:
                        confirm_msg += "🧪 Bắt đầu gửi TEST (cho chính mình)?"
                    else:
                        confirm_msg += "📧 Bắt đầu gửi THẬT (cho khách hàng)?"
                    
                    if not messagebox.askyesno("Sẵn sàng", confirm_msg):
                        self.log(self.email_log, "❌ Đã hủy")
                        return
                    
                    self.log(self.email_log, "🚀 Bắt đầu gửi email...")
                
                page.close()
            
            # Xử lý - truyền test_mode vào master agent
            result = master.execute_full_pipeline(
                excel_file=self.email_file.get(),
                send_email=True,
                output_file=None,
                skip_confirmation=True,
                test_mode=test_mode  # Thêm tham số này
            )
            
            self.log(self.email_log, "")
            self.log(self.email_log, "=" * 50)
            self.log(self.email_log, "✅ HOÀN THÀNH!")
            self.log(self.email_log, "=" * 50)
            self.log(self.email_log, f"📊 Tổng số: {result.get('total', 0)}")
            self.log(self.email_log, f"✅ Thành công: {result.get('success', 0)}")
            self.log(self.email_log, f"❌ Lỗi: {result.get('failed', 0)}")
            
            if test_mode:
                self.log(self.email_log, f"\n🧪 Tất cả email đã gửi đến: {config.SENDER_EMAIL}")
                self.log(self.email_log, "💡 Kiểm tra hộp thư để xem email test")
            
            self.log(self.email_log, "=" * 50)
            
            self.email_progress.stop()
            self.update_status(self.email_status, "Hoàn thành!", "#28a745")
            
            success_msg = f"Đã gửi xong!\n\nTổng: {result.get('total', 0)}\nThành công: {result.get('success', 0)}\nLỗi: {result.get('failed', 0)}"
            if test_mode:
                success_msg += f"\n\n🧪 Tất cả email đã gửi đến:\n{config.SENDER_EMAIL}\n\nKiểm tra hộp thư để xem!"
            
            messagebox.showinfo("Hoàn thành", success_msg)
            
        except Exception as e:
            self.log(self.email_log, f"\n❌ LỖI: {str(e)}")
            self.email_progress.stop()
            self.update_status(self.email_status, "Lỗi!", "#dc3545")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n\n{str(e)}")
        
        finally:
            self.email_test_btn.config(state=tk.NORMAL)
            self.email_real_btn.config(state=tk.NORMAL)
            self.email_stop_btn.config(state=tk.DISABLED)


def main():
    """Chạy ứng dụng"""
    root = tk.Tk()
    app = EasyInvoiceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
