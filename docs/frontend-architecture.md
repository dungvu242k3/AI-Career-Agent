# Frontend Architecture Specification: AI Career Agent

> **Phiên bản:** 1.0.0  
> **Tech Stack:** Next.js (App Router) + TypeScript Strict + Tailwind CSS + shadcn/ui + TanStack Query + Zustand + Zod + SSE  
> **Mục tiêu:** Production-ready, Bounded Context theo Feature-based, Strict Typing, Tách biệt Server/Client State, Hỗ trợ AI Agent Real-time Streaming.

---

## 1. Tổng quan Kiến trúc (High-Level Architecture)

Hệ thống Frontend được xây dựng theo mô hình **4 Tầng Phân Lớp (Layered Architecture)** kết hợp với **Feature-Based Module System**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Next.js App Router                              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Presentation Layer (Routing, Layouts, Page Composition)            │  │
│  │    fe/app/(marketing), fe/app/(auth), fe/app/(app)                 │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │ 2. Feature Layer (Business Modules & Bounded Contexts)                │  │
│  │    career-workspace, cv-analysis, job-matching, interview, learning...│  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │ 3. Domain & Entity Layer (Core Business Models & Micro-Components)    │  │
│  │    entities/user, resume, job, skill, interview, application          │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │ 4. Infrastructure & Shared Layer (API, SSE, Storage, UI Primitives)   │  │
│  │    fe/lib/ (api, sse, auth, query, upload) | fe/shared/ (ui, hooks) │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ HTTPS / SSE (EventStream)
                                       ▼
                       ┌───────────────────────────────┐
                       │    FastAPI Backend & Agents   │
                       │    (LangGraph / AI Engines)   │
                       └───────────────────────────────┘
