import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "Desync Commerce", description: "Secure Commerce" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
