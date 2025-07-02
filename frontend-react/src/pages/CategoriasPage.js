import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, Grid, Button } from '@mui/material';
import CategoriasService from '../services/CategoriasService';
import COLORS from '../theme/colors';
import CategoriaFormModal from '../components/CategoriaFormModal';

const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

function CategoriasPage() {
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [openModal, setOpenModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [categoriaEdit, setCategoriaEdit] = useState(null);
  const categoriasPorPagina = 10;

  useEffect(() => {
    CategoriasService.getAll().then(data => {
      setCategorias(data.data || []);
      setLoading(false);
    });
  }, []);

  // Ordenar categorías por id ascendente
  const categoriasOrdenadas = [...categorias].sort((a, b) => a.id - b.id);
  // Filtrado por nombre
  const categoriasFiltradas = categoriasOrdenadas.filter((c) =>
    c.nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  // Paginación
  const totalPaginas = Math.ceil(categoriasFiltradas.length / categoriasPorPagina);
  const categoriasPagina = categoriasFiltradas.slice((pagina - 1) * categoriasPorPagina, pagina * categoriasPorPagina);

  // Acción de editar (a implementar)
  const handleEdit = (categoria) => {
    setCategoriaEdit(categoria);
    setEditModal(true);
  };
  const handleDelete = async (categoria) => {
    if (window.confirm(`¿Seguro que deseas eliminar la categoría "${categoria.nombre}"?`)) {
      try {
        await CategoriasService.delete(categoria.id);
        setLoading(true);
        const data = await CategoriasService.getAll();
        setCategorias(data.data || []);
        setLoading(false);
      } catch (err) {
        alert('Error al eliminar la categoría');
      }
    }
  };
  const handleCreateCategoria = async (form) => {
    try {
      await CategoriasService.create(form);
      setOpenModal(false);
      setLoading(true);
      const data = await CategoriasService.getAll();
      setCategorias(data.data || []);
      setLoading(false);
    } catch (err) {
      alert('Error al guardar la categoría');
    }
  };
  const handleUpdateCategoria = async (form) => {
    try {
      await CategoriasService.update(categoriaEdit.id, form);
      setEditModal(false);
      setLoading(true);
      const data = await CategoriasService.getAll();
      setCategorias(data.data || []);
      setLoading(false);
    } catch (err) {
      alert('Error al actualizar la categoría');
    }
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de categorías</Typography>
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={() => setOpenModal(true)}
          >
            + Categoría Nueva
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
          <Table size="small">
            <TableHead sx={{ background: COLORS.verdeSuave }}>
              <TableRow>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>ID</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Nombre</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Descripción</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {categoriasPagina.map((c, idx) => (
                <TableRow key={c.id} hover sx={{ height: 36, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{c.id}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.nombre}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{c.descripcion}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 13 }}>
                    <button onClick={() => handleEdit(c)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} title="Editar">
                      <EditIcon />
                    </button>
                    <button onClick={() => handleDelete(c)} style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: 8 }} title="Eliminar">
                      <DeleteIcon />
                    </button>
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
      <CategoriaFormModal open={openModal} onClose={() => setOpenModal(false)} onSubmit={handleCreateCategoria} />
      <CategoriaFormModal open={editModal} onClose={() => setEditModal(false)} onSubmit={handleUpdateCategoria} initialData={categoriaEdit} />
    </Box>
  );
}

export default CategoriasPage;
