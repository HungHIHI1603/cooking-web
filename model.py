# Nạp thư viện chuẩn để đọc JSON, xử lý chuỗi và chuẩn hóa tiếng Việt.
import json  # Đọc dữ liệu công thức từ tệp JSON.
import re  # Tách nguyên liệu và chuẩn hóa khoảng trắng.
import unicodedata  # Chuẩn hóa dấu tiếng Việt khi tìm kiếm.
from pathlib import Path  # Tạo đường dẫn tệp độc lập với hệ điều hành.

# Xác định vị trí data.json nằm cùng thư mục với model.py.
DUONG_DAN_DATA = Path(__file__).with_name("data.json")

# Đọc toàn bộ công thức từ tệp dữ liệu JSON.
def doc_cong_thuc():
    # Mở tệp ở chế độ đọc và dùng UTF-8 để giữ nguyên tiếng Việt.
    with DUONG_DAN_DATA.open("r", encoding="utf-8") as tep:
        # Chuyển nội dung JSON thành danh sách và từ điển của Python.
        ds_mon = json.load(tep)
    # Trả dữ liệu cho các chức năng khác sử dụng.
    return ds_mon

# Chuẩn hóa văn bản để tìm kiếm không phân biệt chữ hoa, chữ thường và dấu.
def bo_dau(chuoi):
    # Chuyển văn bản về chữ thường và tách dấu khỏi ký tự gốc.
    chuoi = unicodedata.normalize("NFD", str(chuoi).lower().strip())
    # Loại bỏ các ký tự dấu kết hợp.
    chuoi = "".join(ch for ch in chuoi if unicodedata.category(ch) != "Mn")
    # Gộp nhiều khoảng trắng liên tiếp thành một khoảng trắng.
    return re.sub(r"\s+", " ", chuoi)

# Tách danh sách nguyên liệu do người dùng nhập.
def tach_nguyen_lieu(chuoi):
    # Chia chuỗi theo dấu phẩy, chấm phẩy hoặc xuống dòng và bỏ mục rỗng.
    return [x.strip() for x in re.split(r"[,;\n]+", str(chuoi or "")) if x.strip()]

# Tính Jaccard cho hai danh sách đặc trưng dạng văn bản.
def diem_jaccard(ds_a, ds_b):
    # Chuẩn hóa từng phần tử rồi tạo tập hợp để loại phần tử trùng.
    tap_a = {bo_dau(x) for x in ds_a if str(x).strip()}
    # Chuẩn hóa tập đặc trưng thứ hai.
    tap_b = {bo_dau(x) for x in ds_b if str(x).strip()}
    # Tính số phần tử chung giữa hai tập hợp.
    giao = len(tap_a & tap_b)
    # Tính số phần tử khác nhau trong hợp của hai tập hợp.
    hop = len(tap_a | tap_b)
    # Nếu cả hai tập đều rỗng thì trả 0 để tránh chia cho 0.
    return giao / hop if hop else 0.0

# Tính chi tiết các điểm tương đồng của hai món ăn.
def chi_tiet_diem_tuong_dong(mon_goc, mon_so_sanh):
    # So sánh tập nguyên liệu bằng hệ số Jaccard.
    diem_nguyen_lieu = diem_jaccard(mon_goc.get("nguyen_lieu", []), mon_so_sanh.get("nguyen_lieu", []))
    # So sánh danh mục và cho điểm 1 nếu hai món cùng danh mục.
    diem_loai = 1.0 if bo_dau(mon_goc.get("loai", "")) == bo_dau(mon_so_sanh.get("loai", "")) else 0.0
    # Lấy thời gian nấu của hai món và chuyển về số nguyên an toàn.
    thoi_gian_goc = int(mon_goc.get("thoi_gian", 0) or 0)
    # Lấy thời gian nấu của món so sánh.
    thoi_gian_khac = int(mon_so_sanh.get("thoi_gian", 0) or 0)
    # Tính chênh lệch thời gian tuyệt đối.
    chenhlech = abs(thoi_gian_goc - thoi_gian_khac)
    # Quy đổi chênh lệch thời gian thành điểm từ 0 đến 1; chênh 120 phút trở lên được 0.
    diem_thoi_gian = max(0.0, 1.0 - chenhlech / 120.0)
    # So sánh các nhãn cách chế biến bằng hệ số Jaccard.
    diem_che_bien = diem_jaccard(mon_goc.get("cach_che_bien", []), mon_so_sanh.get("cach_che_bien", []))
    # Kết hợp bốn đặc trưng với trọng số được thiết kế cho phiên bản này.
    diem_tong = diem_nguyen_lieu * 0.50 + diem_loai * 0.15 + diem_thoi_gian * 0.10 + diem_che_bien * 0.25
    # Trả điểm từng thành phần và điểm tổng hợp để có thể giải thích kết quả.
    return {
        "nguyen_lieu": round(diem_nguyen_lieu, 4),
        "danh_muc": round(diem_loai, 4),
        "thoi_gian": round(diem_thoi_gian, 4),
        "cach_che_bien": round(diem_che_bien, 4),
        "tong": round(diem_tong, 4),
    }

# Trả điểm tương đồng tổng hợp giữa hai món ăn.
def diem_tuong_dong(mon_goc, mon_so_sanh):
    # Lấy trường tổng từ hàm tính điểm chi tiết.
    return chi_tiet_diem_tuong_dong(mon_goc, mon_so_sanh)["tong"]

