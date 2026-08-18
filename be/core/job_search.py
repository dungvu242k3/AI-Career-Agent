"""Multi-Channel Job Aggregator & Domain-Based Job Search Engine.

Supports filtering by candidate domain (Backend, Frontend, Fullstack, DevOps, Mobile, AI/Data),
years of experience, location, and recruitment platforms (ITviec, TopCV, VietnamWorks, LinkedIn).
"""

from typing import Any
from be.api.v1.schemas import JobItemSchema


# Real-world styled job database with accurate company profiles, tech stacks, and requirements
JOB_DATABASE: list[JobItemSchema] = [
    # --- BACKEND JOBS ---
    JobItemSchema(
        id="job-be-001",
        title="Senior Backend Engineer (Python / FastAPI / Async)",
        company="VNG Corporation",
        platform="ITviec",
        platform_color="#ea580c",  # ITviec Orange/Red
        experience_required="3 - 5 năm kinh nghiệm",
        min_years_exp=3.0,
        max_years_exp=6.0,
        domain="backend",
        location="TP. Hồ Chí Minh (Hybrid)",
        salary_range="$2,200 - $3,200",
        job_url="https://itviec.com/jobs/vng-senior-backend-engineer",
        skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka", "Docker"],
        description="Tham gia phát triển hệ thống backend phân tán phục vụ hàng triệu người dùng hoạt động hàng ngày. Thiết kế kiến trúc microservices tối ưu hóa latency và xử lý dữ liệu thời gian thực.",
        requirements="• Tối thiểu 3 năm kinh nghiệm phát triển backend với Python (FastAPI/Django).\n• Thành thạo PostgreSQL (tối ưu query, indexing) và Redis Caching.\n• Kinh nghiệm với Message Queue (Kafka/RabbitMQ) và kiến trúc Event-Driven.\n• Hiểu biết vững về Docker, Kubernetes và quy trình CI/CD.",
        benefits="• Tháng lương 13 + Thưởng hiệu suất (2-4 tháng lương).\n• Bảo hiểm sức khỏe PVI cao cấp cho nhân viên và người thân.\n• Cung cấp Macbook Pro M3 và trợ cấp học chứng chỉ quốc tế.",
        posted_date="2 giờ trước",
    ),
    JobItemSchema(
        id="job-be-002",
        title="Backend Developer (Golang / High Concurrency)",
        company="Tiki Corporation",
        platform="TopCV",
        platform_color="#10b981",  # TopCV Green
        experience_required="2 - 4 năm kinh nghiệm",
        min_years_exp=2.0,
        max_years_exp=5.0,
        domain="backend",
        location="Hà Nội / TP. HCM",
        salary_range="35 - 55 triệu VNĐ",
        job_url="https://www.topcv.vn/viec-lam/tiki-golang-backend-developer",
        skills=["Golang", "gRPC", "MySQL", "Redis", "Kafka", "Elasticsearch"],
        description="Xây dựng và bảo trì các dịch vụ thanh toán và quản lý đơn hàng lõi của Tiki. Tối ưu throughput hệ thống đảm bảo xử lý mượt mà trong các đợt Siêu Sale lớn.",
        requirements="• Từ 2+ năm kinh nghiệm lập trình Go (Golang).\n• Nắm chắc kiến trúc gRPC, RESTful API và Concurrency/Goroutines.\n• Có kinh nghiệm tối ưu truy vấn MySQL quy mô hàng chục triệu bản ghi.\n• Tinh thần Ownership cao, chủ động giải quyết vấn đề.",
        benefits="• 15 ngày phép/năm, làm việc hybrid linh hoạt.\n• Review lương định kỳ 2 lần/năm.\n• Môi trường công nghệ e-commerce hàng đầu.",
        posted_date="Hôm nay",
    ),
    JobItemSchema(
        id="job-be-003",
        title="Lead Java Backend Architect",
        company="Techcombank",
        platform="VietnamWorks",
        platform_color="#2563eb",  # VietnamWorks Blue
        experience_required="5+ năm kinh nghiệm",
        min_years_exp=5.0,
        max_years_exp=12.0,
        domain="backend",
        location="Hà Nội (Onsite)",
        salary_range="$3,500 - $4,800",
        job_url="https://www.vietnamworks.com/techcombank-java-backend-lead",
        skills=["Java", "Spring Boot", "Microservices", "Oracle DB", "Kafka", "AWS"],
        description="Dẫn dắt đội ngũ kỹ sư backend phát triển nền tảng ngân hàng số thế hệ mới. Đảm bảo tính sẵn sàng cao (High Availability), bảo mật chuẩn PCI-DSS và khả năng mở rộng hệ thống.",
        requirements="• 5+ năm kinh nghiệm Java/Spring Boot và thiết kế Microservices.\n• Am hiểu sâu về bảo mật ngân hàng, mã hóa dữ liệu, OAuth2, JWT.\n• Kinh nghiệm triển khai hệ thống Cloud-native trên AWS hoặc GCP.\n• Khả năng lãnh đạo và mentor đội ngũ kỹ sư trẻ.",
        benefits="• Gói đãi ngộ tài chính vượt trội, thưởng hiệu suất hàng năm cao.\n• Khám sức khỏe toàn diện tại bệnh viện quốc tế.\n• Cơ hội định hình kiến trúc ngân hàng số lớn nhất VN.",
        posted_date="1 ngày trước",
    ),
    JobItemSchema(
        id="job-be-004",
        title="Junior / Mid Node.js Backend Engineer",
        company="One Mount Group",
        platform="LinkedIn",
        platform_color="#0a66c2",  # LinkedIn Blue
        experience_required="1 - 3 năm kinh nghiệm",
        min_years_exp=1.0,
        max_years_exp=3.0,
        domain="backend",
        location="Hà Nội",
        salary_range="22 - 35 triệu VNĐ",
        job_url="https://www.linkedin.com/jobs/view/onemount-nodejs-engineer",
        skills=["Node.js", "TypeScript", "NestJS", "PostgreSQL", "Docker"],
        description="Tham gia phát triển hệ sinh thái VinShop & VinID. Viết API hiệu năng cao phục vụ ứng dụng người dùng cuối và hệ thống đối tác đại lý.",
        requirements="• 1-3 năm kinh nghiệm làm việc với Node.js, TypeScript, NestJS/Express.\n• Hiểu biết tốt về Async programming, Event Loop.\n• Sử dụng thành thạo Git, PostgreSQL và ORM (Prisma/TypeORM).",
        benefits="• Môi trường công nghệ hiện đại, trẻ trung và cởi mở.\n• Bữa trưa miễn phí tại canteen công ty, phòng gym nội bộ.",
        posted_date="3 ngày trước",
    ),

    # --- FRONTEND JOBS ---
    JobItemSchema(
        id="job-fe-001",
        title="Senior Frontend Engineer (React / Next.js / TypeScript)",
        company="Shopee Vietnam",
        platform="ITviec",
        platform_color="#ea580c",
        experience_required="3 - 6 năm kinh nghiệm",
        min_years_exp=3.0,
        max_years_exp=6.0,
        domain="frontend",
        location="TP. Hồ Chí Minh",
        salary_range="$2,000 - $3,000",
        job_url="https://itviec.com/jobs/shopee-senior-frontend-engineer",
        skills=["React", "Next.js", "TypeScript", "Tailwind CSS", "Redux Toolkit", "Web Performance"],
        description="Xây dựng giao diện web ứng dụng mua sắm hàng đầu Đông Nam Á. Tối ưu Core Web Vitals, giảm TBT (Total Blocking Time) và tăng tốc độ tải trang trên mọi thiết bị.",
        requirements="• 3+ năm kinh nghiệm chuyên sâu về React và Next.js (App Router/SSR/SSG).\n• Thành thạo TypeScript, quản lý state và kỹ thuật tối ưu bundle size.\n• Nắm vững kiến thức về responsive design, Accessibility (a11y) và CSS Animation.",
        benefits="• Lương tháng 13 + thưởng quý hấp dẫn.\n• Hỗ trợ ăn trưa, bảo hiểm cao cấp, văn phòng hạng A.",
        posted_date="1 ngày trước",
    ),
    JobItemSchema(
        id="job-fe-002",
        title="Middle Frontend Developer (Vue.js / Nuxt 3)",
        company="FPT Software",
        platform="TopCV",
        platform_color="#10b981",
        experience_required="2 - 4 năm kinh nghiệm",
        min_years_exp=2.0,
        max_years_exp=4.0,
        domain="frontend",
        location="Đà Nẵng / Hà Nội",
        salary_range="25 - 40 triệu VNĐ",
        job_url="https://www.topcv.vn/viec-lam/fpt-frontend-vuejs",
        skills=["Vue.js", "Nuxt 3", "Pinia", "TypeScript", "TailwindCSS"],
        description="Tham gia dự án chuyển đổi số toàn diện cho đối tác quốc tế tại Nhật Bản và Singapore. Xây dựng dashboard tương tác realtime phân tích dữ liệu sản xuất.",
        requirements="• 2+ năm kinh nghiệm với Vue 3 Composition API và Nuxt 3.\n• Kỹ năng viết code sạch, component tái sử dụng cao và viết unit test với Vitest.",
        benefits="• Cơ hội Onsite ngắn hạn và dài hạn tại Nhật Bản/Singapore.\n• Thưởng dự án liên tục theo từng giai đoạn bàn giao.",
        posted_date="2 ngày trước",
    ),

    # --- FULLSTACK JOBS ---
    JobItemSchema(
        id="job-fs-001",
        title="Senior Fullstack Developer (Node.js + React / Next.js)",
        company="KMS Technology",
        platform="LinkedIn",
        platform_color="#0a66c2",
        experience_required="4 - 7 năm kinh nghiệm",
        min_years_exp=4.0,
        max_years_exp=7.0,
        domain="fullstack",
        location="TP. Hồ Chí Minh / Remote",
        salary_range="$2,500 - $3,800",
        job_url="https://www.linkedin.com/jobs/view/kms-senior-fullstack-dev",
        skills=["TypeScript", "React", "Node.js", "NestJS", "PostgreSQL", "AWS"],
        description="Phát triển trọn gói sản phẩm SaaS phục vụ các doanh nghiệp tại thị trường Bắc Mỹ. Làm việc trực tiếp với Product Manager để hiện thực hóa tính năng từ thiết kế DB đến UI/UX.",
        requirements="• 4+ năm kinh nghiệm Fullstack (React/Next.js cho Frontend và Node.js/NestJS cho Backend).\n• Khả năng tự chủ thiết kế Database Schema, REST/GraphQL API và Deploy Cloud AWS.\n• Tiếng Anh giao tiếp tốt (làm việc trực tiếp với khách hàng US).",
        benefits="• Chế độ làm việc Remote 100% linh hoạt.\n• Tài trợ 100% học phí các chứng chỉ AWS / PMP.",
        posted_date="Vừa đăng",
    ),
    JobItemSchema(
        id="job-fs-002",
        title="Fullstack Engineer (Python / Django + React)",
        company="Got It AI Vietnam",
        platform="ITviec",
        platform_color="#ea580c",
        experience_required="2 - 5 năm kinh nghiệm",
        min_years_exp=2.0,
        max_years_exp=5.0,
        domain="fullstack",
        location="Hà Nội (Hybrid)",
        salary_range="$1,800 - $2,800",
        job_url="https://itviec.com/jobs/got-it-fullstack-python-react",
        skills=["Python", "Django", "React", "TypeScript", "PostgreSQL", "Docker"],
        description="Phát triển nền tảng AI Conversational Agent phục vụ khách hàng toàn cầu. Tích hợp các mô hình LLM vào sản phẩm với giao diện trực quan và backend chịu tải.",
        requirements="• 2+ năm kinh nghiệm với Python (Django/FastAPI) và React (TypeScript).\n• Đam mê AI và công nghệ mới. Kỹ năng tư duy logic và giải quyết vấn đề tốt.",
        benefits="• Cổ phần ESOP hấp dẫn cho nhân viên có đóng góp xuất sắc.\n• Snack bar không giới hạn, máy pha cà phê xịn.",
        posted_date="4 giờ trước",
    ),

    # --- DEVOPS / CLOUD JOBS ---
    JobItemSchema(
        id="job-ops-001",
        title="DevOps / Cloud Infrastructure Engineer (Kubernetes & AWS)",
        company="Momo (M-Service)",
        platform="ITviec",
        platform_color="#ea580c",
        experience_required="3 - 6 năm kinh nghiệm",
        min_years_exp=3.0,
        max_years_exp=6.0,
        domain="devops",
        location="TP. Hồ Chí Minh",
        salary_range="$2,200 - $3,500",
        job_url="https://itviec.com/jobs/momo-devops-engineer",
        skills=["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Prometheus", "Grafana"],
        description="Vận hành hạ tầng điện toán đám mây cho ví điện tử số 1 Việt Nam. Tự động hóa quy trình triển khai CI/CD, thiết lập giám sát Observability và bảo mật hệ thống.",
        requirements="• 3+ năm kinh nghiệm DevOps, quản trị Kubernetes Cluster production.\n• Thành thạo Infrastructure as Code (Terraform) và quản lý AWS Cloud.\n• Kinh nghiệm thiết lập CI/CD pipeline với GitLab CI / GitHub Actions.",
        benefits="• Môi trường Fintech phát triển thần tốc.\n• Lương thưởng cạnh tranh, cơ hội học hỏi từ các chuyên gia hàng đầu.",
        posted_date="1 ngày trước",
    ),

    # --- MOBILE JOBS ---
    JobItemSchema(
        id="job-mb-001",
        title="Senior Mobile Developer (React Native / Flutter)",
        company="ZaloPay",
        platform="TopCV",
        platform_color="#10b981",
        experience_required="3 - 5 năm kinh nghiệm",
        min_years_exp=3.0,
        max_years_exp=5.0,
        domain="mobile",
        location="TP. Hồ Chí Minh",
        salary_range="40 - 65 triệu VNĐ",
        job_url="https://www.topcv.vn/viec-lam/zalopay-mobile-developer",
        skills=["React Native", "Flutter", "iOS", "Android", "TypeScript", "Mobile Security"],
        description="Phát triển các tính năng thanh toán, chuyển tiền và dịch vụ tiện ích trên ứng dụng di động ZaloPay. Tối ưu performance và trải nghiệm người dùng mượt mà.",
        requirements="• 3+ năm kinh nghiệm phát triển Mobile App với React Native hoặc Flutter.\n• Nắm vững vòng đời ứng dụng, quản lý bộ nhớ, Native Bridge và Offline Storage.\n• Có app đã phát hành trên Google Play Store và Apple App Store.",
        benefits="• Lương tháng 13 + thưởng kinh doanh hàng năm.\n• Bảo hiểm sức khỏe quốc tế cao cấp.",
        posted_date="Hôm nay",
    ),

    # --- AI & DATA JOBS ---
    JobItemSchema(
        id="job-ai-001",
        title="AI / LLM Application Engineer",
        company="Viettel AI Center",
        platform="LinkedIn",
        platform_color="#0a66c2",
        experience_required="2 - 5 năm kinh nghiệm",
        min_years_exp=2.0,
        max_years_exp=5.0,
        domain="ai_data",
        location="Hà Nội",
        salary_range="$2,000 - $3,500",
        job_url="https://www.linkedin.com/jobs/view/viettel-ai-engineer",
        skills=["Python", "PyTorch", "LangChain", "RAG", "Vector DB", "FastAPI"],
        description="Xây dựng các giải pháp ứng dụng Generative AI, RAG (Retrieval-Augmented Generation) và AI Agents phục vụ doanh nghiệp và cơ quan chính phủ.",
        requirements="• 2+ năm kinh nghiệm với Python, PyTorch/Transformers và hệ sinh thái GenAI.\n• Hiểu sâu về Prompt Engineering, Fine-tuning, Embeddings và Vector Database (Milvus/Pinecone/Chroma).\n• Kỹ năng xây dựng API dịch vụ triển khai mô hình AI.",
        benefits="• Làm việc với hệ thống siêu máy tính GPU mạnh nhất VN.\n• Tham gia các đề án quốc gia có tầm ảnh hưởng lớn.",
        posted_date="2 ngày trước",
    ),
]


