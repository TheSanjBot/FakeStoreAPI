import { useNavigate } from 'react-router-dom'
import { clearAuthenticatedUser } from '../utils/auth'

type NavbarProps = {
  onRefresh: () => Promise<void> | void
}

const Navbar = ({ onRefresh }: NavbarProps) => {
  const navigate = useNavigate()

  const logout = () => {
    clearAuthenticatedUser()
    navigate('/')
  }

  return (
    <header className="dashboard-nav">
      <h1>Dashboard</h1>
      <div className="dashboard-nav__actions">
        <button type="button" onClick={() => void onRefresh()}>
          Refresh
        </button>
        <button type="button" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  )
}

export default Navbar
