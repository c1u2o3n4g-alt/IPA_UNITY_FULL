# Hướng dẫn sử dụng AUTO BUILD IPA TOOL

## 🚀 Giới thiệu

Tool tự động hóa **TOÀN BỘ** quy trình build IPA:
1. ✅ Push code lên GitHub
2. ✅ Trigger workflow tự động
3. ✅ Theo dõi tiến trình real-time
4. ✅ Download IPA khi build xong
5. ✅ Hiển thị progress chi tiết

## 📋 Yêu cầu

### Đã setup GitHub Token local
Chạy một lần:
```powershell
.\set-token-local.ps1
```

Token sẽ được lưu trong file `.env` và dùng cho mọi lần build sau.

## 🎯 Cách sử dụng

### Cách 1: Chạy file .bat (Đơn giản nhất)

```cmd
auto-build-full.bat
```

Tool sẽ hỏi:
- **Commit message** (Enter = auto)
- **Build config** (Enter = Release)
- **Branch** (Enter = main)

### Cách 2: Chạy PowerShell trực tiếp

```powershell
.\auto-build-full.ps1
```

Hoặc với tham số tùy chỉnh:

```powershell
.\auto-build-full.ps1 -CommitMessage "Fix bug ABC" -BuildConfig "Debug" -Branch "develop"
```

### Cách 3: Chạy nhanh với default

```powershell
.\auto-build-full.ps1 -CommitMessage "Update game"
```

## 📊 Hiển thị tiến trình

### Bước 1: Load Token
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BƯỚC 1: LOAD GITHUB TOKEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Đã load token từ local environment
```

### Bước 2: Push Code
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BƯỚC 2: PUSH CODE LÊN GITHUB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏳ Đang push lên GitHub...
  ✅ Đã push code lên GitHub
```

### Bước 3: Trigger Workflow
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BƯỚC 3: TRIGGER WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏳ Đang trigger workflow...
  ✅ Đã trigger workflow thành công!
```

### Bước 4: Theo dõi Build (Real-time)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BƯỚC 4: THEO DÕI TIẾN TRÌNH BUILD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Tìm thấy workflow run: #123456789
  ℹ️  URL: https://github.com/c1u2o3n4g-alt/IPA_UNITY_FULL/actions/runs/123456789
  
  ℹ️  Đang theo dõi tiến trình build...
  ℹ️  Ước tính: 20-30 phút
  
  🔄 Status: in_progress (Elapsed: 2.3 min)
  🔨 Build and Archive - 45% (9/20 steps)
  🔨 Export IPA - 60% (12/20 steps)
  
  ✅ BUILD THÀNH CÔNG! (Thời gian: 24.5 phút)
```

### Bước 5: Download IPA
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BƯỚC 5: DOWNLOAD IPA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏳ Đang tìm artifacts...
  ✅ Tìm thấy artifact: NROFLY.ipa (156.23 MB)
  ⏳ Đang download IPA...
  ✅ Đã download artifact
  ⏳ Đang giải nén...
  ✅ Đã giải nén IPA
  
  ✅ HOÀN TẤT!
  
  ℹ️  File IPA: .\output\NROFLY.ipa
  ℹ️  Kích thước: 156.23 MB
```

## 🎨 Tính năng nổi bật

### 1. Tự động hóa 100%
Không cần tương tác gì sau khi chạy lệnh

### 2. Hiển thị progress real-time
- ✅ Status workflow (queued, in_progress, completed)
- ✅ Progress từng step (percentage, current step)
- ✅ Thời gian đã chạy (elapsed time)
- ✅ Ước tính thời gian hoàn thành

### 3. Sử dụng token local
- ✅ Đọc token từ file `.env`
- ✅ Không ảnh hưởng các project khác
- ✅ An toàn, không expose token

### 4. Error handling
- ✅ Retry mechanism khi tìm workflow
- ✅ Hiển thị lỗi rõ ràng
- ✅ Thông báo khi build fail

### 5. Tự động mở thư mục output
Sau khi download xong, tự động mở thư mục chứa IPA

## 🔧 Tham số

| Tham số | Mô tả | Default | Ví dụ |
|---------|-------|---------|-------|
| `-CommitMessage` | Message cho commit | Auto timestamp | `"Fix bug ABC"` |
| `-BuildConfig` | Release hoặc Debug | `Release` | `"Debug"` |
| `-Branch` | Branch để build | `main` | `"develop"` |

## 📝 Ví dụ

### Build Release với commit message tùy chỉnh
```powershell
.\auto-build-full.ps1 -CommitMessage "Update version 1.2.3"
```

### Build Debug trên branch develop
```powershell
.\auto-build-full.ps1 -CommitMessage "Test new feature" -BuildConfig "Debug" -Branch "develop"
```

### Chạy với tất cả default
```powershell
.\auto-build-full.ps1
```

## ⚠️ Lưu ý

### Token permissions
Token cần có quyền:
- ✅ **Actions**: Read and write (để trigger và monitor workflow)
- ✅ **Contents**: Read and write (để push code)

### GitHub LFS
Tool tự động sử dụng Git LFS, không cần setup thêm gì.

### Internet connection
Cần kết nối internet ổn định trong suốt quá trình build (20-30 phút).

### Output folder
File IPA sẽ được lưu trong: `.\output\NROFLY.ipa`

## 🐛 Troubleshooting

### "Không tìm thấy GitHub Token"
```powershell
# Chạy lại setup token
.\set-token-local.ps1
```

### "Không thể trigger workflow"
- Kiểm tra token có đủ quyền không
- Kiểm tra repository và branch name đúng không

### "Không tìm thấy workflow run"
- Đợi thêm vài giây, workflow có thể khởi động chậm
- Kiểm tra GitHub Actions có bị disable không

### "Build thất bại"
- Xem log chi tiết tại URL được hiển thị
- Kiểm tra XCODE files có đầy đủ không

## 💡 Tips

### Chạy nhiều build cùng lúc
Tool hỗ trợ, mỗi build sẽ có workflow run riêng.

### Monitor build đang chạy
Có thể xem thêm chi tiết tại GitHub Actions web UI (link được hiển thị).

### Hủy build
Nếu muốn hủy, Ctrl+C trong terminal hoặc cancel trên GitHub Actions web.

## 📊 So sánh với cách manual

| Công việc | Manual | Auto Tool |
|-----------|--------|-----------|
| Push code | 3 commands | ✅ Auto |
| Vào GitHub web | ✅ Cần | ✅ Auto |
| Trigger workflow | ✅ Click manual | ✅ Auto |
| Đợi build | ❌ Không biết progress | ✅ Real-time progress |
| Download IPA | ✅ Click manual | ✅ Auto |
| Giải nén | ✅ Manual | ✅ Auto |
| **Tổng thời gian thao tác** | ~5 phút | ~30 giây |

## 🎯 Kết luận

Tool giúp bạn **TIẾT KIỆM THỜI GIAN** và **THEO DÕI TIẾN TRÌNH** một cách trực quan, chỉ cần 1 lệnh!
