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
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from 'react-native-paper';
import * as Speech from 'expo-speech';
import { Audio } from 'expo-av';
import { assistantAPI, handleAPIError } from '../services/api';
import { theme } from '../theme/theme';

const ChatScreen = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState(null);
  const flatListRef = useRef(null);
  const paperTheme = useTheme();

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: '1',
        text: '¡Hola! Soy tu asistente personal de IA. ¿En qué puedo ayudarte hoy?',
        isUser: false,
        timestamp: new Date(),
        suggestions: [
          '¿Puedes ayudarme a organizar mis tareas?',
          '¿Cómo puedo mejorar mi productividad?',
          '¿Puedes crear un nuevo hábito para mí?',
        ],
      },
    ]);
  }, []);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await assistantAPI.chat(text.trim());
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        isUser: false,
        timestamp: new Date(),
        suggestions: response.data.suggestions || [],
        intent: response.data.intent,
        confidence: response.data.confidence,
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Speak the response
      if (response.data.response) {
        Speech.speak(response.data.response, {
          language: 'es',
          pitch: 1,
          rate: 0.9,
        });
      }
    } catch (error) {
      const errorMessage = handleAPIError(error);
      Alert.alert('Error', errorMessage);
      
      const errorResponse = {
        id: (Date.now() + 1).toString(),
        text: 'Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?',
        isUser: false,
        timestamp: new Date(),
        suggestions: ['Intenta reformular tu pregunta', 'Verifica tu conexión a internet'],
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permisos necesarios', 'Necesitamos permisos de micrófono para grabar audio.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      Alert.alert('Error', 'No se pudo iniciar la grabación.');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      // Send audio file to backend for transcription
      const formData = new FormData();
      formData.append('audio_file', {
        uri,
        type: 'audio/wav',
        name: 'voice_message.wav',
      });

      const response = await assistantAPI.transcribeVoice(formData);
      const transcribedText = response.data.transcribed_text;
      
      if (transcribedText && transcribedText !== 'Transcripción de voz no implementada aún') {
        setInputText(transcribedText);
        sendMessage(transcribedText);
      } else {
        Alert.alert('Error', 'No se pudo transcribir el audio. Por favor, escribe tu mensaje.');
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'No se pudo procesar la grabación.');
    }
  };

  const handleSuggestionPress = (suggestion) => {
    sendMessage(suggestion);
  };

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageContainer,
      item.isUser ? styles.userMessage : styles.aiMessage
    ]}>
      <View style={[
        styles.messageBubble,
        item.isUser ? styles.userBubble : styles.aiBubble
      ]}>
        <Text style={[
          styles.messageText,
          item.isUser ? styles.userText : styles.aiText
        ]}>
          {item.text}
        </Text>
        
        {!item.isUser && item.suggestions && item.suggestions.length > 0 && (
          <View style={styles.suggestionsContainer}>
            {item.suggestions.map((suggestion, index) => (
              <TouchableOpacity
                key={index}
                style={styles.suggestionButton}
                onPress={() => handleSuggestionPress(suggestion)}
              >
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
        
        <Text style={styles.timestamp}>
          {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </View>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
        onLayout={() => flatListRef.current?.scrollToEnd()}
      />

      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={theme.colors.primary} />
          <Text style={styles.loadingText}>El asistente está pensando...</Text>
        </View>
      )}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Escribe tu mensaje..."
          placeholderTextColor={theme.colors.textSecondary}
          multiline
          maxLength={500}
        />
        
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[
              styles.voiceButton,
              isRecording && styles.recordingButton
            ]}
            onPress={isRecording ? stopRecording : startRecording}
          >
            <Ionicons
              name={isRecording ? 'stop' : 'mic'}
              size={24}
              color={isRecording ? theme.colors.error : theme.colors.primary}
            />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.sendButton,
              !inputText.trim() && styles.sendButtonDisabled
            ]}
            onPress={() => sendMessage(inputText)}
            disabled={!inputText.trim() || isLoading}
          >
            <Ionicons
              name="send"
              size={20}
              color={theme.colors.onPrimary}
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    padding: theme.spacing.md,
  },
  messageContainer: {
    marginBottom: theme.spacing.md,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  aiMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.lg,
  },
  userBubble: {
    backgroundColor: theme.colors.chatBubble.user,
    borderBottomRightRadius: theme.borderRadius.sm,
  },
  aiBubble: {
    backgroundColor: theme.colors.chatBubble.assistant,
    borderBottomLeftRadius: theme.borderRadius.sm,
  },
  messageText: {
    fontSize: theme.typography.body1.fontSize,
    lineHeight: 20,
  },
  userText: {
    color: theme.colors.text,
  },
  aiText: {
    color: theme.colors.text,
  },
  suggestionsContainer: {
    marginTop: theme.spacing.sm,
  },
  suggestionButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.xs,
  },
  suggestionText: {
    color: theme.colors.onPrimary,
    fontSize: theme.typography.body2.fontSize,
  },
  timestamp: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
    alignSelf: 'flex-end',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.md,
  },
  loadingText: {
    marginLeft: theme.spacing.sm,
    color: theme.colors.textSecondary,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  textInput: {
    flex: 1,
    backgroundColor: theme.colors.card,
    borderRadius: theme.borderRadius.lg,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    marginRight: theme.spacing.sm,
    maxHeight: 100,
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.text,
  },
  buttonContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  voiceButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: theme.colors.card,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: theme.spacing.sm,
  },
  recordingButton: {
    backgroundColor: theme.colors.error + '20',
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: theme.colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: theme.colors.border,
  },
});

export default ChatScreen;
