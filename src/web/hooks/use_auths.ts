import { create } from "zustand";
import type { User } from "@/web/types";

interface AuthState {
  user: User | null;
  signIn: (email: string, password: string) => Promise<User>;
  signOut: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  signIn: async (email) => {
    await new Promise((r) => setTimeout(r, 600));
    const name = email.split("@")[0].replace(/[._]/g, " ");
    const user: User = {
      email,
      name: name.replace(/\b\w/g, (c) => c.toUpperCase()),
      role: "inspector",
    };
    set({ user });
    return user;
  },
  signOut: () => set({ user: null }),
}));
