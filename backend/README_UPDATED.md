# XWeather Backend API - Cập nhật cho XWeather API

Backend API đã được cập nhật để phù hợp với dữ liệu thực tế từ XWeather API.

## Thay đổi chính

### 1. Cấu trúc Database mới

- **Bảng `storm`**: Thay đổi từ `storms` để phù hợp với XWeather API
- **Bảng `track`**: Thay đổi từ `tracks` với cấu trúc dữ liệu mới
- **Bảng `forecast`**: Thay đổi từ `forecasts` với cấu trúc dữ liệu mới

### 2. Dữ liệu XWeather API

Dữ liệu được lấy từ XWeather API với cấu trúc:

```json
{
  "response": [
    {
      "id": "storm_id",
      "profile": {
        "name": "Storm Name",
        "basinCurrent": "AL",
        "event": "Hurricane",
        "maxStormType": "Hurricane",
        "maxStormCat": "H3",
        "lifespan": {
          "startDateTimeISO": "2024-01-01T00:00:00Z"
        }
      },
      "position": {
        "location": {
          "coordinates": [-80.0, 25.0]
        }
      },
      "track": [...],
      "forecast": [...]
    }
  ]
}
```

### 3. Cấu trúc dữ liệu mới

#### Storm (Bão)

- `storm_id`: ID bão từ XWeather API
- `name`: Tên bão
- `start_time`: Thời gian bắt đầu (startDateTimeISO)
- `basin`: Vùng biển (AL, EP, CP, WP, IO, SH)
- `event`: Loại sự kiện
- `storm_type`: Loại bão (maxStormType)
- `storm_cat`: Cấp độ bão (maxStormCat)
- `lon`, `lat`: Tọa độ hiện tại

#### Track (Đường đi)

- `storm_id`: ID bão
- `track_time`: Thời gian (dateTimeISO)
- `track_name`: Tên bão tại thời điểm đó
- `storm_type`, `storm_cat`: Loại và cấp độ bão
- `advisory`: Số báo cáo
- `directionDEG`: Hướng di chuyển (độ)
- `speed`: Tốc độ di chuyển (knots)
- `wind_speed`: Tốc độ gió (km/h)
- `gust_speed`: Tốc độ gió giật (km/h)
- `pressure`: Áp suất (mb)
- `lon`, `lat`: Tọa độ

#### Forecast (Dự báo)

- Cấu trúc tương tự Track nhưng cho dữ liệu dự báo

## Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Tạo file `.env` với nội dung:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/xweather
XWEATHER_CLIENT_ID=your_client_id
XWEATHER_CLIENT_SECRET=your_client_secret
```

### 3. Migration dữ liệu

```bash
# Từ CSV files
python migrate_data.py --csv-dir /path/to/csv/files

# Tạo dữ liệu mẫu
python migrate_data.py --create-sample
```

### 4. Chạy ứng dụng

```bash
python run.py
```

## API Endpoints

### Storms

- `GET /api/v1/storms` - Danh sách bão
- `GET /api/v1/storms/active` - Bão đang hoạt động
- `GET /api/v1/storms/{storm_id}` - Chi tiết bão
- `GET /api/v1/storms/{storm_id}/geojson` - Dữ liệu GeoJSON cho visualization

### Tracks

- `GET /api/v1/tracks/storm/{storm_id}` - Đường đi bão
- `GET /api/v1/tracks/storm/{storm_id}/path` - Đường đi dạng GeoJSON
- `GET /api/v1/tracks/storm/{storm_id}/current-position` - Vị trí hiện tại

### Forecasts

- `GET /api/v1/forecasts/storm/{storm_id}` - Dự báo bão
- `GET /api/v1/forecasts/storm/{storm_id}/track-forecast` - Đường đi dự báo
- `GET /api/v1/forecasts/storm/{storm_id}/cone` - Hình nón dự báo

## Tích hợp với Frontend

Backend đã được cập nhật để cung cấp dữ liệu phù hợp với:

- **StormMap.jsx**: Hiển thị bản đồ bão
- **Dữ liệu GeoJSON**: Cho visualization
- **API endpoints**: Tương thích với cấu trúc dữ liệu XWeather

## Lưu ý

1. **XWeather API**: Cần credentials hợp lệ để lấy dữ liệu thực
2. **Mock Data**: Sử dụng dữ liệu giả khi không có credentials
3. **Database**: Sử dụng PostgreSQL với cấu trúc mới
4. **Migration**: Script migration có sẵn để chuyển đổi dữ liệu cũ
