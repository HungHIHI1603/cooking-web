# SmartCook AI — phiên bản nâng cấp

## 1. Chức năng
- `/` — Trang chủ giới thiệu ứng dụng.
- `/nguyen-lieu` — Tìm món theo nguyên liệu đang có; danh sách gợi ý nhanh đã được mở rộng.
- `/cong-thuc` — Thư viện công thức, tìm kiếm và lọc món.
- `/cong-thuc/<id>` — Chi tiết món và gợi ý các món tương tự.
- `/phu-bep` — Quy đổi định lượng tham khảo theo số người ăn (1–50 người).
- `/api/mon-an` — API nội bộ trả danh sách món theo điều kiện tìm kiếm.
- `/api/cong-thuc/<id>/tuong-tu` — API nội bộ trả món tương tự.

## 2. Thuật toán gợi ý
Ứng dụng sử dụng Content-Based Filtering, không gọi API AI bên ngoài. Mỗi món được so sánh theo:
- Nguyên liệu: 50%.
- Danh mục món ăn: 15%.
- Thời gian nấu: 10%.
- Cách chế biến: 25%.

Công thức:
`Điểm = 0.50 × Jaccard_nguyên_liệu + 0.15 × Điểm_danh_mục + 0.10 × Điểm_thời_gian + 0.25 × Jaccard_cách_chế_biến`

Hệ số Jaccard:
`J(A, B) = |A giao B| / |A hợp B|`

Điểm thời gian:
`max(0, 1 - abs(thời_gian_A - thời_gian_B) / 120)`

Các trọng số là tham số thiết kế ban đầu, chưa được tối ưu bằng thực nghiệm. Trường `cach_che_bien` đã được bổ sung cho 20 công thức trong `data.json`.

## 3. Phụ Bếp
Tệp `phu_bep.py` quy đổi lượng nguyên liệu theo công thức tham khảo:
`Lượng mới = Lượng gốc cho 2 người × số người / 2`

Các định lượng gốc là dữ liệu tham khảo trong đồ án, không thay thế việc nếm và điều chỉnh gia vị khi nấu. Số người hợp lệ từ 1 đến 50; dữ liệu ngoài giới hạn sẽ được báo lỗi thay vì âm thầm tự đổi số.

## 4. AI/API key
- Không tích hợp OpenAI, Gemini, Claude hoặc API AI bên ngoài.
- Không cần API key cho phiên bản hiện tại.
- API trong dự án là các tuyến nội bộ do Flask cung cấp.
- Dữ liệu món ăn được đọc từ `data.json`.

## 5. Cài đặt và chạy
1. Cài Python 3.10 trở lên.
2. Mở Terminal tại thư mục có `app.py`.
3. Chạy `python -m pip install -r requirements.txt`.
4. Chạy `python app.py`.
5. Mở `http://127.0.0.1:5000` trong trình duyệt.

## 6. Chạy kiểm thử
Sau khi cài Flask, chạy:
`python -m unittest -v`

Bộ kiểm thử kiểm tra việc đọc dữ liệu, điểm tương đồng, gợi ý món, tìm nguyên liệu, quy đổi Phụ Bếp và các trang/API Flask cơ bản.

## Phiên bản mở rộng kho công thức và trang sơ chế

- Kho dữ liệu hiện có **72 công thức**; mỗi món có danh mục, thời gian nấu, nguyên liệu, định lượng tham khảo cho 2 người, các bước nấu và nhãn cách chế biến.
- Mỗi nguyên liệu có trường `so_che` mô tả cách làm sạch/cắt/chuẩn bị trước khi nấu.
- Trang chi tiết `/cong-thuc/<ma_mon>` trình bày hai cột: bên trái là công thức nấu từng bước, bên phải là bảng sơ chế và định lượng nguyên liệu. Người dùng có thể đánh dấu từng nguyên liệu đã chuẩn bị.
- Trang chủ `/` là trang giới thiệu riêng; `/cong-thuc` là thư viện công thức riêng; nhấn một món sẽ mở trang chi tiết riêng.
- Hệ gợi ý vẫn theo Content-Based Filtering. Các đặc trưng bám theo đề tài trong tài liệu môn học: nguyên liệu, loại món, thời gian nấu; cách chế biến được bổ sung để đáp ứng phần mục tiêu đề tài.
- Các định lượng là mức tham khảo cho 2 người, cần điều chỉnh theo khẩu vị, kích thước nguyên liệu và thực tế chế biến. Không xem hệ số quy đổi gia vị là tuyệt đối.

### Kiểm thử

Cài Flask bằng `python -m pip install -r requirements.txt`, sau đó chạy:

```powershell
python -m unittest -v
```

Khởi động website:

```powershell
python app.py
```
