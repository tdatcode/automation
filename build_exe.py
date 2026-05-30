"""
Script để build EXE từ GUI app
"""

import PyInstaller.__main__
import os
import sys

# Lấy đường dẫn hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build EXE
PyInstaller.__main__.run([
    'gui_app.py',
    '--name=EasyInvoiceAuto',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    f'--add-data={os.path.join(current_dir, "invoice_agents")};invoice_agents',
    '--hidden-import=playwright',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=python-dotenv',
    '--hidden-import=tkinter',
    '--collect-all=playwright',
    '--noconfirm',
])

print("\n" + "=" * 70)
print("✅ BUILD HOÀN THÀNH!")
print("=" * 70)
print(f"📁 File EXE: {os.path.join(current_dir, 'dist', 'EasyInvoiceAuto.exe')}")
print("=" * 70)
