/** Paginas publicas (login, registro) — sempre acessiveis, mesmo logado. */
export default function PublicRoute({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
