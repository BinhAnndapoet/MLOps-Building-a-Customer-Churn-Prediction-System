# 🚀 Hướng Dẫn Thiết Lập Floci & Tích Hợp DVC (Local S3)

Tài liệu này mô tả quy trình thiết lập **Floci** (AWS Local Emulator) để cung cấp dịch vụ **S3 cục bộ**, phục vụ việc lưu trữ dữ liệu bằng **DVC (Data Version Control)** trong dự án **MLOps-Building-a-Customer-Churn-Prediction-System**.

---
## 📥 1. Chuẩn Bị: Clone Floci Về Máy

Trước khi khởi tạo môi trường AWS cục bộ, cần tải mã nguồn Floci về máy.

Mở Terminal hoặc PowerShell và thực hiện:

```text
cd D:\MLOps\
git clone https://github.com/floci-io/floci.git
```
---

---

## 📁 2. Cấu Trúc Thư Mục

Để tách biệt dữ liệu hạ tầng khỏi mã nguồn dự án, tổ chức thư mục theo cấu trúc sau:

```text
D:\MLOps\
├── floci\                                              # Local AWS Server (S3, Redis...)
│   ├── compose.yaml
│   └── data\                                           # Nơi lưu trữ dữ liệu vật lý
│
└── MLOps-Building-a-Customer-Churn-Prediction-System\  # Source Code
    ├── data-pipeline\
    ├── requirements.txt
    └── ...
```

---

## 🐳 3. Thiết Lập Floci (Local AWS)

### Bước 3.1: Tạo file `compose.yaml`

Di chuyển vào thư mục `floci` và tạo file `compose.yaml`:

```yaml
services:
  floci:
    image: floci/floci:latest
    ports:
      - "4566:4566"
    environment:
      - FLOCI_STORAGE_MODE=hybrid
      - FLOCI_STORAGE_PERSISTENT_PATH=/data
    volumes:
      - ./data:/data
```

**Ý nghĩa cấu hình:**

* `FLOCI_STORAGE_MODE=hybrid`: Cho phép lưu dữ liệu bền vững.
* `FLOCI_STORAGE_PERSISTENT_PATH=/data`: Đường dẫn lưu dữ liệu bên trong container.
* `./data:/data`: Mount dữ liệu ra thư mục host để không bị mất khi container dừng.

---

### Bước 3.2: Khởi động Floci

> Yêu cầu: Docker Desktop đang chạy.

```powershell
cd D:\MLOps\floci
docker compose up -d
```

Kiểm tra container:

```powershell
docker ps
```

---

## ☁️ 4. Cấu Hình AWS CLI & Tạo Bucket S3

Thiết lập biến môi trường để AWS CLI trỏ tới Floci thay vì AWS Cloud.

### PowerShell

```powershell
$env:AWS_ENDPOINT_URL="http://localhost:4566"
$env:AWS_DEFAULT_REGION="us-east-1"
$env:AWS_ACCESS_KEY_ID="test"
$env:AWS_SECRET_ACCESS_KEY="test"
```

### Tạo Bucket S3

```powershell
aws s3 mb s3://churn-data
```

### Kiểm tra Bucket

```powershell
aws s3 ls
```

Kết quả mong đợi:

```text
2025-xx-xx xx:xx:xx churn-data
```

---

## 🔗 5. Tích Hợp DVC Với Floci S3

Di chuyển vào thư mục dự án:

```powershell
cd D:\MLOps\MLOps-Building-a-Customer-Churn-Prediction-System
```

### Bước 1: Khai báo remote storage

```powershell
dvc remote add -d local-s3 s3://churn-data/dvc-store
```

### Bước 2: Trỏ DVC tới Floci

```powershell
dvc remote modify local-s3 endpointurl http://localhost:4566
```

### Bước 3: Cấu hình credentials

```powershell
dvc remote modify local-s3 access_key_id test

dvc remote modify local-s3 secret_access_key test

dvc remote modify local-s3 region us-east-1
```

### Kiểm tra cấu hình

```powershell
dvc remote list
```

Kết quả:

```text
local-s3    s3://churn-data/dvc-store (default)
```

---

## 🔄 6. Workflow Hàng Ngày

Sau khi hoàn tất thiết lập, quy trình làm việc sẽ như sau:

### 1. Chạy pipeline xử lý dữ liệu

```powershell
python data-pipeline/scripts/split_data.py
```

### 2. Theo dõi dữ liệu bằng DVC

```powershell
dvc add data-pipeline/data/raw/train_period_1.csv
```

DVC sẽ tạo:

```text
train_period_1.csv.dvc
```

### 3. Commit metadata lên Git

```powershell
git add train_period_1.csv.dvc .gitignore
git commit -m "Track training dataset with DVC"
```

### 4. Đẩy dữ liệu lên Local S3

```powershell
dvc push
```

---

## ✅ 7. Kiểm Tra Dữ Liệu Đã Được Lưu Trữ

### Cách 1: Kiểm tra trạng thái DVC

```powershell
dvc status -c
```

Kết quả mong đợi:

```text
Data and pipelines are up to date.
```

---

### Cách 2: Kiểm tra qua AWS CLI

```powershell
aws s3 ls s3://churn-data/dvc-store --recursive
```

Kết quả mong đợi:

```text
2025-xx-xx xx:xx:xx    12345  files/md5/ab/cdef123456...
```

Các file này chính là object được DVC lưu trữ theo hash.

---

### Cách 3: Kiểm tra trực tiếp trên ổ cứng

Mở thư mục:

```text
D:\MLOps\floci\data
```

Bạn sẽ thấy toàn bộ object được DVC push lên S3 được lưu vật lý tại đây.

---

## 📥 8. Khôi Phục Dữ Liệu Từ Remote

Nếu clone project trên máy mới:

```powershell
git clone <repository-url>

cd MLOps-Building-a-Customer-Churn-Prediction-System
```

Sau khi cấu hình DVC remote:

```powershell
dvc pull
```

DVC sẽ tải dữ liệu từ Floci S3 về thư mục làm việc.

---

## 🛠️ Troubleshooting

### Floci không khởi động

Kiểm tra Docker:

```powershell
docker ps -a
docker logs <container-id>
```

### DVC không kết nối được S3

Kiểm tra endpoint:

```powershell
aws s3 ls --endpoint-url http://localhost:4566
```

### Kiểm tra cấu hình DVC

```powershell
dvc remote list
dvc remote modify --list local-s3
```

---

## 🔮 Mở Rộng Trong Tương Lai

Floci không chỉ hỗ trợ S3 mà còn hỗ trợ nhiều dịch vụ AWS giả lập khác như:

* Redis (ElastiCache)
* SNS
* SQS
* Lambda
* DynamoDB

Trong giai đoạn tiếp theo của dự án, Redis có thể được sử dụng làm **Feast Online Store** phục vụ inference thời gian thực.

---

## 📌 Tóm Tắt

```text
Data Pipeline
      │
      ▼
  DVC Add
      │
      ▼
  DVC Push
      │
      ▼
 Local S3 (Floci)
      │
      ▼
  Persistent Storage
(D:\MLOps\floci\data)
```

Mô hình này giúp:

✅ Version hóa dữ liệu bằng DVC
✅ Lưu trữ dữ liệu cục bộ như AWS S3
✅ Không làm phình repository Git
✅ Dễ dàng mở rộng sang MLOps production trong tương lai
