import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, MenuItem, Grid } from '@mui/material';
import ProductosService from '../services/ProductosService';
import ProveedoresService from '../services/ProveedoresService';

function EntradaStockFormModal({ open, onClose, onSubmit, initialData }) {
  const [form, setForm] = useState({
    producto: '',
    cantidad: '',
    proveedor: '',
    precio_compra: '',
    precio_venta: '',
    observacion: ''
  });
  const [productos, setProductos] = useState([]);
  const [proveedores, setProveedores] = useState([]);

  useEffect(() => {
    if (open) {
      ProductosService.getAll().then(data => setProductos(data.productos || []));
      ProveedoresService.getAll().then(data => setProveedores(data.data || []));
      if (initialData) {
        setForm({
          producto: initialData.producto || initialData.producto_id || '',
          cantidad: initialData.cantidad || '',
          proveedor: initialData.proveedor || initialData.proveedor_id || '',
          precio_compra: initialData.precio_compra || '',
          precio_venta: initialData.precio_venta || '',
          observacion: initialData.observacion || ''
        });
      }
    } else if (!open) {
      setForm({
        producto: '',
        cantidad: '',
        proveedor: '',
        precio_compra: '',
        precio_venta: '',
        observacion: ''
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
      <DialogTitle>{initialData ? 'Editar Entrada de Stock' : 'Nueva Entrada de Stock'}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField select label="Producto" name="producto" value={form.producto} onChange={handleChange} fullWidth required>
                <MenuItem value="">Seleccionar</MenuItem>
                {productos.map((prod) => (
                  <MenuItem key={prod[0]} value={prod[0]}>{prod[1]}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField select label="Proveedor" name="proveedor" value={form.proveedor} onChange={handleChange} fullWidth required>
                <MenuItem value="">Seleccionar</MenuItem>
                {proveedores.map((prov) => (
                  <MenuItem key={prov.id} value={prov.id}>{prov.nombre}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Cantidad" name="cantidad" value={form.cantidad} onChange={handleChange} type="number" fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Precio Compra" name="precio_compra" value={form.precio_compra} onChange={handleChange} type="number" fullWidth required />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Precio Venta" name="precio_venta" value={form.precio_venta} onChange={handleChange} type="number" fullWidth />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Observación" name="observacion" value={form.observacion} onChange={handleChange} fullWidth />
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

export default EntradaStockFormModal;
