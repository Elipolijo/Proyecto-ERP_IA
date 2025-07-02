import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import COLORS from '../theme/colors';

function DashboardPage() {
  return (
    <Box flex={1} p={4}>
      {/* Encabezado gerencial */}
      <Typography variant="h4" fontWeight={900} color={COLORS.verdeOscuro} mb={4} letterSpacing={2} fontFamily="'Montserrat', 'Segoe UI', 'Roboto', 'Arial', sans-serif" sx={{ textShadow: `0 2px 8px ${COLORS.verdeSuave}` }}>
        Dashboard Gerencial — Panel del Gerente
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={4} sx={{ p: 3, background: COLORS.blanco, borderLeft: `6px solid ${COLORS.verdeBrillante}` }}>
            <Typography variant="h6" color={COLORS.verdeOscuro} fontWeight="bold" gutterBottom>
              Ventas Totales (Mes)
            </Typography>
            <Typography variant="h3" color={COLORS.verdeBrillante} fontWeight={900}>
              $ 0
            </Typography>
            <Typography variant="body2" color={COLORS.grisOscuro}>
              Actualizado al día de hoy
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={4} sx={{ p: 3, background: COLORS.blanco, borderLeft: `6px solid ${COLORS.verdeIntermedio}` }}>
            <Typography variant="h6" color={COLORS.verdeOscuro} fontWeight="bold" gutterBottom>
              Stock Crítico
            </Typography>
            <Typography variant="h3" color={COLORS.acentoRojo} fontWeight={900}>
              0
            </Typography>
            <Typography variant="body2" color={COLORS.grisOscuro}>
              Productos por debajo del mínimo
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={4} sx={{ p: 3, background: COLORS.blanco, borderLeft: `6px solid ${COLORS.acentoRojo}` }}>
            <Typography variant="h6" color={COLORS.verdeOscuro} fontWeight="bold" gutterBottom>
              Clientes Activos
            </Typography>
            <Typography variant="h3" color={COLORS.verdeIntermedio} fontWeight={900}>
              0
            </Typography>
            <Typography variant="body2" color={COLORS.grisOscuro}>
              Últimos 30 días
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;
