import axios from 'axios';

const API_URL = 'http://localhost:5000';

const ProductosService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/productos`);
      return res.data;
    } catch (err) {
      return { productos: [] };
    }
  },
  create: async (producto) => {
    try {
      const res = await axios.post(`${API_URL}/productos`, producto);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  update: async (id, producto) => {
    try {
      const res = await axios.put(`${API_URL}/productos/${id}`, producto);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  delete: async (id) => {
    try {
      const res = await axios.delete(`${API_URL}/productos/${id}`);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default ProductosService;
