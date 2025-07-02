import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, Grid, Button } from '@mui/material';
import ProveedoresService from '../services/ProveedoresService';
import COLORS from '../theme/colors';

const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

function ProveedoresPage() {
  const [proveedores, setProveedores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const proveedoresPorPagina = 10;

  useEffect(() => {
    ProveedoresService.getAll().then(data => {
      setProveedores(data.data || []);
      setLoading(false);
    });
  }, []);

  // Filtrado por nombre
  const proveedoresFiltrados = proveedores.filter((p) =>
    p.nombre?.toLowerCase().includes(busqueda.toLowerCase())
  );

  // Paginación
  const totalPaginas = Math.ceil(proveedoresFiltrados.length / proveedoresPorPagina);
  const proveedoresPagina = proveedoresFiltrados.slice((pagina - 1) * proveedoresPorPagina, pagina * proveedoresPorPagina);

  // Acciones de editar y eliminar (a implementar)
  const handleEdit = (proveedor) => {
    alert(`Editar proveedor: ${proveedor.nombre}`);
  };
  const handleDelete = (proveedor) => {
    alert(`Eliminar proveedor: ${proveedor.nombre}`);
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de proveedores</Typography>
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={() => alert('Funcionalidad de alta de proveedor próximamente')}
          >
            + Proveedor Nuevo
          </Button>
        </Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              label="Buscar por nombre"
              value={busqueda}
              onChange={e => setBusqueda(e.target.value)}
              fullWidth
              size="small"
              sx={{ background: COLORS.verdeSuave }}
            />
          </Grid>
        </Grid>
      </Paper>
      {loading ? <CircularProgress sx={{ color: COLORS.verdeBrillante }} /> : (
        <TableContainer component={Paper} sx={{ background: COLORS.blanco, borderRadius: 3, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, maxHeight: 420, overflowY: 'auto', '::-webkit-scrollbar': { width: 8 }, '::-webkit-scrollbar-thumb': { background: COLORS.verdeSuave, borderRadius: 4 } }}>
          <Table size="small" sx={{
            '& .MuiTableCell-root': {
              fontSize: 13,
              paddingTop: '4px',
              paddingBottom: '4px',
              height: 32
            },
            '& .MuiTableRow-root': {
              height: 32
            }
          }}>
            <TableHead sx={{ background: COLORS.verdeSuave }}>
              <TableRow>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>ID</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Nombre</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Contacto</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Teléfono</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Email</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Dirección</TableCell>
                <TableCell align="center" sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {proveedoresPagina.map((p) => (
                <TableRow key={p.id} hover sx={{ height: 32, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{p.id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p.nombre}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p.contacto}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p.telefono}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p.email}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p.direccion}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 13 }}>
                    <span style={{ display: 'inline-flex', gap: 8 }}>
                      <button onClick={() => handleEdit(p)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Editar">
                        <EditIcon />
                      </button>
                      <button onClick={() => handleDelete(p)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Eliminar">
                        <DeleteIcon />
                      </button>
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      {/* Paginación simple */}
      <Box display="flex" justifyContent="center" alignItems="center" mt={2}>
        <Button
          variant="outlined"
          size="small"
          sx={{ mr: 1, minWidth: 32, color: COLORS.verdeOscuro, borderColor: COLORS.verdeSuave }}
          disabled={pagina === 1}
          onClick={() => setPagina(pagina - 1)}
        >
          {'<'}
        </Button>
        <Typography variant="body2" color={COLORS.verdeOscuro}>
          Página {pagina} de {totalPaginas}
        </Typography>
        <Button
          variant="outlined"
          size="small"
          sx={{ ml: 1, minWidth: 32, color: COLORS.verdeOscuro, borderColor: COLORS.verdeSuave }}
          disabled={pagina === totalPaginas}
          onClick={() => setPagina(pagina + 1)}
        >
          {'>'}
        </Button>
      </Box>
    </Box>
  );
}

export default ProveedoresPage;
