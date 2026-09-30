import {createContext, useContext, useMemo, useState} from 'react';
import apiClient from "../api/client";

// global auth state using react's context api

const AuthContext = createContext(null);

function decodeToken(token){
    const payloadSegment = token.split('.')[1];
    return JSON.parse(atob(payloadSegment));
    // atob = ascii to binary
}

export function AuthProvider({children}) {
    const [token, setToken] = useState(() => localStorage.getItem('medToken'));
    
    const user = useMemo(() => (token ? decodeToken(token): null), [token]);

    const login = async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiClient.post('/auth/token', formData, {
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        });
        localStorage.setItem('medToken', response.data.access_token);
        setToken(response.data.access_token);
    }

    const logout = () => {
        localStorage.removeItem('medToken');
        setToken(null);
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