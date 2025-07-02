import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, Grid, Button } from '@mui/material';
import FacturasService from '../services/FacturasService';
import ClientesService from '../services/ClientesService';
import ProductosService from '../services/ProductosService';
import FacturasFormModal from '../components/FacturasFormModal';
import COLORS from '../theme/colors';

const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

function FacturasPage() {
  const [facturas, setFacturas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [openModal, setOpenModal] = useState(false);
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const facturasPorPagina = 10;

  useEffect(() => {
    fetchFacturas();
    ClientesService.getAll().then(data => setClientes(data.data || []));
    ProductosService.getAll().then(data => setProductos(data.productos || []));
  }, []);

  const fetchFacturas = () => {
    setLoading(true);
    FacturasService.getAll().then(data => {
      setFacturas(data.data || []);
      setLoading(false);
    });
  };

  // El backend devuelve facturas como arrays, no objetos. Adaptar para la tabla:
  const adaptFactura = (f) => ({
    id: f[0],
    cliente_id: f[1],
    nombre_cliente: f[2],
    email_cliente: f[3],
    fecha: f[4],
    total: f[5]
  });
  const facturasAdaptadas = facturas.map(adaptFactura);
  // Filtrado por nombre de cliente
  const facturasFiltradas = facturasAdaptadas.filter((f) =>
    (f.nombre_cliente || '').toLowerCase().includes(busqueda.toLowerCase())
  );
  // Paginación
  const totalPaginas = Math.ceil(facturasFiltradas.length / facturasPorPagina);
  const facturasPagina = facturasFiltradas.slice((pagina - 1) * facturasPorPagina, pagina * facturasPorPagina);

  // Acciones de editar y eliminar (a implementar)
  const handleEdit = (factura) => {
    alert(`Editar factura: ${factura.id}`);
  };
  const handleDelete = (factura) => {
    alert(`Eliminar factura: ${factura.id}`);
  };
  const handleAddFactura = async (form) => {
    try {
      await FacturasService.create(form);
      setOpenModal(false);
      fetchFacturas();
    } catch (err) {
      alert('Error al guardar la factura');
    }
  };

  // Al hacer clic en Factura Nueva, navegar a /facturas/nueva
  const handleNuevaFactura = () => {
    window.location.href = '/facturas/nueva';
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de facturas</Typography>
      <FacturasFormModal open={openModal} onClose={() => setOpenModal(false)} onSubmit={handleAddFactura} clientes={clientes} productos={productos} />
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={handleNuevaFactura}
          >
            + Factura Nueva
          </Button>
        </Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              label="Buscar por cliente"
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
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Cliente</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Fecha</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Total</TableCell>
                <TableCell align="center" sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {facturasPagina.map((f) => (
                <TableRow key={f.id} hover sx={{ height: 32, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{f.id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{f.nombre_cliente || f.cliente_id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{f.fecha}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{f.total}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 13 }}>
                    <span style={{ display: 'inline-flex', gap: 8 }}>
                      <button onClick={() => handleEdit(f)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Editar">
                        <EditIcon />
                      </button>
                      <button onClick={() => handleDelete(f)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Eliminar">
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

export default FacturasPage;
