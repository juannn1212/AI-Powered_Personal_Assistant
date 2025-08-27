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
import { Ionicons } from '@expo/vector-icons';
import { API_BASE_URL, getAuthHeaders } from '../config/api';

const HabitsScreen = () => {
  const { theme } = useTheme();
  const { user, token } = useAuth();
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    completed_today: 0,
    streak_average: 0,
  });

  const [newHabit, setNewHabit] = useState({
    name: '',
    description: '',
    frequency: 'daily',
    time_of_day: 'flexible',
    category: '',
    motivation_tip: '',
  });

  useEffect(() => {
    loadHabits();
    loadStats();
  }, []);

  const loadHabits = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/habits`, {
        headers: getAuthHeaders(token),
      });

      if (!response.ok) {
        throw new Error('Error al cargar hábitos');
      }

      const data = await response.json();
      setHabits(data.habits || []);
    } catch (error) {
      console.error('Error loading habits:', error);
      Alert.alert('Error', 'No se pudieron cargar los hábitos');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/habits/stats/summary`, {
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

  const addHabit = async () => {
    if (!newHabit.name.trim()) {
      Alert.alert('Error', 'El nombre del hábito es requerido');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/habits`, {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          name: newHabit.name.trim(),
          description: newHabit.description.trim(),
          frequency: newHabit.frequency,
          time_of_day: newHabit.time_of_day,
          category: newHabit.category.trim(),
          motivation_tip: newHabit.motivation_tip.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error('Error al crear el hábito');
      }

      const data = await response.json();
      setHabits(prev => [data.habit, ...prev]);
      setShowAddModal(false);
      setNewHabit({ name: '', description: '', frequency: 'daily', time_of_day: 'flexible', category: '', motivation_tip: '' });
      loadStats();
      Alert.alert('Éxito', 'Hábito creado correctamente');
    } catch (error) {
      console.error('Error creating habit:', error);
      Alert.alert('Error', 'No se pudo crear el hábito');
    }
  };

  const toggleHabitStatus = async (habitId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/habits/${habitId}/toggle`, {
        method: 'POST',
        headers: getAuthHeaders(token),
      });

      if (!response.ok) {
        throw new Error('Error al actualizar el hábito');
      }

      const data = await response.json();
      setHabits(prev => prev.map(habit => 
        habit.id === habitId 
          ? { ...habit, last_completed: data.last_completed, streak: data.streak }
          : habit
      ));
      loadStats();
    } catch (error) {
      console.error('Error toggling habit:', error);
      Alert.alert('Error', 'No se pudo actualizar el hábito');
    }
  };

  const deleteHabit = async (habitId) => {
    Alert.alert(
      'Eliminar hábito',
      '¿Estás seguro de que quieres eliminar este hábito?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(`${API_BASE_URL}/habits/${habitId}`, {
                method: 'DELETE',
                headers: getAuthHeaders(token),
              });

              if (!response.ok) {
                throw new Error('Error al eliminar el hábito');
              }

              setHabits(prev => prev.filter(habit => habit.id !== habitId));
              loadStats();
              Alert.alert('Éxito', 'Hábito eliminado correctamente');
            } catch (error) {
              console.error('Error deleting habit:', error);
              Alert.alert('Error', 'No se pudo eliminar el hábito');
            }
          },
        },
      ]
    );
  };

  const getFilteredHabits = () => {
    switch (selectedFilter) {
      case 'active':
        return habits.filter(habit => habit.is_active);
      case 'completed_today':
        return habits.filter(habit => {
          const today = new Date().toDateString();
          const lastCompleted = habit.last_completed ? new Date(habit.last_completed).toDateString() : null;
          return lastCompleted === today;
        });
      default:
        return habits;
    }
  };

  const getFrequencyText = (frequency) => {
    switch (frequency) {
      case 'daily':
        return 'Diario';
      case 'weekly':
        return 'Semanal';
      case 'monthly':
        return 'Mensual';
      default:
        return frequency;
    }
  };

  const getTimeOfDayText = (timeOfDay) => {
    switch (timeOfDay) {
      case 'morning':
        return 'Mañana';
      case 'afternoon':
        return 'Tarde';
      case 'evening':
        return 'Noche';
      case 'flexible':
        return 'Flexible';
      default:
        return timeOfDay;
    }
  };

  const isCompletedToday = (habit) => {
    const today = new Date().toDateString();
    const lastCompleted = habit.last_completed ? new Date(habit.last_completed).toDateString() : null;
    return lastCompleted === today;
  };

  const renderHabit = ({ item }) => {
    const completedToday = isCompletedToday(item);

    return (
      <View style={[styles.habitCard, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.habitHeader}>
          <View style={styles.habitTitleContainer}>
            <TouchableOpacity
              style={[
                styles.checkbox,
                { 
                  borderColor: theme.colors.border,
                  backgroundColor: completedToday ? theme.colors.primary : 'transparent'
                }
              ]}
              onPress={() => toggleHabitStatus(item.id)}
            >
              {completedToday && (
                <Ionicons name="checkmark" size={16} color={theme.colors.textInverse} />
              )}
            </TouchableOpacity>
            <View style={styles.habitInfo}>
              <Text style={[styles.habitTitle, { color: theme.colors.text }]}>
                {item.name}
              </Text>
              <Text style={[styles.habitSubtitle, { color: theme.colors.textSecondary }]}>
                {getFrequencyText(item.frequency)} • {getTimeOfDayText(item.time_of_day)}
              </Text>
            </View>
          </View>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => deleteHabit(item.id)}
          >
            <Ionicons name="trash-outline" size={16} color={theme.colors.error} />
          </TouchableOpacity>
        </View>

        {item.description && (
          <Text style={[styles.habitDescription, { color: theme.colors.textSecondary }]}>
            {item.description}
          </Text>
        )}

        <View style={styles.habitFooter}>
          {item.category && (
            <View style={[styles.categoryBadge, { backgroundColor: theme.colors.backgroundSecondary }]}>
              <Text style={[styles.categoryText, { color: theme.colors.textSecondary }]}>
                {item.category}
              </Text>
            </View>
          )}
          
          <View style={[styles.streakBadge, { backgroundColor: theme.colors.primaryLight }]}>
            <Ionicons name="flame" size={12} color={theme.colors.primary} />
            <Text style={[styles.streakText, { color: theme.colors.primary }]}>
              {item.streak || 0} días
            </Text>
          </View>
        </View>

        {item.motivation_tip && (
          <View style={[styles.motivationContainer, { backgroundColor: theme.colors.backgroundSecondary }]}>
            <Ionicons name="bulb-outline" size={16} color={theme.colors.primary} />
            <Text style={[styles.motivationText, { color: theme.colors.textSecondary }]}>
              {item.motivation_tip}
            </Text>
          </View>
        )}
      </View>
    );
  };

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
          Mis Hábitos
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
            {stats.active}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Activos
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.warning }]}>
            {stats.completed_today}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Hoy
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
            {stats.streak_average}
          </Text>
          <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
            Promedio
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
        <FilterButton title="Todos" filter="all" count={stats.total} />
        <FilterButton title="Activos" filter="active" count={stats.active} />
        <FilterButton title="Completados hoy" filter="completed_today" count={stats.completed_today} />
      </ScrollView>

      {/* Habits List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>
            Cargando hábitos...
          </Text>
        </View>
      ) : (
        <FlatList
          data={getFilteredHabits()}
          renderItem={renderHabit}
          keyExtractor={(item) => item.id.toString()}
          style={styles.habitsList}
          contentContainerStyle={styles.habitsContainer}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="repeat-outline" size={64} color={theme.colors.textTertiary} />
              <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
                No hay hábitos {selectedFilter !== 'all' ? `en ${selectedFilter}` : ''}
              </Text>
              <TouchableOpacity
                style={[styles.emptyButton, { backgroundColor: theme.colors.primary }]}
                onPress={() => setShowAddModal(true)}
              >
                <Text style={[styles.emptyButtonText, { color: theme.colors.textInverse }]}>
                  Crear primer hábito
                </Text>
              </TouchableOpacity>
            </View>
          }
        />
      )}

      {/* Add Habit Modal */}
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
              Nuevo Hábito
            </Text>
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Nombre del hábito"
              placeholderTextColor={theme.colors.textTertiary}
              value={newHabit.name}
              onChangeText={(text) => setNewHabit({ ...newHabit, name: text })}
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Descripción (opcional)"
              placeholderTextColor={theme.colors.textTertiary}
              value={newHabit.description}
              onChangeText={(text) => setNewHabit({ ...newHabit, description: text })}
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
              value={newHabit.category}
              onChangeText={(text) => setNewHabit({ ...newHabit, category: text })}
            />

            <View style={styles.frequencyContainer}>
              <Text style={[styles.frequencyLabel, { color: theme.colors.text }]}>
                Frecuencia:
              </Text>
              <View style={styles.frequencyButtons}>
                {['daily', 'weekly', 'monthly'].map((frequency) => (
                  <TouchableOpacity
                    key={frequency}
                    style={[
                      styles.frequencyButton,
                      {
                        backgroundColor: newHabit.frequency === frequency 
                          ? theme.colors.primary 
                          : theme.colors.backgroundSecondary,
                        borderColor: theme.colors.border,
                      }
                    ]}
                    onPress={() => setNewHabit({ ...newHabit, frequency })}
                  >
                    <Text style={[
                      styles.frequencyButtonText,
                      { 
                        color: newHabit.frequency === frequency 
                          ? theme.colors.textInverse 
                          : theme.colors.text 
                      }
                    ]}>
                      {getFrequencyText(frequency)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.timeContainer}>
              <Text style={[styles.timeLabel, { color: theme.colors.text }]}>
                Momento del día:
              </Text>
              <View style={styles.timeButtons}>
                {['morning', 'afternoon', 'evening', 'flexible'].map((time) => (
                  <TouchableOpacity
                    key={time}
                    style={[
                      styles.timeButton,
                      {
                        backgroundColor: newHabit.time_of_day === time 
                          ? theme.colors.primary 
                          : theme.colors.backgroundSecondary,
                        borderColor: theme.colors.border,
                      }
                    ]}
                    onPress={() => setNewHabit({ ...newHabit, time_of_day: time })}
                  >
                    <Text style={[
                      styles.timeButtonText,
                      { 
                        color: newHabit.time_of_day === time 
                          ? theme.colors.textInverse 
                          : theme.colors.text 
                      }
                    ]}>
                      {getTimeOfDayText(time)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Consejo motivacional (opcional)"
              placeholderTextColor={theme.colors.textTertiary}
              value={newHabit.motivation_tip}
              onChangeText={(text) => setNewHabit({ ...newHabit, motivation_tip: text })}
              multiline
              numberOfLines={2}
            />

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
                onPress={addHabit}
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
  habitsList: {
    flex: 1,
  },
  habitsContainer: {
    padding: 16,
  },
  habitCard: {
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
  habitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  habitTitleContainer: {
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
  habitInfo: {
    flex: 1,
  },
  habitTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  habitSubtitle: {
    fontSize: 12,
  },
  actionButton: {
    padding: 4,
  },
  habitDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  habitFooter: {
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
  streakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  streakText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 4,
  },
  motivationContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 12,
    borderRadius: 8,
  },
  motivationText: {
    fontSize: 14,
    lineHeight: 20,
    marginLeft: 8,
    flex: 1,
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
    width: '90%',
    borderRadius: 12,
    padding: 24,
    maxWidth: 400,
    maxHeight: '85%',
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
    padding: 16,
    marginBottom: 20,
    fontSize: 16,
  },
  frequencyContainer: {
    marginBottom: 16,
  },
  frequencyLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  frequencyButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  frequencyButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  frequencyButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  timeContainer: {
    marginBottom: 16,
  },
  timeLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  timeButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  timeButton: {
    flex: 1,
    minWidth: '48%',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
    marginHorizontal: 2,
    marginBottom: 8,
  },
  timeButtonText: {
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

export default HabitsScreen;
