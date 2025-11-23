#!/usr/bin/env python3
"""
Auto Build IPA Tool
Tự động: Push code → Trigger workflow → Đợi build xong → Download IPA về máy
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

try:
    import requests
    import zipfile
    import shutil
except ImportError:
    print("❌ Cần cài đặt thư viện requests:")
    print("   pip install requests")
    sys.exit(1)

# ============== CẤU HÌNH ==============
REPO_OWNER = "cuong1206"
REPO_NAME = "IPA_UNITY_FULL"
WORKFLOW_FILE = "build-ipa.yml"
OUTPUT_DIR = "output"
BRANCH = "main"
XCODE_DIR = "XCODE"
ASSETS_ZIP = "xcode-assets.zip"

# GitHub API endpoints
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, message):
    """In ra bước thực hiện"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[Bước {step_num}]{Colors.ENDC} {message}")

def print_success(message):
    """In thông báo thành công"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """In thông báo lỗi"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_info(message):
    """In thông tin"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def print_warning(message):
    """In cảnh báo"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def get_github_token():
    """Lấy GitHub token từ environment hoặc user input"""
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print_warning("Chưa có GitHub Personal Access Token!")
        print_info("Tạo token tại: https://github.com/settings/tokens")
        print_info("Quyền cần thiết: repo, workflow, actions:read")
        token = input(f"{Colors.CYAN}Nhập GitHub Token: {Colors.ENDC}").strip()
    
    if not token:
        print_error("Không có token, không thể tiếp tục!")
        sys.exit(1)
    
    return token