# Kiểm tra nguyên liệu nhập có khớp với tên nguyên liệu trong công thức hay không.
def nguyen_lieu_khop(nguyen_lieu_nhap, nguyen_lieu_trong_mon):
    # Chuẩn hóa hai chuỗi để so sánh không phụ thuộc dấu và chữ hoa.
    nhap = bo_dau(nguyen_lieu_nhap)
    # Chuẩn hóa tên nguyên liệu trong công thức.
    trong_mon = bo_dau(nguyen_lieu_trong_mon)
    # Khớp nếu tên nguyên liệu bằng nhau hoặc một tên dài chứa cụm nguyên liệu người dùng nhập.
    # Giới hạn cụm nhập tối thiểu 3 ký tự để giảm khớp nhầm các từ quá ngắn như "cá".
    return nhap == trong_mon or (len(nhap) >= 3 and nhap in trong_mon) or (len(trong_mon) >= 3 and trong_mon in nhap)

# Tìm món phù hợp với nguyên liệu có sẵn, từ khóa, danh mục và giới hạn thời gian.
def goi_y_mon_an(ds_mon, nguyen_lieu_co_san=None, tu_khoa="", loai="Tất cả", thoi_gian_toi_da=None):
    # Chuẩn hóa từng nguyên liệu người dùng đang có.
    san_co = [bo_dau(x) for x in (nguyen_lieu_co_san or []) if str(x).strip()]
    # Chuẩn hóa từ khóa tìm kiếm.
    q = bo_dau(tu_khoa)
    # Tạo danh sách kết quả ban đầu.
    ket_qua = []
    # Duyệt qua từng món trong dữ liệu.
    for mon in ds_mon:
        # Bỏ qua món không thuộc danh mục đã chọn.
        if loai != "Tất cả" and mon.get("loai") != loai:
            continue
        # Bỏ qua món có thời gian vượt giới hạn người dùng chọn.
        if thoi_gian_toi_da is not None and int(mon.get("thoi_gian", 0)) > thoi_gian_toi_da:
            continue
        # Ghép tên, mô tả, danh mục, nguyên liệu và cách chế biến để tìm kiếm.
        van_ban = " ".join([mon.get("ten", ""), mon.get("mo_ta", ""), mon.get("loai", ""), *mon.get("nguyen_lieu", []), *mon.get("cach_che_bien", [])])
        # Bỏ qua món nếu không chứa từ khóa sau chuẩn hóa.
        if q and q not in bo_dau(van_ban):
            continue
        # Lấy các nguyên liệu của món khớp với ít nhất một nguyên liệu người dùng nhập.
        khop = [ten for ten in mon.get("nguyen_lieu", []) if any(nguyen_lieu_khop(nhap, ten) for nhap in san_co)]
        # Nếu người dùng đã nhập nguyên liệu mà không khớp nguyên liệu nào thì bỏ qua món.
        if san_co and not khop:
            continue
        # Sao chép dữ liệu để bổ sung kết quả mà không sửa dữ liệu gốc.
        ban_sao = dict(mon)
        # Lưu danh sách nguyên liệu khớp để giao diện có thể hiển thị.
        ban_sao["nguyen_lieu_khop"] = khop
        # Lưu số nguyên liệu khớp.
        ban_sao["so_nguyen_lieu_khop"] = len(khop)
        # Tạo danh sách nguyên liệu chưa có.
        ban_sao["con_thieu"] = [x for x in mon.get("nguyen_lieu", []) if x not in khop]
        # Tính phần trăm nguyên liệu khớp nếu người dùng có nhập nguyên liệu.
        ban_sao["ti_le_phu_hop"] = round(len(khop) / len(mon["nguyen_lieu"]) * 100) if san_co and mon.get("nguyen_lieu") else 0
        # Thêm món đạt điều kiện vào danh sách kết quả.
        ket_qua.append(ban_sao)
    # Khi tìm bằng nguyên liệu, ưu tiên món khớp nhiều nguyên liệu và còn thiếu ít nguyên liệu.
    if san_co:
        ket_qua.sort(key=lambda x: (x["so_nguyen_lieu_khop"], -len(x["con_thieu"])), reverse=True)
    # Trả danh sách món đã lọc về cho ứng dụng.
    return ket_qua

# Gợi ý các món tương tự món đang xem bằng phương pháp Content-Based Filtering.
def goi_y_mon_tuong_tu(ds_mon, ma_mon, so_luong=4):
    # Tìm món gốc theo mã; nếu mã không tồn tại thì không có gợi ý.
    mon_goc = next((m for m in ds_mon if int(m.get("id", -1)) == int(ma_mon)), None)
    # Trả danh sách rỗng nếu không tìm thấy món gốc.
    if mon_goc is None:
        return []
    # Tạo danh sách kết quả có điểm tương đồng.
    danh_sach = []
    # So sánh món gốc với từng món trong dữ liệu.
    for mon in ds_mon:
        # Không gợi ý chính món người dùng đang xem.
        if int(mon.get("id", -1)) == int(ma_mon):
            continue
        # Tính điểm chi tiết để có thể giải thích vì sao món được gợi ý.
        diem_chi_tiet = chi_tiet_diem_tuong_dong(mon_goc, mon)
        # Sao chép công thức và thêm điểm tương đồng tổng hợp theo phần trăm.
        ban_sao = dict(mon)
        ban_sao["diem_tuong_dong"] = round(diem_chi_tiet["tong"] * 100)
        # Gắn điểm thành phần để tiện kiểm thử hoặc giải thích thuật toán.
        ban_sao["chi_tiet_diem"] = diem_chi_tiet
        # Thêm món đã chấm điểm vào danh sách.
        danh_sach.append(ban_sao)
    # Xếp món có điểm tương đồng cao nhất lên trước.
    danh_sach.sort(key=lambda x: (x["diem_tuong_dong"], x["ten"]), reverse=True)
    # Trả số lượng món người dùng yêu cầu.
    return danh_sach[:max(0, int(so_luong))]
