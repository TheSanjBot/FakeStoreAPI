import { useEffect, useState } from 'react'
import ProductForm from '../components/AddPost'
import Navbar from '../components/Navbar'
import ProductList from '../components/PostList'
import type { Product, ProductInput } from '../types/product'

const PRODUCTS_ENDPOINT = 'http://localhost:3001/products'

const getErrorMessage = (error: unknown) => {
  if (error instanceof TypeError) {
    return 'Could not reach the products API on port 3001. Start it with `npm run api` and try again.'
  }

  return error instanceof Error
    ? error.message
    : 'Something went wrong while talking to the products API.'
}

const getResponseErrorMessage = async (
  response: Response,
  fallback: string,
) => {
  try {
    const payload = (await response.json()) as { message?: string }
    return payload.message ?? fallback
  } catch {
    return fallback
  }
}

const fetchProducts = async (signal?: AbortSignal) => {
  const response = await fetch(PRODUCTS_ENDPOINT, { signal })

  if (!response.ok) {
    throw new Error(
      await getResponseErrorMessage(
        response,
        'Unable to load products from the API.',
      ),
    )
  }

  return (await response.json()) as Product[]
}

const createProductRequest = async (product: ProductInput) => {
  const response = await fetch(PRODUCTS_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  })

  if (!response.ok) {
    throw new Error(
      await getResponseErrorMessage(
        response,
        'Unable to create the product.',
      ),
    )
  }

  return (await response.json()) as Product
}

const updateProductRequest = async (product: Product) => {
  const response = await fetch(`${PRODUCTS_ENDPOINT}/${product.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  })

  if (!response.ok) {
    throw new Error(
      await getResponseErrorMessage(
        response,
        'Unable to update the product.',
      ),
    )
  }

  return (await response.json()) as Product
}

const deleteProductRequest = async (productId: number) => {
  const response = await fetch(`${PRODUCTS_ENDPOINT}/${productId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(
      await getResponseErrorMessage(
        response,
        'Unable to delete the product.',
      ),
    )
  }
}

const Dashboard = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  const refreshProducts = async () => {
    setIsLoading(true)
    setError('')

    try {
      const nextProducts = await fetchProducts()
      setProducts(nextProducts)
    } catch (error) {
      setError(getErrorMessage(error))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    let isMounted = true
    const controller = new AbortController()

    const loadProducts = async () => {
      setIsLoading(true)
      setError('')

      try {
        const nextProducts = await fetchProducts(controller.signal)

        if (isMounted) {
          setProducts(nextProducts)
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }

        if (isMounted) {
          setError(getErrorMessage(error))
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadProducts()

    return () => {
      isMounted = false
      controller.abort()
    }
  }, [])

  const handleAddProduct = async (product: ProductInput) => {
    setIsSaving(true)
    setError('')

    try {
      const createdProduct = await createProductRequest(product)
      setProducts((currentProducts) => [createdProduct, ...currentProducts])
    } catch (error) {
      setError(getErrorMessage(error))
      throw error
    } finally {
      setIsSaving(false)
    }
  }

  const handleToggleStock = async (product: Product) => {
    setError('')

    try {
      const updatedProduct = await updateProductRequest({
        ...product,
        inStock: !product.inStock,
      })

      setProducts((currentProducts) =>
        currentProducts.map((currentProduct) =>
          currentProduct.id === updatedProduct.id
            ? updatedProduct
            : currentProduct,
        ),
      )
    } catch (error) {
      setError(getErrorMessage(error))
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    setError('')

    try {
      await deleteProductRequest(productId)
      setProducts((currentProducts) =>
        currentProducts.filter(
          (currentProduct) => currentProduct.id !== productId,
        ),
      )
    } catch (error) {
      setError(getErrorMessage(error))
    }
  }

  return (
    <div className="page">
      <Navbar onRefresh={refreshProducts} />

      {error ? <p className="error-text">{error}</p> : null}

      <div className="dashboard-layout">
        <ProductForm isSaving={isSaving} onAddProduct={handleAddProduct} />
        <ProductList
          isLoading={isLoading}
          products={products}
          onDeleteProduct={handleDeleteProduct}
          onToggleStock={handleToggleStock}
        />
      </div>
    </div>
  )
}

export default Dashboard
