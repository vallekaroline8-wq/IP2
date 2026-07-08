const styles = {
  disponible: "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-400",
  ocupada: "bg-red-100 text-red-800 dark:bg-red-500/15 dark:text-red-400",
  reservada: "bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-400",
  activa: "bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-400",
  liberada: "bg-slate-100 text-slate-600 dark:bg-slate-500/15 dark:text-slate-400",
};

export const StatusBadge = ({ status, label }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.liberada}`}>
    {label || status?.charAt(0).toUpperCase() + status?.slice(1)}
  </span>
);
