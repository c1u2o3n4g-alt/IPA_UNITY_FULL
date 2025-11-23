# 🚀 Hướng Dẫn Sử Dụng Auto Build IPA Tool

Tool tự động hoàn toàn: **Push code → Trigger workflow → Đợi build → Download IPA về máy**

## 📋 Yêu Cầu

### 1. Cài đặt Python
```bash
python --version  # Cần Python 3.7+
```

### 2. Cài đặt thư viện
```bash
pip install requests
```

### 3. Tạo GitHub Personal Access Token

1. Vào: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Đặt tên: `IPA Build Tool`
4. Chọn quyền:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Actions workflows)
   - ✅ `actions:read` (Read access to Actions)
5. Click **Generate token**
6. **QUAN TRỌNG**: Copy token ngay, không xem lại được!

### 4. Cấu hình Token (Khuyến nghị)

**Cách 1: Biến môi trường (An toàn hơn)**

Windows PowerShell:
```powershell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxx"
```

Windows CMD:
```cmd
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
```

Linux/Mac:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxx"
```

**Cách 2: Nhập mỗi lần chạy**
- Tool sẽ tự hỏi nếu không có biến môi trường

---

## 🎯 Sử Dụng Cơ Bản

### Build Release (Mặc định)
```bash
python auto_build_ipa.py
```

**Quá trình tự động:**
1. ✅ Push code lên GitHub (nếu có thay đổi)
2. ✅ Trigger workflow build IPA
3. ✅ Đợi build xong (~10-20 phút)
4. ✅ Tải file IPA về thư mục `output/`

### Build Debug
```bash
python auto_build_ipa.py --config Debug
```

### Chỉ định thư mục output
```bash
python auto_build_ipa.py --output my_builds
```

---

## 🔧 Tùy Chọn Nâng Cao

### 1. Không push code, chỉ trigger workflow
```bash
python auto_build_ipa.py --no-push
```
**Khi nào dùng**: Code đã push rồi, chỉ muốn build lại.

### 2. Force push (Ghi đè lịch sử)
```bash
python auto_build_ipa.py --force-push
```
**⚠️ Cẩn thận**: Ghi đè history, chỉ dùng khi cần thiết!

### 3. Không đợi build xong
```bash
python auto_build_ipa.py --no-wait
```
**Khi nào dùng**: Trigger rồi làm việc khác, tải về sau thủ công.

### 4. Kết hợp nhiều option
```bash
python auto_build_ipa.py --config Debug --output debug_builds --no-push
```

---

## 📊 Output

### Cấu trúc thư mục sau khi chạy:
```
E:\IOSBUILD\
├── auto_build_ipa.py
├── output/                    ← IPA sẽ ở đây
│   └── NROFLY.ipa            ← File build mới nhất
└── XCODE/
```

### Thông tin file IPA:
```bash
# Xem kích thước
dir output\NROFLY.ipa

# Tool tự động hiển thị:
📦 output/NROFLY.ipa
   Kích thước: 125.34 MB
```

---

## 🔍 Xử Lý Lỗi

### Lỗi 1: "Chưa có GitHub Personal Access Token"
```
⚠️  Chưa có GitHub Personal Access Token!
ℹ️  Tạo token tại: https://github.com/settings/tokens
```
**Giải pháp**: Tạo token theo hướng dẫn mục "Yêu Cầu" → Bước 3.

### Lỗi 2: "error: src refspec main does not match any"
```
❌ Lỗi khi chạy command: git push origin main
```
**Giải pháp**: 
```bash
git branch  # Kiểm tra branch hiện tại
git checkout main  # Chuyển sang main nếu cần
```

### Lỗi 3: "Build thất bại! Conclusion: failure"
```
❌ Build thất bại! Conclusion: failure
❌ Chi tiết: https://github.com/cuong1206/IPA_UNITY_FULL/actions/runs/...
```
**Giải pháp**: 
1. Mở link chi tiết
2. Xem log lỗi ở bước nào
3. Sửa code/workflow theo lỗi

### Lỗi 4: "Không tìm thấy artifacts"
```
⚠️  Không tìm thấy artifacts!
```
**Nguyên nhân**: Build fail hoặc không tạo ra file IPA.
**Giải pháp**: Kiểm tra workflow run trên GitHub Actions.

### Lỗi 5: "Timeout sau 3600s"
```
❌ Timeout sau 3600s!
```
**Nguyên nhân**: Build quá lâu (>1 giờ).
**Giải pháp**: Kiểm tra log xem bị stuck ở đâu, có thể project quá lớn.

---

## 💡 Tips & Tricks

### 1. Chạy nhanh (1 dòng lệnh)
```bash
# Windows PowerShell
$env:GITHUB_TOKEN="ghp_xxx"; python auto_build_ipa.py

