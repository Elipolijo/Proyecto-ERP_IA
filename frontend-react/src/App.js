import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ProductosPage from './pages/ProductosPage';
import CategoriasPage from './pages/CategoriasPage';
import ClientesPage from './pages/ClientesPage';
import DashboardPage from './pages/DashboardPage';
import EntradaStockPage from './pages/EntradaStockPage';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import COLORS from './theme/colors';
import ProveedoresPage from './pages/ProveedoresPage';
import FacturasPage from './pages/FacturasPage';
import FacturaFullPage from './pages/FacturaFullPage';
import DemandaHistoricaPage from './pages/DemandaHistoricaPage';

function App() {
  // Persistencia de autenticación
  const [isAuthenticated, setIsAuthenticated] = React.useState(() => {
    return localStorage.getItem('isAuthenticated') === 'true';
  });
  const location = useLocation();

  // Guardar en localStorage cuando cambia
  React.useEffect(() => {
    localStorage.setItem('isAuthenticated', isAuthenticated);
  }, [isAuthenticated]);

  // Mostrar sidebar solo si está autenticado y no en la página de login
  const showSidebar = isAuthenticated && location.pathname !== '/login';

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: COLORS.grisClaro }}>
      {showSidebar && <Sidebar />}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {isAuthenticated && <Navbar setIsAuthenticated={setIsAuthenticated} />}
        <Routes>
          <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/dashboard" element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />} />
          <Route path="/productos" element={isAuthenticated ? <ProductosPage /> : <Navigate to="/login" />} />
          <Route path="/categorias" element={isAuthenticated ? <CategoriasPage /> : <Navigate to="/login" />} />
          <Route path="/clientes" element={isAuthenticated ? <ClientesPage /> : <Navigate to="/login" />} />
          <Route path="/entrada-stock" element={isAuthenticated ? <EntradaStockPage /> : <Navigate to="/login" />} />
          <Route path="/proveedores" element={isAuthenticated ? <ProveedoresPage /> : <Navigate to="/login" />} />
          <Route path="/facturas" element={isAuthenticated ? <FacturasPage /> : <Navigate to="/login" />} />
          <Route path="/facturas/nueva" element={isAuthenticated ? <FacturaFullPage /> : <Navigate to="/login" />} />
          <Route path="/movimiento-stock" element={isAuthenticated ? <DemandaHistoricaPage /> : <Navigate to="/login" />} />
          {/* Aquí puedes agregar más rutas para las nuevas páginas */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
