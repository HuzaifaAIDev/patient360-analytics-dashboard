import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="text-center py-24">
      <p className="font-display text-5xl mb-3">404</p>
      <p className="text-slate-400 mb-6">This page doesn't exist.</p>
      <Link to="/" className="text-clinical-400 hover:underline text-sm">
        Back to search
      </Link>
    </div>
  );
}
