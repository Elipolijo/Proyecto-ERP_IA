import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Grid } from '@mui/material';

function CategoriaFormModal({ open, onClose, onSubmit, initialData }) {
  const [form, setForm] = useState({ nombre: '', descripcion: '' });

  useEffect(() => {
    if (open && initialData) {
      setForm({
        nombre: initialData.nombre || '',
        descripcion: initialData.descripcion || ''
      });
    } else if (!open) {
      setForm({ nombre: '', descripcion: '' });
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
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{initialData ? 'Editar Categoría' : 'Nueva Categoría'}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField label="Nombre" name="nombre" value={form.nombre} onChange={handleChange} fullWidth required />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Descripción" name="descripcion" value={form.descripcion} onChange={handleChange} fullWidth />
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

export default CategoriaFormModal;
