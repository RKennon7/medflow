import axios from 'axios';

//axios.creat builds a reusable pre-configured client
const apiClient = axios.create({
    // FastAPI endpoint
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('medToken');
    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default apiClient;