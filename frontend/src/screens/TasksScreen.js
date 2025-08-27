import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
  ScrollView,
  Platform,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { useTasks } from '../context/TasksContext';
import { Ionicons } from '@expo/vector-icons';
import { API_BASE_URL, getAuthHeaders } from '../config/api';

const TasksScreen = () => {
  const { theme } = useTheme();
  const { user, token } = useAuth();
  const { tasks, loading, addTask, updateTask, deleteTask, loadTasks } = useTasks();
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    pending: 0,
    in_progress: 0,
  });

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: '',
    due_date: '',
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/stats/summary`, {
        headers: getAuthHeaders(token),
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleAddTask = async () => {
    if (!newTask.title.trim()) {
      Alert.alert('Error', 'El título de la tarea es requerido');
      return;
    }

    try {
      const result = await addTask({
        title: newTask.title.trim(),
        description: newTask.description.trim(),
        priority: newTask.priority,
        category: newTask.category.trim(),
        due_date: newTask.due_date || null,
      });

      if (result.success) {
        setShowAddModal(false);
        setNewTask({ title: '', description: '', priority: 'medium', category: '', due_date: '' });
        loadStats();
        Alert.alert('Éxito', 'Tarea creada correctamente');
      }
    } catch (error) {
      console.error('Error creating task:', error);
      Alert.alert('Error', 'No se pudo crear la tarea');
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      const result = await updateTask(taskId, { 
        status: newStatus,
        completed_at: newStatus === 'completed' ? new Date().toISOString() : null
      });
      
      if (result.success) {
        loadStats();
      }
    } catch (error) {
      console.error('Error updating task:', error);
      Alert.alert('Error', 'No se pudo actualizar la tarea');
    }
  };

  const handleDeleteTask = async (taskId) => {
    Alert.alert(
      'Eliminar tarea',
      '¿Estás seguro de que quieres eliminar esta tarea?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            try {
              const result = await deleteTask(taskId);
              if (result.success) {
                loadStats();
                Alert.alert('Éxito', 'Tarea eliminada correctamente');
              }
            } catch (error) {
              console.error('Error deleting task:', error);
              Alert.alert('Error', 'No se pudo eliminar la tarea');
            }
          },
        },
      ]
    );
  };

  const getFilteredTasks = () => {
    switch (selectedFilter) {
      case 'pending':
        return tasks.filter(task => task.status === 'pending');
      case 'in_progress':
        return tasks.filter(task => task.status === 'in_progress');
      case 'completed':
        return tasks.filter(task => task.status === 'completed');
      default:
        return tasks;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return theme.colors.error;
      case 'medium':
        return theme.colors.warning;
      case 'low':
        return theme.colors.success;
      default:
        return theme.colors.textSecondary;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return theme.colors.success;
      case 'in_progress':
        return theme.colors.primary;
      case 'pending':
        return theme.colors.warning;
      default:
        return theme.colors.textSecondary;
    }
  };

  const renderTask = ({ item }) => (
    <View style={[styles.taskCard, { backgroundColor: theme.colors.surface }]}>
      <View style={styles.taskHeader}>
        <View style={styles.taskTitleContainer}>
          <TouchableOpacity
            style={[styles.checkbox, { borderColor: theme.colors.border }]}
            onPress={() => updateTaskStatus(item.id, item.status === 'completed' ? 'pending' : 'completed')}
          >
            {item.status === 'completed' && (
              <Ionicons name="checkmark" size={16} color={theme.colors.primary} />
            )}
          </TouchableOpacity>
          <Text style={[
            styles.taskTitle,
            { color: theme.colors.text },
            item.status === 'completed' && styles.completedTask
          ]}>
            {item.title}
          </Text>
        </View>
        
        <View style={styles.taskActions}>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) + '20' }]}>
            <Text style={[styles.priorityText, { color: getPriorityColor(item.priority) }]}>
              {item.priority}
            </Text>
          </View>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => handleDeleteTask(item.id)}
          >
            <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
          </TouchableOpacity>
        </View>
      </View>

      {item.description && (
        <Text style={[styles.taskDescription, { color: theme.colors.textSecondary }]}>
          {item.description}
        </Text>
      )}

      <View style={styles.taskFooter}>
        {item.category && (
          <View style={[styles.categoryBadge, { backgroundColor: theme.colors.backgroundSecondary }]}>
            <Text style={[styles.categoryText, { color: theme.colors.textSecondary }]}>
              {item.category}
            </Text>
          </View>
        )}
        
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
          <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
            {item.status === 'completed' ? 'Completada' : 
             item.status === 'in_progress' ? 'En progreso' : 'Pendiente'}
          </Text>
        </View>
      </View>

      {item.due_date && (
        <View style={styles.dueDateContainer}>
          <Ionicons name="calendar-outline" size={14} color={theme.colors.textTertiary} />
          <Text style={[styles.dueDateText, { color: theme.colors.textTertiary }]}>
            {new Date(item.due_date).toLocaleDateString()}
          </Text>
        </View>
      )}
    </View>
  );

  const FilterButton = ({ title, filter, count }) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        {
          backgroundColor: selectedFilter === filter ? theme.colors.primary : theme.colors.surface,
          borderColor: theme.colors.border,
        }
      ]}
      onPress={() => setSelectedFilter(filter)}
    >
      <Text style={[
        styles.filterButtonText,
        { color: selectedFilter === filter ? theme.colors.textInverse : theme.colors.text }
      ]}>
        {title} ({count})
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <Text style={[styles.headerTitle, { color: theme.colors.text }]}>
          Mis Tareas
        </Text>
        <TouchableOpacity
          style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
          onPress={() => setShowAddModal(true)}
        >
          <Ionicons name="add" size={24} color={theme.colors.textInverse} />
        </TouchableOpacity>
      </View>

      {/* Stats */}
      <View style={[styles.statsContainer, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
            {stats.total}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Total
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.success }]}>
            {stats.completed}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Completadas
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.warning }]}>
            {stats.pending}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Pendientes
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
            {stats.in_progress}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            En progreso
          </Text>
        </View>
      </View>

      {/* Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filtersContainer}
        contentContainerStyle={styles.filtersContent}
      >
        <FilterButton title="Todas" filter="all" count={stats.total} />
        <FilterButton title="Pendientes" filter="pending" count={stats.pending} />
        <FilterButton title="En progreso" filter="in_progress" count={stats.in_progress} />
        <FilterButton title="Completadas" filter="completed" count={stats.completed} />
      </ScrollView>

      {/* Tasks List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>
            Cargando tareas...
          </Text>
        </View>
      ) : (
        <FlatList
          data={getFilteredTasks()}
          renderItem={renderTask}
          keyExtractor={(item) => item?.id?.toString() || Math.random().toString()}
          style={styles.tasksList}
          contentContainerStyle={styles.tasksContainer}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="checkmark-circle-outline" size={64} color={theme.colors.textTertiary} />
              <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
                No hay tareas {selectedFilter !== 'all' ? `en ${selectedFilter}` : ''}
              </Text>
              <TouchableOpacity
                style={[styles.emptyButton, { backgroundColor: theme.colors.primary }]}
                onPress={() => setShowAddModal(true)}
              >
                <Text style={[styles.emptyButtonText, { color: theme.colors.textInverse }]}>
                  Crear primera tarea
                </Text>
              </TouchableOpacity>
            </View>
          }
        />
      )}

      {/* Add Task Modal */}
      <Modal
        visible={showAddModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={[styles.modalOverlay, { backgroundColor: theme.colors.overlay }]}>
          <ScrollView 
            contentContainerStyle={styles.modalScrollContainer}
            showsVerticalScrollIndicator={false}
          >
            <View style={[styles.modalContent, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              Nueva Tarea
            </Text>
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Título de la tarea"
              placeholderTextColor={theme.colors.textTertiary}
              value={newTask.title}
              onChangeText={(text) => setNewTask({ ...newTask, title: text })}
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Descripción (opcional)"
              placeholderTextColor={theme.colors.textTertiary}
              value={newTask.description}
              onChangeText={(text) => setNewTask({ ...newTask, description: text })}
              multiline
              numberOfLines={3}
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Categoría (opcional)"
              placeholderTextColor={theme.colors.textTertiary}
              value={newTask.category}
              onChangeText={(text) => setNewTask({ ...newTask, category: text })}
            />

            <View style={styles.priorityContainer}>
              <Text style={[styles.priorityLabel, { color: theme.colors.text }]}>
                Prioridad:
              </Text>
              <View style={styles.priorityButtons}>
                {['low', 'medium', 'high'].map((priority) => (
                  <TouchableOpacity
                    key={priority}
                    style={[
                      styles.priorityButton,
                      {
                        backgroundColor: newTask.priority === priority 
                          ? getPriorityColor(priority) 
                          : theme.colors.backgroundSecondary,
                        borderColor: theme.colors.border,
                      }
                    ]}
                    onPress={() => setNewTask({ ...newTask, priority })}
                  >
                    <Text style={[
                      styles.priorityButtonText,
                      { 
                        color: newTask.priority === priority 
                          ? theme.colors.textInverse 
                          : theme.colors.text 
                      }
                    ]}>
                      {priority === 'low' ? 'Baja' : priority === 'medium' ? 'Media' : 'Alta'}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowAddModal(false)}
              >
                <Text style={[styles.modalButtonText, { color: theme.colors.textSecondary }]}>
                  Cancelar
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton, { backgroundColor: theme.colors.primary }]}
                onPress={handleAddTask}
              >
                <Text style={[styles.modalButtonText, { color: theme.colors.textInverse }]}>
                  Crear
                </Text>
              </TouchableOpacity>
            </View>
          </View>
            </ScrollView>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  filtersContainer: {
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  filtersContent: {
    padding: 16,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 12,
    borderWidth: 1,
  },
  filterButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  tasksList: {
    flex: 1,
  },
  tasksContainer: {
    padding: 16,
  },
  taskCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  taskTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  completedTask: {
    textDecorationLine: 'line-through',
    opacity: 0.6,
  },
  taskActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  priorityText: {
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  actionButton: {
    padding: 4,
  },
  taskDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '500',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  dueDateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dueDateText: {
    fontSize: 12,
    marginLeft: 4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 24,
    textAlign: 'center',
  },
  emptyButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 24,
  },
  emptyButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalScrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '100%',
    borderRadius: 12,
    padding: 20,
    maxWidth: 400,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  modalInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  priorityContainer: {
    marginBottom: 20,
  },
  priorityLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  priorityButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  priorityButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  priorityButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 8,
  },
  cancelButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  saveButton: {
    // backgroundColor will be set dynamically
  },
  modalButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default TasksScreen;
