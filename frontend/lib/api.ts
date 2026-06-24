export type Product = {
  id: number;
  name: string;
  category: string;
  price: string;
  created_at: string;
  updated_at: string;
};

export type ProductPage = {
  data: Product[];
  next_cursor: string | null;
  has_more: boolean;
};

type FetchProductsInput = {
  limit?: number;
  category?: string;
  cursor?: string | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchProducts({
  limit = 24,
  category,
  cursor
}: FetchProductsInput): Promise<ProductPage> {
  const url = new URL("/api/products", API_URL);
  url.searchParams.set("limit", String(limit));

  if (category) {
    url.searchParams.set("category", category);
  }

  if (cursor) {
    url.searchParams.set("cursor", cursor);
  }

  const response = await fetch(url.toString(), { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load products.");
  }

  return response.json() as Promise<ProductPage>;
}