```

### Nguyên tắc cốt lõi về luồng dữ liệu (Data Flow)
Tuyệt đối không để:
$$\text{Page Component} \xrightarrow{\text{fetch()}} \text{xử lý JSON inline} \xrightarrow{} \text{Render}$$

Luồng dữ liệu chuẩn bắt buộc:
$$\text{Page} \longrightarrow \text{Feature Container} \longrightarrow \text{Feature Hook (Query/Mutation)} \longrightarrow \text{API/SSE Service} \longrightarrow \text{Zod Schema Validator} \longrightarrow \text{HTTP Client}$$

---

## 2. Phân vùng và Trách nhiệm của Thư mục (Directory Taxonomy & Responsibilities)

### 2.1. Cây thư mục hoàn chỉnh
```text
fe/
├── app/                  # Next.js App Router (Routes, Layouts, Metadata, Error/Loading)
├── features/             # Business Features (Tự chứa logic, state, UI của từng nghiệp vụ)
├── entities/             # Core Business Entities (Dùng chung cho nhiều feature)
├── shared/               # Shared Utilities, Generic UI Components, Common Hooks & Types
├── lib/                  # Infrastructure & Third-party integrations (API, SSE, Auth, Query)
└── types/                # Global ambient TypeScript declarations
```

---

### 2.2. Chi tiết trách nhiệm từng tầng

#### A. Tầng `fe/app/` (Presentation & Routing)
Chỉ đóng vai trò **Route Entry Point** và **Page Orchestration** (ghép nối các Features), không chứa logic nghiệp vụ phức tạp.

| Thư mục / File | Trách nhiệm cụ thể |
| :--- | :--- |
| `app/(marketing)/` | Nhóm trang công khai: Landing page, Pricing, About. Không yêu cầu đăng nhập. |
| `app/(auth)/` | Nhóm trang xác thực: Login, Register, Forgot Password. Tách biệt layout auth. |
| `app/(app)/` | Nhóm trang ứng dụng chính (Protected). Chia sẻ chung AppLayout (Header, Sidebar, UserNav). |
| `app/(app)/workspace/` | Bounded Context Career AI Workspace — Màn hình làm việc trọng tâm với Agent. |
| `app/(app)/dashboard/` | Tổng quan tiến độ nghề nghiệp, chỉ số gợi ý việc làm, phân tích nhanh. |
| `app/(app)/jobs/` & `[jobId]/` | Khám phá việc làm, chi tiết công việc, phân tích độ phù hợp với hồ sơ. |
| `app/(app)/applications/` | Quản lý lộ trình ứng tuyển (Kanban/Table tracking). |
| `app/(app)/learning/` | Lộ trình bù đắp kỹ năng (Skill Gap Roadmap), khóa học đề xuất. |
| `app/(app)/profile/` | Quản lý thông tin ứng viên, hồ sơ kỹ năng, CVs đã tải lên. |
| `app/(app)/settings/` | Cài đặt tài khoản, cấu hình AI preference, thông báo. |
| `app/providers.tsx` | Quấn toàn bộ Global Providers: QueryClientProvider, ThemeProvider, ToastProvider. |
| `app/error.tsx` & `loading.tsx` | Global Error Boundary và Global Loading Skeleton của Next.js. |

---

#### B. Tầng `fe/features/` (Feature-based Bounded Contexts)
Mỗi thư mục đại diện cho một nghiệp vụ hoàn chỉnh và **tự trị (autonomous)**.

Cấu trúc chuẩn bên trong mỗi feature:
```text
features/[feature-name]/
├── components/          # UI Components đặc thù của feature này
├── hooks/               # Custom hooks quản lý logic nghiệp vụ & integration state
├── api/                 # Các hàm gọi API cụ thể của feature
├── schemas/             # Zod validation schemas (Validate DTO & Form)
├── types/               # TypeScript interfaces/types riêng của feature
└── index.ts             # Public API boundary của feature (chỉ export thứ cần thiết)
```

| Tên Feature | Phạm vi trách nhiệm |
| :--- | :--- |
| `career-workspace` | Điều phối tương tác Agent trực tiếp: SourcePanel (Resume, JD), Main Chat, InsightPanel, Quản lý phiên làm việc đa tác vụ. |
| `cv-analysis` | Phân tích cấu trúc CV, trích xuất kinh nghiệm, phát hiện điểm mạnh/yếu theo chuẩn ATS. |
| `cv-optimization` | Đề xuất tối ưu hóa nội dung CV phù hợp với từng JD cụ thể, diff view so sánh bản cũ/mới. |
| `job-search` | Tìm kiếm việc làm, lọc theo tiêu chí (mức lương, vị trí, tech stack, remote/onsite). |
| `job-matching` | Đánh giá tỷ lệ phù hợp (% Match Score), phân tích ma trận kỹ năng (Skill Gap Matrix). |
| `interview` | Mô phỏng phỏng vấn AI (Mock Interview), câu hỏi theo tình huống JD, chấm điểm phản hồi. |
| `learning` | Tạo lộ trình học tập thích ứng (Adaptive Learning Path) để lấp đầy khoảng trống kỹ năng. |
| `applications` | Theo dõi trạng thái nộp hồ sơ, lịch phỏng vấn, ghi chú nhà tuyển dụng. |
| `auth` | Quản lý phiên đăng nhập, đăng ký tài khoản, xác thực token, bảo vệ phiên người dùng. |

---

#### C. Tầng `fe/entities/` (Core Business Entities)
Chứa các thực thể dữ liệu gốc được sử dụng xuyên suốt nhiều feature khác nhau. Khác với `feature`, entity không chứa luồng nghiệp vụ tương tác phức tạp mà chỉ chứa định dạng dữ liệu, schema chuẩn hóa, và các **Micro UI Components hiển thị dữ liệu gốc**.

```text
entities/[entity-name]/
├── types/               # Entity Data Interface (e.g. Job, Resume, User)
├── schemas/             # Entity Zod Schema
└── components/          # Micro-components hiển thị entity (e.g. JobBadge, SkillTag, MatchScoreBadge)
```

| Entity | Trách nhiệm |
| :--- | :--- |
| `user` | Thông tin người dùng, cài đặt tài khoản, vai trò và quyền hạn. |
| `resume` | Cấu trúc dữ liệu CV (học vấn, kinh nghiệm, dự án, kỹ năng). |
| `job` | Cấu trúc tin tuyển dụng (yêu cầu, quyền lợi, công ty, mức lương). |
| `skill` | Danh mục kỹ năng chuẩn hóa (Framework, Language, Soft Skill, Mức độ thành thạo). |
| `interview` | Lịch sử phỏng vấn, câu hỏi, tiêu chí đánh giá, bản ghi phản hồi. |
| `application` | Bản ghi trạng thái ứng tuyển (Applied, Interviewing, Offered, Rejected). |

---

#### D. Tầng `fe/shared/` (Generic & Reusable Utilities)
Chỉ chứa các thành phần **hoàn toàn phi nghiệp vụ (domain-agnostic)**, có thể tái sử dụng trong bất kỳ dự án nào.

| Thư mục | Trách nhiệm |
| :--- | :--- |
| `shared/components/ui/` | Thư viện UI nguyên tử (Primitives): Button, Input, Modal, Drawer, Skeleton, Badge, Card, Tooltip, FileUploader, DropdownMenu (xây dựng trên nền Radix UI / shadcn). |
| `shared/components/layout/` | Shell khung chuẩn: PageHeader, Container, Section, TwoColumnLayout. |
| `shared/components/feedback/`| EmptyState, ErrorState, LoadingState, AlertBanner. |
| `shared/hooks/` | Hooks tiện ích: `useDebounce`, `useMediaQuery`, `useIntersectionObserver`, `useLocalStorage`, `useClipboard`. |
| `shared/utils/` | Hàm thuần túy: `cn` (clsx + twMerge), `formatDate`, `formatScore`, `formatCurrency`, `sanitizeHtml`. |
| `shared/constants/` | Hằng số hệ thống: Route paths, Storage keys, Regex patterns, App config. |
| `shared/types/` | Kiểu dữ liệu chung: `PaginationParams`, `ApiResponse<T>`, `SortOrder`. |

---

#### E. Tầng `fe/lib/` (Infrastructure & Third-Party Adapters)
Chịu trách nhiệm giao tiếp với hệ thống bên ngoài, Network, Storage, và các thư viện quản trị state/data fetching.

```text
lib/
├── api/
│   ├── client.ts           # Axios / Fetch Wrapper cấu hình baseUrl, timeouts, headers
│   ├── errors.ts           # Custom API Error Classes (ApiError, UnauthorizedError, ValidationError)
│   ├── interceptors.ts     # Request/Response Interceptors (Tự động đính kèm cookie, xử lý refresh token)
│   └── endpoints/          # Định nghĩa URL constants cho từng domain backend
├── auth/
│   ├── session.ts          # Quản lý phiên, kiểm tra trạng thái xác thực client-side
│   └── middleware-auth.ts  # Logic kiểm tra auth phục vụ cho Next.js Middleware
├── query/
│   ├── query-client.ts     # Khởi tạo TanStack QueryClient với cấu hình retry, staleTime chuẩn
│   └── query-keys.ts       # Type-safe Query Keys Factory (tránh duplicate query keys)
├── sse/
│   ├── sse-client.ts       # Wrapper quản lý kết nối EventSource / Fetch SSE stream
│   ├── event-parser.ts     # Bộ giải mã sự kiện từ LangGraph Backend thành Typed Events
│   └── reconnect.ts        # Quản lý Auto-reconnect với Exponential Backoff
├── upload/
│   ├── presigned.ts        # Xử lý luồng upload file qua Presigned URL (S3 / Cloud Storage)
│   └── chunk-uploader.ts   # Xử lý upload chia nhỏ file lớn nếu cần
└── config/
    ├── env.ts              # Zod validation cho biến môi trường (.env.local / .env.production)
    └── site.ts             # Metadata và cấu hình ứng dụng
