import { create } from "zustand";
import { post } from "../api-client";

interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  org?: string;
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  restoreSession: () => void;
}

interface LoginResponse {
  success: boolean;
  data: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    user: AuthUser;
  };
}

interface RefreshResponse {
  success: boolean;
  data: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  refreshToken: null,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const res = await post<LoginResponse>("/auth/login", { email, password });
      const { access_token, refresh_token, user } = res.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("auth_refresh_token", refresh_token);
      set({
        user,
        token: access_token,
        refreshToken: refresh_token,
        isLoading: false,
      });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "ログインに失敗しました",
        isLoading: false,
      });
      throw err;
    }
  },

  logout: async () => {
    const { refreshToken } = get();
    try {
      if (refreshToken) {
        await post("/auth/logout", { refresh_token: refreshToken });
      }
    } catch {
      // ignore logout errors
    } finally {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_refresh_token");
      set({ user: null, token: null, refreshToken: null });
    }
  },

  refresh: async () => {
    const { refreshToken } = get();
    if (!refreshToken) return;
    try {
      const res = await post<RefreshResponse>("/auth/refresh", {
        refresh_token: refreshToken,
      });
      const { access_token, refresh_token } = res.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("auth_refresh_token", refresh_token);
      set({ token: access_token, refreshToken: refresh_token });
    } catch {
      // Refresh failed — clear session
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_refresh_token");
      set({ user: null, token: null, refreshToken: null });
    }
  },

  restoreSession: () => {
    const token = localStorage.getItem("auth_token");
    const refreshToken = localStorage.getItem("auth_refresh_token");
    if (token) {
      set({ token, refreshToken: refreshToken ?? null });
    }
  },
}));
