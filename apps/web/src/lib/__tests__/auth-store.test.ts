import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useAuthStore } from "../store/auth";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
  localStorage.clear();
  // Reset store state between tests
  useAuthStore.setState({
    user: null,
    token: null,
    refreshToken: null,
    isLoading: false,
    error: null,
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function mockOkResponse(body: unknown) {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(""),
  });
}

function mockErrorResponse(status: number) {
  return Promise.resolve({
    ok: false,
    status,
    statusText: "Error",
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(""),
  });
}

const fakeUser = { id: "1", email: "test@example.com", name: "田中 健一", role: "現場監督" };

describe("useAuthStore — login", () => {
  it("sets user and tokens on successful login", async () => {
    mockFetch.mockReturnValueOnce(
      mockOkResponse({
        success: true,
        data: {
          access_token: "access-123",
          refresh_token: "refresh-456",
          token_type: "bearer",
          expires_in: 3600,
          user: fakeUser,
        },
      }),
    );

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login("test@example.com", "password");
    });

    expect(result.current.user).toEqual(fakeUser);
    expect(result.current.token).toBe("access-123");
    expect(result.current.refreshToken).toBe("refresh-456");
    expect(result.current.isLoading).toBe(false);
    expect(localStorage.getItem("auth_token")).toBe("access-123");
    expect(localStorage.getItem("auth_refresh_token")).toBe("refresh-456");
  });

  it("sets error state on failed login", async () => {
    mockFetch.mockReturnValueOnce(mockErrorResponse(401));

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login("bad@example.com", "wrong").catch(() => {});
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.error).toBeTruthy();
    expect(result.current.isLoading).toBe(false);
  });
});

describe("useAuthStore — logout", () => {
  it("clears user, tokens, and localStorage on logout", async () => {
    // Set up logged-in state
    useAuthStore.setState({
      user: fakeUser,
      token: "access-123",
      refreshToken: "refresh-456",
    });
    localStorage.setItem("auth_token", "access-123");
    localStorage.setItem("auth_refresh_token", "refresh-456");

    mockFetch.mockReturnValueOnce(mockOkResponse({ success: true }));

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.refreshToken).toBeNull();
    expect(localStorage.getItem("auth_token")).toBeNull();
  });

  it("clears state even if logout API call fails", async () => {
    useAuthStore.setState({ user: fakeUser, token: "tok", refreshToken: "ref" });
    localStorage.setItem("auth_token", "tok");

    mockFetch.mockReturnValueOnce(mockErrorResponse(500));

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(localStorage.getItem("auth_token")).toBeNull();
  });
});

describe("useAuthStore — restoreSession", () => {
  it("restores token from localStorage", () => {
    localStorage.setItem("auth_token", "stored-token");
    localStorage.setItem("auth_refresh_token", "stored-refresh");

    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.restoreSession();
    });

    expect(result.current.token).toBe("stored-token");
    expect(result.current.refreshToken).toBe("stored-refresh");
  });

  it("leaves state null when localStorage is empty", () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.restoreSession();
    });

    expect(result.current.token).toBeNull();
  });
});
