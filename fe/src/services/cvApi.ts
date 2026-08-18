/**
 * API Service for CV Ingestion, Preview, and Profile Management
 * Follows clean error handling and envelope patterns.
 */

import { CandidateProfile, MessageResponse, UploadResponse } from "../types/candidate";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export class ApiError extends Error {
  statusCode: number;
  detail: string;

  constructor(statusCode: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

/**
 * Upload a PDF CV file to backend for AI structured parsing.
 */
export async function uploadCv(file: File): Promise<UploadResponse> {
  // Client-side validations
  const lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith(".pdf") && !lowerName.endsWith(".docx")) {
    throw new ApiError(400, "Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Microsoft Word (.docx).");
  }

  const MAX_SIZE_MB = 2;
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    throw new ApiError(
      400,
      `Kích thước tệp quá lớn (${(file.size / (1024 * 1024)).toFixed(1)}MB). Giới hạn tối đa là ${MAX_SIZE_MB}MB.`
    );
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/cv/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = "Lỗi không xác định từ máy chủ.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = `Lỗi HTTP ${response.status}: ${response.statusText}`;
      }
      throw new ApiError(response.status, errorMessage);
    }

    const data: UploadResponse = await response.json();
    // Cache active candidate in localStorage for persistence
    saveActiveCandidateLocally(data.candidate_id, data.filename, data.profile);
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, `Không thể kết nối đến máy chủ Backend: ${(error as Error).message}`);
  }
}

/**
 * Fetch candidate profile for preview by ID.
 */
export async function getCandidatePreview(candidateId: string): Promise<CandidateProfile> {
  try {
    const response = await fetch(`${API_BASE}/cv/preview/${candidateId}`);
    if (!response.ok) {
      let errorMessage = "Không tìm thấy hồ sơ ứng viên.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        // use default
      }
      throw new ApiError(response.status, errorMessage);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi khi lấy thông tin hồ sơ: ${(error as Error).message}`);
  }
}

/**
 * Update candidate profile after user edits.
 */
export async function updateCandidatePreview(
  candidateId: string,
  profile: CandidateProfile
): Promise<MessageResponse> {
  try {
    const response = await fetch(`${API_BASE}/cv/preview/${candidateId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ profile }),
    });

    if (!response.ok) {
      let errorMessage = "Không thể cập nhật hồ sơ.";
      try {
        const errorJson = await response.json();
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        // use default
      }
      throw new ApiError(response.status, errorMessage);
    }

    const result: MessageResponse = await response.json();
    saveActiveCandidateLocally(candidateId, getActiveFilenameLocally() || "CV_Cap_Nhat.pdf", profile);
    return result;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(500, `Lỗi khi lưu hồ sơ: ${(error as Error).message}`);
  }
}

// --- Local Storage Helpers ---

const STORAGE_KEYS = {
  CANDIDATE_ID: "careerpilot_candidate_id",
  FILENAME: "careerpilot_filename",
  PROFILE: "careerpilot_profile",
};

export function saveActiveCandidateLocally(candidateId: string, filename: string, profile: CandidateProfile) {
  try {
    localStorage.setItem(STORAGE_KEYS.CANDIDATE_ID, candidateId);
    localStorage.setItem(STORAGE_KEYS.FILENAME, filename);
    localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
  } catch (e) {
    console.warn("Could not save candidate to localStorage:", e);
  }
}

export function getActiveCandidateLocally(): {
  candidateId: string | null;
  filename: string | null;
  profile: CandidateProfile | null;
} {
  try {
    const idStr = localStorage.getItem(STORAGE_KEYS.CANDIDATE_ID);
    const filename = localStorage.getItem(STORAGE_KEYS.FILENAME);
    const profileStr = localStorage.getItem(STORAGE_KEYS.PROFILE);

    return {
      candidateId: idStr || null,
      filename: filename || null,
      profile: profileStr ? JSON.parse(profileStr) : null,
    };
  } catch {
    return { candidateId: null, filename: null, profile: null };
  }
}

export function getActiveFilenameLocally(): string | null {
  return localStorage.getItem(STORAGE_KEYS.FILENAME);
}
