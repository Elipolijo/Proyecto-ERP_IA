import axios from 'axios';

const API_URL = 'http://localhost:5000';

const EntradaStockService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/entradas-stock`); // Cambiado a guion para coincidir con el backend
      return res.data;
    } catch (err) {
      return { entradas: [] };
    }
  },
  create: async (entrada) => {
    try {
      const res = await axios.post(`${API_URL}/entradas-stock`, entrada);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  update: async (id, entrada) => {
    try {
      const res = await axios.put(`${API_URL}/entradas-stock/${id}`, entrada);
      return res.data;
    } catch (err) {
      throw err;
    }
  },
  delete: async (id) => {
    try {
      const res = await axios.delete(`${API_URL}/entradas-stock/${id}`);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default EntradaStockService;
