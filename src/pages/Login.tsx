import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getRegisteredUser, setAuthenticatedUser } from '../utils/auth'

const Login = () => {
  const [login, setLogin] = useState({
    email: '',
    password: '',
  })
  const navigate = useNavigate()

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    const registeredUser = getRegisteredUser()

    if (!registeredUser) {
      alert('No registered user found')
      return
    }

    if (
      registeredUser.email === login.email &&
      registeredUser.password === login.password
    ) {
      setAuthenticatedUser(registeredUser)
      navigate('/dashboard', { replace: true })
      return
    }

    alert('Invalid credentials')
  }

  return (
    <div className="page narrow-page">
      <h1>Login</h1>

      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={login.email}
            onChange={(e) => setLogin({ ...login, email: e.target.value })}
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={login.password}
            onChange={(e) => setLogin({ ...login, password: e.target.value })}
          />
        </label>

        <button type="submit">Login</button>
      </form>

      <p className="link-row">
        <Link to="/register">Register</Link>
      </p>
    </div>
  )
}

export default Login
