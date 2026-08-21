import axios from "axios";

let accessToken: string | null = null;

export const getAccessToken = (): string | null => accessToken;
export const setAccessToken = (token: string | null): void => {
  accessToken = token;
};

let refreshInFlight: Promise<string | null> | null = null;

export async function refreshAccessToken(): Promise<string | null> {
  if (!refreshInFlight) {
    refreshInFlight = axios
      .post<{ accessToken: string }>(`${authApi.defaults.baseURL}/refresh`, {}, { withCredentials: true })
      .then(({ data }) => {
        setAccessToken(data.accessToken);
        return data.accessToken;
      })
      .catch(() => {
        setAccessToken(null);
        return null;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

// Create a custom axios instance for Auth Service
export const authApi = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API_URL || "http://localhost:4000/api/v1/auth",
  withCredentials: true, // Important for sending/receiving HttpOnly cookies
});

// Request interceptor to attach Access Token to headers
authApi.interceptors.request.use((config) => {
  const token = getAccessToken();
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
        const token = await refreshAccessToken();
        if (!token) throw new Error("Refresh token rejected");
        
        // Save new token
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return authApi(originalRequest);
      } catch (refreshError) {
        // If refresh fails, user must log in again
        setAccessToken(null);
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

export const logoutUser = async (): Promise<void> => {
  try {
    await authApi.post("/logout");
  } catch (err) {
    console.error("Logout request error:", err);
  } finally {
    setAccessToken(null);
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
      window.location.href = "/login";
    }
  }
};

export async function loginUser(email: string, password: string): Promise<void> {
  const { data } = await authApi.post<{ accessToken: string }>("/login", { email, password });
  setAccessToken(data.accessToken);
}

export async function registerUser(email: string, password: string): Promise<void> {
  await authApi.post("/register", { email, password });
}
