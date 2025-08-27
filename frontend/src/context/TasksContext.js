import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { API_BASE_URL } from '../config/api';
import { useAuth } from './AuthContext';

const TasksContext = createContext();

export const useTasks = () => {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error('useTasks must be used within a TasksProvider');
  }
  return context;
};

export const TasksProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(false);
  const { token, user, handleSessionExpired } = useAuth();

  // Cargar tareas y hábitos al iniciar
  useEffect(() => {
    if (token && user) {
      loadTasks();
      loadHabits();
    }
  }, [token, user]);

  const getAuthHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  });

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data);
        // Guardar en AsyncStorage para persistencia
        await AsyncStorage.setItem('tasks_data', JSON.stringify(data));
      } else {
        console.error('Error loading tasks:', response.status);
        
        // Manejar error de autenticación
        if (response.status === 401) {
          console.log('Sesión expirada al cargar tareas');
          // No mostrar error aquí, solo log para evitar spam
        }
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
      
      // Manejar error de autenticación
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        console.log('Sesión expirada al cargar tareas');
        // No mostrar error aquí, solo log para evitar spam
      }
    } finally {
      setLoading(false);
    }
  };

  const loadHabits = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/habits`, {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setHabits(data);
        // Guardar en AsyncStorage para persistencia
        await AsyncStorage.setItem('habits_data', JSON.stringify(data));
      } else {
        console.error('Error loading habits:', response.status);
        
        // Manejar error de autenticación
        if (response.status === 401) {
          console.log('Sesión expirada al cargar hábitos');
          // No mostrar error aquí, solo log para evitar spam
        }
      }
    } catch (error) {
      console.error('Error loading habits:', error);
      
      // Manejar error de autenticación
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        console.log('Sesión expirada al cargar hábitos');
        // No mostrar error aquí, solo log para evitar spam
      }
    } finally {
      setLoading(false);
    }
  };

  const addTask = async (taskData) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(taskData)
      });

      if (response.ok) {
        const newTask = await response.json();
        setTasks(prevTasks => [...prevTasks, newTask]);
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('tasks_data', JSON.stringify([...tasks, newTask]));
        return { success: true, task: newTask };
      } else {
        const error = await response.json();
        
        // Manejar error de autenticación
        if (response.status === 401) {
          console.log('Sesión expirada al crear tarea');
          await handleSessionExpired();
          throw new Error('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
        }
        
        throw new Error(error.detail || 'Error al crear la tarea');
      }
    } catch (error) {
      console.error('Error adding task:', error);
      
      // Manejar error de autenticación
      if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('sesión ha expirado')) {
        // Ya se manejó con handleSessionExpired
        return { success: false, error: error.message };
      } else {
        Alert.alert('Error', error.message);
      }
      
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const addHabit = async (habitData) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/habits`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(habitData)
      });

      if (response.ok) {
        const newHabit = await response.json();
        setHabits(prevHabits => [...prevHabits, newHabit]);
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('habits_data', JSON.stringify([...habits, newHabit]));
        return { success: true, habit: newHabit };
      } else {
        const error = await response.json();
        
        // Manejar error de autenticación
        if (response.status === 401) {
          console.log('Sesión expirada al crear hábito');
          await handleSessionExpired();
          throw new Error('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
        }
        
        throw new Error(error.detail || 'Error al crear el hábito');
      }
    } catch (error) {
      console.error('Error adding habit:', error);
      
      // Manejar error de autenticación
      if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('sesión ha expirado')) {
        // Ya se manejó con handleSessionExpired
        return { success: false, error: error.message };
      } else {
        Alert.alert('Error', error.message);
      }
      
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId ? updatedTask : task
          )
        );
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('tasks_data', JSON.stringify(tasks.map(task => 
          task.id === taskId ? updatedTask : task
        )));
        return { success: true, task: updatedTask };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error al actualizar la tarea');
      }
    } catch (error) {
      console.error('Error updating task:', error);
      Alert.alert('Error', error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const updateHabit = async (habitId, updates) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/habits/${habitId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        const updatedHabit = await response.json();
        setHabits(prevHabits => 
          prevHabits.map(habit => 
            habit.id === habitId ? updatedHabit : habit
          )
        );
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('habits_data', JSON.stringify(habits.map(habit => 
          habit.id === habitId ? updatedHabit : habit
        )));
        return { success: true, habit: updatedHabit };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error al actualizar el hábito');
      }
    } catch (error) {
      console.error('Error updating habit:', error);
      Alert.alert('Error', error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (response.ok) {
        setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('tasks_data', JSON.stringify(tasks.filter(task => task.id !== taskId)));
        return { success: true };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error al eliminar la tarea');
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      Alert.alert('Error', error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteHabit = async (habitId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/habits/${habitId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (response.ok) {
        setHabits(prevHabits => prevHabits.filter(habit => habit.id !== habitId));
        // Actualizar AsyncStorage
        await AsyncStorage.setItem('habits_data', JSON.stringify(habits.filter(habit => habit.id !== habitId)));
        return { success: true };
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error al eliminar el hábito');
      }
    } catch (error) {
      console.error('Error deleting habit:', error);
      Alert.alert('Error', error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    await loadTasks();
    await loadHabits();
  };

  const value = {
    tasks,
    habits,
    loading,
    addTask,
    addHabit,
    updateTask,
    updateHabit,
    deleteTask,
    deleteHabit,
    refreshData,
    loadTasks,
    loadHabits
  };

  return (
    <TasksContext.Provider value={value}>
      {children}
    </TasksContext.Provider>
  );
};
