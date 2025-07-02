import axios from 'axios';

const API_URL = 'http://localhost:5000';

const ClientesService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/clientes`);
      return res.data;
    } catch (err) {
      return { data: [] };
    }
  },
  create: async (cliente) => {
    try {
      const res = await axios.post(`${API_URL}/clientes`, cliente);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default ClientesService;