```

---

## 3. Quy tắc Ranh giới Phụ thuộc (Dependency & Import Boundary Rules)

Để tránh tình trạng "Spaghetti Code" và circular dependencies, dự án áp dụng nghiêm ngặt quy tắc phân cấp một chiều:

```text
fe/app  ──▶  fe/features  ──▶  fe/entities  ──▶  fe/shared
  │                 │                  │                ▲
  └─────────────────┴──────────────────┴────────────────┘
                            │
                            ▼
                         fe/lib
```

### 🚫 Các hành vi bị nghiêm cấm tuyệt đối:
1. **`shared` KHÔNG ĐƯỢC import `entities` hoặc `features`:** Shared phải hoàn toàn độc lập với nghiệp vụ.
2. **`entities` KHÔNG ĐƯỢC import `features`:** Entities chỉ mô tả dữ liệu lõi, không chứa flow của tính năng.
3. **`feature A` KHÔNG ĐƯỢC import trực tiếp nội bộ `feature B`:** 
   - *Sai:* `import { InterviewModal } from '@/features/interview/components/InterviewModal'` trong `features/job-matching`.
   - *Đúng:* Nếu cần phối hợp 2 feature, thực hiện phối hợp ở tầng `fe/app` (Page Level) hoặc trích xuất dữ liệu dùng chung thành `entity` / `shared component`.
4. **Component KHÔNG ĐƯỢC gọi `fetch()` hoặc `axios` trực tiếp:** Bắt buộc phải thông qua `feature/api` $\to$ `lib/api/client`.

---

## 4. Chiến lược Quản lý Trạng thái 3 Tầng (3-Tier State Architecture)

| Loại Trạng thái | Giải pháp kỹ thuật | Ví dụ sử dụng | Nguyên tắc quản lý |
| :--- | :--- | :--- | :--- |
| **Server State** | **TanStack Query (v5)** | CV data, Job listings, Match results, Interview history, Recommendations | - Không bao giờ lưu vào Zustand.<br>- Quản lý cache, staleTime, background refetch tự động.<br>- Tự động hủy query khi unmount. |
| **Client UI State** | **Zustand** | `sidebarOpen`, `activeWorkspaceTab`, `selectedJobForModal`, `chatPanelExpanded`, `themeMode` | - Chỉ lưu trạng thái giao diện thuần túy.<br>- Không lưu dữ liệu fetched từ API.<br>- Cấu trúc store nhỏ gọn theo từng domain. |
| **URL State** | **URL Search Params (nuqs)** | `/jobs?role=ai-engineer&exp=senior&location=hanoi&remote=true` | - Mọi bộ lọc, phân trang, từ khóa tìm kiếm phải phản ánh lên URL.<br>- Cho phép Bookmark, Share link, và duy trì lịch sử Browser. |

---

## 5. Kiến trúc Streaming Agent thời gian thực (SSE Protocol)

Khi người dùng yêu cầu AI phân tích CV hoặc so khớp JD, quá trình xử lý qua nhiều Agent (Profile Agent $\to$ JD Agent $\to$ Matching Agent) mất 10–25 giây. Thay vì giữ request dạng blocking, hệ thống sử dụng **Server-Sent Events (SSE)**.

### 5.1. Luồng truyền thông điệp (Event Stream Sequence)

```text
[Frontend Next.js]                   [FastAPI Backend]                 [LangGraph Agents]
       │                                     │                                 │
       │── POST /api/career/session/stream ─▶│                                 │
       │                                     │── Khởi tạo Workflow ───────────▶│
       │◀── HTTP 200 (text/event-stream) ────│                                 │
       │                                     │◀── ProfileAgent: Started ───────│
       │◀── event: agent_started ────────────│                                 │
       │    data: {"agent": "ProfileAgent"}  │                                 │
       │                                     │◀── ProfileAgent: Extracted CV ──│
       │◀── event: profile_extracted ────────│                                 │
       │                                     │◀── MatchingAgent: Skill Gap ────│
       │◀── event: skill_gap_detected ───────│                                 │
       │    data: {"missing": ["Docker"]}    │                                 │
       │                                     │◀── MatchingAgent: Complete ─────│
       │◀── event: match_completed ──────────│                                 │
       │    data: {"score": 88, "fit": "High"}                                │
       │                                     │                                 │
       │◀── event: done ─────────────────────│                                 │
       │── Đóng Stream kết nối ──────────────│                                 │
