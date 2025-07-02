import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, Grid, Button } from '@mui/material';
import COLORS from '../theme/colors';
import EntradaStockService from '../services/EntradaStockService';
import EntradaStockFormModal from '../components/EntradaStockFormModal';
import ProductosService from '../services/ProductosService';
import ProveedoresService from '../services/ProveedoresService';

const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

// Simulación de servicio (reemplazar por API real)
const fetchEntradasStock = async () => {
  // Aquí deberías llamar a tu API real
  return [
    { id: 1, producto: 'Producto A', cantidad: 10, fecha: '2025-06-25', proveedor: 'Proveedor X', observacion: 'Ingreso inicial' },
    { id: 2, producto: 'Producto B', cantidad: 5, fecha: '2025-06-24', proveedor: 'Proveedor Y', observacion: 'Reposición' },
    // ...
  ];
};

function EntradaStockPage() {
  const [entradas, setEntradas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [openModal, setOpenModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [entradaEdit, setEntradaEdit] = useState(null);
  const entradasPorPagina = 10;

  useEffect(() => {
    EntradaStockService.getAll().then(data => {
      setEntradas(data.data || []); // Usar la clave correcta del backend
      setLoading(false);
    });
  }, []);

  // Filtrado por producto
  const entradasFiltradas = entradas.filter((e) =>
    e.nombre_producto?.toLowerCase().includes(busqueda.toLowerCase())
  );

  // Paginación
  const totalPaginas = Math.ceil(entradasFiltradas.length / entradasPorPagina);
  const entradasPagina = entradasFiltradas.slice((pagina - 1) * entradasPorPagina, pagina * entradasPorPagina);

  // Acciones de editar y eliminar (a implementar)
  const handleEdit = (entrada) => {
    setEntradaEdit(entrada);
    setEditModal(true);
  };
  const handleDelete = async (entrada) => {
    if (window.confirm(`¿Seguro que deseas eliminar la entrada de "${entrada.nombre_producto || entrada.producto}"?`)) {
      try {
        await EntradaStockService.delete(entrada.id);
        setLoading(true);
        const data = await EntradaStockService.getAll();
        setEntradas(data.data || []);
        setLoading(false);
      } catch (err) {
        alert('Error al eliminar la entrada de stock');
      }
    }
  };
  const handleCreateEntrada = async (form) => {
    // Buscar IDs
    const productoId = form.producto;
    const proveedorId = form.proveedor;
    const nuevaEntrada = {
      producto_id: parseInt(productoId),
      proveedor_id: parseInt(proveedorId),
      cantidad: parseInt(form.cantidad),
      precio_compra: parseFloat(form.precio_compra),
      precio_venta: form.precio_venta ? parseFloat(form.precio_venta) : null,
      observacion: form.observacion || ''
    };
    try {
      await EntradaStockService.create(nuevaEntrada);
      setOpenModal(false);
      setLoading(true);
      const data = await EntradaStockService.getAll();
      setEntradas(data.data || []);
      setLoading(false);
    } catch (err) {
      alert('Error al guardar la entrada de stock');
    }
  };
  const handleUpdateEntrada = async (form) => {
    try {
      await EntradaStockService.update(entradaEdit.id, form);
      setEditModal(false);
      setLoading(true);
      const data = await EntradaStockService.getAll();
      setEntradas(data.data || []);
      setLoading(false);
    } catch (err) {
      alert('Error al actualizar la entrada de stock');
    }
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de entradas de stock</Typography>
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={() => setOpenModal(true)}
          >
            + Entrada de Stock
          </Button>
        </Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              label="Buscar por producto"
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
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Producto ID</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Producto</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Proveedor ID</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Proveedor</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Usuario ID</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Cantidad</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Precio Compra</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Precio Venta</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Fecha</TableCell>
                <TableCell align="center" sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {entradasPagina.map((e, idx) => (
                <TableRow key={e.id} hover sx={{ height: 36, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{e.id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.producto_id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.nombre_producto}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.proveedor_id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.nombre_proveedor}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.usuario_id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.cantidad}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.precio_compra}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.precio_venta}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{e.fecha}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 13 }}>
                    <span style={{ display: 'inline-flex', gap: 8 }}>
                      <button onClick={() => handleEdit(e)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Editar">
                        <EditIcon />
                      </button>
                      <button onClick={() => handleDelete(e)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Eliminar">
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
      <EntradaStockFormModal open={openModal} onClose={() => setOpenModal(false)} onSubmit={handleCreateEntrada} />
      <EntradaStockFormModal open={editModal} onClose={() => setEditModal(false)} onSubmit={handleUpdateEntrada} initialData={entradaEdit} />
    </Box>
  );
}

export default EntradaStockPage;
