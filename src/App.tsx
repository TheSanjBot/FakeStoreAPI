import './App.css'
import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import { Register } from './pages/Register'
import { AUTH_CHANGE_EVENT, isAuthenticated } from './utils/auth'

function App() {
  const [isAuth, setIsAuth] = useState(() => isAuthenticated())

  useEffect(() => {
    const syncAuth = () => {
      setIsAuth(isAuthenticated())
    }

    window.addEventListener(AUTH_CHANGE_EVENT, syncAuth)
    window.addEventListener('storage', syncAuth)

    return () => {
      window.removeEventListener(AUTH_CHANGE_EVENT, syncAuth)
      window.removeEventListener('storage', syncAuth)
    }
  }, [])

  return (
    <div className="app-shell">
      <Routes>
        <Route
          path="/"
          element={isAuth ? <Navigate replace to="/dashboard" /> : <LandingPage />}
        />
        <Route
          path="/login"
          element={isAuth ? <Navigate replace to="/dashboard" /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuth ? <Navigate replace to="/dashboard" /> : <Register />}
        />
        <Route
          path="/dashboard"
          element={isAuth ? <Dashboard /> : <Navigate replace to="/login" />}
        />
        <Route
          path="*"
          element={<Navigate replace to={isAuth ? '/dashboard' : '/'} />}
        />
      </Routes>
    </div>
  )
}

export default App