def run_command(cmd, check=True, capture_output=False):
    """Chạy command và trả về kết quả"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True, encoding='utf-8')
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return None
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Lỗi khi chạy command: {cmd}")
            print_error(f"Error: {e}")
            sys.exit(1)
        return None

def is_file_locked(file_path):
    """Kiểm tra xem file có đang bị lock không"""
    if not file_path.exists():
        return False
    try:
        # Thử mở file để kiểm tra
        with open(file_path, 'a'):
            pass
        return False
    except (PermissionError, IOError):
        return True

def compress_xcode_assets():
    """Nén các file lớn trong XCODE thành ZIP"""
    print_step(0, "Nén file lớn từ XCODE...")
    
    xcode_path = Path(XCODE_DIR)
    if not xcode_path.exists():
        print_error(f"Thư mục {XCODE_DIR} không tồn tại!")
        return None
    
    # Kiểm tra file ZIP có đang được sử dụng không
    zip_path = Path(ASSETS_ZIP)
    if is_file_locked(zip_path):
        print_warning(f"File {ASSETS_ZIP} đang được sử dụng bởi process khác!")
        print_info("Có thể bạn đang chạy tool ở terminal khác. Đợi process đó hoàn thành hoặc dừng nó.")
        
        # Kiểm tra xem file có hợp lệ không
        if zip_path.exists() and zip_path.stat().st_size > 100 * 1024 * 1024:  # > 100MB
            print_success(f"File ZIP đã tồn tại và có vẻ hợp lệ ({zip_path.stat().st_size / (1024*1024):.2f} MB)")
            return str(zip_path)
        else:
            print_error("Không thể tạo file ZIP mới vì file đang bị lock và không hợp lệ")
            return None
    
    # Nén toàn bộ thư mục XCODE (không chỉ 3 thư mục con)
    print_info(f"Nén toàn bộ thư mục {XCODE_DIR}...")
    
    # Xóa file ZIP cũ nếu có
    if zip_path.exists():
        print_info(f"Xóa file ZIP cũ: {ASSETS_ZIP}")
        zip_path.unlink()
    
    print_info(f"Đang nén toàn bộ thư mục {XCODE_DIR} thành {ASSETS_ZIP}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Nén toàn bộ thư mục XCODE
            for root, dirs, files in os.walk(xcode_path):
                for file in files:
                    file_path = Path(root) / file
                    # Tạo archive name tương đối từ parent của XCODE
                    arcname = file_path.relative_to(xcode_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"\r   Đã nén: {arcname}", end='')
        
        print()  # New line
        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print_success(f"Đã tạo file ZIP: {ASSETS_ZIP} ({file_size_mb:.2f} MB)")
        return str(zip_path)
    except Exception as e:
        print_error(f"Lỗi khi nén file: {e}")
        return None

def get_or_create_release(token, tag_name):
    """Lấy hoặc tạo Release mới"""
    url = f"{API_BASE}/releases/tags/{tag_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Kiểm tra Release có tồn tại không
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print_success(f"Tìm thấy Release: {tag_name}")
        return response.json()
    
    # Tạo Release mới
    print_info(f"Tạo Release mới: {tag_name}")
    url = f"{API_BASE}/releases"
    payload = {
        "tag_name": tag_name,
        "name": f"XCODE Assets {tag_name}",
        "body": f"Large files for XCODE project build\n\nCreated automatically by auto_build_ipa.py",
        "draft": False,
        "prerelease": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print_success(f"Đã tạo Release: {tag_name}")
        return response.json()
    else:
        print_error(f"Lỗi khi tạo Release: {response.status_code}")
        print_error(response.text)
        return None

def delete_release_asset(token, asset_id):
    """Xóa asset khỏi Release"""
    url = f"{API_BASE}/releases/assets/{asset_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

def upload_to_release(token, release_id, file_path):
    """Upload file lên GitHub Release"""
    file_name = Path(file_path).name
    file_size = Path(file_path).stat().st_size
    file_size_mb = file_size / (1024*1024)
    
    # Xóa asset cũ nếu có
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    release_url = f"{API_BASE}/releases/{release_id}"
    response = requests.get(release_url, headers=headers)
    if response.status_code == 200:
        release_data = response.json()
        for asset in release_data.get('assets', []):
            if asset['name'] == file_name:
                print_info(f"Xóa asset cũ: {file_name}")
                delete_release_asset(token, asset['id'])
                break
    
    print_info(f"Đang upload {file_name} ({file_size_mb:.2f} MB)...")
    print_info("⏳ Upload có thể mất 5-15 phút tùy tốc độ mạng...")
    print_info("💡 Đang upload, vui lòng đợi... (không có progress bar cho upload lớn)")
    
    url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
    params = {"name": file_name}
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/zip"
    }
    
    start_time = time.time()
    
    try:
        # Upload file với timeout 30 phút
        with open(file_path, 'rb') as f:
            response = requests.post(
                url, 
                headers=headers, 
                params=params, 
                data=f,
                timeout=1800  # 30 phút
            )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 201:
            avg_speed = file_size_mb / elapsed if elapsed > 0 else 0
            print_success(f"Đã upload {file_name} lên Release!")
            print_info(f"Thời gian: {elapsed:.1f}s ({elapsed/60:.1f} phút) | Tốc độ trung bình: {avg_speed:.2f} MB/s")
            return response.json()
        else:
            print_error(f"Lỗi khi upload: {response.status_code}")
            print_error(response.text)
            if response.status_code == 413:
                print_error("File quá lớn! GitHub giới hạn 2 GB cho mỗi file.")
            elif response.status_code == 422:
                print_error("File không hợp lệ hoặc Release không tồn tại.")
            return None
            
    except requests.exceptions.Timeout:
        print_error("Upload timeout sau 30 phút!")
        print_info("💡 Thử lại hoặc kiểm tra kết nối mạng")
        return None
    except requests.exceptions.ConnectionError:
        print_error("Lỗi kết nối mạng!")
        print_info("💡 Kiểm tra kết nối internet và thử lại")
        return None
    except Exception as e:
        print_error(f"Lỗi khi upload: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_workflow_file(release_tag, asset_name):
    """Cập nhật workflow file với RELEASE_TAG và ASSET_NAME"""
    workflow_path = Path(f".github/workflows/{WORKFLOW_FILE}")
    
    if not workflow_path.exists():
        print_warning(f"Workflow file không tồn tại: {workflow_path}")
        return False
    
    # Đọc file
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cập nhật RELEASE_TAG và ASSET_NAME
    import re
    content = re.sub(
        r'RELEASE_TAG="[^"]*"',
        f'RELEASE_TAG="{release_tag}"',
        content
    )
    content = re.sub(
        r'ASSET_NAME="[^"]*"',
        f'ASSET_NAME="{asset_name}"',
        content
    )
    
    # Ghi lại file
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"Đã cập nhật workflow: RELEASE_TAG={release_tag}, ASSET_NAME={asset_name}")
    return True

def setup_releases(token):
    """Tự động setup GitHub Releases: Nén file, tạo Release, upload"""
    print_step(0, "Tự động setup GitHub Releases...")
    
    # Bước 1: Nén file
    zip_path = compress_xcode_assets()
    if not zip_path:
        print_error("Không thể nén file!")
        return False
    
    # Bước 2: Tạo tag và Release (dùng tag cố định)
    release_tag = "v1.0-latest"
    
    release = get_or_create_release(token, release_tag)
    if not release:
        return False
    
    release_id = release['id']
    
    # Bước 3: Upload file (có thể mất 5-15 phút)
    print_info("💡 Tip: Upload file lớn có thể mất 5-15 phút, vui lòng đợi...")
    asset = upload_to_release(token, release_id, zip_path)
    if not asset:
        print_error("Upload thất bại! Kiểm tra:")
        print_info("   1. Kết nối mạng có ổn định không?")
        print_info("   2. File có quá lớn không? (GitHub giới hạn 2 GB)")
        print_info("   3. GitHub Token có quyền 'repo' không?")
        return False
    
    asset_name = asset['name']
    
    # Bước 4: Đợi một chút để đảm bảo file đã có trên Releases
    print_info("Đợi 5 giây để đảm bảo file đã có trên Releases...")
    time.sleep(5)
    
    # Bước 5: Kiểm tra file có thực sự trên Releases không
    print_info("Kiểm tra file trên Releases...")
    release_check_url = f"{API_BASE}/releases/tags/{release_tag}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    check_response = requests.get(release_check_url, headers=headers)
    if check_response.status_code == 200:
        release_data = check_response.json()
        assets = release_data.get('assets', [])
        asset_found = any(a['name'] == asset_name for a in assets)
        if asset_found:
            print_success(f"Đã xác nhận file {asset_name} có trên Releases!")
        else:
            print_warning(f"File {asset_name} chưa thấy trên Releases, đợi thêm 10 giây...")
            time.sleep(10)
    
    print_success("Đã setup GitHub Releases thành công!")
    return True

def git_push(branch=BRANCH, force=False):
    """Push code lên GitHub"""
    print_step(1, "Đẩy code lên GitHub...")
    
    # Đảm bảo file ZIP không bị add vào git
    zip_path = Path(ASSETS_ZIP)
    if zip_path.exists():
        # Reset file ZIP nếu đã được staged
        run_command(f'git reset HEAD {ASSETS_ZIP}', check=False)
        # Đảm bảo file ZIP trong .gitignore
        run_command(f'git check-ignore -q {ASSETS_ZIP} || echo "{ASSETS_ZIP}" >> .gitignore', check=False)
    
    # Kiểm tra có thay đổi không (loại trừ file ZIP)
    status = run_command("git status --porcelain", capture_output=True)
    
    # Lọc bỏ file ZIP khỏi status
    if status:
        lines = status.split('\n')
        filtered_lines = [line for line in lines if ASSETS_ZIP not in line]
        status = '\n'.join(filtered_lines) if filtered_lines else None
    
    if not status:
        print_info("Không có thay đổi để commit")
        return False
    else:
        # Add và commit (không add file ZIP)
        print_info("Đang commit thay đổi...")
        run_command("git add -A")
        # Reset file ZIP nếu vẫn bị add
        run_command(f'git reset HEAD {ASSETS_ZIP}', check=False)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto build IPA - {timestamp}"
        run_command(f'git commit -m "{commit_msg}"', check=False)
    
    # Push
    print_info(f"Đang push lên branch {branch}...")
    push_cmd = f"git push origin {branch}"
    if force:
        push_cmd += " --force"
    
    run_command(push_cmd)
    print_success(f"Đã push code lên {branch}!")
    return True

def get_workflow_id(token, workflow_file):
    """Lấy workflow ID từ tên file"""
    url = f"{API_BASE}/actions/workflows"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        workflows = response.json().get('workflows', [])
        # Tìm workflow theo tên file
        for workflow in workflows:
            if workflow['path'].endswith(workflow_file) or workflow['name'] == workflow_file:
                return workflow['id']
        
        # Nếu không tìm thấy, thử tìm theo đường dẫn đầy đủ
        full_path = f".github/workflows/{workflow_file}"
        for workflow in workflows:
            if workflow['path'] == full_path:
                return workflow['id']
    
    return None

def trigger_workflow(token, build_config="Release"):
    """Trigger GitHub Actions workflow"""
    print_step(2, f"Kích hoạt workflow build IPA (config: {build_config})...")
    
    # Lấy workflow ID
    workflow_id = get_workflow_id(token, WORKFLOW_FILE)
    
    if not workflow_id:
        print_warning(f"Không tìm thấy workflow '{WORKFLOW_FILE}', thử dùng đường dẫn đầy đủ...")
        # Thử dùng đường dẫn đầy đủ
        workflow_path = f".github/workflows/{WORKFLOW_FILE}"
        url = f"{API_BASE}/actions/workflows/{workflow_path}/dispatches"
    else:
        print_info(f"Tìm thấy workflow ID: {workflow_id}")
        url = f"{API_BASE}/actions/workflows/{workflow_id}/dispatches"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "ref": BRANCH,
        "inputs": {
            "build_configuration": build_config
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 204:
        print_success("Đã kích hoạt workflow!")
        # Đợi 3 giây để workflow được tạo
        time.sleep(3)
        return True
    else:
        print_error(f"Lỗi khi trigger workflow: {response.status_code}")
        print_error(response.text)
        
        # Hiển thị danh sách workflows có sẵn để debug
        if response.status_code == 404:
            print_info("Đang liệt kê workflows có sẵn...")
            list_url = f"{API_BASE}/actions/workflows"
            list_response = requests.get(list_url, headers=headers)
            if list_response.status_code == 200:
                workflows = list_response.json().get('workflows', [])
                print_info(f"Tìm thấy {len(workflows)} workflow(s):")
                for wf in workflows:
                    print(f"   - {wf['name']} ({wf['path']})")
        
        return False

def get_latest_workflow_run(token):
    """Lấy workflow run mới nhất"""
    # Lấy workflow ID
    workflow_id = get_workflow_id(token, WORKFLOW_FILE)
    
    if workflow_id:
        url = f"{API_BASE}/actions/workflows/{workflow_id}/runs"
    else:
        # Fallback: dùng đường dẫn đầy đủ
        workflow_path = f".github/workflows/{WORKFLOW_FILE}"
        url = f"{API_BASE}/actions/workflows/{workflow_path}/runs"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "branch": BRANCH,
        "per_page": 1
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['workflow_runs']:
            return data['workflow_runs'][0]
    
    return None

def wait_for_workflow_completion(token, run_id, timeout=3600):
    """Đợi workflow hoàn thành"""
    print_step(3, "Đang đợi workflow build xong...")
    
    url = f"{API_BASE}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    start_time = time.time()
    last_status = None
    
    while True:
        if time.time() - start_time > timeout:
            print_error(f"Timeout sau {timeout}s!")
            return False
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print_error(f"Lỗi khi check status: {response.status_code}")
            return False
        
        run_data = response.json()
        status = run_data['status']
        conclusion = run_data.get('conclusion')
        
        # In progress nếu status thay đổi
        if status != last_status:
            elapsed = int(time.time() - start_time)
            print_info(f"Status: {status} | Đã chạy: {elapsed}s | URL: {run_data['html_url']}")
            last_status = status
        
        if status == 'completed':
            if conclusion == 'success':
                print_success(f"Build thành công! (Thời gian: {int(time.time() - start_time)}s)")
                return True
            else:
                print_error(f"Build thất bại! Conclusion: {conclusion}")
                print_error(f"Chi tiết: {run_data['html_url']}")
                return False
        
        # Đợi 10s trước khi check lại
        time.sleep(10)

def list_artifacts(token, run_id):
    """Liệt kê artifacts của workflow run"""
    url = f"{API_BASE}/actions/runs/{run_id}/artifacts"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['artifacts']
    
    return []

def download_artifact(token, artifact_id, artifact_name, output_dir):
    """Download artifact từ GitHub"""
    print_step(4, f"Đang tải file {artifact_name}...")
    
    # Tạo thư mục output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Download artifact (ZIP format)
    url = f"{API_BASE}/actions/artifacts/{artifact_id}/zip"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
    
    if response.status_code == 200:
        # Lưu file
        zip_file = output_path / f"{artifact_name}.zip"
        
        with open(zip_file, 'wb') as f:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Đang tải: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')
        
        print()  # New line
        print_success(f"Đã tải về: {zip_file}")
        
        # Giải nén nếu cần
        if artifact_name.endswith('.ipa'):
            # Artifact là .ipa nhưng GitHub wrap trong ZIP
            # Giải nén để lấy file IPA
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Lấy tên file đầu tiên trong zip
                    file_list = zip_ref.namelist()
                    if file_list:
                        ipa_file = file_list[0]
                        zip_ref.extract(ipa_file, output_path)
                        
                        # Đổi tên nếu cần
                        extracted_path = output_path / ipa_file
                        final_ipa = output_path / artifact_name
                        
                        if extracted_path != final_ipa:
                            extracted_path.rename(final_ipa)
                        
                        print_success(f"File IPA: {final_ipa}")
                        
                        # Xóa file ZIP
                        zip_file.unlink()
                        
                        return str(final_ipa)
            except Exception as e:
                print_warning(f"Không thể giải nén: {e}")
                print_info(f"File ZIP vẫn có tại: {zip_file}")
        
        return str(zip_file)
    else:
        print_error(f"Lỗi khi tải artifact: {response.status_code}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Auto Build IPA Tool - Tự động build và download IPA từ GitHub Actions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python auto_build_ipa.py                    # Tự động: Nén file → Upload Releases → Build → Download IPA
  python auto_build_ipa.py --config Debug     # Build Debug
  python auto_build_ipa.py --skip-releases    # Bỏ qua setup Releases (dùng Release có sẵn)
  python auto_build_ipa.py --no-push          # Chỉ trigger workflow, không push code
  python auto_build_ipa.py --output myipa     # Lưu IPA vào thư mục myipa/
  
Biến môi trường:
  GITHUB_TOKEN    GitHub Personal Access Token (cần quyền: repo, workflow)
  
Tính năng tự động:
  ✅ Tự động nén file lớn từ XCODE/ thành ZIP
  ✅ Tự động tạo GitHub Release với tag mới
  ✅ Tự động upload file ZIP lên Releases
  ✅ Tự động cập nhật workflow file
  ✅ Tự động trigger workflow build
  ✅ Tự động download IPA về máy
        """
    )
    
    parser.add_argument('--config', '-c', 
                       choices=['Release', 'Debug'],
                       default='Release',
                       help='Build configuration (mặc định: Release)')
    
    parser.add_argument('--no-push', 
                       action='store_true',
                       help='Không push code, chỉ trigger workflow')
    
    parser.add_argument('--output', '-o',
                       default=OUTPUT_DIR,
                       help=f'Thư mục lưu IPA (mặc định: {OUTPUT_DIR})')
    
    parser.add_argument('--force-push', '-f',
                       action='store_true',
                       help='Force push code (cẩn thận!)')
    
    parser.add_argument('--no-wait',
                       action='store_true',
                       help='Không đợi build xong, chỉ trigger và thoát')
    
    parser.add_argument('--skip-releases',
                       action='store_true',
                       help='Bỏ qua setup GitHub Releases (dùng Release có sẵn)')
    
    args = parser.parse_args()
    
    # Banner
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 AUTO BUILD IPA TOOL 🚀{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    print_info(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print_info(f"Branch: {BRANCH}")
    print_info(f"Build Config: {args.config}")
    print_info(f"Output: {args.output}/")
    
    # Lấy GitHub token
    token = get_github_token()
    
    # Bước 0: Setup GitHub Releases (tự động)
    if not args.skip_releases:
        if not setup_releases(token):
            print_error("Không thể setup GitHub Releases!")
            sys.exit(1)
    else:
        print_info("Bỏ qua setup GitHub Releases (--skip-releases)")
    
    # Bước 1: Push code (nếu cần)
    if not args.no_push:
        has_changes = git_push(branch=BRANCH, force=args.force_push)
        if not has_changes and not args.skip_releases:
            print_info("Không có thay đổi code, nhưng đã cập nhật Release")
    else:
        print_info("Bỏ qua push code (--no-push)")
    
    # Bước 2: Trigger workflow
    if not trigger_workflow(token, args.config):
        sys.exit(1)
    
    # Lấy workflow run mới nhất
    print_info("Đang tìm workflow run...")
    run = get_latest_workflow_run(token)
    
    if not run:
        print_error("Không tìm thấy workflow run!")
        sys.exit(1)
    
    run_id = run['id']
    print_success(f"Workflow Run ID: {run_id}")
    print_info(f"URL: {run['html_url']}")
    
    # Bước 3: Đợi workflow hoàn thành
    if args.no_wait:
        print_info("Không đợi build xong (--no-wait)")
        print_info(f"Theo dõi tại: {run['html_url']}")
        sys.exit(0)
    
    if not wait_for_workflow_completion(token, run_id, timeout=3600):
        sys.exit(1)
    
    # Bước 4: Download artifacts
    print_info("Đang tìm artifacts...")
    artifacts = list_artifacts(token, run_id)
    
    if not artifacts:
        print_warning("Không tìm thấy artifacts!")
        sys.exit(1)
    
    print_success(f"Tìm thấy {len(artifacts)} artifact(s)")
    
    downloaded_files = []
    for artifact in artifacts:
        artifact_name = artifact['name']
        artifact_id = artifact['id']
        
        # Chỉ download IPA artifacts
        if 'ipa' in artifact_name.lower():
            file_path = download_artifact(token, artifact_id, artifact_name, args.output)
            if file_path:
                downloaded_files.append(file_path)
    
    # Kết quả
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 HOÀN TẤT! 🎉{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}\n")
    
    if downloaded_files:
        print_success(f"Đã tải về {len(downloaded_files)} file:")
        for file_path in downloaded_files:
            print(f"   📦 {file_path}")
            print_info(f"      Kích thước: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
    else:
        print_warning("Không có file nào được tải về!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Bị hủy bởi người dùng{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

