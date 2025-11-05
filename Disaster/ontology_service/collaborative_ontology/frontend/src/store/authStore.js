import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (credentials) => {
        try {
          const formData = new FormData();
          formData.append('username', credentials.email);
          formData.append('password', credentials.password);
          
          const response = await axios.post(`${API_URL}/auth/login`, formData);
          const { access_token, user } = response.data;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
          });
          
          // Set default auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          return { success: true };
        } catch (error) {
          return {
            success: false,
            error: error.response?.data?.detail || '로그인 실패',
          };
        }
      },
      
      register: async (userData) => {
        try {
          const response = await axios.post(`${API_URL}/auth/register`, userData);
          const { access_token, user } = response.data;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
          });
          
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          return { success: true };
        } catch (error) {
          return {
            success: false,
            error: error.response?.data?.detail || '회원가입 실패',
          };
        }
      },
      
      logout: async () => {
        try {
          await axios.post(`${API_URL}/auth/logout`);
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
          delete axios.defaults.headers.common['Authorization'];
        }
      },
      
      fetchUser: async () => {
        try {
          const token = get().token;
          if (!token) return;
          
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get(`${API_URL}/auth/me`);
          
          set({ user: response.data });
        } catch (error) {
          console.error('Fetch user error:', error);
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);

// Initialize axios interceptor
useAuthStore.subscribe((state) => {
  if (state.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
  }
});
