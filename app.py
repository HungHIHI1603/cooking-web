# app.py - Khởi tạo website SmartCook AI và định nghĩa các địa chỉ truy cập.
from flask import Flask, render_template, request, jsonify, abort  # Nhập công cụ tạo web, nhận dữ liệu và trả JSON.
from model import doc_cong_thuc, goi_y_mon_an, goi_y_mon_tuong_tu, tach_nguyen_lieu  # Nhập các hàm xử lý dữ liệu và gợi ý.
from phu_bep import tao_ke_hoach_phu_bep  # Nhập chức năng quy đổi công thức theo số người ăn.

# Tạo ứng dụng Flask và bật chế độ tự tìm thư mục templates/static mặc định.
app = Flask(__name__)

# Hiển thị trang chủ giới thiệu SmartCook AI; mỗi chức năng nằm ở trang riêng.
@app.route("/")
def trang_chu():
    # Đọc danh sách công thức để hiển thị số món ăn trong phần giới thiệu.
    ds_mon = doc_cong_thuc()
    # Hiển thị trang chào mừng và giới thiệu các chức năng chính.
    return render_template("home.html", tong_mon=len(ds_mon))

# Hiển thị trang tìm món dựa trên nguyên liệu người dùng đang có.
@app.route("/nguyen-lieu")
def trang_nguyen_lieu():
    # Đọc công thức để dựng sẵn các thẻ món trước khi lọc.
    ds_mon = doc_cong_thuc()
    # Hiển thị trang nguyên liệu và truyền danh sách món ban đầu.
    return render_template("ingredients.html", mon_an=ds_mon)

# Hiển thị trang duyệt, tìm kiếm và lọc toàn bộ công thức.
@app.route("/cong-thuc")
def trang_cong_thuc():
    # Đọc danh sách công thức từ tệp dữ liệu.
    ds_mon = doc_cong_thuc()
    # Tạo danh sách danh mục không trùng lặp cho bộ lọc.
    loai_mon = sorted({mon["loai"] for mon in ds_mon})
    # Hiển thị riêng trang danh sách công thức.
    return render_template("recipes.html", mon_an=ds_mon, loai_mon=loai_mon)

# Hiển thị chi tiết công thức dựa trên mã món ăn trong đường dẫn.
@app.route("/cong-thuc/<int:ma_mon>")
def chi_tiet(ma_mon):
    # Đọc danh sách công thức.
    ds_mon = doc_cong_thuc()
    # Tìm món có mã trùng với mã trên đường dẫn.
    mon = next((m for m in ds_mon if int(m["id"]) == ma_mon), None)
    # Trả về trang lỗi 404 nếu mã món không tồn tại.
    if mon is None:
        abort(404)
    # Tính các món tương tự dựa trên nguyên liệu, danh mục và thời gian nấu.
    mon_tuong_tu = goi_y_mon_tuong_tu(ds_mon, ma_mon, so_luong=6)
    # Hiển thị công thức chi tiết cùng danh sách món gợi ý.
    return render_template("recipe.html", mon=mon, mon_tuong_tu=mon_tuong_tu)

# Hiển thị trang trợ lý phụ bếp để quy đổi công thức theo số người ăn.
@app.route("/phu-bep", methods=["GET", "POST"])
def trang_phu_bep():
    # Đọc công thức để tạo danh sách chọn món trên giao diện.
    ds_mon = doc_cong_thuc()
    # Mặc định chưa có kết quả cho đến khi người dùng gửi biểu mẫu.
    ke_hoach = None
    # Tạo thông báo lỗi rỗng để hiển thị khi dữ liệu nhập chưa hợp lệ.
    loi = ""
    # Xử lý biểu mẫu khi người dùng yêu cầu tính nguyên liệu.
    if request.method == "POST":
        try:
            # Lấy mã món được chọn, mặc định chọn món đầu tiên nếu thiếu dữ liệu.
            ma_mon = int(request.form.get("ma_mon", ds_mon[0]["id"]))
            # Lấy số người ăn, mặc định là hai người.
            so_nguoi = int(request.form.get("so_nguoi", 2))
            # Tạo kế hoạch gồm nguyên liệu quy đổi và các bước nấu.
            ke_hoach = tao_ke_hoach_phu_bep(ma_mon, so_nguoi)
        except (ValueError, TypeError):
            # Thông báo nếu người dùng nhập số người không hợp lệ.
            loi = "Vui lòng chọn món và nhập số người từ 1 đến 50."
    # Hiển thị trang trợ lý cùng danh sách món, kết quả và thông báo.
    return render_template("phu_bep.html", mon_an=ds_mon, ke_hoach=ke_hoach, loi=loi)

# Cung cấp API tìm kiếm và lọc món ăn để JavaScript cập nhật trang mà không tải lại.
@app.route("/api/mon-an")
def api_mon_an():
    # Nhận từ khóa tìm kiếm từ thanh tìm kiếm trên giao diện.
    tu_khoa = request.args.get("q", "")
    # Nhận danh mục món ăn được chọn.
    loai = request.args.get("loai", "Tất cả")
    # Tách chuỗi nguyên liệu thành danh sách nguyên liệu riêng biệt.
    nguyen_lieu = tach_nguyen_lieu(request.args.get("nguyen_lieu", ""))
    # Đọc giới hạn thời gian nấu; nếu tham số không hợp lệ thì không áp dụng giới hạn.
    try:
        thoi_gian_toi_da = int(request.args["thoi_gian"]) if request.args.get("thoi_gian") else None
    except ValueError:
        thoi_gian_toi_da = None
    # Gọi thuật toán lọc và xếp hạng món theo dữ liệu người dùng cung cấp.
    ket_qua = goi_y_mon_an(doc_cong_thuc(), nguyen_lieu, tu_khoa, loai, thoi_gian_toi_da)
    # Trả kết quả ở định dạng JSON để trình duyệt hiển thị.
    return jsonify(ket_qua)

# Cung cấp API lấy danh sách món tương tự cho các ứng dụng hoặc kiểm thử.
@app.route("/api/cong-thuc/<int:ma_mon>/tuong-tu")
def api_mon_tuong_tu(ma_mon):
    # Đọc dữ liệu và tính danh sách món tương tự.
    ket_qua = goi_y_mon_tuong_tu(doc_cong_thuc(), ma_mon)
    # Nếu không tìm thấy món gốc, phản hồi mã 404.
    if not any(int(m["id"]) == ma_mon for m in doc_cong_thuc()):
        return jsonify({"loi": "Không tìm thấy công thức."}), 404
    # Trả danh sách món tương tự dưới dạng JSON.
    return jsonify(ket_qua)

# Hiển thị trang thông báo khi người dùng truy cập địa chỉ không tồn tại.
@app.errorhandler(404)
def khong_tim_thay(loi):
    # Trả trang 404 cùng mã trạng thái HTTP tương ứng.
    return render_template("404.html"), 404

# Chỉ khởi chạy máy chủ phát triển khi chạy trực tiếp tệp app.py.
if __name__ == "__main__":
    # Chạy trên máy tính cá nhân; tắt debug khi triển khai công khai.
    app.run(debug=True)