```

### 5.2. Chuẩn hóa Định dạng Event (Typed SSE Events)
Tất cả các sự kiện streaming đều được parse qua Zod schema tại `fe/lib/sse/event-parser.ts`:
- `agent_started`: Báo hiệu agent nào đang đảm nhận xử lý.
- `agent_thinking`: Thông điệp suy luận trung gian hiển thị dạng step-by-step.
- `token_delta`: Stream từng từ của câu trả lời AI (Typewriter effect).
- `insight_generated`: Dữ liệu phân tích từng phần (Skill gaps, Strengths, Red flags).
- `session_completed`: Kết quả tổng hợp cuối cùng và cập nhật TanStack Query Cache.
- `error`: Lỗi xử lý kèm mã lỗi và hướng dẫn retry.

---

## 6. Kiến trúc Xác thực và Bảo mật (Authentication & Security)

1. **HttpOnly Secure Cookies:** JWT Access & Refresh Token không được lưu trong `localStorage` để chống tấn công XSS. Token được đính kèm tự động trong cookie `SameSite=Lax`.
2. **Next.js Middleware Gatekeeper:**
   - File `fe/middleware.ts` kiểm tra cookie xác thực trước khi route vào `(app)/*`.
   - Nếu chưa xác thực $\to$ Redirect về `/login?callbackUrl=...`.
3. **Strict Input Sanitization:** Mọi nội dung text trả về từ AI hoặc người dùng nhập vào đều được làm sạch trước khi render (tránh Stored XSS khi hiển thị CV/JD rich text).

---

## 7. Kiến trúc Xử lý Lỗi & Khả năng Phục hồi (Error Resilience)

```text
[Người dùng tương tác]
       │
       ▼
[React Error Boundary (Feature Level)] ──▶ Hiển thị Fallback UI của riêng widget đó
       │ (nếu lỗi nghiêm trọng không bắt được)
       ▼
[Next.js error.tsx (Page Level)] ────────▶ Hiển thị Trang thông báo sự cố & nút Thử lại
       │
       ▼
[Global Toast / Alert Handler] ──────────▶ Thông báo mã lỗi thân thiện, không bao giờ lộ Raw 500 JSON
```

- **Skeletons:** Mỗi component có trạng thái loading riêng biệt (không dùng 1 spinner toàn trang).
- **Empty States:** Luôn cung cấp Call-To-Action rõ ràng khi không có dữ liệu (ví dụ: "Chưa có CV nào, Tải lên ngay").
- **Automatic Retry:** TanStack Query cấu hình retry thông minh cho các lỗi mạng (Network Error / 503) và dừng retry ngay lập tức với lỗi 401, 403, 422.
