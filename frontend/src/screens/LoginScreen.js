import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { TextInput, Button, ActivityIndicator } from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { theme } from '../theme/theme';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Por favor completa todos los campos');
      return;
    }

    if (!isValidEmail(email)) {
      Alert.alert('Error', 'Por favor ingresa un email válido');
      return;
    }

    setIsLoading(true);
    try {
      const result = await login(email.trim(), password);
      if (!result.success) {
        Alert.alert('Error', result.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Error de conexión. Verifica tu conexión a internet.');
    } finally {
      setIsLoading(false);
    }
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Ionicons name="chatbubbles" size={80} color={theme.colors.primary} />
          </View>
          <Text style={styles.title}>AI Personal Assistant</Text>
          <Text style={styles.subtitle}>Tu asistente inteligente de productividad</Text>
        </View>

        <View style={styles.formContainer}>
          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.input}
            theme={{
              colors: {
                primary: theme.colors.primary,
                placeholder: theme.colors.textSecondary,
              },
            }}
          />

          <TextInput
            label="Contraseña"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry={!showPassword}
            style={styles.input}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
            theme={{
              colors: {
                primary: theme.colors.primary,
                placeholder: theme.colors.textSecondary,
              },
            }}
          />

          <Button
            mode="contained"
            onPress={handleLogin}
            disabled={isLoading}
            style={styles.loginButton}
            contentStyle={styles.loginButtonContent}
            labelStyle={styles.loginButtonLabel}
          >
            {isLoading ? (
              <ActivityIndicator color={theme.colors.onPrimary} />
            ) : (
              'Iniciar Sesión'
            )}
          </Button>

          <TouchableOpacity
            style={styles.forgotPassword}
            onPress={() => Alert.alert('Info', 'Función de recuperación de contraseña próximamente')}
          >
            <Text style={styles.forgotPasswordText}>¿Olvidaste tu contraseña?</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>¿No tienes una cuenta?</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.registerLink}>Regístrate aquí</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.featuresContainer}>
          <Text style={styles.featuresTitle}>Características principales:</Text>
          <View style={styles.featureItem}>
            <Ionicons name="mic" size={20} color={theme.colors.primary} />
            <Text style={styles.featureText}>Reconocimiento de voz</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="analytics" size={20} color={theme.colors.primary} />
            <Text style={styles.featureText}>Análisis de productividad</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="brain" size={20} color={theme.colors.primary} />
            <Text style={styles.featureText}>Machine Learning</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="calendar" size={20} color={theme.colors.primary} />
            <Text style={styles.featureText}>Gestión de calendario</Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: theme.spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginTop: theme.spacing.xxl,
    marginBottom: theme.spacing.xl,
  },
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: theme.colors.primary + '20',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.lg,
  },
  title: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    fontSize: theme.typography.body1.fontSize,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  formContainer: {
    marginBottom: theme.spacing.xl,
  },
  input: {
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  loginButton: {
    marginTop: theme.spacing.md,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
  },
  loginButtonContent: {
    height: 50,
  },
  loginButtonLabel: {
    fontSize: theme.typography.h4.fontSize,
    fontWeight: '600',
  },
  forgotPassword: {
    alignItems: 'center',
    marginTop: theme.spacing.md,
  },
  forgotPasswordText: {
    color: theme.colors.primary,
    fontSize: theme.typography.body2.fontSize,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  footerText: {
    color: theme.colors.textSecondary,
    fontSize: theme.typography.body2.fontSize,
  },
  registerLink: {
    color: theme.colors.primary,
    fontSize: theme.typography.body2.fontSize,
    fontWeight: '600',
    marginLeft: theme.spacing.xs,
  },
  featuresContainer: {
    backgroundColor: theme.colors.card,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.lg,
  },
  featuresTitle: {
    fontSize: theme.typography.h4.fontSize,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  featureText: {
    marginLeft: theme.spacing.sm,
    fontSize: theme.typography.body2.fontSize,
    color: theme.colors.text,
  },
});

export default LoginScreen;
