import React from 'react';
import { AppBar, Toolbar, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import COLORS from '../theme/colors';

function Navbar({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate('/login');
  };
  return (
    <AppBar position="static" sx={{ bgcolor: COLORS.verdeOscuro, boxShadow: `0 2px 8px 0 ${COLORS.verdeBrillante}55` }}>
      <Toolbar>
        <Button color="inherit" onClick={handleLogout} sx={{ color: COLORS.acentoRojo, fontWeight: 'bold', ml: 'auto' }}>
          Salir
        </Button>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
