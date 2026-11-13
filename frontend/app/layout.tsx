import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Grupo VISA AI · Asistente OCD",
  description: "Prepara solicitudes de cambio y consulta los modelos operativos con el asistente OCD.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="es"><body>{children}</body></html>;
}