from ai.analysis.hybrid_search import HybridJobSearchEngine
from ai.analysis.job_reranker import JobCrossEncoderReranker
from ai.models.candidate import CandidateProfile

_hybrid_engine = HybridJobSearchEngine()
_reranker = JobCrossEncoderReranker()


def detect_candidate_domain(title: str | None, skills_summary: list[str] | None = None) -> str:
    """Intelligently infer candidate's primary domain from job title and skill set."""
    text_to_check = f"{title or ''} {' '.join(skills_summary or [])}".lower()

    if any(k in text_to_check for k in ["fullstack", "full stack", "full-stack"]):
        return "fullstack"
    if any(k in text_to_check for k in ["devops", "cloud", "sre", "infrastructure", "kubernetes"]):
        return "devops"
    if any(k in text_to_check for k in ["mobile", "android", "ios", "flutter", "react native"]):
        return "mobile"
    if any(k in text_to_check for k in ["ai", "machine learning", "data", "ml", "nlp", "llm"]):
        return "ai_data"
    if any(k in text_to_check for k in ["frontend", "front-end", "react", "vue", "angular", "ui/ux", "web developer"]):
        # Verify it's not predominantly backend
        if "backend" not in text_to_check:
            return "frontend"
    # Default to backend as widely applicable
    return "backend"


