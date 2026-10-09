import axios from 'axios';

//axios.creat builds a reusable pre-configured client
const apiClient = axios.create({
    // FastAPI endpoint
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
});

export const tokenStore = {
    getAccess: () => localStorage.getItem("accessToken"),
    getRefresh: () => localStorage.getItem("refreshToken"),
    set: ({access_token, refresh_token}) => {
        localStorage.setItem("accessToken", access_token);
        localStorage.setItem("refreshToken", refresh_token);
    },
    clear: () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
    },
};

// Lets AuthContext react when the session dies
let onSessionExpired = () => {};
let onTokensRefreshed = () => {};
export const setSessionExpiredHandler = (fn) => { onSessionExpired = fn; };
export const setTokensRefreshedHandler = (fn) => { onTokensRefreshed = fn; };

// bare instance for /refresh: no interceptors so a failing refresh can't loop
const refreshClient = axios.create({baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'})



apiClient.interceptors.request.use((config) => {
    //const token = localStorage.getItem('accessToken');
    const token = tokenStore.getAccess();
    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

let refreshPromise = null; // shared by all requests that fail at the same time

function refreshTokens() {
    if (!refreshPromise) {
        const refresh_token = tokenStore.getRefresh();
        refreshPromise = refreshClient
            .post("/auth/refresh", {refresh_token})
            .then((res) => {
                tokenStore.set(res.data);
                onTokensRefreshed(res.data.access_token);
                return res.data.access_token;
            })
            .finally(() => { refreshPromise = null; });
    }
    return refreshPromise;
}

apiClient.interceptors.response.use(
    (res) => res,
    async (error) => {
        const original = error.config;
        /** NOTE: check this later */
        const expired = 
            error.response?.status === 401 &&
            error.response?.data.detail === "Token expired";

        if(!expired || original._retry){
            return Promise.reject(error);
        }
        if (!tokenStore.getRefresh()){
            tokenStore.clear();
            onSessionExpired();
            return Promise.reject(error);
        }

        original._retry = true;
        try {
            const newAccess = await refreshTokens();
            original.headers.Authorization = `Bearer ${newAccess}`;
            return apiClient(original);
        } catch (refreshError) {
            tokenStore.clear();
            onSessionExpired();
            return Promise.reject(refreshError);
        }
    }
);

export default apiClient;