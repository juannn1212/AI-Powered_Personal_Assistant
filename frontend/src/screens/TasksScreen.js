import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/theme';

const TasksScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Gestión de Tareas</Text>
      <Text style={styles.subtitle}>Pantalla en desarrollo</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  subtitle: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
});

export default TasksScreen;
