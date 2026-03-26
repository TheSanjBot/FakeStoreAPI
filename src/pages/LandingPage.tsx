import { Link } from 'react-router-dom'

const LandingPage = () => {
  return (
    <div className="page narrow-page">
      <h1>Products App</h1>
      <div className="actions">
        <Link to="/register">Register</Link>
        <Link to="/login">Login</Link>
      </div>
    </div>
  )
}

export default LandingPage
