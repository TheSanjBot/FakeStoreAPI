export type StoredUser = {
  username: string
  email: string
  password: string
}

const REGISTERED_USER_KEY = 'registeredUser'
const AUTH_USER_KEY = 'authUser'
const LEGACY_USER_KEY = 'user'

export const AUTH_CHANGE_EVENT = 'authchange'

const readUserFromStorage = (key: string) => {
  const value = localStorage.getItem(key)

  if (!value) {
    return null
  }

  try {
    return JSON.parse(value) as StoredUser
  } catch {
    return null
  }
}

export const getRegisteredUser = () =>
  readUserFromStorage(REGISTERED_USER_KEY) ?? readUserFromStorage(LEGACY_USER_KEY)

export const setRegisteredUser = (user: StoredUser) => {
  localStorage.setItem(REGISTERED_USER_KEY, JSON.stringify(user))
  localStorage.removeItem(LEGACY_USER_KEY)
}

export const getAuthenticatedUser = () => readUserFromStorage(AUTH_USER_KEY)

export const isAuthenticated = () => Boolean(getAuthenticatedUser())

export const setAuthenticatedUser = (user: StoredUser) => {
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
}

export const clearAuthenticatedUser = () => {
  localStorage.removeItem(AUTH_USER_KEY)
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
}
