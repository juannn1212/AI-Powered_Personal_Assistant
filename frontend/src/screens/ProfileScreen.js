import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  ActivityIndicator,
  Switch,
  Platform,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const ProfileScreen = ({ navigation }) => {
  const { theme, isDarkMode, toggleTheme } = useTheme();
  const { user, logout, updateProfile, changePassword, deleteAccount, loading } = useAuth();
  
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  const [editForm, setEditForm] = useState({
    full_name: user?.full_name || '',
    bio: user?.bio || '',
  });
  
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const handleLogout = async () => {
    console.log('🔄 Botón de logout presionado');
    try {
      console.log('🔄 Iniciando proceso de logout directamente...');
      console.log('🔍 Llamando a la función logout del AuthContext...');
      console.log('🔍 Función logout disponible:', typeof logout);
      const result = await logout();
      console.log('📊 Resultado del logout:', result);
      if (result.success) {
        console.log('✅ Logout exitoso');
        console.log('🔄 La navegación automática debería llevarte al login');
        // Mostrar mensaje de confirmación
        Alert.alert('Sesión cerrada', 'Has cerrado sesión correctamente');
      } else {
        console.error('❌ Error en logout:', result.error);
        Alert.alert('Error', 'No se pudo cerrar sesión');
      }
    } catch (error) {
      console.error('❌ Error en handleLogout:', error);
      Alert.alert('Error', 'Error al cerrar sesión');
    }
  };

  const handleUpdateProfile = async () => {
    if (!editForm.full_name.trim()) {
      Alert.alert('Error', 'El nombre completo es requerido');
      return;
    }

    const result = await updateProfile(editForm);
    if (result.success) {
      Alert.alert('Éxito', 'Perfil actualizado correctamente');
      setShowEditModal(false);
    }
  };

  const handleChangePassword = async () => {
    if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
      Alert.alert('Error', 'Por favor completa todos los campos');
      return;
    }

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      Alert.alert('Error', 'Las contraseñas no coinciden');
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      Alert.alert('Error', 'La nueva contraseña debe tener al menos 6 caracteres');
      return;
    }

    const result = await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
    if (result.success) {
      Alert.alert('Éxito', 'Contraseña cambiada correctamente');
      setShowPasswordModal(false);
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
    }
  };

  const handleDeleteAccount = async () => {
    Alert.alert(
      'Eliminar cuenta',
      'Esta acción es irreversible. ¿Estás seguro de que quieres eliminar tu cuenta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: async () => {
            const result = await deleteAccount();
            if (result.success) {
              Alert.alert('Cuenta eliminada', 'Tu cuenta ha sido eliminada permanentemente');
            }
          },
        },
      ]
    );
  };

  const ProfileSection = ({ title, children }) => (
    <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>{title}</Text>
      {children}
    </View>
  );

  const ProfileItem = ({ icon, title, subtitle, onPress, showArrow = true, danger = false }) => (
    <TouchableOpacity
      style={[styles.profileItem, { borderBottomColor: theme.colors.border }]}
      onPress={() => {
        console.log('🔍 TouchableOpacity onPress ejecutado para:', title);
        if (onPress) {
          onPress();
        }
      }}
    >
      <View style={styles.profileItemLeft}>
        <View style={[styles.iconContainer, { backgroundColor: theme.colors.backgroundSecondary }]}>
          <Ionicons
            name={icon}
            size={20}
            color={danger ? theme.colors.error : theme.colors.primary}
          />
        </View>
        <View style={styles.profileItemText}>
          <Text style={[styles.profileItemTitle, { color: theme.colors.text }]}>{title}</Text>
          {subtitle && (
            <Text style={[styles.profileItemSubtitle, { color: theme.colors.textSecondary }]}>
              {subtitle}
            </Text>
          )}
        </View>
      </View>
      {showArrow && (
        <Ionicons
          name="chevron-forward"
          size={20}
          color={theme.colors.textSecondary}
        />
      )}
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <LinearGradient
          colors={[theme.colors.primary, theme.colors.primaryDark]}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <View style={[styles.avatar, { backgroundColor: theme.colors.background }]}>
              <Ionicons
                name="person"
                size={40}
                color={theme.colors.primary}
              />
            </View>
            <Text style={[styles.userName, { color: theme.colors.textInverse }]}>
              {user?.full_name || 'Usuario'}
            </Text>
            <Text style={[styles.userEmail, { color: theme.colors.textInverse }]}>
              {user?.email || 'usuario@ejemplo.com'}
            </Text>
          </View>
        </LinearGradient>

        {/* Profile Sections */}
        <View style={styles.content}>
          <ProfileSection title="Información personal">
            <ProfileItem
              icon="person-outline"
              title="Editar perfil"
              subtitle="Actualiza tu información personal"
              onPress={() => setShowEditModal(true)}
            />
            <ProfileItem
              icon="lock-closed-outline"
              title="Cambiar contraseña"
              subtitle="Actualiza tu contraseña de seguridad"
              onPress={() => setShowPasswordModal(true)}
            />
          </ProfileSection>

          <ProfileSection title="Preferencias">
            <View style={[styles.profileItem, { borderBottomColor: theme.colors.border }]}>
              <View style={styles.profileItemLeft}>
                <View style={[styles.iconContainer, { backgroundColor: theme.colors.backgroundSecondary }]}>
                  <Ionicons
                    name={isDarkMode ? "moon" : "sunny"}
                    size={20}
                    color={theme.colors.primary}
                  />
                </View>
                <View style={styles.profileItemText}>
                  <Text style={[styles.profileItemTitle, { color: theme.colors.text }]}>
                    Modo oscuro
                  </Text>
                  <Text style={[styles.profileItemSubtitle, { color: theme.colors.textSecondary }]}>
                    {isDarkMode ? 'Activado' : 'Desactivado'}
                  </Text>
                </View>
              </View>
              <Switch
                value={isDarkMode}
                onValueChange={toggleTheme}
                trackColor={{ false: theme.colors.border, true: theme.colors.primaryLight }}
                thumbColor={isDarkMode ? theme.colors.primary : theme.colors.textSecondary}
              />
            </View>
          </ProfileSection>

          <ProfileSection title="Cuenta">
            <ProfileItem
              icon="log-out-outline"
              title="Cerrar sesión"
              subtitle="Salir de tu cuenta"
              onPress={() => {
                console.log('🔍 ProfileItem onPress ejecutado');
                handleLogout();
              }}
              danger={true}
            />
            <ProfileItem
              icon="trash-outline"
              title="Eliminar cuenta"
              subtitle="Eliminar permanentemente tu cuenta"
              onPress={handleDeleteAccount}
              danger={true}
            />
          </ProfileSection>

          <ProfileSection title="Información de la app">
            <ProfileItem
              icon="information-circle-outline"
              title="Versión"
              subtitle="1.0.0"
              onPress={() => {}}
              showArrow={false}
            />
            <ProfileItem
              icon="document-text-outline"
              title="Términos y condiciones"
              onPress={() => Alert.alert('Términos', 'Términos y condiciones de la aplicación')}
            />
            <ProfileItem
              icon="shield-checkmark-outline"
              title="Política de privacidad"
              onPress={() => Alert.alert('Privacidad', 'Política de privacidad de la aplicación')}
            />
          </ProfileSection>
        </View>
      </ScrollView>

      {/* Edit Profile Modal */}
      <Modal
        visible={showEditModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowEditModal(false)}
      >
        <View style={[styles.modalOverlay, { backgroundColor: theme.colors.overlay }]}>
          <View style={[styles.modalContent, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              Editar perfil
            </Text>
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Nombre completo"
              placeholderTextColor={theme.colors.textTertiary}
              value={editForm.full_name}
              onChangeText={(text) => setEditForm({ ...editForm, full_name: text })}
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Biografía (opcional)"
              placeholderTextColor={theme.colors.textTertiary}
              value={editForm.bio}
              onChangeText={(text) => setEditForm({ ...editForm, bio: text })}
              multiline
              numberOfLines={3}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowEditModal(false)}
              >
                <Text style={[styles.modalButtonText, { color: theme.colors.textSecondary }]}>
                  Cancelar
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton, { backgroundColor: theme.colors.primary }]}
                onPress={handleUpdateProfile}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color={theme.colors.textInverse} />
                ) : (
                  <Text style={[styles.modalButtonText, { color: theme.colors.textInverse }]}>
                    Guardar
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Change Password Modal */}
      <Modal
        visible={showPasswordModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowPasswordModal(false)}
      >
        <View style={[styles.modalOverlay, { backgroundColor: theme.colors.overlay }]}>
          <View style={[styles.modalContent, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              Cambiar contraseña
            </Text>
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Contraseña actual"
              placeholderTextColor={theme.colors.textTertiary}
              value={passwordForm.currentPassword}
              onChangeText={(text) => setPasswordForm({ ...passwordForm, currentPassword: text })}
              secureTextEntry
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Nueva contraseña"
              placeholderTextColor={theme.colors.textTertiary}
              value={passwordForm.newPassword}
              onChangeText={(text) => setPasswordForm({ ...passwordForm, newPassword: text })}
              secureTextEntry
            />
            
            <TextInput
              style={[styles.modalInput, { 
                color: theme.colors.text,
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.backgroundSecondary
              }]}
              placeholder="Confirmar nueva contraseña"
              placeholderTextColor={theme.colors.textTertiary}
              value={passwordForm.confirmPassword}
              onChangeText={(text) => setPasswordForm({ ...passwordForm, confirmPassword: text })}
              secureTextEntry
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowPasswordModal(false)}
              >
                <Text style={[styles.modalButtonText, { color: theme.colors.textSecondary }]}>
                  Cancelar
                </Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton, { backgroundColor: theme.colors.primary }]}
                onPress={handleChangePassword}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color={theme.colors.textInverse} />
                ) : (
                  <Text style={[styles.modalButtonText, { color: theme.colors.textInverse }]}>
                    Cambiar
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
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
    paddingTop: 60,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  headerContent: {
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 8,
      },
    }),
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 16,
    opacity: 0.9,
  },
  content: {
    padding: 20,
  },
  section: {
    borderRadius: 12,
    marginBottom: 20,
    overflow: 'hidden',
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
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    padding: 16,
    paddingBottom: 8,
  },
  profileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
  },
  profileItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  profileItemText: {
    flex: 1,
  },
  profileItemTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 2,
  },
  profileItemSubtitle: {
    fontSize: 14,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    width: '100%',
    borderRadius: 12,
    padding: 20,
    maxWidth: 400,
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
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
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

export default ProfileScreen;
