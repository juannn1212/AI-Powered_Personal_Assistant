import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { API_BASE_URL } from '../config/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('auth_token');
      const storedUser = await AsyncStorage.getItem('user_data');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en el inicio de sesión');
      }

      const { access_token, user: userData } = data;
      
      // Guardar en AsyncStorage
      await AsyncStorage.setItem('auth_token', access_token);
      await AsyncStorage.setItem('user_data', JSON.stringify(userData));
      
      // Actualizar estado
      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Error', error.message || 'Error en el inicio de sesión');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password, fullName) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en el registro');
      }

      const { access_token, user: userData } = data;
      
      // Guardar en AsyncStorage
      await AsyncStorage.setItem('auth_token', access_token);
      await AsyncStorage.setItem('user_data', JSON.stringify(userData));
      
      // Actualizar estado
      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      console.error('Register error:', error);
      Alert.alert('Error', error.message || 'Error en el registro');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const handleSessionExpired = async () => {
    console.log('🔐 Manejando expiración de sesión...');
    
    // Limpiar datos de sesión
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user_data');
    
    // Actualizar estado
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    
    // Mostrar alerta
    Alert.alert(
      'Sesión Expirada',
      'Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.',
      [
        {
          text: 'OK',
          onPress: () => {
            // La navegación se manejará automáticamente por el estado de autenticación
          }
        }
      ]
    );
  };

  const logout = async () => {
    try {
      console.log('🔄 Iniciando logout...');
      setLoading(true);
      
      // Llamar al endpoint de logout del backend si hay token
      if (token) {
        console.log('🌐 Llamando al endpoint de logout...');
        try {
          const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            console.log('✅ Endpoint de logout exitoso');
          } else {
            console.log('⚠️ Endpoint de logout falló, pero continuando...');
          }
        } catch (error) {
          console.log('⚠️ Error en endpoint de logout, pero continuando...');
        }
      }
      
      // Limpiar AsyncStorage
      console.log('🗑️ Limpiando AsyncStorage...');
      await AsyncStorage.removeItem('auth_token');
      await AsyncStorage.removeItem('user_data');
      console.log('✅ AsyncStorage limpiado');
      
      // Limpiar estado de forma síncrona
      console.log('🔄 Limpiando estado...');
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      console.log('✅ Estado limpiado');
      
      // Forzar actualización del estado
      console.log('🔄 Forzando actualización...');
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('✅ Logout completado exitosamente');
      console.log('📊 Estado final - isAuthenticated:', false);
      console.log('📊 Estado final - user:', null);
      console.log('📊 Estado final - token:', null);
      
      return { success: true };
    } catch (error) {
      console.error('❌ Logout error:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setLoading(true);
      
      console.log('Actualizando perfil con datos:', profileData);
      console.log('Token:', token);
      
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        throw new Error(data.detail || 'Error al actualizar perfil');
      }

      // Actualizar usuario en estado y AsyncStorage
      const updatedUser = { ...user, ...data };
      setUser(updatedUser);
      await AsyncStorage.setItem('user_data', JSON.stringify(updatedUser));
      
      console.log('Perfil actualizado exitosamente:', updatedUser);
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Update profile error:', error);
      Alert.alert('Error', error.message || 'Error al actualizar perfil');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al cambiar contraseña');
      }

      return { success: true };
    } catch (error) {
      console.error('Change password error:', error);
      Alert.alert('Error', error.message || 'Error al cambiar contraseña');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async (email) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al procesar solicitud');
      }

      return { success: true };
    } catch (error) {
      console.error('Forgot password error:', error);
      Alert.alert('Error', error.message || 'Error al procesar solicitud');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email, newPassword) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, new_password: newPassword }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al restablecer contraseña');
      }

      return { success: true };
    } catch (error) {
      console.error('Reset password error:', error);
      Alert.alert('Error', error.message || 'Error al restablecer contraseña');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteAccount = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al eliminar cuenta');
      }

      // Limpiar datos
      await logout();
      
      return { success: true };
    } catch (error) {
      console.error('Delete account error:', error);
      Alert.alert('Error', error.message || 'Error al eliminar cuenta');
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    deleteAccount,
    handleSessionExpired,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
