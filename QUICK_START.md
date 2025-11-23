# ⚡ Quick Start - Build IPA trong 5 phút

## Bước 1: Cài đặt (1 phút)

```bash
# Clone hoặc đã có repo
cd E:\IOSBUILD

# Cài Python dependencies
pip install requests
```

## Bước 2: Tạo GitHub Token (2 phút)

1. Vào: https://github.com/settings/tokens
2. **Generate new token (classic)**
3. Đặt tên: `IPA Auto Build`
4. Chọn quyền:
   - ✅ `repo`
   - ✅ `workflow`
   - ✅ `actions:read`
5. **Generate token** → Copy token

## Bước 3: Chạy Tool (1 dòng lệnh)

### Windows PowerShell:
```powershell
$env:GITHUB_TOKEN="ghp_PASTE_TOKEN_Ở_ĐÂY"; python auto_build_ipa.py
```

### Windows CMD:
```cmd
set GITHUB_TOKEN=ghp_PASTE_TOKEN_Ở_ĐÂY
python auto_build_ipa.py
```

### Linux/Mac:
```bash
GITHUB_TOKEN="ghp_PASTE_TOKEN_Ở_ĐÂY" python auto_build_ipa.py
```

## Bước 4: Đợi và nhận IPA (15-20 phút)

Tool sẽ tự động:
1. ✅ Push code lên GitHub (nếu có thay đổi)
2. ✅ Trigger workflow build
3. ✅ Hiển thị tiến trình real-time
4. ✅ Download IPA về `output/NROFLY.ipa`

**Output:**
```
🚀 AUTO BUILD IPA TOOL 🚀
============================================================

[Bước 1] Đẩy code lên GitHub...
✅ Đã push code lên main!

[Bước 2] Kích hoạt workflow build IPA (config: Release)...
✅ Đã kích hoạt workflow!
✅ Workflow Run ID: 123456789
ℹ️  URL: https://github.com/cuong1206/IPA_UNITY_FULL/actions/runs/123456789

[Bước 3] Đang đợi workflow build xong...
ℹ️  Status: queued | Đã chạy: 5s
ℹ️  Status: in_progress | Đã chạy: 30s
ℹ️  Status: in_progress | Đã chạy: 120s
...
✅ Build thành công! (Thời gian: 847s)

[Bước 4] Đang tải file NROFLY.ipa...
   Đang tải: 100.0% (131457280/131457280 bytes)
✅ Đã tải về: output\NROFLY.ipa

============================================================
🎉 HOÀN TẤT! 🎉
============================================================

✅ Đã tải về 1 file:
   📦 output\NROFLY.ipa
      ℹ️  Kích thước: 125.34 MB
```

## Xong! 🎉

File IPA của bạn ở: **`output/NROFLY.ipa`**

---

## Lần sau build nhanh hơn

Sau lần đầu setup token, chỉ cần:

```bash
python auto_build_ipa.py
```

---

## Options hữu ích

```bash
# Build Debug
python auto_build_ipa.py --config Debug

# Lưu vào thư mục khác
python auto_build_ipa.py --output my_builds

# Không đợi build xong (làm việc khác)
python auto_build_ipa.py --no-wait

# Xem tất cả options
python auto_build_ipa.py --help
```

---

## Troubleshooting nhanh

### Lỗi: "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### Lỗi: "Chưa có GitHub Personal Access Token"
- Làm lại Bước 2
- Hoặc nhập token khi tool hỏi

### Lỗi: "Build thất bại"
- Mở URL workflow run mà tool in ra
- Xem log lỗi chi tiết
- Thường do: Xcode project lỗi, thiếu file, hoặc workflow config sai

### Hủy giữa chừng?
- Nhấn `Ctrl+C`
- Workflow vẫn chạy trên GitHub
- Tải về sau: `python auto_build_ipa.py --no-push`

---

## 📖 Đọc thêm

- Chi tiết tool: [AUTO_BUILD_GUIDE.md](AUTO_BUILD_GUIDE.md)
- Build thủ công: [build_ipa_guide.md](build_ipa_guide.md)
- Tổng quan: [README.md](README.md)

---

**Chúc build IPA thành công!** 🚀

