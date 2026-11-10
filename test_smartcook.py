# Kiểm thử các chức năng chính của SmartCook AI bằng thư viện unittest có sẵn trong Python.
import unittest  # Cung cấp công cụ viết và chạy kiểm thử.
from model import doc_cong_thuc, diem_tuong_dong, chi_tiet_diem_tuong_dong, goi_y_mon_an, goi_y_mon_tuong_tu  # Nhập thuật toán cần kiểm tra.
from phu_bep import tao_ke_hoach_phu_bep  # Nhập chức năng quy đổi nguyên liệu.
from app import app  # Nhập ứng dụng Flask để kiểm tra các trang và API.

# Gom các kiểm thử của SmartCook AI vào một lớp.
class KiemThuSmartCookAI(unittest.TestCase):
    # Đọc dữ liệu một lần trước mỗi kiểm thử để dùng bộ công thức thực tế.
    def setUp(self):
        self.ds_mon = doc_cong_thuc()

    # Kiểm tra kho dữ liệu có công thức và nhãn cách chế biến.
    def test_du_lieu_co_cach_che_bien(self):
        self.assertGreaterEqual(len(self.ds_mon), 50)
        self.assertTrue(all(mon.get("cach_che_bien") for mon in self.ds_mon))

    # Kiểm tra kho dữ liệu có định lượng và hướng dẫn sơ chế cho từng nguyên liệu.
    def test_du_lieu_so_che_va_dinh_luong(self):
        for mon in self.ds_mon:
            self.assertEqual(set(mon["nguyen_lieu"]), set(mon["so_che"]))
            self.assertTrue(set(mon["nguyen_lieu"]).issubset(set(mon["dinh_luong_2_nguoi"])))

    # Kiểm tra Jaccard và điểm tổng hợp luôn nằm trong khoảng hợp lệ.
    def test_diem_tuong_dong_hop_le(self):
        diem = diem_tuong_dong(self.ds_mon[0], self.ds_mon[1])
        self.assertGreaterEqual(diem, 0)
        self.assertLessEqual(diem, 1)
        self.assertIn("cach_che_bien", chi_tiet_diem_tuong_dong(self.ds_mon[0], self.ds_mon[1]))

    # Kiểm tra hệ thống không gợi ý lại chính món gốc.
    def test_goi_y_mon_tuong_tu(self):
        ket_qua = goi_y_mon_tuong_tu(self.ds_mon, self.ds_mon[0]["id"], 4)
        self.assertLessEqual(len(ket_qua), 4)
        self.assertTrue(all(mon["id"] != self.ds_mon[0]["id"] for mon in ket_qua))
        self.assertEqual(sorted([m["diem_tuong_dong"] for m in ket_qua], reverse=True),
                         [m["diem_tuong_dong"] for m in ket_qua])

    # Kiểm tra tìm món theo nguyên liệu trứng trả về kết quả phù hợp.
    def test_tim_mon_theo_nguyen_lieu(self):
        ket_qua = goi_y_mon_an(self.ds_mon, ["trứng"])
        self.assertTrue(ket_qua)
        self.assertTrue(all(mon["so_nguyen_lieu_khop"] > 0 for mon in ket_qua))

    # Kiểm tra không khớp nhầm nguyên liệu quá ngắn như "cá" với "cà chua".
    def test_nguyen_lieu_ngan_khong_khop_nham(self):
        ket_qua = goi_y_mon_an(self.ds_mon, ["cá"])
        self.assertTrue(all("cà chua" not in mon.get("nguyen_lieu_khop", []) for mon in ket_qua))

    # Kiểm tra Phụ Bếp tăng lượng nguyên liệu gấp ba khi đổi từ hai lên sáu người.
    def test_phu_bep_sau_nguoi(self):
        ke_hoach = tao_ke_hoach_phu_bep(1, 6)
        self.assertEqual(ke_hoach["so_nguoi"], 6)
        self.assertEqual(next(nl for nl in ke_hoach["nguyen_lieu"] if nl["ten"] == "thịt bò")["so_luong"], "750")

    # Kiểm tra Phụ Bếp từ chối số người ngoài giới hạn.
    def test_phu_bep_tu_choi_so_nguoi_khong_hop_le(self):
        with self.assertRaises(ValueError):
            tao_ke_hoach_phu_bep(1, 0)
        with self.assertRaises(ValueError):
            tao_ke_hoach_phu_bep(1, 51)

    # Kiểm tra trang chính trả về mã HTTP thành công.
    def test_trang_chu(self):
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    # Kiểm tra API tìm món trả về dữ liệu JSON.
    def test_api_tim_mon(self):
        client = app.test_client()
        response = client.get("/api/mon-an?q=phở")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

# Cho phép chạy tệp kiểm thử trực tiếp hoặc qua lệnh unittest.
if __name__ == "__main__":
    unittest.main()
