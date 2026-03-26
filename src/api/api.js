import { createServer } from 'node:http'
import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const PORT = 3001
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const dbPath = path.resolve(__dirname, '../data/db.json')

const baseHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
}

const sendJson = (res, statusCode, payload) => {
  res.writeHead(statusCode, baseHeaders)
  res.end(JSON.stringify(payload, null, 2))
}

const readDatabase = async () => {
  const fileContent = await readFile(dbPath, 'utf8')
  return JSON.parse(fileContent)
}

const writeDatabase = async (data) => {
  await writeFile(dbPath, `${JSON.stringify(data, null, 2)}\n`, 'utf8')
}

const parseRequestBody = (req) =>
  new Promise((resolve, reject) => {
    let body = ''

    req.on('data', (chunk) => {
      body += chunk

      if (body.length > 1_000_000) {
        reject(new Error('Request body is too large.'))
      }
    })

    req.on('end', () => {
      if (!body) {
        resolve({})
        return
      }

      try {
        resolve(JSON.parse(body))
      } catch {
        reject(new Error('Request body must be valid JSON.'))
      }
    })

    req.on('error', reject)
  })

const validateProductInput = (payload) => {
  const name = typeof payload.name === 'string' ? payload.name.trim() : ''
  const description =
    typeof payload.description === 'string' ? payload.description.trim() : ''
  const category =
    typeof payload.category === 'string' ? payload.category.trim() : ''
  const price = Number(payload.price)
  const inStock =
    typeof payload.inStock === 'boolean' ? payload.inStock : Boolean(payload.inStock)

  if (!name || !description || !category) {
    return {
      error:
        'Product name, description, and category are all required fields.',
    }
  }

  if (!Number.isFinite(price) || price <= 0) {
    return {
      error: 'Product price must be a number greater than 0.',
    }
  }

  return {
    value: {
      name,
      description,
      category,
      price,
      inStock,
    },
  }
}

createServer(async (req, res) => {
  if (!req.url || !req.method) {
    sendJson(res, 400, { message: 'Request is missing a URL or method.' })
    return
  }

  if (req.method === 'OPTIONS') {
    res.writeHead(204, baseHeaders)
    res.end()
    return
  }

  const url = new URL(req.url, `http://localhost:${PORT}`)
  const productRouteMatch = url.pathname.match(/^\/products\/(\d+)$/)

  try {
    if (url.pathname === '/' || url.pathname === '/health') {
      sendJson(res, 200, {
        message: 'Products API is running.',
        dbPath,
        port: PORT,
      })
      return
    }

    if (url.pathname === '/products' && req.method === 'GET') {
      const database = await readDatabase()
      sendJson(res, 200, database.products ?? [])
      return
    }

    if (url.pathname === '/products' && req.method === 'POST') {
      const payload = await parseRequestBody(req)
      const validated = validateProductInput(payload)

      if (validated.error) {
        sendJson(res, 400, { message: validated.error })
        return
      }

      const database = await readDatabase()
      const nextId = (database.products ?? []).reduce(
        (largestId, product) => Math.max(largestId, Number(product.id) || 0),
        0,
      ) + 1

      const createdProduct = {
        id: nextId,
        ...validated.value,
      }

      database.products = [createdProduct, ...(database.products ?? [])]
      await writeDatabase(database)
      sendJson(res, 201, createdProduct)
      return
    }

    if (productRouteMatch && req.method === 'PUT') {
      const productId = Number(productRouteMatch[1])
      const payload = await parseRequestBody(req)
      const validated = validateProductInput(payload)

      if (validated.error) {
        sendJson(res, 400, { message: validated.error })
        return
      }

      const database = await readDatabase()
      const productIndex = (database.products ?? []).findIndex(
        (product) => Number(product.id) === productId,
      )

      if (productIndex === -1) {
        sendJson(res, 404, { message: 'Product not found.' })
        return
      }

      const updatedProduct = {
        id: productId,
        ...validated.value,
      }

      database.products[productIndex] = updatedProduct
      await writeDatabase(database)
      sendJson(res, 200, updatedProduct)
      return
    }

    if (productRouteMatch && req.method === 'DELETE') {
      const productId = Number(productRouteMatch[1])
      const database = await readDatabase()
      const existingProducts = database.products ?? []
      const filteredProducts = existingProducts.filter(
        (product) => Number(product.id) !== productId,
      )

      if (filteredProducts.length === existingProducts.length) {
        sendJson(res, 404, { message: 'Product not found.' })
        return
      }

      database.products = filteredProducts
      await writeDatabase(database)
      sendJson(res, 200, { message: 'Product deleted successfully.' })
      return
    }

    sendJson(res, 404, { message: 'Route not found.' })
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Unexpected server error while processing the request.'

    sendJson(res, 500, { message })
  }
}).listen(PORT, () => {
  console.log(`Products API running at http://localhost:${PORT}`)
})
