# phu_bep.py - Bộ xử lý trợ lý phụ bếp giúp quy đổi nguyên liệu theo số người ăn.
from model import doc_cong_thuc  # Dùng dữ liệu công thức hiện có của SmartCook AI.

def dinh_dang_so(so):  # Hiển thị số lượng gọn, không để số thập phân dài.
    return str(int(so)) if float(so).is_integer() else str(round(so, 2)).rstrip("0").rstrip(".")

def tao_ke_hoach_phu_bep(ma_mon, so_nguoi):  # Tạo bảng nguyên liệu đã quy đổi và hướng dẫn nấu.
    ds_mon = doc_cong_thuc()  # Đọc danh sách công thức từ data.json.
    mon = next((m for m in ds_mon if int(m["id"]) == int(ma_mon)), None)  # Tìm món theo mã.
    if mon is None:  # Kiểm tra món có tồn tại trong dữ liệu hay không.
        raise ValueError("Không tìm thấy món ăn bạn đã chọn.")  # Báo lỗi rõ ràng nếu mã món sai.
    so_nguoi = int(so_nguoi)  # Chuyển số người về số nguyên để kiểm tra chính xác.
    if not 1 <= so_nguoi <= 50:  # Kiểm tra giới hạn số người mà giao diện công bố.
        raise ValueError("Số người ăn phải nằm trong khoảng từ 1 đến 50.")  # Báo lỗi thay vì tự ý đổi số người.
    he_so = so_nguoi / 2  # Định lượng gốc được ước tính cho hai người.
    nguyen_lieu = []  # Tạo danh sách nguyên liệu đã tính lại.
    for ten, dinh_luong in mon.get("dinh_luong_2_nguoi", {}).items():  # Duyệt định lượng gốc từng nguyên liệu.
        so_luong = float(dinh_luong["so_luong"]) * he_so  # Nhân định lượng theo tỷ lệ số người ăn.
        don_vi = dinh_luong["don_vi"]  # Giữ nguyên đơn vị đo ban đầu.
        nguyen_lieu.append({"ten": ten, "so_luong": dinh_dang_so(so_luong), "don_vi": don_vi})  # Lưu dòng nguyên liệu đã quy đổi.
    ghi_chu = "Định lượng tham khảo, nên nêm gia vị từng ít một rồi nếm lại theo khẩu vị gia đình."  # Nhắc điều chỉnh gia vị an toàn.
    if so_nguoi >= 8:  # Nêu lưu ý riêng khi nấu số lượng lớn.
        ghi_chu += " Với nồi lớn, hãy dùng nồi đủ dung tích, tăng thời gian làm nóng/ninh khi cần và kiểm tra độ chín kỹ."
    return {"mon": mon, "so_nguoi": so_nguoi, "nguyen_lieu": nguyen_lieu, "ghi_chu": ghi_chu}  # Trả dữ liệu cho trang web.
