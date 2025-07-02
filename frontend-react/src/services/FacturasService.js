import axios from 'axios';

const API_URL = 'http://localhost:5000';

const FacturasService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/facturas`);
      return res.data;
    } catch (err) {
      return { data: [] };
    }
  },
  create: async (factura) => {
    try {
      const res = await axios.post(`${API_URL}/facturas`, factura);
      return res.data;
    } catch (err) {
      throw err;
    }
  }
};

export default FacturasService;
