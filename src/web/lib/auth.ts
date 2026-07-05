import type { User } from "@/web/types";

/** Mock credential check — replace with a real call once backend auth exists. */
export async function authenticate(email: string, _password: string): Promise<User> {
  await new Promise((r) => setTimeout(r, 400));
  const name = email.split("@")[0].replace(/[._]/g, " ");
  return {
    email,
    name: name.replace(/\b\w/g, (c) => c.toUpperCase()),
    role: "inspector",
  };
}
