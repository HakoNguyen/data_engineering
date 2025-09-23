# XWeather Backend API

Backend API đơn giản để cung cấp dữ liệu bão cho frontend visualization. Dữ liệu được lấy từ database (đã được Airflow xử lý).

## Kiến trúc

```
Airflow DAGs → Database (PostgreSQL) → Backend API → Frontend
```

- **Airflow**: Lấy dữ liệu từ XWeather API và lưu vào database
- **Backend**: Chỉ đọc dữ liệu từ database và cung cấp API endpoints
- **Frontend**: Sử dụng API để hiển thị dữ liệu

## Tính năng

- **API đơn giản**: Chỉ đọc dữ liệu từ database
- **RESTful endpoints**: Cho storm, track, forecast data
- **GeoJSON support**: Cho map visualization
- **CORS enabled**: Cho frontend integration
- **Database stats**: Thống kê dữ liệu trong database

## API Endpoints

### Storms (Bão)

- `GET /api/v1/storms` - Danh sách bão
- `GET /api/v1/storms/active` - Bão đang hoạt động
- `GET /api/v1/storms/{storm_id}` - Chi tiết bão
- `GET /api/v1/storms/{storm_id}/geojson` - Dữ liệu GeoJSON

### Tracks (Đường đi)

- `GET /api/v1/tracks/storm/{storm_id}` - Đường đi bão
- `GET /api/v1/tracks/storm/{storm_id}/path` - Đường đi GeoJSON
- `GET /api/v1/tracks/storm/{storm_id}/current-position` - Vị trí hiện tại

### Forecasts (Dự báo)

- `GET /api/v1/forecasts/storm/{storm_id}` - Dự báo bão
- `GET /api/v1/forecasts/storm/{storm_id}/track-forecast` - Đường đi dự báo
- `GET /api/v1/forecasts/storm/{storm_id}/cone` - Hình nón dự báo

### Database Management

- `GET /api/v1/database/stats` - Thống kê database
- `POST /api/v1/database/cleanup` - Dọn dẹp dữ liệu cũ

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình database

Đảm bảo database đã có dữ liệu từ Airflow:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/xweather
```

### 3. Migration dữ liệu (nếu cần)

```bash
# Từ CSV files
python migrate_data.py --csv-dir /path/to/csv/files

# Tạo dữ liệu mẫu
python migrate_data.py --create-sample
```

### 4. Chạy backend

```bash
python run.py
```

API sẽ có sẵn tại: `http://localhost:8000`

## Cấu trúc Database

### Bảng `storm`

- `storm_id`: ID bão (primary key)
- `name`: Tên bão
- `start_time`: Thời gian bắt đầu
- `basin`: Vùng biển (AL, EP, CP, WP, IO, SH)
- `event`: Loại sự kiện
- `storm_type`: Loại bão
- `storm_cat`: Cấp độ bão
- `lon`, `lat`: Tọa độ hiện tại

### Bảng `track`

- `id`: ID track (primary key)
- `storm_id`: ID bão (foreign key)
- `track_time`: Thời gian
- `track_name`: Tên bão
- `storm_type`, `storm_cat`: Loại và cấp độ
- `advisory`: Số báo cáo
- `directionDEG`: Hướng di chuyển
- `speed`: Tốc độ di chuyển
- `wind_speed`: Tốc độ gió
- `gust_speed`: Tốc độ gió giật
- `pressure`: Áp suất
- `lon`, `lat`: Tọa độ

### Bảng `forecast`

- Cấu trúc tương tự `track` nhưng cho dữ liệu dự báo

## Tích hợp với Frontend

Backend cung cấp dữ liệu phù hợp cho:

- **StormMap.jsx**: Hiển thị bản đồ bão
- **GeoJSON format**: Cho map visualization
- **RESTful API**: Dễ dàng tích hợp với React

## Lưu ý

1. **Không cần XWeather API credentials** - dữ liệu đã có trong database
2. **Airflow xử lý data ingestion** - backend chỉ đọc dữ liệu
3. **Database phải có dữ liệu** - chạy Airflow DAGs trước
4. **Đơn giản và nhanh** - không có background processes phức tạp
