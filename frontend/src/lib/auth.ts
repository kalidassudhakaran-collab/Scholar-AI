import { api } from "./api";

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  plan: string;
}

export async function login(email: string, password: string) {
  const { data } = await api.post("/auth/login/", { email, password });
  sessionStorage.setItem("access_token", data.access);
  sessionStorage.setItem("refresh_token", data.refresh);
  return data;
}

export async function register(payload: {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
  full_name?: string;
}) {
  const { data } = await api.post("/auth/register/", payload);
  sessionStorage.setItem("access_token", data.access);
  sessionStorage.setItem("refresh_token", data.refresh);
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get("/auth/me/");
  return data;
}

export function logout() {
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!sessionStorage.getItem("access_token");
}
