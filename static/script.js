// Lưu danh mục đang chọn trên trang công thức.
let loai = 'Tất cả';
// Lấy các điều khiển nếu chúng có mặt trên trang hiện tại.
const input = document.getElementById('nguyenLieu');
const q = document.getElementById('tuKhoa');
const luoi = document.getElementById('luoi');
const rong = document.getElementById('rong');
const dem = document.getElementById('dem');
const thoiGian = document.getElementById('thoiGian');

// Đọc danh sách món yêu thích đã lưu trên trình duyệt.
function docYeuThich() { try { return JSON.parse(localStorage.getItem('smartcook_yeu_thich') || '[]'); } catch (e) { return []; } }
// Lưu danh sách món yêu thích vào bộ nhớ trình duyệt.
function luuYeuThich(ds) { localStorage.setItem('smartcook_yeu_thich', JSON.stringify(ds)); }
// Lấy danh sách nguyên liệu người dùng đã nhập; nếu trang không có ô nhập thì trả danh sách rỗng.
function dsNguyenLieu() { return input ? input.value.split(/[,;\n]+/).map(x => x.trim()).filter(Boolean) : []; }
// Cập nhật thông báo số nguyên liệu đã nhập.
function capNhatDem() { if (!dem) return; const ds = dsNguyenLieu(); dem.textContent = ds.length ? `Đã chọn ${ds.length} nguyên liệu: ${ds.join(', ')}` : 'Chưa nhập nguyên liệu'; }
// Khi bấm nguyên liệu gợi ý, thêm vào ô nhập nếu chưa có.
document.querySelectorAll('.chip').forEach(b => b.onclick = () => { if (!input) return; const ds = dsNguyenLieu(); if (!ds.some(x => x.toLowerCase() === b.dataset.value.toLowerCase())) ds.push(b.dataset.value); input.value = ds.join(', '); capNhatDem(); });
// Cập nhật số lượng nguyên liệu khi người dùng nhập.
if (input) input.addEventListener('input', capNhatDem);
// Xóa nguyên liệu và cập nhật danh sách món.
const nutXoa = document.getElementById('xoa');
if (nutXoa) nutXoa.onclick = () => { if (input) input.value = ''; if (q) q.value = ''; loai = 'Tất cả'; if (thoiGian) thoiGian.value = ''; document.querySelectorAll('.filter').forEach(b => b.classList.toggle('active', b.dataset.loai === loai)); capNhatDem(); taiMon(); };
// Nút tìm món chỉ tải kết quả trên trang gợi ý nguyên liệu.
const nutTim = document.getElementById('tim');
if (nutTim) nutTim.onclick = taiMon;
// Lọc công thức khi người dùng chọn một danh mục.
document.querySelectorAll('.filter').forEach(b => b.onclick = () => { document.querySelectorAll('.filter').forEach(x => x.classList.remove('active')); b.classList.add('active'); loai = b.dataset.loai; taiMon(); });
// Tự tìm khi nhập tên món hoặc đổi giới hạn thời gian.
if (q) q.addEventListener('input', taiMon);
if (thoiGian) thoiGian.addEventListener('change', taiMon);
// Nút xem tất cả xóa từ khóa và bộ lọc trên trang công thức.
const nutTatCa = document.getElementById('xemTatCa');
if (nutTatCa) nutTatCa.onclick = () => { if (q) q.value = ''; loai = 'Tất cả'; if (thoiGian) thoiGian.value = ''; document.querySelectorAll('.filter').forEach(b => b.classList.toggle('active', b.dataset.loai === loai)); taiMon(); };
// Mã hóa dữ liệu văn bản trước khi chèn vào HTML.
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
// Chọn biểu tượng theo tên món ăn.
function icon(n) { const ten = n.toLowerCase(); if (ten.includes('phở') || ten.includes('bún')) return '🍜'; if (ten.includes('cơm')) return '🍚'; if (ten.includes('trứng')) return '🍳'; if (ten.includes('gà')) return '🍗'; if (ten.includes('rau')) return '🥬'; if (ten.includes('đậu')) return '🥘'; if (ten.includes('mì')) return '🍝'; if (ten.includes('bò') || ten.includes('thịt')) return '🥩'; if (ten.includes('cá')) return '🐟'; return '🍲'; }
// Tạo thẻ món cho kết quả API.
function taoTheMon(m, i) { const yeuThich = docYeuThich().includes(Number(m.id)); const khop = m.so_nguyen_lieu_khop ? `<div class="meta">Khớp ${m.so_nguyen_lieu_khop} nguyên liệu · phù hợp ${m.ti_le_phu_hop}%</div>` : ''; return `<article class="card"><div class="food food${i % 6}"><a href="/cong-thuc/${m.id}"><span>${icon(m.ten)}</span><small>${esc(m.loai)}</small><i>↗</i></a><button class="favorite-btn ${yeuThich ? 'is-favorite' : ''}" data-id="${m.id}" aria-label="Lưu món yêu thích">${yeuThich ? '♥' : '♡'}</button></div><div class="cardbody"><div class="meta">◷ ${m.thoi_gian} phút · ${esc(m.do_kho)}</div><h3><a href="/cong-thuc/${m.id}">${esc(m.ten)}</a></h3><p>${esc(m.mo_ta)}</p>${khop}<div class="cardfoot"><span>${m.nguyen_lieu.length} nguyên liệu</span><a href="/cong-thuc/${m.id}">Xem cách nấu →</a></div></div></article>`; }
// Gọi API và hiển thị kết quả phù hợp với các bộ lọc hiện tại.
async function taiMon() { if (!luoi || !rong) return; const thamSo = new URLSearchParams({q: q ? q.value : '', loai: loai, nguyen_lieu: dsNguyenLieu().join(', ')}); if (thoiGian && thoiGian.value) thamSo.set('thoi_gian', thoiGian.value); try { const phanHoi = await fetch('/api/mon-an?' + thamSo); if (!phanHoi.ok) throw new Error('Không tải được công thức'); const ds = await phanHoi.json(); luoi.innerHTML = ds.map(taoTheMon).join(''); rong.hidden = ds.length > 0; luoi.hidden = ds.length === 0; ganSuKienYeuThich(); } catch (e) { console.error(e); } }
// Bật hoặc tắt yêu thích cho các thẻ món được tạo bởi JavaScript.
function ganSuKienYeuThich() { document.querySelectorAll('.favorite-btn').forEach(nut => nut.onclick = () => { const ma = Number(nut.dataset.id); let ds = docYeuThich(); ds = ds.includes(ma) ? ds.filter(x => x !== ma) : [...ds, ma]; luuYeuThich(ds); taiMon(); }); }
// Khởi tạo số nguyên liệu và tải dữ liệu động nếu trang có danh sách món.
capNhatDem();
if (luoi && rong) taiMon();
