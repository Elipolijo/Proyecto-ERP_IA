import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, Grid, Button } from '@mui/material';
import ClientesService from '../services/ClientesService';
import ClienteFormModal from '../components/ClienteFormModal';
import COLORS from '../theme/colors';

const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

function ClientesPage() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [openModal, setOpenModal] = useState(false);
  const clientesPorPagina = 10;

  useEffect(() => {
    fetchClientes();
  }, []);

  const fetchClientes = () => {
    setLoading(true);
    ClientesService.getAll().then(data => {
      setClientes(data.data || []);
      setLoading(false);
    });
  };

  // Ordenar clientes por id ascendente
  const clientesOrdenados = [...clientes].sort((a, b) => a.id - b.id);
  // Filtrado por nombre
  const clientesFiltrados = clientesOrdenados.filter((c) =>
    c.nombre?.toLowerCase().includes(busqueda.toLowerCase())
  );

  // Paginación
  const totalPaginas = Math.ceil(clientesFiltrados.length / clientesPorPagina);
  const clientesPagina = clientesFiltrados.slice((pagina - 1) * clientesPorPagina, pagina * clientesPorPagina);

  // Acciones de editar y eliminar (a implementar)
  const handleEdit = (cliente) => {
    alert(`Editar cliente: ${cliente.nombre}`);
  };
  const handleDelete = (cliente) => {
    alert(`Eliminar cliente: ${cliente.nombre}`);
  };
  const handleAddCliente = async (form) => {
    try {
      await ClientesService.create(form);
      setOpenModal(false);
      fetchClientes();
    } catch (err) {
      alert('Error al guardar el cliente');
    }
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de clientes</Typography>
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={() => setOpenModal(true)}
          >
            + Cliente Nuevo
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
        <ClienteFormModal open={openModal} onClose={() => setOpenModal(false)} onSubmit={handleAddCliente} />
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
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>DNI</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Teléfono</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Email</TableCell>
                <TableCell align="center" sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clientesPagina.map((c) => (
                <TableRow key={c.id} hover sx={{ height: 32, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{c.id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.nombre}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.dni}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.telefono}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.email}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 13 }}>
                    <span style={{ display: 'inline-flex', gap: 8 }}>
                      <button onClick={() => handleEdit(c)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Editar">
                        <EditIcon />
                      </button>
                      <button onClick={() => handleDelete(c)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Eliminar">
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

export default ClientesPage;
