import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/context/AuthContext';
import { TasksProvider } from './src/context/TasksContext';
import { ThemeProvider } from './src/context/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthProvider>
          <TasksProvider>
            <AppNavigator />
            <StatusBar style="auto" />
          </TasksProvider>
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
