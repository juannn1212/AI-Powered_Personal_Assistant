import axios from 'axios';

// Create axios instance
export const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Change this to your backend URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshResponse = await api.post('/auth/refresh');
        const { access_token } = refreshResponse.data;

        // Update token in storage
        localStorage.setItem('auth_token', access_token);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refresh: () => api.post('/auth/refresh'),
  me: () => api.get('/auth/me'),
  updateProfile: (userData) => api.put('/auth/me', userData),
};

export const assistantAPI = {
  chat: (message, context) => api.post('/assistant/chat', { message, context }),
  getConversations: (limit = 20) => api.get(`/assistant/conversations?limit=${limit}`),
  getTaskSuggestions: () => api.post('/assistant/suggestions/tasks'),
  analyzeProductivity: () => api.get('/assistant/analytics/productivity'),
  transcribeVoice: (audioFile) => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    return api.post('/assistant/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  analyzeIntent: (message) => api.get(`/assistant/intent/analyze?message=${encodeURIComponent(message)}`),
};

export const calendarAPI = {
  getEvents: (startDate, endDate) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return api.get(`/calendar/events?${params.toString()}`);
  },
  createEvent: (eventData) => api.post('/calendar/events', eventData),
  updateEvent: (eventId, eventData) => api.put(`/calendar/events/${eventId}`, eventData),
  deleteEvent: (eventId) => api.delete(`/calendar/events/${eventId}`),
  getEvent: (eventId) => api.get(`/calendar/events/${eventId}`),
  checkConflicts: (startTime, endTime) => {
    const params = new URLSearchParams({
      start_time: startTime,
      end_time: endTime,
    });
    return api.get(`/calendar/schedule/conflicts?${params.toString()}`);
  },
  getSuggestions: (durationMinutes) => {
    const params = new URLSearchParams({
      duration_minutes: durationMinutes,
    });
    return api.get(`/calendar/schedule/suggestions?${params.toString()}`);
  },
};

export const analyticsAPI = {
  trackDaily: (analyticsData) => api.post('/analytics/track', analyticsData),
  getDashboard: (days = 30) => api.get(`/analytics/dashboard?days=${days}`),
  getInsights: () => api.get('/analytics/insights'),
  getPredictions: () => api.get('/analytics/predictions'),
  comparePeriods: (period1Start, period1End, period2Start, period2End) => {
    const params = new URLSearchParams({
      period1_start: period1Start,
      period1_end: period1End,
      period2_start: period2Start,
      period2_end: period2End,
    });
    return api.get(`/analytics/comparison?${params.toString()}`);
  },
};

// Error handling utility
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.detail || 'Datos inválidos';
      case 401:
        return 'No autorizado. Por favor, inicia sesión.';
      case 403:
        return 'Acceso denegado';
      case 404:
        return 'Recurso no encontrado';
      case 422:
        return data.detail || 'Datos de validación incorrectos';
      case 500:
        return 'Error interno del servidor';
      default:
        return data.detail || 'Error desconocido';
    }
  } else if (error.request) {
    // Network error
    return 'Error de conexión. Verifica tu conexión a internet.';
  } else {
    // Other error
    return error.message || 'Error desconocido';
  }
};

// Success response utility
export const handleAPISuccess = (response) => {
  return {
    success: true,
    data: response.data,
    message: response.data.message || 'Operación exitosa',
  };
};
