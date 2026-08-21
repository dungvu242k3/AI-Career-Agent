import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FaGoogle, FaGithub, FaLinkedin } from "react-icons/fa";
import { Eye, EyeOff } from "lucide-react";
import { loginUser } from "../services/authApi";

// Validation schema
const loginSchema = z.object({
  email: z.string().min(1, "Vui lòng nhập email").email("Email không hợp lệ"),
  password: z.string().min(1, "Vui lòng nhập mật khẩu"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      setSubmitError(null);
      await loginUser(data.email, data.password);
      navigate("/workspace");
    } catch {
      setSubmitError("Email hoáº·c máº­t kháº©u khÃ´ng Ä‘Ãºng.");
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
             {/* Use an abstract SVG for growth/career */}
             <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-white opacity-90"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <h1 className="text-5xl font-bold mb-6 tracking-tight leading-tight">Elevate Your<br/>Career Path.</h1>
          <p className="text-lg text-blue-100 mb-10 leading-relaxed font-light">
            Access exclusive resources, connect with AI mentors, and track your professional development journey seamlessly.
          </p>
          <button className="bg-white/10 hover:bg-white/20 text-white border border-white/30 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all">
            LEARN MORE
          </button>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-[#F8FAFC]">
        <div className="w-full max-w-[420px] bg-white p-10 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Welcome to ProGrowth</h2>
            <p className="text-sm text-gray-500 mt-2">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
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

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#0A3D7C] hover:bg-[#082E5C] text-white font-semibold py-3 rounded-lg text-sm transition-all shadow-sm mt-2 disabled:opacity-70 flex justify-center items-center"
            >
              {isSubmitting ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                "SIGN IN"
              )}
            </button>
            {submitError && <p className="text-red-500 text-sm text-center">{submitError}</p>}
            
            <div className="flex flex-col items-center gap-3 text-sm mt-4">
              <a href="#" className="text-gray-500 hover:text-[#0A3D7C] transition-colors">Forgot password?</a>
              <Link to="/register" className="text-[#0A3D7C] font-semibold hover:underline">Create an account</Link>
            </div>
          </form>

          <div className="mt-8 flex items-center">
            <div className="flex-1 border-t border-gray-200"></div>
            <span className="px-3 text-xs text-gray-400 font-medium bg-white">or sign in with</span>
            <div className="flex-1 border-t border-gray-200"></div>
          </div>

          <div className="mt-6 flex flex-col gap-3">
            <button className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2.5 rounded-lg text-sm transition-all shadow-sm">
              <FaGoogle className="text-red-500" /> Continue with Google
            </button>
            <button className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2.5 rounded-lg text-sm transition-all shadow-sm">
              <FaGithub /> Continue with GitHub
            </button>
            <button className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2.5 rounded-lg text-sm transition-all shadow-sm">
              <FaLinkedin className="text-blue-600" /> Continue with LinkedIn
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
