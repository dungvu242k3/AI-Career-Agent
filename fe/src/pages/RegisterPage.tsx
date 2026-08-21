import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FaGoogle, FaGithub, FaLinkedin } from "react-icons/fa";
import { Eye, EyeOff } from "lucide-react";
import { registerUser } from "../services/authApi";

// Validation schema for Registration
const registerSchema = z.object({
  email: z.string().min(1, "Vui lòng nhập email").email("Email không hợp lệ"),
  password: z.string()
    .min(8, "Mật khẩu phải có ít nhất 8 ký tự")
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/, 
      "Mật khẩu phải chứa chữ hoa, chữ thường, số và ký tự đặc biệt"),
  confirmPassword: z.string().min(1, "Vui lòng xác nhận mật khẩu"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Mật khẩu xác nhận không khớp",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    try {
      setSubmitError(null);
      await registerUser(data.email, data.password);
      navigate("/login");
    } catch {
      setSubmitError("KhÃ´ng thá»ƒ táº¡o tÃ i khoáº£n. Email cÃ³ thá»ƒ Ä‘Ã£ tá»“n táº¡i.");
    }
  };

  return (
    <div className="min-h-screen flex bg-white font-['Inter',sans-serif]">
      {/* Left side - Graphic & Value Proposition */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#0A3D7C] text-white flex-col justify-center items-center p-12 relative overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
           <svg className="absolute w-[800px] h-[800px] -top-32 -left-32 text-white" fill="currentColor" viewBox="0 0 200 200"><path fill="currentColor" d="M44.7,-76.4C58.8,-69.2,71.8,-59.1,81.1,-46.5C90.3,-33.8,95.8,-18.6,96.4,-3.2C97,12.2,92.7,27.8,84.6,41.9C76.4,56,64.4,68.6,50.3,77.2C36.2,85.8,20.1,90.4,3.7,85.8C-12.7,81.2,-28.6,67.3,-41.8,57.1C-55,46.8,-65.4,40.1,-74.6,30.3C-83.8,20.4,-91.7,7.4,-92.3,-5.7C-92.9,-18.8,-86.2,-31.9,-76.4,-42.6C-66.6,-53.4,-53.7,-61.8,-40.5,-69.4C-27.3,-77,-13.7,-83.8,1,-85.4C15.7,-87,30.6,-83.6,44.7,-76.4Z" transform="translate(100 100) scale(1.1)" /></svg>
        </div>
        
        <div className="z-10 max-w-lg text-left">
          <div className="mb-8">
             <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-white opacity-90"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <h1 className="text-5xl font-bold mb-6 tracking-tight leading-tight">Elevate Your<br/>Career Path.</h1>
          <p className="text-lg text-blue-100 mb-10 leading-relaxed font-light">
            Join thousands of professionals accelerating their careers with AI-powered resume building and interview prep.
          </p>
        </div>
      </div>

      {/* Right side - Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#F8FAFC] overflow-y-auto">
        <div className="w-full max-w-[420px] bg-white p-10 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 my-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Create an Account</h2>
            <p className="text-sm text-gray-500 mt-2">Start your journey with ProGrowth</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email Address</label>
              <input
                {...register("email")}
                type="email"
                placeholder="name@company.com"
                className={`w-full px-4 py-3 rounded-lg border ${errors.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-600 focus:ring-blue-600'} bg-white text-gray-900 text-sm focus:ring-1 outline-none transition-all`}
              />
              {errors.email && <p className="text-red-500 text-xs mt-1.5">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  className={`w-full px-4 py-3 rounded-lg border ${errors.password ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-600 focus:ring-blue-600'} bg-white text-gray-900 text-sm focus:ring-1 outline-none transition-all`}
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1.5">{errors.password.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm Password</label>
              <input
                {...register("confirmPassword")}
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                className={`w-full px-4 py-3 rounded-lg border ${errors.confirmPassword ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-600 focus:ring-blue-600'} bg-white text-gray-900 text-sm focus:ring-1 outline-none transition-all`}
              />
              {errors.confirmPassword && <p className="text-red-500 text-xs mt-1.5">{errors.confirmPassword.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#0A3D7C] hover:bg-[#082E5C] text-white font-semibold py-3 rounded-lg text-sm transition-all shadow-sm mt-4 disabled:opacity-70 flex justify-center items-center"
            >
              {isSubmitting ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                "CREATE ACCOUNT"
              )}
            </button>
            {submitError && <p className="text-red-500 text-sm text-center">{submitError}</p>}
            
            <div className="text-center text-sm mt-4">
              <span className="text-gray-500">Already have an account? </span>
              <Link to="/login" className="text-[#0A3D7C] font-semibold hover:underline">Sign in</Link>
            </div>
          </form>

          <div className="mt-8 flex items-center">
            <div className="flex-1 border-t border-gray-200"></div>
            <span className="px-3 text-xs text-gray-400 font-medium bg-white">or sign up with</span>
            <div className="flex-1 border-t border-gray-200"></div>
          </div>

          <div className="mt-6 flex flex-col gap-3">
            <button className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2.5 rounded-lg text-sm transition-all shadow-sm">
              <FaGoogle className="text-red-500" /> Sign up with Google
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
