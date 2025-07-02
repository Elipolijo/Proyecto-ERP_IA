import axios from 'axios';

const API_URL = 'http://localhost:5000';

const ProveedoresService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/proveedores`);
      return res.data;
    } catch (err) {
      return { data: [] };
    }
  },
  create: async (proveedor) => {
    try {
      const res = await axios.post(`${API_URL}/proveedores`, proveedor);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default ProveedoresService;