def search_jobs(
    domain: str | None = None,
    keyword: str | None = None,
    platform: str | None = None,
    min_exp_years: float | None = None,
    location: str | None = None,
    limit: int = 10,
    candidate_profile: CandidateProfile | None = None,
) -> list[JobItemSchema]:
    """Search and filter jobs using Hybrid Dense-Sparse Search and Cross-Encoder Re-Ranking."""
    # If candidate profile is provided, run Hybrid Search + Semantic Re-ranking!
    if candidate_profile:
        jobs_as_dicts = [j.model_dump() for j in JOB_DATABASE]
        ranked = _hybrid_engine.search_and_rank(
            jobs=jobs_as_dicts,
            query=keyword or "",
            candidate_profile=candidate_profile,
            domain_filter=domain,
            experience_filter=min_exp_years,
        )
        reranked = _reranker.rerank_top_k(
            candidate_profile=candidate_profile,
            ranked_jobs=ranked,
            top_k=limit,
        )
        return [JobItemSchema(**r) for r in reranked]

    # Standard fast filtering when candidate profile is not provided
    results: list[JobItemSchema] = []
    clean_domain = (domain or "").lower().strip()
    clean_keyword = (keyword or "").lower().strip()
    clean_location = (location or "").lower().strip()
    clean_platform = (platform or "").lower().strip()

    for job in JOB_DATABASE:
        # Match Domain
        if clean_domain and clean_domain != "all":
            if clean_domain not in job.domain and job.domain not in clean_domain:
                # Also check title match
                if clean_domain not in job.title.lower():
                    continue

        # Match Platform (ITviec, TopCV, VietnamWorks, LinkedIn)
        if clean_platform and clean_platform != "all":
            if clean_platform not in job.platform.lower():
                continue

        # Match Location
        if clean_location:
            if clean_location not in job.location.lower():
                continue

        # Match Experience Range (if provided)
        if min_exp_years is not None:
            # Allow some margin (e.g. candidate with 3 years can match 2-4 or 3-5 years)
            if job.min_years_exp > min_exp_years + 2.0 or job.max_years_exp < min_exp_years - 2.0:
                continue

        # Match Keyword in Title, Description, Skills
        if clean_keyword:
            content_blob = f"{job.title} {job.company} {job.description} {' '.join(job.skills)}".lower()
            if clean_keyword not in content_blob:
                continue

        results.append(job)

    # If domain specified had no exact matches, fallback to return top domain jobs
    if not results and clean_domain and clean_domain != "all":
        results = [j for j in JOB_DATABASE if j.domain == clean_domain or clean_domain in j.domain]

    return results[:limit]


def get_job_by_id(job_id: str) -> JobItemSchema | None:
    """Retrieve a single job item with full descriptions."""
    for job in JOB_DATABASE:
        if job.id == job_id:
            return job
    return None
