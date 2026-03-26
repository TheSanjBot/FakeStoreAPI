export interface Product {
  id: number
  name: string
  description: string
  category: string
  price: number
  inStock: boolean
}

export type ProductInput = Omit<Product, 'id'>
