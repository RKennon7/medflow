import {createContext, useContext, useEffect, useMemo, useState} from 'react';
import { tokenStore, setSessionExpiredHandler, setTokensRefreshedHandler } from "../api/client";
import apiClient from "../api/client";

// global auth state using react's context api

const AuthContext = createContext(null);

function decodeToken(token){
    const payloadSegment = token.split('.')[1];
    return JSON.parse(atob(payloadSegment));
    // atob = ascii to binary
}

export function AuthProvider({children}) {
    const [token, setToken] = useState(() => tokenStore.getAccess());
    
    const user = useMemo(() => (token ? decodeToken(token): null), [token]);

    // let axios interceptor update React state
    useEffect(() => {
        setTokensRefreshedHandler((newAccess) => setToken(newAccess));
        setSessionExpiredHandler(() => setToken(null));
    }, []);

    const login = async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiClient.post('/auth/token', formData, {
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        });

        tokenStore.set(response.data);
        setToken(response.data.access_token);
    };

    const logout = async () => {
        const refreshToken = tokenStore.getRefresh();
        tokenStore.clear();
        setToken(null);
        if(refreshToken) {
            try {
                await apiClient.post('/auth/logout', { refresh_token: refreshToken });
            } catch {
                /** already logged out locally -> ignore */
            }
        }
    };

    // bundles auth state vars and action function into a single obj
    const value = {token, user, isAuthenticated: Boolean(token), login, logout};

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === null){
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context;
}