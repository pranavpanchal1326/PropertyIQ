import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useTheme } from './hooks/useTheme'

// Layouts
import AdminLayout  from './components/layout/AdminLayout'
import ClientLayout from './components/layout/ClientLayout'

// Admin pages
import DriftMonitor  from './pages/Admin/DriftMonitor'
import ModelHealth   from './pages/Admin/ModelHealth'
import CityAnalytics from './pages/Admin/CityAnalytics'
import AlertLog      from './pages/Admin/AlertLog'

// Client Portal
import ClientPortal from './pages/Client/index'

// Landing Page
import Landing from './pages/Landing/index'

export default function App() {
  const { theme, toggle, isDark } = useTheme()
  
  return (
    <BrowserRouter>
      <Routes>
        
        {/* ── Landing Page ─────────────────────────── */}
        <Route path="/" element={<Landing />} />
        
        {/* ── Admin Console ────────────────────────── */}
        <Route
          path="/admin"
          element={
            <AdminLayout
              theme={theme}
              onToggle={toggle}
              isDark={isDark}
            />
          }
        >
          {/* Default → Drift Monitor */}
          <Route index element={<Navigate to="drift" replace />} />
          <Route path="drift"   element={<DriftMonitor  />} />
          <Route path="model"   element={<ModelHealth   />} />
          <Route path="city"    element={<CityAnalytics />} />
          <Route path="alerts"  element={<AlertLog      />} />
        </Route>
        
        {/* ── Client Portal ─────────────────────────── */}
        <Route path="/client" element={<ClientLayout />}>
          <Route index element={<ClientPortal />} />
        </Route>
        
        {/* ── Catch-all ─────────────────────────────── */}
        <Route path="*" element={<Navigate to="/" replace />} />
       </Routes>
    </BrowserRouter>
  )
}
