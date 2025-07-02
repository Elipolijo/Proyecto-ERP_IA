import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, TextField, MenuItem, Grid, Button } from '@mui/material';
import ProductosService from '../services/ProductosService';
import CategoriasService from '../services/CategoriasService';
import ProveedoresService from '../services/ProveedoresService';
import COLORS from '../theme/colors';
import ProductoFormModal from '../components/ProductoFormModal';

// Iconos SVG inline para evitar problemas de dependencias
const EditIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
);
const DeleteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
);

function ProductosPage() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categorias, setCategorias] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [categoriaFiltro, setCategoriaFiltro] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [openModal, setOpenModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [productoEdit, setProductoEdit] = useState(null);
  const productosPorPagina = 10;

  useEffect(() => {
    ProductosService.getAll().then(data => {
      setProductos(data.productos || []);
      setLoading(false);
    });
    CategoriasService.getAll().then(data => {
      setCategorias(data.data || []);
    });
    ProveedoresService.getAll().then(data => {
      setProveedores(data.data || []);
    });
  }, []);

  // Filtrado por categoría y búsqueda por nombre
  const productosFiltrados = productos.filter((p) => {
    const coincideCategoria = categoriaFiltro ? p[7] === categoriaFiltro : true;
    const coincideNombre = p[1].toLowerCase().includes(busqueda.toLowerCase());
    return coincideCategoria && coincideNombre;
  });

  // Paginación
  const totalPaginas = Math.ceil(productosFiltrados.length / productosPorPagina);
  const productosPagina = productosFiltrados.slice((pagina - 1) * productosPorPagina, pagina * productosPorPagina);

  // Acciones de editar y eliminar (a implementar)
  const handleEdit = (producto) => {
    setProductoEdit(producto);
    setEditModal(true);
  };
  const handleDelete = async (producto) => {
    if (window.confirm(`¿Seguro que deseas eliminar el producto "${producto[1]}"?`)) {
      try {
        await ProductosService.delete(producto[0]);
        setLoading(true);
        const data = await ProductosService.getAll();
        setProductos(data.productos || []);
        setLoading(false);
      } catch (err) {
        alert('Error al eliminar el producto');
      }
    }
  };
  const handleCreateProducto = async (form) => {
    // Buscar IDs de categoría y proveedor
    const categoriaObj = categorias.find(cat => cat.nombre === form.categoria);
    const proveedorObj = form.proveedor ? proveedores.find(prov => prov.nombre === form.proveedor) : null;
    const nuevoProducto = {
      nombre: form.nombre,
      descripcion: form.descripcion,
      precio_compra: parseFloat(form.precio_compra),
      precio_venta: parseFloat(form.precio_venta),
      stock_actual: parseInt(form.stock),
      stock_minimo: parseInt(form.stock_minimo),
      categoria_id: categoriaObj ? categoriaObj.id : null,
      proveedor_id: proveedorObj ? proveedorObj.id : null
    };
    try {
      await ProductosService.create(nuevoProducto);
      setOpenModal(false);
      setLoading(true);
      const data = await ProductosService.getAll();
      setProductos(data.productos || []);
      setLoading(false);
    } catch (err) {
      alert('Error al guardar el producto');
    }
  };
  const handleUpdateProducto = async (form) => {
    try {
      await ProductosService.update(productoEdit[0], form);
      setEditModal(false);
      setLoading(true);
      const data = await ProductosService.getAll();
      setProductos(data.productos || []);
      setLoading(false);
    } catch (err) {
      alert('Error al actualizar el producto');
    }
  };

  return (
    <Box p={3} bgcolor={COLORS.grisClaro} minHeight="100vh">
      <Typography variant="h6" mb={2} color={COLORS.verdeOscuro} fontWeight="bold">Lista de productos</Typography>
      <ProductoFormModal open={openModal} onClose={() => setOpenModal(false)} onSubmit={handleCreateProducto} categorias={categorias} proveedores={proveedores} />
      <ProductoFormModal open={editModal} onClose={() => setEditModal(false)} onSubmit={handleUpdateProducto} categorias={categorias} proveedores={proveedores} initialData={productoEdit} />
      <Paper sx={{ p: 2, mb: 2, background: COLORS.blanco }}>
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={2}>
          <Button
            variant="contained"
            sx={{ bgcolor: COLORS.verdeIntermedio, color: COLORS.blanco, fontWeight: 'bold', borderRadius: 2, boxShadow: `0 2px 8px 0 ${COLORS.verdeSuave}`, fontSize: 13, py: 0.5, px: 2 }}
            onClick={() => setOpenModal(true)}
          >
            + Producto Nuevo
          </Button>
        </Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              select
              label="Filtrar por categoría"
              value={categoriaFiltro}
              onChange={e => setCategoriaFiltro(e.target.value)}
              fullWidth
              size="small"
              sx={{ background: COLORS.verdeSuave }}
            >
              <MenuItem value="">Todas</MenuItem>
              {categorias.map((cat) => (
                <MenuItem key={cat.id} value={cat.nombre}>{cat.nombre}</MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={5}>
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
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Precio Compra</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Precio Venta</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Stock Actual</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Stock Mínimo</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Categoría</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13 }}>Proveedor</TableCell>
                <TableCell sx={{ color: COLORS.verdeOscuro, fontWeight: 'bold', fontSize: 13, textAlign: 'center' }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {productosPagina.map((p, idx) => (
                <TableRow key={idx} hover sx={{ height: 36, '&:hover': { background: COLORS.verdeSuave } }}>
                  <TableCell sx={{ fontSize: 13 }}>{p[0]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[1]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[2]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[3]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[4]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[5]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[6]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[7]}</TableCell>
                  <TableCell sx={{ fontSize: 13 }}>{p[8]}</TableCell>
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

export default ProductosPage;
