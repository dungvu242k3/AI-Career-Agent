/**
 * API Service for AI Career Copilot Chat and Multi-Channel Job Search.
 */

import { JobItem } from "../types/job";
import { ApiError } from "./cvApi";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export interface ChatResponsePayload {
  reply: string;
  detected_intent: string;
  jobs_found: JobItem[];
}

/**
 * Send a chat message or search command to the Career Copilot.
 */
export async function sendChatMessage(params: {
  message: string;
  candidateId?: string;
  domainOverride?: string;
  location?: string;
}): Promise<ChatResponsePayload> {
  try {
    const response = await fetch(`${API_BASE}/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: params.message,
        candidate_id: params.candidateId || null,
        domain_override: params.domainOverride || null,
        location: params.location || null,
      }),
    });

    if (!response.ok) {
      let errDetail = "Không thể gửi tin nhắn đến Trợ lý AI.";
      try {
        const errJson = await response.json();
        if (errJson.detail) errDetail = errJson.detail;
      } catch {
        // use fallback
      }
      throw new ApiError(response.status, errDetail);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi kết nối mạng: ${(error as Error).message}`);
  }
}

/**
 * Retrieve jobs directly by domain and experience level.
 */
export async function getJobsByDomain(params: {
  domain?: string;
  expYears?: number;
  location?: string;
  platform?: string;
  keyword?: string;
}): Promise<{ total: number; domain: string; jobs: JobItem[] }> {
  try {
    const searchParams = new URLSearchParams();
    if (params.domain) searchParams.append("domain", params.domain);
    if (params.expYears !== undefined) searchParams.append("exp_years", params.expYears.toString());
    if (params.location) searchParams.append("location", params.location);
    if (params.platform) searchParams.append("platform", params.platform);
    if (params.keyword) searchParams.append("keyword", params.keyword);

    const response = await fetch(`${API_BASE}/jobs/by-domain?${searchParams.toString()}`);

    if (!response.ok) {
      throw new ApiError(response.status, "Không thể tải danh sách việc làm.");
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi kết nối: ${(error as Error).message}`);
  }
}

/**
 * Retrieve full inside details of a specific job by ID.
 */
export async function getJobDetails(jobId: string): Promise<JobItem> {
  try {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    if (!response.ok) {
      throw new ApiError(response.status, `Không tìm thấy chi tiết công việc #${jobId}.`);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi kết nối: ${(error as Error).message}`);
  }
}
