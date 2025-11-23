# 🚀 Chạy Auto Build IPA Tool

## Cách 1: Dùng script set_token.ps1 (Nhanh nhất)

```powershell
# Mở PowerShell trong thư mục E:\IOSBUILD

# Chạy 2 lệnh này (mỗi lần build):
.\set_token.ps1
python auto_build_ipa.py
```

**Hoặc chạy 1 dòng duy nhất:**
```powershell
.\set_token.ps1; python auto_build_ipa.py
```

---

## Cách 2: Set token thủ công mỗi lần

```powershell
$env:GITHUB_TOKEN='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d'
python auto_build_ipa.py
```

---

## Cách 3: Set token vĩnh viễn (System Environment Variable)

### Windows:
1. Nhấn `Windows + R` → gõ `sysdm.cpl` → Enter
2. Tab **Advanced** → **Environment Variables**
3. Phần **User variables** → Click **New**
   - Variable name: `GITHUB_TOKEN`
   - Variable value: `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d`
4. **OK** → **OK**
5. **Đóng và mở lại PowerShell**

Sau đó chỉ cần:
```powershell
python auto_build_ipa.py
```

---

## Options khác

```powershell
# Build Debug
.\set_token.ps1; python auto_build_ipa.py --config Debug

# Lưu vào thư mục khác
.\set_token.ps1; python auto_build_ipa.py --output my_builds

# Không đợi build xong
.\set_token.ps1; python auto_build_ipa.py --no-wait

# Xem tất cả options
python auto_build_ipa.py --help
```

---

## ⚠️ Bảo mật

**QUAN TRỌNG**: 
- File `set_token.ps1` đã được thêm vào `.gitignore`
- Token sẽ **KHÔNG** bị push lên GitHub
- **KHÔNG** chia sẻ token với người khác!

---

## 🎯 Quick Start

```powershell
# Mở PowerShell
cd E:\IOSBUILD

# Chạy (1 dòng duy nhất)
.\set_token.ps1; python auto_build_ipa.py

# File IPA sẽ ở: output/NROFLY.ipa
```

