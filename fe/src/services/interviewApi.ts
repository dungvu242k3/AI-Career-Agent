import { InterviewSession } from "../types/interview";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

export async function startInterviewSession(
  candidateId: string,
  targetRole: string = "Software Engineer",
  jdText?: string
): Promise<InterviewSession> {
  const response = await fetch(`${API_BASE_URL}/interview/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      candidate_id: candidateId,
      target_role: targetRole,
      jd_text: jdText,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Lỗi kết nối máy chủ." }));
    throw new Error(err.detail || "Không thể khởi tạo phiên phỏng vấn.");
  }

  return response.json();
}

export async function submitInterviewAnswer(
  sessionId: string,
  turnIndex: number,
  answerText: string
): Promise<InterviewSession> {
  const response = await fetch(`${API_BASE_URL}/interview/submit-answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      turn_index: turnIndex,
      answer_text: answerText,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Lỗi gửi câu trả lời." }));
    throw new Error(err.detail || "Không thể gửi câu trả lời.");
  }

  return response.json();
}

export async function getInterviewSession(sessionId: string): Promise<InterviewSession> {
  const response = await fetch(`${API_BASE_URL}/interview/session/${sessionId}`);
  if (!response.ok) {
    throw new Error("Không tìm thấy thông tin phiên phỏng vấn.");
  }
  return response.json();
}
