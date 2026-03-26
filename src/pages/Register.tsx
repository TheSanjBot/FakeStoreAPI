import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { setRegisteredUser } from '../utils/auth'

export const Register = () => {
  const [user, setUser] = useState({
    username: '',
    email: '',
    password: '',
  })

  const navigate = useNavigate()

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setRegisteredUser(user)
    navigate('/login')
  }

  return (
    <div className="page narrow-page">
      <h1>Register</h1>

      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Username</span>
          <input
            type="text"
            value={user.username}
            onChange={(e) => setUser({ ...user, username: e.target.value })}
          />
        </label>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={user.email}
            onChange={(e) => setUser({ ...user, email: e.target.value })}
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={user.password}
            onChange={(e) => setUser({ ...user, password: e.target.value })}
          />
        </label>

        <button type="submit">Register</button>
      </form>

      <p className="link-row">
        <Link to="/login">Login</Link>
      </p>
    </div>
  )
}
