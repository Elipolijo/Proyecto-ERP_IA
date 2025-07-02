import axios from 'axios';

const API_URL = 'http://localhost:5000';

const DemandaHistoricaService = {
  getAll: async () => {
    try {
      const res = await axios.get(`${API_URL}/demanda-historica`);
      return res.data;
    } catch (err) {
      return { data: [] };
    }
  }
};

export default DemandaHistoricaService;
