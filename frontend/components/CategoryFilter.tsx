"use client";

import { motion } from "framer-motion";

type CategoryFilterProps = {
  categories: string[];
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
};

export function CategoryFilter({
  categories,
  selectedCategory,
  onSelectCategory
}: CategoryFilterProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {categories.map((category) => {
        const selected = category === selectedCategory;

        return (
          <button
            key={category}
            type="button"
            onClick={() => onSelectCategory(category)}
            className="relative shrink-0 rounded-md border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-teal-400 dark:border-slate-700 dark:text-slate-200 dark:hover:border-teal-400"
          >
            {selected ? (
              <motion.span
                layoutId="category-pill"
                className="absolute inset-0 rounded-md bg-teal-500"
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              />
            ) : null}
            <span className={selected ? "relative text-white" : "relative"}>
              {category}
            </span>
          </button>
        );
      })}
    </div>
  );
}

