"use client";

import { motion } from "framer-motion";
import type { Product } from "@/lib/api";

type ProductCardProps = {
  product: Product;
};

const dateFormatter = new Intl.DateTimeFormat("en", {
  month: "short",
  day: "numeric",
  year: "numeric"
});

export function ProductCard({ product }: ProductCardProps) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-soft dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="flex items-start justify-between gap-4">
        <span className="rounded-md bg-teal-50 px-2.5 py-1 text-xs font-semibold text-teal-700 dark:bg-teal-400/10 dark:text-teal-200">
          {product.category}
        </span>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          #{product.id}
        </span>
      </div>

      <h2 className="mt-5 min-h-14 text-base font-semibold leading-7 text-slate-950 dark:text-white">
        {product.name}
      </h2>

      <div className="mt-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Price
          </p>
          <p className="mt-1 text-2xl font-bold text-coral">${product.price}</p>
        </div>
        <div className="text-right text-xs text-slate-500 dark:text-slate-400">
          <p>Updated</p>
          <p className="mt-1 font-medium text-slate-700 dark:text-slate-200">
            {dateFormatter.format(new Date(product.updated_at))}
          </p>
        </div>
      </div>
    </motion.article>
  );
}

