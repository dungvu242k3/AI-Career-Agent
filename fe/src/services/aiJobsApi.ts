import { apiFetch } from "./apiClient";
import { ApiError } from "./apiError";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export type AIJobOperation = "cv-ingestion" | "cv-generation";
export type AIJobState = "queued" | "running" | "succeeded" | "failed";

export interface AIJobAccepted {
  job_id: string;
  status: AIJobState;
  poll_url: string;
}

export interface AIJobStatus<T = Record<string, unknown>> {
  job_id: string;
  operation: AIJobOperation;
  status: AIJobState;
  progress: number;
  result: T | null;
  error_code: string | null;
  trace_id: string | null;
  attempts: number;
}

function newIdempotencyKey(): string {
  return crypto.randomUUID();
}

async function responseError(response: Response, fallback: string): Promise<ApiError> {
  let message = fallback;
  try {
    const body = await response.json();
    const detail = body?.detail;
    message = typeof detail === "string" ? detail : detail?.message || detail?.code || fallback;
  } catch {
    // Preserve the stable fallback when a proxy returns a non-JSON response.
  }
  return new ApiError(response.status, message);
}

export async function enqueueAIJob(
  operation: AIJobOperation,
  body: FormData | Record<string, unknown>,
  idempotencyKey = newIdempotencyKey(),
): Promise<AIJobAccepted> {
  const response = await apiFetch(`${API_BASE}/ai-jobs/${operation}`, {
    method: "POST",
    headers: {
      ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      "Idempotency-Key": idempotencyKey,
    },
    body: body instanceof FormData ? body : JSON.stringify(body),
  });
  if (!response.ok) throw await responseError(response, "Unable to enqueue AI job");
  return response.json();
}

export async function getAIJob<T = Record<string, unknown>>(jobId: string): Promise<AIJobStatus<T>> {
  const response = await apiFetch(`${API_BASE}/ai-jobs/${jobId}`);
  if (!response.ok) throw await responseError(response, "Unable to read AI job status");
  return response.json();
}

export async function waitForAIJob<T = Record<string, unknown>>(
  jobId: string,
  options: { intervalMs?: number; timeoutMs?: number; signal?: AbortSignal } = {},
): Promise<AIJobStatus<T>> {
  const intervalMs = options.intervalMs ?? 800;
  const timeoutMs = options.timeoutMs ?? 180_000;
  const startedAt = Date.now();

  while (true) {
    if (options.signal?.aborted) throw new DOMException("AI job polling cancelled", "AbortError");
    const job = await getAIJob<T>(jobId);
    if (job.status === "succeeded") return job;
    if (job.status === "failed") {
      throw new ApiError(502, job.error_code || "AI job failed");
    }
    if (Date.now() - startedAt >= timeoutMs) {
      throw new ApiError(504, "AI job is still processing; please retry from job history");
    }
    await new Promise<void>((resolve, reject) => {
      const timer = window.setTimeout(resolve, intervalMs);
      options.signal?.addEventListener("abort", () => {
        window.clearTimeout(timer);
        reject(new DOMException("AI job polling cancelled", "AbortError"));
      }, { once: true });
    });
  }
}

export async function downloadOwnerFile(storageKey: string): Promise<Blob> {
  const response = await apiFetch(`${API_BASE}/cv/file/${encodeURI(storageKey)}`);
  if (!response.ok) throw await responseError(response, "Unable to download generated CV");
  return response.blob();
}
