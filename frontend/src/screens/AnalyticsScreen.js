import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { API_BASE_URL, getAuthHeaders } from '../config/api';

const AnalyticsScreen = () => {
  const { theme } = useTheme();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [analytics, setAnalytics] = useState({
    productivity: {},
    habits: {},
    tasks: {},
    chat: {},
    insights: [],
    summary: {},
  });

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const [productivityRes, habitsRes, tasksRes, chatRes, insightsRes, summaryRes] = await Promise.all([
        fetch(`${API_BASE_URL}/analytics/productivity?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
        fetch(`${API_BASE_URL}/analytics/habits?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
        fetch(`${API_BASE_URL}/analytics/tasks?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
        fetch(`${API_BASE_URL}/analytics/chat?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
        fetch(`${API_BASE_URL}/analytics/insights?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
        fetch(`${API_BASE_URL}/analytics/summary?period=${selectedPeriod}`, {
          headers: getAuthHeaders(token),
        }),
      ]);

      const [productivity, habits, tasks, chat, insights, summary] = await Promise.all([
        productivityRes.ok ? productivityRes.json() : {},
        habitsRes.ok ? habitsRes.json() : {},
        tasksRes.ok ? tasksRes.json() : {},
        chatRes.ok ? chatRes.json() : {},
        insightsRes.ok ? insightsRes.json() : {},
        summaryRes.ok ? summaryRes.json() : {},
      ]);

      setAnalytics({
        productivity,
        habits,
        tasks,
        chat,
        insights: insights.insights || [],
        summary,
      });
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, subtitle, icon, color, trend }) => (
    <View style={[styles.statCard, { backgroundColor: theme.colors.surface }]}>
      <View style={styles.statHeader}>
        <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
          <Ionicons name={icon} size={24} color={color} />
        </View>
        {trend && (
          <View style={[styles.trendContainer, { backgroundColor: trend > 0 ? theme.colors.success + '20' : theme.colors.error + '20' }]}>
            <Ionicons 
              name={trend > 0 ? 'trending-up' : 'trending-down'} 
              size={12} 
              color={trend > 0 ? theme.colors.success : theme.colors.error} 
            />
            <Text style={[styles.trendText, { color: trend > 0 ? theme.colors.success : theme.colors.error }]}>
              {Math.abs(trend)}%
            </Text>
          </View>
        )}
      </View>
      <Text style={[styles.statValue, { color: theme.colors.text }]}>
        {value}
      </Text>
      <Text style={[styles.statTitle, { color: theme.colors.text }]}>
        {title}
      </Text>
      {subtitle && (
        <Text style={[styles.statSubtitle, { color: theme.colors.textSecondary }]}>
          {subtitle}
        </Text>
      )}
    </View>
  );

  const InsightCard = ({ insight, index }) => (
    <View style={[styles.insightCard, { backgroundColor: theme.colors.surface }]}>
      <View style={styles.insightHeader}>
        <View style={[styles.insightIcon, { backgroundColor: theme.colors.primaryLight }]}>
          <Ionicons name="bulb-outline" size={20} color={theme.colors.primary} />
        </View>
        <Text style={[styles.insightTitle, { color: theme.colors.text }]}>
          Insight #{index + 1}
        </Text>
      </View>
      <Text style={[styles.insightText, { color: theme.colors.textSecondary }]}>
        {insight}
      </Text>
    </View>
  );

  const PeriodButton = ({ period, label }) => (
    <TouchableOpacity
      style={[
        styles.periodButton,
        {
          backgroundColor: selectedPeriod === period ? theme.colors.primary : theme.colors.surface,
          borderColor: theme.colors.border,
        }
      ]}
      onPress={() => setSelectedPeriod(period)}
    >
      <Text style={[
        styles.periodButtonText,
        { color: selectedPeriod === period ? theme.colors.textInverse : theme.colors.text }
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>
          Cargando analytics...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <Text style={[styles.headerTitle, { color: theme.colors.text }]}>
          Analytics
        </Text>
        <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
          Tu progreso de productividad
        </Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Period Selector */}
        <View style={[styles.periodContainer, { backgroundColor: theme.colors.surface }]}>
          <Text style={[styles.periodLabel, { color: theme.colors.text }]}>
            Período:
          </Text>
          <View style={styles.periodButtons}>
            <PeriodButton period="week" label="Semana" />
            <PeriodButton period="month" label="Mes" />
            <PeriodButton period="year" label="Año" />
          </View>
        </View>

        {/* Summary Stats */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Resumen General
          </Text>
          <View style={styles.statsGrid}>
            <StatCard
              title="Productividad"
              value={`${analytics.summary.productivity_score || 0}%`}
              subtitle="Puntuación general"
              icon="trending-up"
              color={theme.colors.primary}
              trend={analytics.summary.productivity_trend}
            />
            <StatCard
              title="Tareas Completadas"
              value={analytics.summary.tasks_completed || 0}
              subtitle="de {analytics.summary.total_tasks || 0} totales"
              icon="checkmark-circle"
              color={theme.colors.success}
              trend={analytics.summary.tasks_trend}
            />
            <StatCard
              title="Hábitos Activos"
              value={analytics.summary.habits_active || 0}
              subtitle="de {analytics.summary.total_habits || 0} totales"
              icon="repeat"
              color={theme.colors.warning}
              trend={analytics.summary.habits_trend}
            />
            <StatCard
              title="Sesiones Chat"
              value={analytics.summary.chat_sessions || 0}
              subtitle="interacciones con IA"
              icon="chatbubbles"
              color={theme.colors.primary}
              trend={analytics.summary.chat_trend}
            />
          </View>
        </View>

        {/* Productivity Analytics */}
        {analytics.productivity && Object.keys(analytics.productivity).length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Análisis de Productividad
            </Text>
            <View style={[styles.analyticsCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Horas más productivas:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.productivity.peak_hours || 'N/A'}
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Día más productivo:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.productivity.peak_day || 'N/A'}
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Tiempo promedio por tarea:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.productivity.avg_task_time || 'N/A'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Tasks Analytics */}
        {analytics.tasks && Object.keys(analytics.tasks).length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Análisis de Tareas
            </Text>
            <View style={[styles.analyticsCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Tasa de completación:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.tasks.completion_rate || 0}%
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Categoría más común:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.tasks.top_category || 'N/A'}
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Prioridad promedio:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.tasks.avg_priority || 'N/A'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Habits Analytics */}
        {analytics.habits && Object.keys(analytics.habits).length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Análisis de Hábitos
            </Text>
            <View style={[styles.analyticsCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Tasa de adherencia:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.habits.adherence_rate || 0}%
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Racha más larga:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.habits.longest_streak || 0} días
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Hábito más exitoso:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.habits.most_successful || 'N/A'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Chat Analytics */}
        {analytics.chat && Object.keys(analytics.chat).length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Análisis de Chat
            </Text>
            <View style={[styles.analyticsCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Mensajes enviados:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.chat.messages_sent || 0}
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Intención más común:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.chat.top_intent || 'N/A'}
                </Text>
              </View>
              <View style={styles.analyticsRow}>
                <Text style={[styles.analyticsLabel, { color: theme.colors.textSecondary }]}>
                  Sentimiento promedio:
                </Text>
                <Text style={[styles.analyticsValue, { color: theme.colors.text }]}>
                  {analytics.chat.avg_sentiment || 'N/A'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Insights */}
        {analytics.insights && analytics.insights.length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Insights de IA
            </Text>
            {analytics.insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} index={index} />
            ))}
          </View>
        )}

        {/* Empty State */}
        {!loading && Object.keys(analytics.summary).length === 0 && (
          <View style={styles.emptyContainer}>
            <Ionicons name="analytics-outline" size={64} color={theme.colors.textTertiary} />
            <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
              No hay datos de analytics disponibles
            </Text>
            <Text style={[styles.emptySubtext, { color: theme.colors.textTertiary }]}>
              Comienza a usar la app para ver tus estadísticas
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
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
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
  },
  periodContainer: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.1)',
  },
  periodLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  periodButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  periodButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  periodButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
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
  statHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  trendText: {
    fontSize: 12,
    fontWeight: '500',
    marginLeft: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  statSubtitle: {
    fontSize: 12,
  },
  analyticsCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
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
  analyticsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.05)',
  },
  analyticsLabel: {
    fontSize: 14,
    flex: 1,
  },
  analyticsValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  insightCard: {
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
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  insightText: {
    fontSize: 14,
    lineHeight: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    textAlign: 'center',
  },
});

export default AnalyticsScreen;
