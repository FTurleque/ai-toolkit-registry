export interface Product {
  id: string;
  name: string;
  priceCents: number;
}

export class CatalogError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
  }
}

export class CatalogClient {
  constructor(private readonly baseUrl: string, private readonly apiToken: string) {}

  async product(id: string): Promise<Product> {
    const response = await fetch(`${this.baseUrl}/products/${encodeURIComponent(id)}`, {
      headers: { Authorization: `Bearer ${this.apiToken}` },
    });
    if (!response.ok) {
      throw new CatalogError(`Cannot update product view for ${id}`, response.status);
    }
    return (await response.json()) as Product;
  }

  async products(ids: string[]): Promise<Product[]> {
    const found: Product[] = [];
    for (const id of ids) {
      found.push(await this.product(id));
    }
    return found;
  }

  averagePrice(products: Product[]): number {
    if (products.length === 0) {
      return 0;
    }
    const total = products.reduce((sum, product) => sum + product.priceCents, 0);
    return total / products.length;
  }

  parseCached(raw: string): Product | undefined {
    try {
      return JSON.parse(raw) as Product;
    } catch (error) {
      throw new CatalogError(`Corrupted cache entry: ${String(error)}`);
    }
  }
}