# Linux/Mac
GITHUB_TOKEN="ghp_xxx" python auto_build_ipa.py
```

### 2. Build nhiều config liên tiếp
```bash
# Build Release
python auto_build_ipa.py --config Release --output release

# Build Debug
python auto_build_ipa.py --config Debug --output debug --no-push
```

### 3. Theo dõi progress
Tool sẽ tự động in ra:
```
ℹ️  Status: in_progress | Đã chạy: 120s | URL: https://...
ℹ️  Status: in_progress | Đã chạy: 240s | URL: https://...
✅ Build thành công! (Thời gian: 847s)
```

### 4. Hủy giữa chừng
- Nhấn `Ctrl+C` để hủy
- Workflow trên GitHub vẫn tiếp tục chạy
- Tải IPA về sau bằng cách chạy:
  ```bash
  python auto_build_ipa.py --no-push
  ```

---

## 🎬 Workflow Hoàn Chỉnh

### Kịch bản 1: Build thường xuyên
```bash
# 1. Sửa code Unity project
# 2. Copy sang XCODE/
cp -r "D:\UnityProject\Build\iOS\*" "E:\IOSBUILD\XCODE\"

# 3. Chạy tool (tự động hết)
python auto_build_ipa.py

# 4. Chờ ~15 phút, xong có IPA trong output/
```

### Kịch bản 2: Thay đổi app khác
```bash
# 1. Xóa XCODE cũ
rm -rf XCODE

# 2. Copy Xcode project mới
cp -r "D:\NewApp\Build\iOS" XCODE

# 3. Build
python auto_build_ipa.py --config Release

# 4. IPA mới trong output/
```

### Kịch bản 3: Debug nhanh
```bash
# Build Debug không đợi
python auto_build_ipa.py --config Debug --no-wait

# Làm việc khác...

# Sau 15-20 phút, download thủ công
python auto_build_ipa.py --no-push
```

---

## 📞 Hỗ Trợ

### Xem hết options:
```bash
python auto_build_ipa.py --help
```

### Check workflow runs thủ công:
```bash
# Vào GitHub
https://github.com/cuong1206/IPA_UNITY_FULL/actions

# Xem run mới nhất → Download artifact
```

### Xóa output cũ:
```bash
# Windows
rmdir /s /q output

# Linux/Mac
rm -rf output
```

---

## ⚡ Performance

| Thao tác | Thời gian | Ghi chú |
|----------|-----------|---------|
| Push code | ~5-30s | Tùy kích thước thay đổi |
| Trigger workflow | ~3s | Gần như tức thì |
| Queue time | ~5-60s | Đợi macOS runner |
| Build time | ~10-20 phút | Unity project trung bình |
| Download IPA | ~30-60s | File ~100-150MB |
| **TỔNG** | **~15-25 phút** | Tự động hoàn toàn |

---

## 🔒 Bảo Mật

### ✅ Nên:
- Dùng biến môi trường `GITHUB_TOKEN`
- Không commit token vào code
- Xóa token cũ khi không dùng
- Giới hạn quyền token (chỉ `repo`, `workflow`, `actions:read`)

### ❌ Không nên:
- Chia sẻ token với người khác
- Hardcode token vào script
- Dùng token với quyền `admin`
- Để token trong clipboard lâu

---

## 🎉 Kết Luận

**Tool này giúp bạn:**
- ✅ **Không cần mở GitHub** → Tất cả từ command line
- ✅ **Không cần click chuột** → Fully automated
- ✅ **Không cần đợi chờ** → Làm việc khác trong lúc build
- ✅ **Không cần Mac** → Build trên GitHub cloud

**Một lệnh = Có IPA!** 🚀

