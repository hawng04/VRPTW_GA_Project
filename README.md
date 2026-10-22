# Đồ án: Giải quyết Bài toán Định tuyến xe có Cửa sổ thời gian (VRPTW) bằng Giải thuật Di truyền (GA)

**Tác giả:** Bảo Hân
**Ngôn ngữ lập trình:** Python 3.x

## Tổng quan dự án
Dự án này cài đặt Giải thuật Di truyền (Genetic Algorithm) kết hợp cơ chế giải mã Split để giải quyết bài toán VRPTW trên bộ dữ liệu chuẩn Solomon Benchmark (ví dụ: RC101, C101, R101).

## Yêu cầu hệ thống (Prerequisites)
- Python 3.8 trở lên.
- Git (để quản lý mã nguồn).

## Hướng dẫn cài đặt

**Bước 1: Clone dự án và di chuyển vào thư mục gốc**
git clone <link_git_cua_ban>
cd VRPTW_GA_Project

**Bước 2: Tạo môi trường ảo (Khuyên dùng)**
python -m venv venv

**Bước 3: Kích hoạt môi trường ảo**
- Trên Windows (PowerShell/CMD):
  .\venv\Scripts\activate
- Trên Linux/Mac/WSL:
  source venv/bin/activate

**Bước 4: Cài đặt thư viện phụ thuộc**
pip install -r requirements.txt

## Cấu trúc thư mục cốt lõi
- `/data/`: Chứa các tệp dữ liệu Solomon (.txt).
- `/src/dataloader.py`: Module trích xuất dữ liệu ma trận.
- `/src/main.py`: File cấu hình và khởi chạy toàn bộ hệ thống.

## Cách chạy chương trình
Từ thư mục gốc (đảm bảo đã kích hoạt môi trường ảo venv), chạy lệnh sau:

python src/main.py