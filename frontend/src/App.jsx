import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'
import Signin from './pages/Signin'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'

function ProtectedLayout({ children }) {
  return (
    <PrivateRoute>
      <Layout>{children}</Layout>
    </PrivateRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/signin" replace />} />
        <Route path="/signin" element={<Signin />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
        <Route path="/view"      element={<ProtectedLayout><div className="p-8 text-white">View Data</div></ProtectedLayout>} />
        <Route path="/clean"     element={<ProtectedLayout><div className="p-8 text-white">Clean</div></ProtectedLayout>} />
        <Route path="/transform" element={<ProtectedLayout><div className="p-8 text-white">Transform</div></ProtectedLayout>} />
        <Route path="/visualize" element={<ProtectedLayout><div className="p-8 text-white">Visualize</div></ProtectedLayout>} />
        <Route path="/report"    element={<ProtectedLayout><div className="p-8 text-white">Report</div></ProtectedLayout>} />
      </Routes>
    </BrowserRouter>
  )
}