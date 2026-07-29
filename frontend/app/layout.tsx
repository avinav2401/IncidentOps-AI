import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/app-shell";
import { AuthProvider } from "@/lib/auth-context";
import { QueryProvider } from "@/lib/query-provider";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  title: "IncidentOps AI",
  description: "An intelligent command center for incident response.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body>
        <QueryProvider>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
