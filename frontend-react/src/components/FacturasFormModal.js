import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Grid, MenuItem } from '@mui/material';
import ClienteFormModal from './ClienteFormModal';

function FacturasFormModal({ open, onClose, onSubmit, clientes, productos }) {
  const [form, setForm] = useState({ cliente_id: '', productos: [], fecha: '', total: '' });
  const [openClienteModal, setOpenClienteModal] = useState(false);

  const handleChange = (e) => {
    if (e.target.name === 'cliente_id' && e.target.value === 'nuevo') {
      setOpenClienteModal(true);
      return;
    }
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddCliente = (formCliente) => {
    setOpenClienteModal(false);
    // Aquí deberías refrescar la lista de clientes y seleccionar el nuevo si lo deseas
  };

  const handleProductoChange = (idx, field, value) => {
    const nuevosProductos = [...form.productos];
    nuevosProductos[idx] = { ...nuevosProductos[idx], [field]: value };
    setForm({ ...form, productos: nuevosProductos });
  };

  const handleAddProducto = () => {
    setForm({ ...form, productos: [...form.productos, { producto_id: '', cantidad: 1 }] });
  };

  const handleRemoveProducto = (idx) => {
    const nuevosProductos = form.productos.filter((_, i) => i !== idx);
    setForm({ ...form, productos: nuevosProductos });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Nueva Factura</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                select
                label="Seleccionar cliente"
                name="cliente_id"
                value={form.cliente_id}
                onChange={handleChange}
                fullWidth
                required
              >
                <MenuItem value="" disabled>Seleccionar cliente</MenuItem>
                <MenuItem value="db">De la base de datos</MenuItem>
                {clientes.map((c) => (
                  <MenuItem key={c.id} value={c.id}>{c.nombre}</MenuItem>
                ))}
                <MenuItem value="nuevo">Nuevo cliente</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <Button onClick={handleAddProducto} variant="outlined" size="small">+ Producto</Button>
            </Grid>
            {form.productos.map((prod, idx) => (
              <Grid container spacing={1} key={idx} alignItems="center" sx={{ mb: 1 }}>
                <Grid item xs={6}>
                  <TextField
                    select
                    label="Producto"
                    value={prod.producto_id}
                    onChange={e => handleProductoChange(idx, 'producto_id', e.target.value)}
                    fullWidth
                    required
                  >
                    {productos.map((p) => (
                      <MenuItem key={p.id} value={p.id}>{p.nombre}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    label="Cantidad"
                    type="number"
                    value={prod.cantidad}
                    onChange={e => handleProductoChange(idx, 'cantidad', e.target.value)}
                    fullWidth
                    required
                  />
                </Grid>
                <Grid item xs={2}>
                  <Button onClick={() => handleRemoveProducto(idx)} color="error" size="small">Eliminar</Button>
                </Grid>
              </Grid>
            ))}
            <Grid item xs={12}>
              <TextField
                label="Fecha"
                name="fecha"
                type="date"
                value={form.fecha}
                onChange={handleChange}
                fullWidth
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancelar</Button>
          <Button type="submit" variant="contained">Guardar</Button>
        </DialogActions>
      </form>
      {openClienteModal && (
        <ClienteFormModal open={openClienteModal} onClose={() => setOpenClienteModal(false)} onSubmit={handleAddCliente} />
      )}
    </Dialog>
  );
}

export default FacturasFormModal;
