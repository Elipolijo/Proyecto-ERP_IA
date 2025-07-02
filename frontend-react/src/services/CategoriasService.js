import axios from 'axios';

const API_URL = 'http://localhost:5000';

const CategoriasService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/categorias`);
      return res.data;
    } catch (err) {
      return { data: [] };
    }
  },
  create: async (categoria) => {
    try {
      const res = await axios.post(`${API_URL}/categorias`, categoria);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  update: async (id, categoria) => {
    try {
      const res = await axios.put(`${API_URL}/categorias/${id}`, categoria);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  delete: async (id) => {
    try {
      const res = await axios.delete(`${API_URL}/categorias/${id}`);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default CategoriasService;
