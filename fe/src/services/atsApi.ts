/**
 * API Service for ATS Matching, STAR Bullet Point Rewriting, and Analysis History.
 */

import { ATSHistoryItem, JDMatchReport, STARResult } from "../types/ats";
import { ApiError } from "./cvApi";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

/**
 * Match a candidate's CV against a target Job Description (text or file).
 */
export async function matchJd(
  candidateId: string,
  options: { jdText?: string; jdFile?: File }
): Promise<JDMatchReport> {
  const formData = new FormData();
  formData.append("candidate_id", candidateId);

  if (options.jdFile) {
    const file = options.jdFile;
    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".pdf") && !lower.endsWith(".docx")) {
      throw new ApiError(400, "Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Word (.docx).");
    }
    if (file.size > 2 * 1024 * 1024) {
      throw new ApiError(400, "Kích thước tệp JD vượt quá giới hạn 2MB.");
    }
    formData.append("jd_file", file);
  } else if (options.jdText && options.jdText.trim()) {
    formData.append("jd_text", options.jdText.trim());
  } else {
    throw new ApiError(400, "Vui lòng nhập văn bản JD hoặc tải tệp lên.");
  }

  try {
    const response = await fetch(`${API_BASE}/ats/match`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = "Không thể phân tích độ phù hợp của JD.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = `Lỗi HTTP ${response.status}: ${response.statusText}`;
      }
      throw new ApiError(response.status, errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Không thể kết nối đến máy chủ AI: ${(error as Error).message}`);
  }
}

/**
 * Rewrite a raw bullet point or missing skill into high-impact STAR format.
 */
export async function rewriteBulletToStar(payload: {
  raw_input: string;
  target_role?: string;
  context?: string;
}): Promise<STARResult> {
  try {
    const response = await fetch(`${API_BASE}/ats/rewrite-star`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        raw_input: payload.raw_input,
        target_role: payload.target_role || "Software Engineer",
        context: payload.context || null,
      }),
    });

    if (!response.ok) {
      let errorMessage = "Không thể viết lại câu chuẩn STAR.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = `Lỗi HTTP ${response.status}: ${response.statusText}`;
      }
      throw new ApiError(response.status, errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi khi kết nối dịch vụ viết lại STAR: ${(error as Error).message}`);
  }
}

/**
 * Fetch analysis history for candidate.
 */
export async function getAtsHistory(candidateId: string): Promise<ATSHistoryItem[]> {
  try {
    const response = await fetch(`${API_BASE}/ats/history/${candidateId}`);
    if (!response.ok) {
      return [];
    }
    return await response.json();
  } catch {
    return [];
  }
}

/**
 * Generate 1-Page Tailored Harvard CV in PDF format.
 */
export async function generateHarvardCVPdf(payload: {
  candidate_id: string;
  jd_text: string;
  language?: "vi" | "en";
}): Promise<{
  blob: Blob;
  filename: string;
  estimatedScore: number;
  wordCount: number;
  criticScore: number;
  criticApproved: boolean;
  reflectionIterations: number;
}> {
  try {
    const response = await fetch(`${API_BASE}/ats/generate-cv`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        candidate_id: payload.candidate_id,
        jd_text: payload.jd_text,
        language: payload.language || "vi",
        format: "pdf",
      }),
    });

    if (!response.ok) {
      let errorMessage = "Không thể tạo CV tối ưu chuẩn Harvard.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = `Lỗi HTTP ${response.status}: ${response.statusText}`;
      }
      throw new ApiError(response.status, errorMessage);
    }

    const disposition = response.headers.get("Content-Disposition");
    let filename = `Harvard_CV_${payload.language || "vi"}.pdf`;
    if (disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    const estimatedScore = parseInt(response.headers.get("X-Estimated-ATS-Score") || "88", 10);
    const wordCount = parseInt(response.headers.get("X-Estimated-Word-Count") || "450", 10);
    const criticScore = parseInt(response.headers.get("X-Critic-Score") || "92", 10);
    const criticApproved = response.headers.get("X-Critic-Approved") === "true";
    const reflectionIterations = parseInt(response.headers.get("X-Reflection-Iterations") || "1", 10);

    const blob = await response.blob();
    return {
      blob,
      filename,
      estimatedScore,
      wordCount,
      criticScore,
      criticApproved,
      reflectionIterations,
    };
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi khi xuất PDF CV: ${(error as Error).message}`);
  }
}

