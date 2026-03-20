import { Outlet } from 'react-router-dom'

export default function ClientLayout() {
  return (
    <div style={{
      minHeight:  '100vh',
      background: '#FFFFFF',
    }}>
      <Outlet />
    </div>
  )
}
