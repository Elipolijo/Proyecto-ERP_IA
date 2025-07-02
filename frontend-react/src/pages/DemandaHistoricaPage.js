import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress } from '@mui/material';
import DemandaHistoricaService from '../services/DemandaHistoricaService';
import ProductosService from '../services/ProductosService';
import COLORS from '../theme/colors';

function DemandaHistoricaPage() {
  const [demanda, setDemanda] = useState([]);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    DemandaHistoricaService.getAll().then(data => {
      setDemanda(data.data || []);
      setLoading(false);
    });
    ProductosService.getAll().then(data => setProductos(data.productos || []));
  }, []);

  // Mapear producto_id a nombre
  const getNombreProducto = (id) => {
    const prod = productos.find(p => p[0] === id || p.id === id);
    return prod ? (prod[1] || prod.nombre) : id;
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Movimientos de Stock (Salidas por Factura)</Typography>
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        {loading ? <CircularProgress sx={{ color: COLORS.verdeBrillante }} /> : (
          <TableContainer component={Paper} sx={{ background: COLORS.blanco, borderRadius: 3, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, maxHeight: 420, overflowY: 'auto' }}>
            <Table size="small">
              <TableHead sx={{ background: COLORS.verdeSuave }}>
                <TableRow>
                  <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>ID</TableCell>
                  <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Producto</TableCell>
                  <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Fecha</TableCell>
                  <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Cantidad Vendida</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {demanda.map((d) => (
                  <TableRow key={d[0] || d.id}>
                    <TableCell sx={{ fontSize: 13 }}>{d[0] || d.id}</TableCell>
                    <TableCell sx={{ fontSize: 13 }}>{getNombreProducto(d[1] || d.producto_id)}</TableCell>
                    <TableCell sx={{ fontSize: 13 }}>{d[2] || d.fecha}</TableCell>
                    <TableCell sx={{ fontSize: 13 }}>{d[3] || d.cantidad_vendida}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
}

export default DemandaHistoricaPage;
