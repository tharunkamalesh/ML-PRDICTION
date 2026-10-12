import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  apiGetCurrentUser,
  apiLogin,
  apiRegister,
  apiLogout,
  apiUpdateProfile,
  apiDeleteAccount
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Initial session hydration on app mount
  const checkAuthStatus = useCallback(async () => {
    try {
      setLoadingAuth(true);
      const res = await apiGetCurrentUser();
      if (res && res.authenticated && res.user) {
        setUser(res.user);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.warn('Auth check failed:', err);
      setUser(null);
    } finally {
      setLoadingAuth(false);
    }
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Login handler
  const login = async (email, password) => {
    setAuthError(null);
    try {
      const res = await apiLogin(email, password);
      if (res.user) {
        setUser(res.user);
        return res.user;
      }
      throw new Error('User data not received');
    } catch (err) {
      setAuthError(err.message || 'Login failed');
      throw err;
    }
  };

  // Register handler
  const register = async (fullName, email, password) => {
    setAuthError(null);
    try {
      const res = await apiRegister(fullName, email, password);
      if (res.user) {
        setUser(res.user);
        return res.user;
      }
      throw new Error('Registration succeeded but session could not be established');
    } catch (err) {
      setAuthError(err.message || 'Registration failed');
      throw err;
    }
  };

  // Logout handler
  const logout = async () => {
    try {
      await apiLogout();
    } catch (err) {
      console.warn('Logout error:', err);
    } finally {
      setUser(null);
      setAuthError(null);
    }
  };

  // Profile update handler
  const updateProfile = async (payload) => {
    const res = await apiUpdateProfile(payload);
    if (res.user) {
      setUser(res.user);
    }
    return res;
  };

  // Delete account handler
  const deleteAccount = async (password) => {
    await apiDeleteAccount(password);
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: Boolean(user),
    isAdmin: user?.role === 'admin',
    loadingAuth,
    authError,
    login,
    register,
    logout,
    updateProfile,
    deleteAccount,
    refreshUser: checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
