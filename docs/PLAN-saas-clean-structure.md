# 📋 Kế Hoạch Tái Cấu Trúc: Hệ Thống SaaS Chuẩn 100% (Mô Hình Lựa Chọn 3)

> **Mã kế hoạch:** `PLAN-saas-clean-structure`  
> **Mục tiêu:** Xóa bỏ hoàn toàn sự rối rắm, thiết lập cấu trúc định tuyến SaaS chuẩn: 1 Landing Page duy nhất (`/`) kết hợp 5 trang tính năng độc lập, chuyên biệt.

---

## 🏗️ 1. Bản Đồ Định Tuyến Mới (Clean Routing Map)

```text
careerpilot.vn/
│
├── / (Trang chủ Landing Page - fe/app/(marketing)/page.tsx)
│   └── Giới thiệu sản phẩm, ATS live demo, CTA dẫn vào /workspace
│
└── / (Các trang tính năng chuyên sâu)
    ├── /workspace    (Phân tích CV & Tối ưu hóa ATS với AI Multi-Agent)
    ├── /jobs         (Tìm việc & So khớp năng lực kỹ thuật)
    ├── /interview    (Phòng luyện phỏng vấn giả lập AI Voice & Chat)
    ├── /learning     (Lộ trình nâng cấp kỹ năng & Khóa học)
    └── /applications (Bảng Kanban quản lý tiến trình ứng tuyển)
```

---

## 🗑️ 2. Các Thay Đổi & Dọn Dẹp

1. **Xóa bỏ hoàn toàn `fe/app/(app)/home/`:**
   - Xóa `fe/app/(app)/home/page.tsx`
   - Xóa `fe/app/(app)/home/preview.html`
2. **Chuẩn hóa Header & Logo:**
   - Logo `CareerPilot AI` ở tất cả các trang luôn trỏ về Trang chủ `/`.
   - Header Menu gồm đúng 5 tính năng:
     1. `Phân tích CV` $\rightarrow$ `/workspace`
     2. `Tìm việc & So khớp` $\rightarrow$ `/jobs`
     3. `Phỏng vấn AI` $\rightarrow$ `/interview`
     4. `Lộ trình kỹ năng` $\rightarrow$ `/learning`
     5. `Quản lý ứng tuyển` $\rightarrow$ `/applications`
3. **Triển khai 4 trang tính năng còn lại:**
   - Xây dựng giao diện cơ sở cho `/jobs`, `/interview`, `/learning`, `/applications` đồng bộ theo phong cách **Dark Obsidian Canvas (`#090D16`)** và **Emerald Accent (`#10b981`)**.

---

## 🏁 3. Kế Hoạch Xác Minh

- [ ] `npx tsc --noEmit` đạt 0 lỗi biên dịch.
- [ ] `python -X utf8 .agent/scripts/checklist.py .` đạt 6/6 PASSED.
- [ ] Kiểm tra điều hướng hoạt động trơn tru trên mọi trang.
