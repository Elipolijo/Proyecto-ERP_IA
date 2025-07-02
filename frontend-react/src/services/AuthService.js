import axios from 'axios';

const API_URL = 'http://localhost:5000'; // Cambia el puerto si tu backend usa otro

const AuthService = {
  login: async (nombre, password) => {
    try {
      const res = await axios.post(`${API_URL}/login`, { nombre, password });
      return res.data;
    } catch (err) {
      return { success: false, message: 'Error de red o servidor' };
    }
  }
};

export default AuthService;
