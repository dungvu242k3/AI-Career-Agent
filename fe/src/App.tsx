import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import WorkspacePage from "./pages/WorkspacePage";
import JobsPage from "./pages/JobsPage";
import InterviewPage from "./pages/InterviewPage";
import LearningPage from "./pages/LearningPage";
import ApplicationsPage from "./pages/ApplicationsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import NotFoundPage from "./pages/NotFoundPage";

function AppLayout() {
  const location = useLocation();
  const hideNavbarRoutes = ["/login", "/register"];
  const shouldShowNavbar = !hideNavbarRoutes.includes(location.pathname);

  return (
    <>
      {shouldShowNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/workspace" element={<WorkspacePage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/learning" element={<LearningPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
