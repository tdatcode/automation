@echo off
chcp 65001 >nul
echo ========================================
echo   TẠO PACKAGE PHÂN PHỐI
echo ========================================
echo.

REM Kiểm tra file EXE
if not exist "dist\EasyInvoiceAuto.exe" (
    echo ❌ Chưa có file EXE!
    echo 👉 Chạy: python build_exe.py
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy file EXE
echo.

REM Tạo thư mục package
set PACKAGE_NAME=EasyInvoiceAuto_v1.0
if exist "%PACKAGE_NAME%" (
    echo 🗑️  Xóa package cũ...
    rmdir /s /q "%PACKAGE_NAME%"
)

echo 📁 Tạo thư mục package...
mkdir "%PACKAGE_NAME%"
mkdir "%PACKAGE_NAME%\downloads"

REM Copy file EXE
echo 📦 Copy file EXE...
copy "dist\EasyInvoiceAuto.exe" "%PACKAGE_NAME%\" >nul

REM Copy hướng dẫn
echo 📄 Copy hướng dẫn...
copy "README_EXE.txt" "%PACKAGE_NAME%\README.txt" >nul
copy "HUONG_DAN_NHANH.txt" "%PACKAGE_NAME%\" >nul

REM Tạo file VERSION
echo 📝 Tạo file VERSION...
echo EasyInvoice Auto v1.0 > "%PACKAGE_NAME%\VERSION.txt"
echo Build date: %date% %time% >> "%PACKAGE_NAME%\VERSION.txt"
echo. >> "%PACKAGE_NAME%\VERSION.txt"
echo Chức năng: >> "%PACKAGE_NAME%\VERSION.txt"
echo - Tải PDF + Đổi tên >> "%PACKAGE_NAME%\VERSION.txt"
echo - Tạo hóa đơn mới >> "%PACKAGE_NAME%\VERSION.txt"
echo - Gửi email >> "%PACKAGE_NAME%\VERSION.txt"

echo.
echo ========================================
echo   ✅ HOÀN THÀNH!
echo ========================================
echo.
echo 📁 Package: %PACKAGE_NAME%\
echo 📦 File EXE: %PACKAGE_NAME%\EasyInvoiceAuto.exe
echo 📄 Hướng dẫn: %PACKAGE_NAME%\README.txt
echo 📄 Hướng dẫn nhanh: %PACKAGE_NAME%\HUONG_DAN_NHANH.txt
echo 📁 Thư mục PDF: %PACKAGE_NAME%\downloads\
echo.
echo ========================================
echo   BƯỚC TIẾP THEO
echo ========================================
echo.
echo 1. Kiểm tra thư mục: %PACKAGE_NAME%\
echo 2. Nén thành ZIP: %PACKAGE_NAME%.zip
echo 3. Gửi file ZIP cho người dùng
echo.
echo 💡 Kích thước: ~200MB
echo 💡 Gửi qua: Google Drive / Dropbox / USB
echo.
pause
