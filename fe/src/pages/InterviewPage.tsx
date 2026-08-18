import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  InterviewSession,
  InterviewTurn,
  CandidateAssessmentReport,
} from "../types/interview";
import {
  startInterviewSession,
  submitInterviewAnswer,
} from "../services/interviewApi";
import { getActiveCandidateLocally } from "../services/cvApi";

export default function InterviewPage() {
  const [candidateId, setCandidateId] = useState<string>("");
  const [targetRole, setTargetRole] = useState<string>("Senior Backend Engineer");
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentTurnIdx, setCurrentTurnIdx] = useState<number>(0);
  const [answerText, setAnswerText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showIdealAnswer, setShowIdealAnswer] = useState<boolean>(false);
  const [timerSeconds, setTimerSeconds] = useState<number>(0);

  // Initialize candidate ID from storage
  useEffect(() => {
    const local = getActiveCandidateLocally();
    if (local.candidateId) {
      setCandidateId(local.candidateId);
      if (local.profile?.summary?.detected_title) {
        setTargetRole(local.profile.summary.detected_title);
      }
    }
  }, []);

  // Timer effect when session is active
  useEffect(() => {
    let interval: any = null;
    if (session && !session.is_completed) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [session]);

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const handleStartInterview = async () => {
    if (!candidateId) {
      setErrorMsg("Vui lòng tải lên hoặc chọn một hồ sơ CV tại trang Workspace trước khi bắt đầu phỏng vấn.");
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);
    try {
      const newSession = await startInterviewSession(candidateId, targetRole);
      setSession(newSession);
      setCurrentTurnIdx(0);
      setAnswerText("");
      setTimerSeconds(0);
      setShowIdealAnswer(false);
    } catch (err: any) {
      setErrorMsg(err.message || "Không thể khởi tạo phiên phỏng vấn.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !answerText.trim()) return;

    setIsLoading(true);
    setErrorMsg(null);
    try {
      const updatedSession = await submitInterviewAnswer(
        session.session_id,
        currentTurnIdx + 1,
        answerText
      );
      setSession(updatedSession);
      setShowIdealAnswer(false);
    } catch (err: any) {
      setErrorMsg(err.message || "Lỗi gửi câu trả lời.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextTurn = () => {
    if (!session) return;
    if (currentTurnIdx < session.turns.length - 1) {
      setCurrentTurnIdx((prev) => prev + 1);
      setAnswerText("");
      setShowIdealAnswer(false);
    }
  };

  const currentTurn: InterviewTurn | undefined = session?.turns[currentTurnIdx];
  const isTurnEvaluated = !!currentTurn?.evaluation;

  return (
    <div className="min-h-screen bg-[#090D16] text-[#dfe2ef] antialiased selection:bg-[#10b981] selection:text-[#090D16] font-['Inter',sans-serif]">
      {/* HEADER BAR */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-[#090D16]/90 backdrop-blur-md border-b border-[#1E293B]">
        <div className="max-w-[1300px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              to="/workspace"
              className="text-xs font-semibold text-slate-400 hover:text-emerald-400 flex items-center gap-1.5 transition-colors"
            >
              <span>←</span>
              <span>Trở về Workspace</span>
            </Link>
            <span className="text-slate-600">|</span>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <h1 className="text-sm font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                Adversarial Multi-Agent Mock Interview Arena
              </h1>
            </div>
          </div>

          {session && !session.is_completed && (
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="text-slate-400">⏱️ Thời gian: <span className="text-white font-bold">{formatTimer(timerSeconds)}</span></span>
              <span className="bg-slate-800 text-emerald-400 px-2.5 py-1 rounded border border-slate-700 font-bold">
                Lượt {currentTurnIdx + 1}/{session.turns.length}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="pt-24 pb-16 max-w-[1200px] mx-auto px-6 md:px-12">
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between">
            <span>⚠️ {errorMsg}</span>
            <button
              onClick={() => setErrorMsg(null)}
              className="text-rose-400 hover:text-white font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {/* --- VIEW 1: LOBBY / PREPARATION --- */}
        {!session && (
          <div className="space-y-8">
            <div className="border-b border-[#1E293B] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-2 border border-[#10b981]/30 rounded-full px-3 py-0.5 bg-[#181b25] text-xs font-['JetBrains_Mono',monospace] text-[#4edea3] mb-2">
                  <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
                  ADVERSARIAL 3-AGENT ARENA
                </div>
                <h2 className="font-['Plus_Jakarta_Sans',sans-serif] text-2xl sm:text-3xl font-bold text-[#f8fafc] tracking-tight">
                  Đấu Trường Phỏng Vấn Giả Lập Đa Tác Tử
                </h2>
                <p className="text-sm text-[#94a3b8] mt-1">
                  Trải nghiệm phỏng vấn dồn dập thực tế với 2 Giám khảo AI đối kháng: <strong className="text-sky-400">Mr. Alex (Tech Lead)</strong> và <strong className="text-rose-400">Ms. Sarah (HR Director)</strong>, cùng Trọng tài AI chấm điểm STAR tức thì.
                </p>
              </div>
            </div>

            {/* Persona Introduction Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Persona 1: Tech Lead */}
              <div className="bg-[#111827] border border-[#1E293B] hover:border-sky-500/50 p-6 rounded-2xl transition-all shadow-xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-sky-950 border border-sky-500/40 flex items-center justify-center text-2xl">
                    👨‍💻
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                      Mr. Alex
                    </h3>
                    <p className="text-xs text-sky-400 font-mono font-medium">
                      Tech Lead / System Architect
                    </p>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Sắc sảo, đào sâu vào kiến trúc phân tán, bài toán tải cao (Traffic Spikes), Concurrency, cơ chế Caching Redis, và xử lý lỗi Failover.
                </p>
                <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800">
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">System Design</span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Caching Stampede</span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Concurrency</span>
                </div>
              </div>

              {/* Persona 2: HR Director */}
              <div className="bg-[#111827] border border-[#1E293B] hover:border-rose-500/50 p-6 rounded-2xl transition-all shadow-xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-rose-950 border border-rose-500/40 flex items-center justify-center text-2xl">
                    👩‍💼
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white font-['Plus_Jakarta_Sans',sans-serif]">
                      Ms. Sarah
                    </h3>
                    <p className="text-xs text-rose-400 font-mono font-medium">
                      HR & Culture Director
                    </p>
                  </div>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Tâm lý nhưng trực diện, chen ngang để thử thách kỹ năng giải quyết bất đồng quan điểm kỹ thuật, áp lực Deadline và cấu trúc trả lời STAR.
                </p>
                <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800">
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">STAR Methodology</span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Conflict Resolution</span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Ownership</span>
                </div>
              </div>
            </div>

            {/* Launch Console */}
            <div className="bg-[#111827] border border-emerald-500/40 p-6 rounded-2xl space-y-4 shadow-xl">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h4 className="text-sm font-bold text-white">Vị trí mục tiêu cho buổi phỏng vấn:</h4>
                  <p className="text-xs text-slate-400 mt-0.5">AI sẽ tự động đọc hồ sơ CV của bạn để may đo câu hỏi phản biện.</p>
                </div>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="bg-[#090D16] border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 w-full sm:w-72"
                  placeholder="VD: Senior Backend Engineer"
                />
              </div>

              <button
                type="button"
                onClick={handleStartInterview}
                disabled={isLoading}
                className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-[#090D16] font-bold py-3.5 rounded-xl text-sm transition-all shadow-lg flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></span>
                    <span>Đang khởi tạo phòng phỏng vấn AI...</span>
                  </>
                ) : (
                  <>
                    <span>🎙️</span>
                    <span>Bắt Đầu Phiên Phỏng Vấn Giả Lập Ngay</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* --- VIEW 2: LIVE INTERVIEW ARENA --- */}
        {session && !session.is_completed && currentTurn && (
          <div className="space-y-6">
            {/* Active Interviewer Showcase */}
            <div className="grid grid-cols-2 gap-4">
              <div
                className={`p-4 rounded-xl border transition-all flex items-center gap-3 ${
                  currentTurn.question.interviewer.name === "Alex"
                    ? "bg-sky-950/40 border-sky-500 shadow-lg shadow-sky-500/10"
                    : "bg-[#111827] border-slate-800 opacity-60"
                }`}
              >
                <div className="text-2xl">👨‍💻</div>
                <div>
                  <div className="text-xs font-bold text-white">Mr. Alex (Tech Lead)</div>
                  <div className="text-[10px] text-sky-400 font-mono">
                    {currentTurn.question.interviewer.name === "Alex" ? "🔊 Đang phỏng vấn" : "Đang lắng nghe"}
                  </div>
                </div>
              </div>

              <div
                className={`p-4 rounded-xl border transition-all flex items-center gap-3 ${
                  currentTurn.question.interviewer.name === "Sarah"
                    ? "bg-rose-950/40 border-rose-500 shadow-lg shadow-rose-500/10"
                    : "bg-[#111827] border-slate-800 opacity-60"
                }`}
              >
                <div className="text-2xl">👩‍💼</div>
                <div>
                  <div className="text-xs font-bold text-white">Ms. Sarah (HR Director)</div>
                  <div className="text-[10px] text-rose-400 font-mono">
                    {currentTurn.question.interviewer.name === "Sarah" ? "🔊 Đang phỏng vấn" : "Đang lắng nghe"}
                  </div>
                </div>
              </div>
            </div>

            {/* Question Speech Bubble */}
            <div className="bg-[#111827] border border-slate-800 p-6 rounded-2xl space-y-3 shadow-xl relative">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className="text-[10px] font-bold uppercase px-2 py-0.5 rounded font-mono"
                    style={{
                      backgroundColor: `${currentTurn.question.interviewer.avatar_color}20`,
                      color: currentTurn.question.interviewer.avatar_color,
                      border: `1px solid ${currentTurn.question.interviewer.avatar_color}50`,
                    }}
                  >
                    {currentTurn.question.interviewer.name} ({currentTurn.question.interviewer.role})
                  </span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono uppercase">
                    {currentTurn.question.category.replace("_", " ")}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  Độ khó: <span className="text-amber-400 uppercase font-bold">{currentTurn.question.difficulty}</span>
                </span>
              </div>

              <p className="text-sm sm:text-base font-semibold text-white leading-relaxed font-['Plus_Jakarta_Sans',sans-serif]">
                "{currentTurn.question.question_text}"
              </p>

              {currentTurn.question.context_hint && (
                <p className="text-xs text-slate-400 bg-[#090D16] p-2.5 rounded-lg border border-slate-800 flex items-center gap-1.5">
                  <span>💡 Gợi ý giám khảo:</span>
                  <span>{currentTurn.question.context_hint}</span>
                </p>
              )}
            </div>

            {/* Answer Box & Judge Evaluation */}
            {!isTurnEvaluated ? (
              <div className="bg-[#111827] border border-slate-800 p-6 rounded-2xl space-y-4 shadow-xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase text-slate-300 font-mono">
                    ✍️ Câu trả lời của bạn (Khuyên dùng cấu trúc STAR):
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">
                    {answerText.trim().split(/\s+/).filter(Boolean).length} từ
                  </span>
                </div>

                <textarea
                  rows={6}
                  value={answerText}
                  onChange={(e) => setAnswerText(e.target.value)}
                  placeholder="Nhập câu trả lời của bạn tại đây... (Ví dụ: Trong dự án fintech trước đây khi traffic tăng 5x, tôi đã triển khai Redis caching và Kafka queue giúp giảm 50% độ trễ API...)"
                  className="w-full bg-[#090D16] border border-slate-700 rounded-xl p-4 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-emerald-500 leading-relaxed font-['Inter',sans-serif]"
                />

                <div className="flex items-center justify-between gap-4">
                  <div className="text-[11px] text-slate-400">
                    💡 Mẹo: Nhớ nêu rõ <strong>Tình huống (S)</strong>, <strong>Hành động kỹ thuật (A)</strong> và <strong>Kết quả số liệu (R)</strong>.
                  </div>
                  <button
                    type="button"
                    onClick={handleSubmitAnswer}
                    disabled={isLoading || answerText.trim().length < 5}
                    className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-[#090D16] font-bold px-6 py-2.5 rounded-xl text-xs sm:text-sm transition-all shadow-md flex items-center gap-2 shrink-0"
                  >
                    {isLoading ? (
                      <>
                        <span className="w-3.5 h-3.5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></span>
                        <span>Trọng tài AI đang chấm điểm...</span>
                      </>
                    ) : (
                      <>
                        <span>Gửi câu trả lời</span>
                        <span>➔</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              /* Turn Evaluation Scorecard by Silent Judge */
              <div className="bg-[#111827] border border-emerald-500/40 p-6 rounded-2xl space-y-4 shadow-xl animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 font-mono">
                    <span>⚖️</span>
                    <span>ĐÁNH GIÁ THỜI GIAN THỰC TỪ TRỌNG TÀI AI (SILENT JUDGE)</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-mono text-sm font-black bg-emerald-500/20 text-emerald-300 px-3 py-1 rounded-lg border border-emerald-500/30">
                    <span>Điểm lượt:</span>
                    <span>{currentTurn.evaluation?.score}/100</span>
                  </div>
                </div>

                {/* 4 Score Bars */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                  <div className="bg-[#090D16] p-2.5 rounded-lg border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Technical Depth</div>
                    <div className="text-emerald-400 font-bold mt-1">
                      {currentTurn.evaluation?.technical_depth_score}/30
                    </div>
                  </div>
                  <div className="bg-[#090D16] p-2.5 rounded-lg border border-slate-800">
                    <div className="text-slate-400 text-[10px]">STAR Structure</div>
                    <div className="text-emerald-400 font-bold mt-1">
                      {currentTurn.evaluation?.star_structure_score}/25
                    </div>
                  </div>
                  <div className="bg-[#090D16] p-2.5 rounded-lg border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Confidence</div>
                    <div className="text-emerald-400 font-bold mt-1">
                      {currentTurn.evaluation?.confidence_score}/25
                    </div>
                  </div>
                  <div className="bg-[#090D16] p-2.5 rounded-lg border border-slate-800">
                    <div className="text-slate-400 text-[10px]">Adaptability</div>
                    <div className="text-emerald-400 font-bold mt-1">
                      {currentTurn.evaluation?.adaptability_score}/20
                    </div>
                  </div>
                </div>

                {/* Feedback */}
                <div className="space-y-2 text-xs">
                  <p className="text-slate-300 font-medium">{currentTurn.evaluation?.feedback}</p>
                  {currentTurn.evaluation?.key_strengths && currentTurn.evaluation.key_strengths.length > 0 && (
                    <div className="text-emerald-400 flex items-start gap-1">
                      <span>✅</span>
                      <span>{currentTurn.evaluation.key_strengths.join(" ")}</span>
                    </div>
                  )}
                  {currentTurn.evaluation?.improvement_areas && currentTurn.evaluation.improvement_areas.length > 0 && (
                    <div className="text-amber-400 flex items-start gap-1">
                      <span>⚠️</span>
                      <span>{currentTurn.evaluation.improvement_areas.join(" ")}</span>
                    </div>
                  )}
                </div>

                {/* Expandable Ideal Harvard Answer */}
                <div className="pt-2 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowIdealAnswer(!showIdealAnswer)}
                    className="text-xs text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1.5"
                  >
                    <span>{showIdealAnswer ? "▼ Thu gọn câu trả lời mẫu" : "▶ Xem câu trả lời mẫu chuẩn Harvard STAR"}</span>
                  </button>

                  {showIdealAnswer && currentTurn.evaluation?.ideal_star_answer && (
                    <div className="mt-3 p-3.5 bg-[#090D16] rounded-xl border border-slate-800 text-xs text-slate-300 whitespace-pre-line leading-relaxed">
                      {currentTurn.evaluation.ideal_star_answer}
                    </div>
                  )}
                </div>

                {/* Next Button */}
                <div className="flex justify-end pt-2">
                  <button
                    type="button"
                    onClick={handleNextTurn}
                    className="bg-emerald-500 hover:bg-emerald-400 text-[#090D16] font-bold px-6 py-2.5 rounded-xl text-xs sm:text-sm transition-all shadow-md flex items-center gap-1.5"
                  >
                    <span>Chuyển sang câu hỏi tiếp theo</span>
                    <span>➔</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* --- VIEW 3: FINAL ASSESSMENT REPORT SCORECARD --- */}
        {session && session.is_completed && session.final_report && (
          <div className="space-y-6 animate-fadeIn">
            {/* Header Scorecard */}
            <div className="bg-[#111827] border border-emerald-500 p-8 rounded-2xl shadow-2xl text-center space-y-4">
              <div className="inline-flex items-center gap-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full text-xs font-mono font-bold">
                <span>🏆 PHIÊN PHỎNG VẤN HOÀN TẤT</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-white font-['Plus_Jakarta_Sans',sans-serif]">
                Báo Cáo Thẩm Định Năng Lực Toàn Diện
              </h2>
              <div className="flex items-center justify-center gap-4 pt-2">
                <div className="bg-[#090D16] px-6 py-3 rounded-2xl border border-slate-800">
                  <div className="text-xs text-slate-400 font-mono">XẾP HẠNG CHUNG</div>
                  <div className="text-4xl font-black text-emerald-400 mt-1 font-mono">
                    {session.final_report.overall_grade}
                  </div>
                </div>
                <div className="bg-[#090D16] px-6 py-3 rounded-2xl border border-slate-800">
                  <div className="text-xs text-slate-400 font-mono">TỔNG ĐIỂM</div>
                  <div className="text-4xl font-black text-white mt-1 font-mono">
                    {session.final_report.overall_score}<span className="text-xl text-slate-500">/100</span>
                  </div>
                </div>
              </div>
              <p className="text-sm font-semibold text-emerald-300 max-w-xl mx-auto">
                "{session.final_report.verdict}"
              </p>
            </div>

            {/* 4 Average Dimension Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl text-center">
                <div className="text-xs text-slate-400 font-mono">Technical Depth</div>
                <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                  {session.final_report.technical_average}/30
                </div>
              </div>
              <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl text-center">
                <div className="text-xs text-slate-400 font-mono">STAR Structure</div>
                <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                  {session.final_report.star_structure_average}/25
                </div>
              </div>
              <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl text-center">
                <div className="text-xs text-slate-400 font-mono">Confidence & Tone</div>
                <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                  {session.final_report.confidence_average}/25
                </div>
              </div>
              <div className="bg-[#111827] border border-slate-800 p-4 rounded-xl text-center">
                <div className="text-xs text-slate-400 font-mono">Adaptability</div>
                <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">
                  {session.final_report.adaptability_average}/20
                </div>
              </div>
            </div>

            {/* Strengths & Growth Areas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-[#111827] border border-slate-800 p-6 rounded-2xl space-y-3">
                <h3 className="text-xs font-bold uppercase text-emerald-400 font-mono flex items-center gap-1.5">
                  <span>🌟</span>
                  <span>Điểm mạnh nổi bật:</span>
                </h3>
                <ul className="space-y-2 text-xs text-slate-300">
                  {session.final_report.top_strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-[#111827] border border-slate-800 p-6 rounded-2xl space-y-3">
                <h3 className="text-xs font-bold uppercase text-amber-400 font-mono flex items-center gap-1.5">
                  <span>🎯</span>
                  <span>Khu vực cần rèn luyện thêm:</span>
                </h3>
                <ul className="space-y-2 text-xs text-slate-300">
                  {session.final_report.critical_growth_areas.map((a, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-amber-400">•</span>
                      <span>{a}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Actionable Prep Tips */}
            <div className="bg-[#111827] border border-slate-800 p-6 rounded-2xl space-y-3">
              <h3 className="text-xs font-bold uppercase text-sky-400 font-mono flex items-center gap-1.5">
                <span>🚀</span>
                <span>Lời khuyên hành động thực chiến trước ngày phỏng vấn:</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                {session.final_report.actionable_prep_tips.map((tip, idx) => (
                  <div key={idx} className="bg-[#090D16] p-3.5 rounded-xl border border-slate-800 text-xs text-slate-300">
                    <span className="font-bold text-sky-400 block mb-1">0{idx + 1}.</span>
                    {tip}
                  </div>
                ))}
              </div>
            </div>

            {/* Replay Actions */}
            <div className="flex justify-center gap-4 pt-4">
              <button
                type="button"
                onClick={() => setSession(null)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold px-6 py-3 rounded-xl text-xs sm:text-sm transition-colors border border-slate-700"
              >
                🔄 Luyện tập lại chủ đề mới
              </button>
              <Link
                to="/workspace"
                className="bg-emerald-500 hover:bg-emerald-400 text-[#090D16] font-bold px-6 py-3 rounded-xl text-xs sm:text-sm transition-all shadow-lg"
              >
                Quay lại Workspace MAY ĐO CV ➔
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
