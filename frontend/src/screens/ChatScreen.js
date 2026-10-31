import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { useTasks } from '../context/TasksContext';
import { Ionicons } from '@expo/vector-icons';
import { API_BASE_URL, getAuthHeaders } from '../config/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ChatScreen = ({ navigation }) => {
  const { theme } = useTheme();
  const { user, token, handleSessionExpired } = useAuth();
  const { addTask, addHabit } = useTasks();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const flatListRef = useRef(null);

  useEffect(() => {
    // Mensaje de bienvenida inicial
    setMessages([
      {
        id: 'welcome',
        type: 'ai',
        text: `¡Hola ${user?.full_name || 'Usuario'}! Soy tu asistente de bienestar y productividad: te ayudo con tareas, hábitos y a sobrellevar días pesados. Soy una IA, no un profesional de salud mental ni un servicio de emergencias. ¿Cómo te sientes hoy?`,
        timestamp: new Date().toISOString(),
        suggestions: [
          'Me siento estresado',
          'Ejercicio de respiración',
          'Ver mis tareas'
        ]
      }
    ]);
  }, [user]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      text: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          message: text.trim(),
          user_id: user?.id
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error en la comunicación');
      }

      // Manejar creación de tareas y hábitos
      if (data.data.task_created) {
        console.log('Tarea creada desde chat:', data.data.task_created);
        const result = await addTask(data.data.task_created);
        if (result.success) {
          console.log('Tarea agregada al contexto:', result.task);
        }
      }
      
      if (data.data.habit_created) {
        console.log('Hábito creado desde chat:', data.data.habit_created);
        const result = await addHabit(data.data.habit_created);
        if (result.success) {
          console.log('Hábito agregado al contexto:', result.habit);
        }
      }

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        text: data.data.response,
        timestamp: new Date().toISOString(),
        suggestions: data.data.suggestions || [],
        insights: data.data.insights,
        sentiment: data.data.sentiment,
      };

      setMessages(prev => [...prev, aiMessage]);
      console.log('Sugerencias recibidas:', data.data.suggestions);
      setSuggestions(data.data.suggestions || []);

    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorText = 'Lo siento, hubo un error en la comunicación. Por favor, inténtalo de nuevo.';
      
      // Manejar específicamente el error de autenticación
      if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('Could not validate credentials')) {
        errorText = 'Tu sesión ha expirado. Por favor, vuelve a iniciar sesión para continuar usando el asistente.';
        
        // Usar la función centralizada para manejar la expiración
        await handleSessionExpired();
      }
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        text: errorText,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionPress = (suggestion) => {
    console.log('Sugerencia presionada:', suggestion);
    
    // Solo manejar sugerencias que realmente funcionan
    if (suggestion.includes('Ver todas mis tareas') || suggestion.includes('Ver lista de tareas')) {
      console.log('Navegando a TasksScreen');
      navigation.navigate('Tasks');
      return;
    }
    
    if (suggestion.includes('Ver mis hábitos') || suggestion.includes('Ver hábitos existentes')) {
      console.log('Navegando a HabitsScreen');
      navigation.navigate('Habits');
      return;
    }
    
    if (suggestion.includes('Ir a Tareas')) {
      navigation.navigate('Tasks');
      return;
    }
    
    if (suggestion.includes('Ir a Hábitos')) {
      navigation.navigate('Habits');
      return;
    }
    
    if (suggestion.includes('Ir a Analytics')) {
      navigation.navigate('Analytics');
      return;
    }
    
    if (suggestion.includes('Crear nueva tarea') || suggestion.includes('Crear tarea')) {
      Alert.prompt(
        'Crear nueva tarea',
        '¿Qué tarea quieres crear?',
        [
          { text: 'Cancelar', style: 'cancel' },
          {
            text: 'Crear',
            onPress: async (taskName) => {
              if (taskName && taskName.trim()) {
                console.log('Creando tarea:', taskName);
                const task = await createTaskFromChat(taskName);
                if (task) {
                  navigation.navigate('Tasks');
                }
              }
            }
          }
        ],
        'plain-text'
      );
      return;
    }
    
    if (suggestion.includes('Crear nuevo hábito') || suggestion.includes('Crear hábito')) {
      Alert.prompt(
        'Crear nuevo hábito',
        '¿Qué hábito quieres crear?',
        [
          { text: 'Cancelar', style: 'cancel' },
          {
            text: 'Crear',
            onPress: async (habitName) => {
              if (habitName && habitName.trim()) {
                console.log('Creando hábito:', habitName);
                const habit = await createHabitFromChat(habitName);
                if (habit) {
                  navigation.navigate('Habits');
                }
              }
            }
          }
        ],
        'plain-text'
      );
      return;
    }
    
    // Para sugerencias de consejos, mostrar información útil
    if (suggestion.includes('Gestión del tiempo') || suggestion.includes('Técnica Pomodoro')) {
      const adviceMessage = "⏰ **Técnica Pomodoro:**\n\n• Trabaja en bloques de 25 minutos\n• Toma descansos de 5 minutos\n• Después de 4 pomodoros, toma un descanso largo de 15-30 minutos\n\n¿Te gustaría que te ayude a implementar esta técnica?";
      
      const adviceMsg = {
        id: Date.now().toString(),
        type: 'ai',
        text: adviceMessage,
        timestamp: new Date().toISOString(),
        suggestions: ['Crear tarea con Pomodoro', 'Ver más consejos', 'Configurar recordatorios']
      };
      
      setMessages(prev => [...prev, adviceMsg]);
      return;
    }
    
    if (suggestion.includes('Consejos de productividad') || suggestion.includes('Ayuda con productividad')) {
      const adviceMessage = "🚀 **Consejos de Productividad:**\n\n• Prioriza tus tareas (Matriz de Eisenhower)\n• Elimina distracciones digitales\n• Usa la regla de los 2 minutos\n• Planifica tu día la noche anterior\n• Celebra los pequeños logros\n\n¿Cuál de estos consejos te gustaría implementar?";
      
      const adviceMsg = {
        id: Date.now().toString(),
        type: 'ai',
        text: adviceMessage,
        timestamp: new Date().toISOString(),
        suggestions: ['Crear tarea prioritaria', 'Ver estadísticas', 'Configurar hábitos']
      };
      
      setMessages(prev => [...prev, adviceMsg]);
      return;
    }
    
    // Para sugerencias que no funcionan, mostrar mensaje informativo
    if (suggestion.includes('Marcar tarea como completada') || 
        suggestion.includes('Ver progreso') || 
        suggestion.includes('Comparar períodos') ||
        suggestion.includes('Ver estadísticas') ||
        suggestion.includes('Configurar recordatorios')) {
      
      const infoMessage = `ℹ️ **${suggestion}**\n\nEsta función está disponible en la pantalla correspondiente:\n\n• Para marcar tareas como completadas: Ve a "Tareas"\n• Para ver progreso: Ve a "Hábitos" o "Analytics"\n• Para estadísticas: Ve a "Analytics"\n\n¿Te gustaría ir a esa pantalla?`;
      
      const infoMsg = {
        id: Date.now().toString(),
        type: 'ai',
        text: infoMessage,
        timestamp: new Date().toISOString(),
        suggestions: ['Ir a Tareas', 'Ir a Hábitos', 'Ir a Analytics']
      };
      
      setMessages(prev => [...prev, infoMsg]);
      return;
    }
    
    // Para cualquier otra sugerencia, enviar como mensaje normal
    sendMessage(suggestion);
  };

  const createTaskFromChat = async (taskDescription) => {
    try {
      console.log('Creando tarea desde chat:', taskDescription);
      
      const result = await addTask({
        title: taskDescription,
        description: taskDescription,
        priority: 'medium',
        status: 'pending'
      });

      if (result.success) {
        Alert.alert('Tarea creada', 'La tarea se ha creado exitosamente');
        return result.task;
      } else {
        throw new Error(result.error || 'Error al crear la tarea');
      }

    } catch (error) {
      console.error('Error creating task:', error);
      Alert.alert('Error', 'No se pudo crear la tarea');
      return null;
    }
  };

  const createHabitFromChat = async (habitDescription) => {
    try {
      console.log('Creando hábito desde chat:', habitDescription);
      
      const result = await addHabit({
        name: habitDescription,
        description: habitDescription,
        frequency: 'daily',
        time_of_day: 'flexible'
      });

      if (result.success) {
        Alert.alert('Hábito creado', 'El hábito se ha creado exitosamente');
        return result.habit;
      } else {
        throw new Error(result.error || 'Error al crear el hábito');
      }

    } catch (error) {
      console.error('Error creating habit:', error);
      Alert.alert('Error', 'No se pudo crear el hábito');
      return null;
    }
  };

  const renderMessage = ({ item }) => {
    const isUser = item.type === 'user';
    const isError = item.isError;

    return (
      <View style={[
        styles.messageContainer,
        isUser ? styles.userMessageContainer : styles.aiMessageContainer
      ]}>
        <View style={[
          styles.messageBubble,
          {
            backgroundColor: isUser 
              ? theme.colors.primary 
              : isError 
                ? theme.colors.error 
                : theme.colors.surface,
            borderColor: theme.colors.border,
          }
        ]}>
          <Text style={[
            styles.messageText,
            { color: isUser || isError ? theme.colors.textInverse : theme.colors.text }
          ]}>
            {item.text}
          </Text>
          
          {item.insights && (
            <View style={[styles.insightsContainer, { backgroundColor: theme.colors.backgroundSecondary }]}>
              <Text style={[styles.insightsTitle, { color: theme.colors.primary }]}>
                💡 Insight
              </Text>
              <Text style={[styles.insightsText, { color: theme.colors.textSecondary }]}>
                {item.insights}
              </Text>
            </View>
          )}

          {item.suggestions && item.suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              <Text style={[styles.suggestionsTitle, { color: theme.colors.textSecondary }]}>
                Sugerencias:
              </Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {item.suggestions.map((suggestion, index) => (
                  <TouchableOpacity
                    key={index}
                    style={[styles.suggestionButton, { backgroundColor: theme.colors.primaryLight }]}
                    onPress={() => handleSuggestionPress(suggestion)}
                  >
                    <Text style={[styles.suggestionText, { color: theme.colors.text }]}>
                      {suggestion}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </View>
        
        <Text style={[styles.timestamp, { color: theme.colors.textTertiary }]}>
          {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.headerContent}>
          <View style={[styles.avatar, { backgroundColor: theme.colors.primaryLight }]}>
            <Ionicons name="chatbubbles" size={24} color={theme.colors.primary} />
          </View>
          <View style={styles.headerText}>
            <Text style={[styles.headerTitle, { color: theme.colors.text }]}>
              Asistente IA
            </Text>
            <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
              {isLoading ? 'Escribiendo...' : 'En línea'}
            </Text>
          </View>
        </View>
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Quick Actions */}
      {suggestions.length > 0 && (
        <View style={[styles.quickActionsContainer, { backgroundColor: theme.colors.surface }]}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {suggestions.map((suggestion, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.quickActionButton, { backgroundColor: theme.colors.primaryLight }]}
                onPress={() => handleSuggestionPress(suggestion)}
              >
                <Text style={[styles.quickActionText, { color: theme.colors.text }]}>
                  {suggestion}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Input */}
      <View style={[styles.inputContainer, { backgroundColor: theme.colors.surface }]}>
        <View style={[styles.inputWrapper, { borderColor: theme.colors.border }]}>
          <TextInput
            style={[styles.textInput, { color: theme.colors.text }]}
            placeholder="Escribe tu mensaje..."
            placeholderTextColor={theme.colors.textTertiary}
            value={inputText}
            onChangeText={setInputText}
            multiline
            maxLength={500}
            onSubmitEditing={() => sendMessage(inputText)}
          />
          
          <TouchableOpacity
            style={[
              styles.sendButton,
              {
                backgroundColor: inputText.trim() ? theme.colors.primary : theme.colors.border,
                opacity: inputText.trim() ? 1 : 0.5,
              }
            ]}
            onPress={() => sendMessage(inputText)}
            disabled={!inputText.trim() || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={theme.colors.textInverse} size="small" />
            ) : (
              <Ionicons
                name="send"
                size={20}
                color={theme.colors.textInverse}
              />
            )}
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerText: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 2,
  },
  headerSubtitle: {
    fontSize: 14,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  aiMessageContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  insightsContainer: {
    marginTop: 12,
    padding: 12,
    borderRadius: 8,
  },
  insightsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  insightsText: {
    fontSize: 14,
    lineHeight: 20,
  },
  suggestionsContainer: {
    marginTop: 12,
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  suggestionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 4,
  },
  suggestionText: {
    fontSize: 12,
    fontWeight: '500',
  },
  timestamp: {
    fontSize: 12,
    marginTop: 4,
    marginHorizontal: 16,
  },
  quickActionsContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  quickActionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '500',
  },
  inputContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    borderWidth: 1,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    maxHeight: 100,
    paddingVertical: 8,
  },
  sendButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
});

export default ChatScreen;
