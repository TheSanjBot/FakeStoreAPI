import { FormEvent, useState } from 'react'
import type { ProductInput } from '../types/product'

type ProductFormProps = {
  isSaving: boolean
  onAddProduct: (product: ProductInput) => Promise<void>
}

type ProductFormState = {
  name: string
  description: string
  category: string
  price: string
  inStock: boolean
}

const initialFormState: ProductFormState = {
  name: '',
  description: '',
  category: '',
  price: '',
  inStock: true,
}

const ProductForm = ({ isSaving, onAddProduct }: ProductFormProps) => {
  const [formState, setFormState] = useState<ProductFormState>(initialFormState)
  const [formError, setFormError] = useState('')

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    const name = formState.name.trim()
    const description = formState.description.trim()
    const category = formState.category.trim()
    const price = Number(formState.price)

    if (!name || !description || !category) {
      setFormError('Please complete all product fields before saving.')
      return
    }

    if (!Number.isFinite(price) || price <= 0) {
      setFormError('Price must be a number greater than 0.')
      return
    }

    setFormError('')

    try {
      await onAddProduct({
        name,
        description,
        category,
        price,
        inStock: formState.inStock,
      })
      setFormState(initialFormState)
    } catch {
      // The dashboard displays API errors, so we keep the form values for retry.
    }
  }

  return (
    <section className="section">
      <h2>Add Product</h2>

      <form className="form" onSubmit={handleSubmit}>
        {formError ? <p className="error-text">{formError}</p> : null}

        <label className="field">
          <span>Name</span>
          <input
            type="text"
            value={formState.name}
            onChange={(e) =>
              setFormState({ ...formState, name: e.target.value })
            }
          />
        </label>

        <label className="field">
          <span>Category</span>
          <input
            type="text"
            value={formState.category}
            onChange={(e) =>
              setFormState({ ...formState, category: e.target.value })
            }
          />
        </label>

        <label className="field">
          <span>Price</span>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={formState.price}
            onChange={(e) =>
              setFormState({ ...formState, price: e.target.value })
            }
          />
        </label>

        <label className="field">
          <span>Description</span>
          <textarea
            rows={4}
            value={formState.description}
            onChange={(e) =>
              setFormState({ ...formState, description: e.target.value })
            }
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={formState.inStock}
            onChange={(e) =>
              setFormState({ ...formState, inStock: e.target.checked })
            }
          />
          <span>In stock</span>
        </label>

        <button type="submit" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Add Product'}
        </button>
      </form>
    </section>
  )
}

export default ProductForm
