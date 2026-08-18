# PLAN-auth-microservice (Production & Security Standard)

## 1. Quyết Định Kiến Trúc: Microservices (Tách biệt Auth & AI)
Để hệ thống đạt chuẩn **Production** và dễ dàng Scale (mở rộng) sau này, chúng ta sẽ áp dụng kiến trúc **Microservices**:
- **Frontend**: React (TypeScript) xử lý UI (Màn hình Login/Register chia đôi như thiết kế).
- **Auth Service (Backend 1)**: Xây dựng bằng **Node.js (TypeScript/Express)** hoặc **Go (Golang)**. Chịu trách nhiệm hoàn toàn về Database Người dùng, Đăng ký, Đăng nhập, và cấp phát Token.
- **AI Service (Backend 2)**: Chính là hệ thống **Python (FastAPI)** hiện tại. Chỉ làm nhiệm vụ AI (Phân tích CV, Phỏng vấn). Nó sẽ xác thực người dùng bằng cách kiểm tra Token do Auth Service cấp.
- **API Gateway (Nginx / Traefik)**: Đứng trước điều phối traffic (VD: `/api/auth/*` chuyển cho Auth Service, `/api/ai/*` chuyển cho Python).

## 2. Tiêu Chuẩn Bảo Mật Cấp Độ Production (Prod Security Standard)

Phần xác thực sẽ được thiết kế với các lớp bảo mật khắt khe nhất để chống lại hacker:

### A. Quản lý Mật khẩu (Password Security)
- **Thuật toán Băm (Hashing)**: Không dùng MD5/SHA256. Bắt buộc dùng **Argon2id** (tiêu chuẩn cao nhất hiện nay, chống cả tấn công bằng GPU) hoặc **Bcrypt** (Cost factor >= 12).
- **Password Strength**: Backend sẽ từ chối nếu mật khẩu không có chữ hoa, chữ thường, số, và ký tự đặc biệt (Độ dài tối thiểu 8-12 ký tự).

### B. Kiến trúc Token & Chống XSS / CSRF
Tuyệt đối **KHÔNG** lưu token vào `localStorage` (rất dễ bị đánh cắp qua mã độc XSS).
- **Access Token (Ngắn hạn - 15 phút)**: Trả về qua JSON, Frontend lưu trên bộ nhớ tạm (RAM/React State). Dùng để gọi API.
- **Refresh Token (Dài hạn - 7 ngày)**: Cấp phát dưới dạng **Cookie (HttpOnly, Secure, SameSite=Strict)**. Cookie này không thể bị mã độc JavaScript (XSS) đọc được.
- **CSRF Protection**: Các request thay đổi dữ liệu phải đính kèm Header chống giả mạo request (CSRF Token).

### C. Chống Tấn Công Brute Force (Dò Mật Khẩu)
- **Rate Limiting với Redis**: Giới hạn nghiêm ngặt ở API `/login`. Nếu nhập sai mật khẩu quá 5 lần từ 1 IP trong vòng 15 phút, khóa IP đó tạm thời (Lockout).

## 3. Phân chia công việc (Task Breakdown) - Phase 1: Microservice Setup

### Auth Service (Node.js hoặc Go)
- [ ] Khởi tạo thư mục dự án `auth-service/`.
- [ ] Cấu hình Database kết nối tới bảng `users` (PostgreSQL).
- [ ] Viết API `/register`: Validate dữ liệu, Hash mật khẩu bằng Argon2/Bcrypt, lưu DB.
- [ ] Viết API `/login`: Xác thực mật khẩu, sinh cặp `AccessToken` và set `HttpOnly Cookie` cho `RefreshToken`.
- [ ] Tích hợp Redis để làm Rate Limiter chống Brute-force.

### Python AI Service (Cập nhật)
- [ ] Xóa/Không làm phần cấp phát Token ở Python nữa.
- [ ] Viết một Dependency (Middleware) `verify_jwt_token` để giải mã và xác thực Access Token do Auth Service gửi sang (dùng chung chuỗi JWT_SECRET).

### Frontend (UI/UX)
- [ ] Khởi tạo UI Đăng ký / Đăng nhập theo Mockup Enterprise SaaS.
- [ ] Cấu hình `axios` (hoặc `fetch`) để tự động đính kèm `withCredentials: true` (để gửi Cookie) và gắn Bearer Token vào Header.
- [ ] Viết luồng Interceptor tự động gọi API `/refresh-token` nếu Access Token hết hạn (15 phút).

## 4. Verification Checklist (Kiểm thử Bảo mật)
- [ ] Dùng postman gọi API đăng nhập, kiểm tra xem Token có bị lộ trong response body không (Chỉ Access Token được lộ, Refresh Token phải nằm trong Header `Set-Cookie`).
- [ ] Thử cố tình nhập sai mật khẩu 6 lần liên tiếp xem IP có bị block không.
- [ ] Chạy Python AI API với một Token tự chế (Fake Token), đảm bảo Python từ chối truy cập (HTTP 401).
