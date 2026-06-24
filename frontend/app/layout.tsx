import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeVector Product Browser",
  description: "Cursor-paginated product browsing dashboard"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}

