# Hướng dẫn Build IPA với Git LFS

## ⚡ Cách build nhanh

### Bước 1: Push code lên GitHub
```bash
git add .
git commit -m "Update XCODE files"
git push
```

### Bước 2: Chạy workflow trên GitHub Actions
1. Vào repository GitHub: `https://github.com/c1u2o3n4g-alt/IPA_UNITY_FULL`
2. Click tab **Actions**
3. Click workflow **"Build iOS IPA"**
4. Click nút **"Run workflow"**
5. Chọn branch `main` và build config (`Release` hoặc `Debug`)
6. Click **"Run workflow"** màu xanh

### Bước 3: Đợi build hoàn tất
- Workflow sẽ mất khoảng 20-30 phút
- Download file IPA từ **Artifacts** khi build xong

## 🔧 Cách hoạt động

### Git LFS (Large File Storage)
Tất cả file lớn trong XCODE được quản lý bởi Git LFS:
- File `.a`, `.dll`, `.dylib`, `.bundle`
- File `.asset`, `.assets`, `.resS`, `.resource`
- File `.zip`, `.7z`, `.pak`
- File media: `.mp4`, `.wav`, `.mov`

### Workflow tự động
1. **Checkout repository** - Clone code và Git LFS files
2. **Setup Xcode** - Cài đặt Xcode latest
3. **Build & Archive** - Build project thành `.xcarchive`
4. **Export IPA** - Tạo file `.ipa` từ archive
5. **Upload Artifact** - Upload file `NROFLY.ipa`

## ⚠️ Lưu ý quan trọng

### KHÔNG dùng xcode-assets.zip nữa
- ❌ KHÔNG chạy `python auto_build_ipa.py` để tạo xcode-assets.zip
- ✅ Chỉ push code lên GitHub và chạy workflow

### Push tất cả file trong XCODE
- Tất cả file trong folder `XCODE/` sẽ được push đầy đủ
- Không có file nào bị ignore trong XCODE
- Git LFS tự động xử lý file lớn

## 📊 Kiểm tra Git LFS

### Xem file đang được track bởi LFS
```bash
git lfs ls-files
```

### Kiểm tra status
```bash
git lfs status
```

### Pull tất cả LFS files
```bash
git lfs pull
```

## 🚀 Workflow file

Workflow được cấu hình tại: `.github/workflows/build-ipa.yml`

### Các tính năng
- ✅ Tự động checkout Git LFS files
- ✅ Cache LFS objects để build nhanh hơn
- ✅ Build không cần code signing
- ✅ Tự động tạo IPA từ .app bundle nếu export thất bại
- ✅ Upload IPA artifact với retention 30 ngày

## 💡 Troubleshooting

### Build thất bại do thiếu file
```bash
# Verify tất cả LFS files đã được pull
git lfs fetch --all
git lfs checkout

# Kiểm tra file bị thiếu
git lfs ls-files | grep "not found"
```

### File quá lớn không push được
```bash
# Kiểm tra quota LFS (GitHub free: 1GB storage, 1GB bandwidth/month)
git lfs env

# Nếu vượt quota, cân nhắc:
# 1. Upgrade GitHub plan
# 2. Sử dụng Git LFS server riêng
# 3. Giảm kích thước assets
```

## 📝 So sánh với phương pháp cũ

| Tiêu chí | xcode-assets.zip (CŨ) | Git LFS (MỚI) |
|----------|----------------------|---------------|
| **Setup** | Phức tạp, cần Python script | Đơn giản, tự động |
| **Push/Pull** | Manual upload/download | Tự động với git |
| **File integrity** | Có thể thiếu file | Đầy đủ 100% |
| **Build success** | Thấp (thiếu .xcodeproj) | Cao |
| **Maintenance** | Khó, cần update script | Dễ, chỉ git push |
| **GitHub quota** | Không tốn (dùng Release) | Tốn LFS quota |

## ✅ Kết luận

**Dùng Git LFS** là phương pháp đơn giản, ổn định và chính thống nhất để quản lý file lớn trong Git.
