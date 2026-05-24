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
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  restoreSession: () => void;
}

interface LoginResponse {
  success: boolean;
  data: {
    access_token: string;
    user: AuthUser;
  };
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const res = await post<LoginResponse>("/auth/login", { email, password });
      const { access_token, user } = res.data;
      localStorage.setItem("auth_token", access_token);
      set({ user, token: access_token, isLoading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "ログインに失敗しました",
        isLoading: false,
      });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem("auth_token");
    set({ user: null, token: null });
  },

  restoreSession: () => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      set({ token });
    }
  },
}));
