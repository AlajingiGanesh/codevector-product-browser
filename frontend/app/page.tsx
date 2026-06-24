"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Moon, RefreshCw, Sun } from "lucide-react";

import { CategoryFilter } from "@/components/CategoryFilter";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { ProductCard } from "@/components/ProductCard";
import { fetchProducts, type Product } from "@/lib/api";

const categories = [
  "All",
  "Electronics",
  "Clothing",
  "Books",
  "Sports",
  "Home",
  "Beauty",
  "Automotive",
  "Toys",
  "Grocery",
  "Health"
];

export default function ProductsPage() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [products, setProducts] = useState<Product[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(true);
  const loaderRef = useRef<HTMLDivElement | null>(null);
  const loadingRef = useRef(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const loadPage = useCallback(
    async (
      categoryValue: string,
      cursorValue: string | null,
      reset: boolean
    ) => {
      if (loadingRef.current) {
        return;
      }

      loadingRef.current = true;
      setLoading(true);
      setError(null);

      try {
        const page = await fetchProducts({
          limit: 24,
          category: categoryValue === "All" ? undefined : categoryValue,
          cursor: cursorValue
        });

        setProducts((currentProducts) => {
          const merged = reset ? page.data : [...currentProducts, ...page.data];
          return Array.from(
            new Map(merged.map((product) => [product.id, product])).values()
          );
        });
        setCursor(page.next_cursor);
        setHasMore(page.has_more);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unable to load products."
        );
      } finally {
        loadingRef.current = false;
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    setProducts([]);
    setCursor(null);
    setHasMore(true);
    void loadPage(selectedCategory, null, true);
  }, [loadPage, selectedCategory]);

  useEffect(() => {
    const element = loaderRef.current;
    if (!element) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasMore && !loadingRef.current) {
          void loadPage(selectedCategory, cursor, false);
        }
      },
      { rootMargin: "560px" }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [cursor, hasMore, loadPage, selectedCategory]);

  const refresh = () => {
    setProducts([]);
    setCursor(null);
    setHasMore(true);
    void loadPage(selectedCategory, null, true);
  };

  return (
    <main className="min-h-screen bg-paper text-slate-950 transition dark:bg-ink dark:text-white">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-5 border-b border-slate-200 pb-6 dark:border-slate-800 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-teal-600 dark:text-teal-300">
              CodeVector
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-normal sm:text-4xl">
              Product Catalog
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={refresh}
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 transition hover:border-teal-400 hover:text-teal-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
              aria-label="Refresh products"
              title="Refresh products"
            >
              <RefreshCw size={18} />
            </button>
            <button
              type="button"
              onClick={() => setDarkMode((current) => !current)}
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 transition hover:border-teal-400 hover:text-teal-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
              aria-label="Toggle dark mode"
              title="Toggle dark mode"
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </header>

        <div className="grid gap-5 lg:grid-cols-[1fr_220px] lg:items-end">
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
          <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="text-slate-500 dark:text-slate-400">Loaded</p>
            <p className="mt-1 text-2xl font-bold text-slate-950 dark:text-white">
              {products.length}
            </p>
          </div>
        </div>

        {error ? (
          <div className="rounded-lg border border-coral/30 bg-coral/10 p-4 text-sm font-medium text-coral">
            {error}
          </div>
        ) : null}

        <motion.div
          layout
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3"
        >
          <AnimatePresence mode="popLayout">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </AnimatePresence>

          {loading && products.length === 0
            ? Array.from({ length: 9 }, (_, index) => (
                <LoadingSkeleton key={index} />
              ))
            : null}
        </motion.div>

        <div ref={loaderRef} className="min-h-14">
          {loading && products.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 3 }, (_, index) => (
                <LoadingSkeleton key={index} />
              ))}
            </div>
          ) : null}

          {!hasMore && products.length > 0 ? (
            <p className="py-8 text-center text-sm text-slate-500 dark:text-slate-400">
              End of catalog
            </p>
          ) : null}
        </div>
      </section>
    </main>
  );
}

