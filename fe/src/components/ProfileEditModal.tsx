import React, { useState } from "react";
import { X, Save, User, Briefcase, GraduationCap, Code, CheckCircle, AlertCircle, Plus, Trash2 } from "lucide-react";
import { CandidateProfile, SkillCategoryKey, SKILL_CATEGORY_LABELS } from "../types/candidate";
import { updateCandidatePreview } from "../services/cvApi";

interface ProfileEditModalProps {
  isOpen: boolean;
  candidateId: number | null;
  profile: CandidateProfile;
  onClose: () => void;
  onSaved: (updatedProfile: CandidateProfile) => void;
}

export const ProfileEditModal: React.FC<ProfileEditModalProps> = ({
  isOpen,
  candidateId,
  profile,
  onClose,
  onSaved,
}) => {
  const [formData, setFormData] = useState<CandidateProfile>(JSON.parse(JSON.stringify(profile)));
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [activeTab, setActiveTab] = useState<"info" | "skills" | "experience" | "education">("info");
  const [newSkillText, setNewSkillText] = useState("");
  const [selectedSkillCategory, setSelectedSkillCategory] = useState<SkillCategoryKey>("programming_languages");

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!candidateId) {
      // Local only update
      onSaved(formData);
      onClose();
      return;
    }

    setIsSaving(true);
    setSaveStatus("idle");
    setErrorMsg("");

    try {
      await updateCandidatePreview(candidateId, formData);
      setSaveStatus("success");
      onSaved(formData);
      setTimeout(() => {
        onClose();
        setSaveStatus("idle");
      }, 800);
    } catch (err) {
      setSaveStatus("error");
      setErrorMsg((err as Error).message || "Lỗi khi lưu thông tin");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSkill = () => {
    if (!newSkillText.trim()) return;
    const currentList = formData.skills_taxonomy[selectedSkillCategory] || [];
    if (!currentList.includes(newSkillText.trim())) {
      setFormData({
        ...formData,
        skills_taxonomy: {
          ...formData.skills_taxonomy,
          [selectedSkillCategory]: [...currentList, newSkillText.trim()],
        },
      });
    }
    setNewSkillText("");
  };

  const handleRemoveSkill = (category: SkillCategoryKey, skillToRemove: string) => {
    setFormData({
      ...formData,
      skills_taxonomy: {
        ...formData.skills_taxonomy,
        [category]: (formData.skills_taxonomy[category] || []).filter((s) => s !== skillToRemove),
      },
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl bg-[#0f1422] border border-[#1E293B] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1E293B] bg-[#111827] shrink-0">
          <div>
            <h3 className="text-sm font-bold text-[#f8fafc] font-['Plus_Jakarta_Sans',sans-serif]">
              Xem &amp; Chỉnh Sửa Hồ Sơ Đã Bóc Tách
            </h3>
            <p className="text-[11px] text-[#94a3b8]">
              Chỉnh sửa thông tin để AI đánh giá ATS và gợi ý việc làm chính xác nhất
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#94a3b8] hover:text-[#f8fafc] hover:bg-[#181b25] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-[#1E293B] bg-[#0c101b] px-6 shrink-0 gap-4">
          <button
            onClick={() => setActiveTab("info")}
            className={`py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === "info"
                ? "border-[#10b981] text-[#4edea3]"
                : "border-transparent text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            Thông Tin Cá Nhân
          </button>
          <button
            onClick={() => setActiveTab("skills")}
            className={`py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === "skills"
                ? "border-[#10b981] text-[#4edea3]"
                : "border-transparent text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            Kỹ Năng (8 Nhóm)
          </button>
          <button
            onClick={() => setActiveTab("experience")}
            className={`py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === "experience"
                ? "border-[#10b981] text-[#4edea3]"
                : "border-transparent text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            Kinh Nghiệm ({formData.work_experience.length})
          </button>
          <button
            onClick={() => setActiveTab("education")}
            className={`py-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === "education"
                ? "border-[#10b981] text-[#4edea3]"
                : "border-transparent text-[#94a3b8] hover:text-[#dfe2ef]"
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            Học Vấn ({formData.education.length})
          </button>
        </div>

        {/* Tab Contents */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6 scrollbar-thin">
          {/* TAB 1: INFO */}
          {activeTab === "info" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Họ và Tên</label>
                  <input
                    type="text"
                    value={formData.personal_info.full_name || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        personal_info: { ...formData.personal_info, full_name: e.target.value },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Chức danh / Headline</label>
                  <input
                    type="text"
                    value={formData.summary.detected_title || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        summary: { ...formData.summary, detected_title: e.target.value },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Email</label>
                  <input
                    type="email"
                    value={formData.personal_info.email || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        personal_info: { ...formData.personal_info, email: e.target.value },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Số điện thoại</label>
                  <input
                    type="text"
                    value={formData.personal_info.phone || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        personal_info: { ...formData.personal_info, phone: e.target.value },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Địa điểm / Thành phố</label>
                  <input
                    type="text"
                    value={formData.personal_info.location || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        personal_info: { ...formData.personal_info, location: e.target.value },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Tổng số năm kinh nghiệm</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.metadata.total_experience_years || 0}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        metadata: { ...formData.metadata, total_experience_years: parseFloat(e.target.value) || 0 },
                      })
                    }
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3.5 py-2 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[#94a3b8] mb-1.5">Tóm tắt mục tiêu / Profile Summary</label>
                <textarea
                  rows={3}
                  value={formData.summary.summary_text || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      summary: { ...formData.summary, summary_text: e.target.value },
                    })
                  }
                  className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg p-3 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981] leading-relaxed"
                />
              </div>
            </div>
          )}

          {/* TAB 2: SKILLS TAXONOMY */}
          {activeTab === "skills" && (
            <div className="space-y-6">
              {/* Add Skill Control */}
              <div className="p-4 bg-[#111827] border border-[#1E293B] rounded-xl flex flex-wrap gap-3 items-end">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-[11px] text-[#94a3b8] mb-1 font-medium">Thêm kỹ năng mới</label>
                  <input
                    type="text"
                    placeholder="VD: Docker, Next.js, Redis..."
                    value={newSkillText}
                    onChange={(e) => setNewSkillText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAddSkill()}
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc] focus:outline-none focus:border-[#10b981]"
                  />
                </div>
                <div className="w-48">
                  <label className="block text-[11px] text-[#94a3b8] mb-1 font-medium">Nhóm kỹ năng</label>
                  <select
                    value={selectedSkillCategory}
                    onChange={(e) => setSelectedSkillCategory(e.target.value as SkillCategoryKey)}
                    className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#dfe2ef] focus:outline-none focus:border-[#10b981]"
                  >
                    {Object.entries(SKILL_CATEGORY_LABELS).map(([key, item]) => (
                      <option key={key} value={key}>
                        {item.title}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  onClick={handleAddSkill}
                  className="px-4 py-1.5 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Thêm
                </button>
              </div>

              {/* 8 Buckets List */}
              <div className="space-y-4">
                {(Object.keys(SKILL_CATEGORY_LABELS) as SkillCategoryKey[]).map((key) => {
                  const items = formData.skills_taxonomy[key] || [];
                  const meta = SKILL_CATEGORY_LABELS[key];
                  return (
                    <div key={key} className="p-3.5 bg-[#111827] border border-[#1E293B] rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-[#f8fafc]">{meta.title}</span>
                        <span className="text-[10px] text-[#94a3b8] font-['JetBrains_Mono',monospace]">
                          {items.length} kỹ năng
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {items.length === 0 ? (
                          <span className="text-[11px] text-[#64748b] italic">Chưa có kỹ năng trong nhóm này</span>
                        ) : (
                          items.map((skill) => (
                            <span
                              key={skill}
                              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-['JetBrains_Mono',monospace] border ${meta.color}`}
                            >
                              {skill}
                              <button
                                type="button"
                                onClick={() => handleRemoveSkill(key, skill)}
                                className="hover:text-red-400 ml-1"
                              >
                                &times;
                              </button>
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: WORK EXPERIENCE */}
          {activeTab === "experience" && (
            <div className="space-y-4">
              {formData.work_experience.length === 0 ? (
                <div className="text-center py-8 text-[#94a3b8] text-xs">Chưa có thông tin kinh nghiệm</div>
              ) : (
                formData.work_experience.map((exp, idx) => (
                  <div key={idx} className="p-4 bg-[#111827] border border-[#1E293B] rounded-xl space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Công ty</label>
                        <input
                          type="text"
                          value={exp.company}
                          onChange={(e) => {
                            const updated = [...formData.work_experience];
                            updated[idx].company = e.target.value;
                            setFormData({ ...formData, work_experience: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Vị trí / Role</label>
                        <input
                          type="text"
                          value={exp.role}
                          onChange={(e) => {
                            const updated = [...formData.work_experience];
                            updated[idx].role = e.target.value;
                            setFormData({ ...formData, work_experience: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Bắt đầu (YYYY-MM)</label>
                        <input
                          type="text"
                          value={exp.start_date}
                          onChange={(e) => {
                            const updated = [...formData.work_experience];
                            updated[idx].start_date = e.target.value;
                            setFormData({ ...formData, work_experience: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Kết thúc</label>
                        <input
                          type="text"
                          placeholder={exp.is_current ? "Hiện tại" : "YYYY-MM"}
                          value={exp.end_date || ""}
                          onChange={(e) => {
                            const updated = [...formData.work_experience];
                            updated[idx].end_date = e.target.value;
                            setFormData({ ...formData, work_experience: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-[11px] text-[#94a3b8] mb-1">Nhiệm vụ &amp; Thành tích (Bullets)</label>
                      <textarea
                        rows={3}
                        value={exp.raw_bullets.join("\n")}
                        onChange={(e) => {
                          const updated = [...formData.work_experience];
                          updated[idx].raw_bullets = e.target.value.split("\n").filter((b) => b.trim());
                          setFormData({ ...formData, work_experience: updated });
                        }}
                        className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg p-2 text-xs text-[#dfe2ef]"
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 4: EDUCATION */}
          {activeTab === "education" && (
            <div className="space-y-4">
              {formData.education.length === 0 ? (
                <div className="text-center py-8 text-[#94a3b8] text-xs">Chưa có thông tin học vấn</div>
              ) : (
                formData.education.map((edu, idx) => (
                  <div key={idx} className="p-4 bg-[#111827] border border-[#1E293B] rounded-xl space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Trường Đại học / Học viện</label>
                        <input
                          type="text"
                          value={edu.institution}
                          onChange={(e) => {
                            const updated = [...formData.education];
                            updated[idx].institution = e.target.value;
                            setFormData({ ...formData, education: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Chuyên ngành</label>
                        <input
                          type="text"
                          value={edu.field_of_study}
                          onChange={(e) => {
                            const updated = [...formData.education];
                            updated[idx].field_of_study = e.target.value;
                            setFormData({ ...formData, education: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Bằng cấp</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => {
                            const updated = [...formData.education];
                            updated[idx].degree = e.target.value;
                            setFormData({ ...formData, education: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">Năm tốt nghiệp</label>
                        <input
                          type="number"
                          value={edu.end_year || ""}
                          onChange={(e) => {
                            const updated = [...formData.education];
                            updated[idx].end_year = parseInt(e.target.value, 10) || null;
                            setFormData({ ...formData, education: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] text-[#94a3b8] mb-1">GPA</label>
                        <input
                          type="text"
                          value={edu.gpa || ""}
                          onChange={(e) => {
                            const updated = [...formData.education];
                            updated[idx].gpa = e.target.value;
                            setFormData({ ...formData, education: updated });
                          }}
                          className="w-full bg-[#181b25] border border-[#1E293B] rounded-lg px-3 py-1.5 text-xs text-[#f8fafc]"
                        />
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#111827] border-t border-[#1E293B] shrink-0">
          <div className="text-xs">
            {saveStatus === "success" && (
              <span className="text-[#4edea3] flex items-center gap-1.5 font-medium">
                <CheckCircle className="w-4 h-4" /> Đã lưu cập nhật thành công!
              </span>
            )}
            {saveStatus === "error" && (
              <span className="text-red-400 flex items-center gap-1.5 font-medium">
                <AlertCircle className="w-4 h-4" /> {errorMsg}
              </span>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-[#94a3b8] hover:text-[#f8fafc] transition-colors"
            >
              Đóng
            </button>
            <button
              type="button"
              disabled={isSaving}
              onClick={handleSave}
              className="px-5 py-2 bg-[#10b981] hover:bg-[#4edea3] text-[#090D16] text-xs font-bold rounded-lg transition-colors flex items-center gap-2"
            >
              <Save className="w-3.5 h-3.5" />
              {isSaving ? "Đang lưu..." : "Lưu & Cập Nhật Hồ Sơ"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
