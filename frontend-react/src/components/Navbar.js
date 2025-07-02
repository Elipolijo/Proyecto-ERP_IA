import React, { useEffect, useState } from 'react';
import { AppBar, Toolbar, Button, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import COLORS from '../theme/colors';

function Navbar({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate('/login');
  };

  // Estado para fecha y hora
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Formato de fecha: 2/7/2025
  const fecha = `${now.getDate()}/${now.getMonth() + 1}/${now.getFullYear()}`;
  const hora = now.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  return (
    <AppBar position="static" sx={{ bgcolor: COLORS.verdeOscuro, boxShadow: `0 2px 8px 0 ${COLORS.verdeBrillante}55` }}>
      <Toolbar sx={{ justifyContent: 'center', position: 'relative' }}>
        <Box sx={{ position: 'absolute', left: 0, right: 0, mx: 'auto', textAlign: 'center', width: 220 }}>
          <Typography variant="h6" fontWeight={700} color={COLORS.blanco} fontFamily="'Montserrat', 'Segoe UI', 'Roboto', 'Arial', sans-serif">
            {fecha}
          </Typography>
          <Typography variant="subtitle2" color={COLORS.verdeBrillante} fontWeight={500} fontFamily="'Montserrat', 'Segoe UI', 'Roboto', 'Arial', sans-serif">
            {hora}
          </Typography>
        </Box>
        <Button color="inherit" onClick={handleLogout} sx={{ color: COLORS.acentoRojo, fontWeight: 'bold', ml: 'auto' }}>
          Salir
        </Button>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
