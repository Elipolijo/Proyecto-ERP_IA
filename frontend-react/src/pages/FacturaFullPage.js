import React, { useState } from 'react';
import { Box, Typography, Button, Grid, Paper } from '@mui/material';
import FacturasService from '../services/FacturasService';
import ClientesService from '../services/ClientesService';
import ProductosService from '../services/ProductosService';
import CategoriasService from '../services/CategoriasService';
import { useNavigate } from 'react-router-dom';
import ClienteFormModal from '../components/ClienteFormModal';

function FacturaFullPage() {
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [form, setForm] = useState({ cliente_id: '', productos: [], fecha: '', total: '' });
  const [clienteModo, setClienteModo] = useState(''); // "db" o "nuevo"
  const [openClienteModal, setOpenClienteModal] = useState(false);
  const navigate = useNavigate();

  // Estados para descuento e IVA
  const [descuentoPorcentaje, setDescuentoPorcentaje] = useState(0);
  const [ivaPorcentaje, setIvaPorcentaje] = useState(0);

  React.useEffect(() => {
    ClientesService.getAll().then(data => setClientes(data.data || []));
    ProductosService.getAll().then(data => setProductos(data.productos || []));
    CategoriasService.getAll().then(data => setCategorias(data.data || []));
  }, []);

  const handleClienteModoChange = (e) => {
    const value = e.target.value;
    setClienteModo(value);
    if (value === 'nuevo') {
      setOpenClienteModal(true);
    } else {
      setForm({ ...form, cliente_id: '' });
    }
  };

  const handleClienteChange = (e) => {
    setForm({ ...form, cliente_id: e.target.value });
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await FacturasService.create(form);
      navigate('/facturas');
    } catch (err) {
      alert('Error al guardar la factura');
    }
  };

  const handleAddCliente = async (formCliente) => {
    try {
      const res = await ClientesService.create(formCliente);
      setOpenClienteModal(false);
      // Refrescar lista de clientes y seleccionar el nuevo
      const data = await ClientesService.getAll();
      setClientes(data.data || []);
      if (res && res.data && res.data.id) {
        setForm(f => ({ ...f, cliente_id: res.data.id }));
        setClienteModo('db');
      } else {
        setForm(f => ({ ...f, cliente_id: '' }));
      }
    } catch (err) {
      alert('Error al guardar el cliente');
      setForm(f => ({ ...f, cliente_id: '' }));
    }
  };

  // Cálculos de totales
  const subtotal = form.productos.reduce((acc, prod) => {
    let productoObj = productos.find(p => String(p[0] || p.id) === String(prod.producto_id || ''));
    const precio = productoObj
      ? (typeof productoObj === 'object' && !Array.isArray(productoObj)
          ? (productoObj.precio_venta || productoObj.precio || 0)
          : (productoObj[4] || 0))
      : 0;
    const cantidad = Number(prod.cantidad) || 0;
    return acc + (precio * cantidad);
  }, 0);
  const valorDescuento = subtotal * (descuentoPorcentaje / 100);
  const subtotalConDescuento = subtotal - valorDescuento;
  const valorIva = subtotalConDescuento * (ivaPorcentaje / 100);
  const totalPagar = subtotalConDescuento + valorIva;

  return (
    <Box minHeight="100vh" bgcolor="#f7fafc" display="flex" flexDirection="column" alignItems="center" justifyContent="flex-start" p={0} m={0}>
      <Box width="100%" maxWidth={900} mt={4}>
        <Paper sx={{ p: 4, width: '100%' }}>
          <Typography variant="h5" mb={3} fontWeight="bold">Nueva Factura</Typography>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <label style={{ fontWeight: 'bold', marginRight: 8 }}>Seleccionar cliente</label>
                <select value={clienteModo} onChange={handleClienteModoChange} style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', marginTop: 4 }} required>
                  <option value="">Seleccione una opción</option>
                  <option value="db">De la base de datos</option>
                  <option value="nuevo">Nuevo cliente</option>
                </select>
              </Grid>
              {clienteModo === 'db' && (
                <Grid item xs={12} md={6}>
                  <label style={{ fontWeight: 'bold', marginRight: 8 }}>Cliente</label>
                  <select name="cliente_id" value={form.cliente_id} onChange={handleClienteChange} required style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', marginTop: 4 }}>
                    <option value="">Seleccionar cliente</option>
                    {clientes.map((c) => (
                      <option key={c.id} value={c.id}>{c.nombre}</option>
                    ))}
                  </select>
                </Grid>
              )}
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <label>Fecha</label>
                <input type="date" name="fecha" value={form.fecha} onChange={e => setForm({ ...form, fecha: e.target.value })} required style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', marginTop: 4 }} />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" fontWeight="bold" mt={2}>Productos</Typography>
                <Button onClick={handleAddProducto} variant="outlined" size="small" sx={{ ml: 2, mb: 1 }}>+ Producto</Button>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
                  <thead>
                    <tr style={{ background: '#f0f0f0' }}>
                      <th></th>
                      <th>Categoría</th>
                      <th>Producto</th>
                      <th>Stock</th>
                      <th>Cantidad</th>
                      <th>Precio</th>
                      <th>Dscto %</th>
                      <th>Valor Dscto</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {form.productos.map((prod, idx) => {
                      const categoriaSeleccionada = prod.categoria || '';
                      const productosFiltrados = productos.filter(p => p.categoria_id === Number(categoriaSeleccionada));
                      const productoObj = productos.find(p => p.id === prod.producto_id);
                      const stock = productoObj?.stock || 0;
                      const precio = productoObj ? (productoObj[4] || productoObj.precio_venta || 0) : 0;
                      const cantidad = Number(prod.cantidad) || 0;
                      const dsctoPorc = Number(prod.dscto_porc) || 0;
                      const valorDscto = ((precio * cantidad) * dsctoPorc) / 100;
                      const subtotal = (precio * cantidad) - valorDscto;
                      return (
                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ textAlign: 'center' }}>
                            <Button color="error" variant="outlined" size="small" onClick={() => handleRemoveProducto(idx)}>
                              🗑️
                            </Button>
                          </td>
                          <td>
                            <select
                              value={categoriaSeleccionada}
                              onChange={e => {
                                const nuevosProductos = [...form.productos];
                                nuevosProductos[idx] = { ...nuevosProductos[idx], categoria: e.target.value, producto_id: '' };
                                setForm({ ...form, productos: nuevosProductos });
                              }}
                              style={{ maxHeight: 100, overflowY: 'auto' }}
                              required
                            >
                              <option value="">Seleccionar</option>
                              {categorias.map((cat) => (
                                <option key={cat.id} value={cat.nombre}>{cat.nombre}</option>
                              ))}
                            </select>
                          </td>
                          <td>
                            <select
                              value={prod.producto_id || ''}
                              onChange={e => handleProductoChange(idx, 'producto_id', e.target.value)}
                              required
                              disabled={!categoriaSeleccionada}
                            >
                              <option value="">Seleccionar</option>
                              {productos
                                .filter((p) => p[7] === categoriaSeleccionada || p.categoria_nombre === categoriaSeleccionada)
                                .map((p) => (
                                  <option key={p[0] || p.id} value={p[0] || p.id}>{p[1] || p.nombre}</option>
                                ))}
                            </select>
                          </td>
                          <td>
                            {(() => {
                              let productoObj = productos.find(p => String(p[0] || p.id) === String(prod.producto_id || ''));
                              if (productoObj) {
                                if (typeof productoObj === 'object' && !Array.isArray(productoObj)) {
                                  return productoObj.stock_actual || productoObj.stock || 0;
                                } else if (Array.isArray(productoObj)) {
                                  return productoObj[5] || 0;
                                }
                              }
                              return '';
                            })()}
                          </td>
                          <td>
                            <input
                              type="number"
                              min={1}
                              max={(() => {
                                let productoObj = productos.find(p => String(p[0] || p.id) === String(prod.producto_id || ''));
                                if (productoObj) {
                                  if (typeof productoObj === 'object' && !Array.isArray(productoObj)) {
                                    return productoObj.stock_actual || productoObj.stock || 1;
                                  } else if (Array.isArray(productoObj)) {
                                    return productoObj[5] || 1;
                                  }
                                }
                                return 1;
                              })()}
                              value={prod.cantidad || ''}
                              onChange={e => {
                                const max = (() => {
                                  let productoObj = productos.find(p => String(p[0] || p.id) === String(prod.producto_id || ''));
                                  if (productoObj) {
                                    if (typeof productoObj === 'object' && !Array.isArray(productoObj)) {
                                      return productoObj.stock_actual || productoObj.stock || 1;
                                    } else if (Array.isArray(productoObj)) {
                                      return productoObj[5] || 1;
                                    }
                                  }
                                  return 1;
                                })();
                                let value = Number(e.target.value);
                                if (value > max) value = max;
                                handleProductoChange(idx, 'cantidad', value);
                              }}
                              style={{ width: 60 }}
                              required
                            />
                          </td>
                          <td>
                            {(() => {
                              let productoObj = productos.find(p => String(p[0] || p.id) === String(prod.producto_id || ''));
                              if (productoObj) {
                                if (typeof productoObj === 'object' && !Array.isArray(productoObj)) {
                                  return productoObj.precio_venta ? Number(productoObj.precio_venta).toFixed(2) : '';
                                } else if (Array.isArray(productoObj)) {
                                  return productoObj[4] ? Number(productoObj[4]).toFixed(2) : '';
                                }
                              }
                              return '';
                            })()}
                          </td>
                          <td>
                            <input type="number" min={0} max={100} value={prod.dscto_porc || ''} onChange={e => handleProductoChange(idx, 'dscto_porc', e.target.value)} style={{ width: 60 }} />
                          </td>
                          <td>{valorDscto.toFixed(2)}</td>
                          <td>{(precio * cantidad).toFixed(2)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </Grid>
              {/* Tabla de totales y descuentos */}
              <Grid item xs={12}>
                <table style={{ width: '350px', margin: '24px 0', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 'bold', padding: '6px 12px' }}>SUBTOTAL</td>
                      <td style={{ textAlign: 'right', padding: '6px 12px' }}>{subtotal.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 'bold', padding: '6px 12px' }}>DESCUENTO %</td>
                      <td style={{ textAlign: 'right', padding: '6px 12px' }}>
                        <input
                          type="number"
                          min={0}
                          max={100}
                          value={descuentoPorcentaje}
                          onChange={e => setDescuentoPorcentaje(Number(e.target.value))}
                          style={{ width: 60 }}
                        /> %
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 'bold', padding: '6px 12px' }}>VALOR DESCUENTO</td>
                      <td style={{ textAlign: 'right', padding: '6px 12px' }}>{valorDescuento.toFixed(2)}</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 'bold', padding: '6px 12px' }}>IVA %</td>
                      <td style={{ textAlign: 'right', padding: '6px 12px' }}>
                        <input
                          type="number"
                          min={0}
                          max={100}
                          value={ivaPorcentaje}
                          onChange={e => setIvaPorcentaje(Number(e.target.value))}
                          style={{ width: 60 }}
                        /> %
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 'bold', padding: '6px 12px' }}>TOTAL A PAGAR</td>
                      <td style={{ textAlign: 'right', padding: '6px 12px', fontWeight: 'bold', color: '#059669' }}>
                        {totalPagar.toFixed(2)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </Grid>
              <Grid item xs={12}>
                <Button type="submit" variant="contained" color="primary">Guardar Factura</Button>
                <Button sx={{ ml: 2 }} variant="outlined" color="secondary" onClick={() => navigate('/facturas')}>Cancelar</Button>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
      <ClienteFormModal open={openClienteModal} onClose={() => setOpenClienteModal(false)} onSubmit={handleAddCliente} />
    </Box>
  );
}

export default FacturaFullPage;
