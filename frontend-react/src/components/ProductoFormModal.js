import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, MenuItem, Grid } from '@mui/material';

function ProductoFormModal({ open, onClose, onSubmit, categorias, proveedores, initialData }) {
  const [form, setForm] = useState({
    nombre: '',
    descripcion: '',
    precio_compra: '',
    precio_venta: '',
    stock: '',
    stock_minimo: '',
    categoria: '',
    proveedor: ''
  });

  useEffect(() => {
    if (open && initialData) {
      setForm({
        nombre: initialData[1] || '',
        descripcion: initialData[2] || '',
        precio_compra: initialData[3] || '',
        precio_venta: initialData[4] || '',
        stock: initialData[5] || '',
        stock_minimo: initialData[6] || '',
        categoria: initialData[7] || '',
        proveedor: initialData[8] || ''
      });
    } else if (!open) {
      setForm({
        nombre: '',
        descripcion: '',
        precio_compra: '',
        precio_venta: '',
        stock: '',
        stock_minimo: '',
        categoria: '',
        proveedor: ''
      });
    }
  }, [open, initialData]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{initialData ? 'Editar Producto' : 'Nuevo Producto'}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField label="Nombre" name="nombre" value={form.nombre} onChange={handleChange} fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Descripción" name="descripcion" value={form.descripcion} onChange={handleChange} fullWidth />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Precio Compra" name="precio_compra" value={form.precio_compra} onChange={handleChange} type="number" fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Precio Venta" name="precio_venta" value={form.precio_venta} onChange={handleChange} type="number" fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Stock" name="stock" value={form.stock} onChange={handleChange} type="number" fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Stock Mínimo" name="stock_minimo" value={form.stock_minimo} onChange={handleChange} type="number" fullWidth />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField select label="Categoría" name="categoria" value={form.categoria} onChange={handleChange} fullWidth required>
                <MenuItem value="">Seleccionar</MenuItem>
                {categorias.map((cat) => (
                  <MenuItem key={cat.id} value={cat.nombre}>{cat.nombre}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField select label="Proveedor" name="proveedor" value={form.proveedor} onChange={handleChange} fullWidth required>
                <MenuItem value="">Seleccionar</MenuItem>
                {proveedores.map((prov) => (
                  <MenuItem key={prov.id} value={prov.nombre}>{prov.nombre}</MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancelar</Button>
          <Button type="submit" variant="contained">Guardar</Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default ProductoFormModal;
