import axios from "axios";

// Create a custom axios instance for Auth Service
export const authApi = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API_URL || "http://localhost:4000/api/v1/auth",
  withCredentials: true, // Important for sending/receiving HttpOnly cookies
});

// Request interceptor to attach Access Token to headers
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token expiration (401)
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Call the refresh token endpoint
        // (Assuming the Auth service will read the HttpOnly cookie and issue a new token)
        const { data } = await axios.post(
          `${authApi.defaults.baseURL}/refresh`,
          {},
          { withCredentials: true }
        );
        
        // Save new token
        localStorage.setItem("accessToken", data.accessToken);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
        return authApi(originalRequest);
      } catch (refreshError) {
        // If refresh fails, user must log in again
        localStorage.removeItem("accessToken");
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        
        // Fallback navigation if event is not caught
        if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
