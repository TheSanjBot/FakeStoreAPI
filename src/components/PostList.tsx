import type { Product } from '../types/product'

type ProductListProps = {
  isLoading: boolean
  products: Product[]
  onDeleteProduct: (productId: number) => Promise<void>
  onToggleStock: (product: Product) => Promise<void>
}

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

const ProductList = ({
  isLoading,
  products,
  onDeleteProduct,
  onToggleStock,
}: ProductListProps) => {
  return (
    <section className="section">
      <h2>Products</h2>

      {isLoading ? <p>Loading...</p> : null}

      {!isLoading && products.length === 0 ? <p>No products.</p> : null}

      {!isLoading && products.length > 0 ? (
        <div className="product-list">
          {products.map((product) => (
            <article className="product-item" key={product.id}>
              <div className="product-item-header">
                <div>
                  <h3>{product.name}</h3>
                  <p>{product.category}</p>
                </div>
                <span>{product.inStock ? 'In stock' : 'Out of stock'}</span>
              </div>

              <p>{product.description}</p>

              <div className="product-item-footer">
                <strong>{currencyFormatter.format(product.price)}</strong>
                <div className="actions">
                  <button
                    type="button"
                    onClick={() => void onToggleStock(product)}
                  >
                    {product.inStock ? 'Set Out of Stock' : 'Set In Stock'}
                  </button>
                  <button
                    type="button"
                    onClick={() => void onDeleteProduct(product.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  )
}

export default ProductList
