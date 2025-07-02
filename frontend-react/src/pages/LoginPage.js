import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';
import AuthService from '../services/AuthService';

// Paleta de colores profesional
const COLORS = {
  acentoRojo: '#ef4444', // acento
  verdeBrillante: '#34d399', // IA
  verdeSuave: '#d1fae5', // fondo suave
  verdeIntermedio: '#10b981', // acción
  grisClaro: '#f3f4f6', // fondo general
  verdeOscuro: '#059669', // texto importante
  blanco: '#ffffff',
  grisOscuro: '#374151', // texto secundario
};

function LoginPage({ setIsAuthenticated }) {
  const [nombre, setNombre] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await AuthService.login(nombre, password);
      if (res.success) {
        setIsAuthenticated(true);
        navigate('/dashboard'); // Redirigir al dashboard tras login
      } else {
        setError(res.message || 'Error de autenticación');
      }
    } catch (err) {
      setError('Error de servidor');
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor={COLORS.grisClaro} position="relative">
      {/* Marca POLIX.IA en la parte superior izquierda */}
      <Box position="absolute" top={24} left={48} zIndex={2}>
        <Typography
          variant="h3"
          fontWeight={900}
          fontFamily="'Montserrat', 'Segoe UI', 'Roboto', 'Arial', sans-serif"
          letterSpacing={4}
          color={COLORS.verdeOscuro}
          sx={{
            textShadow: `0 2px 8px ${COLORS.verdeSuave}`,
            fontStyle: 'italic',
            textTransform: 'uppercase',
            fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
            userSelect: 'none',
          }}
        >
          POLIX.<span style={{ color: COLORS.verdeBrillante, fontWeight: 700 }}>IA</span>
        </Typography>
      </Box>
      <Paper elevation={8} sx={{
        p: 4,
        minWidth: 340,
        background: `linear-gradient(135deg, ${COLORS.blanco} 80%, ${COLORS.verdeSuave} 100%)`,
        borderRadius: 4,
        boxShadow: `0 8px 32px 0 ${COLORS.verdeBrillante}33`,
        border: `1.5px solid ${COLORS.verdeBrillante}`
      }}>
        <Typography variant="h5" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Iniciar Sesión</Typography>
        <form onSubmit={handleSubmit}>
          <TextField label="Usuario" fullWidth margin="normal" value={nombre} onChange={e => setNombre(e.target.value)} required InputLabelProps={{ style: { color: COLORS.verdeOscuro } }} InputProps={{ style: { color: COLORS.verdeOscuro } }} />
          <TextField label="Contraseña" type="password" fullWidth margin="normal" value={password} onChange={e => setPassword(e.target.value)} required InputLabelProps={{ style: { color: COLORS.verdeOscuro } }} InputProps={{ style: { color: COLORS.verdeOscuro } }} />
          {error && <Typography color="error" variant="body2" sx={{ mt: 1, color: COLORS.acentoRojo }}>{error}</Typography>}
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2, bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', '&:hover': { bgcolor: COLORS.verdeOscuro } }}>
            Entrar
          </Button>
        </form>
        <Box mt={3} textAlign="center">
          <Typography variant="caption" color={COLORS.grisOscuro}>
            © {new Date().getFullYear()} POLIXAI. Todos los derechos reservados.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}

export default LoginPage;
