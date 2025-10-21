/**
 * API Client for PLAF LMS
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Student {
  id_student: number;
  email: string;
  first_name: string;
  last_name: string;
  risk_probability?: number;
  is_at_risk?: boolean;
  num_days_active?: number;
  total_clicks?: number;
  avg_score?: number;
  code_module?: string;
  code_presentation?: string;
  gender?: string;
  region?: string;
  age_band?: string;
  highest_education?: string;
  studied_credits?: number;
  disability?: string;
}

export interface ChatMessage {
  id?: number;
  student_id: number;
  message: string;
  response: string;
  timestamp: string;
}

export interface CourseMaterial {
  id_site: number;
  code_module: string;
  code_presentation: string;
  activity_type: string;
  week_from?: number;
  week_to?: number;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{ success: boolean; student: Student }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, first_name: string, last_name: string) {
    return this.request<{ success: boolean; student: Student }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, first_name, last_name }),
    });
  }

  // Student endpoints
  async getStudent(studentId: number) {
    return this.request<{
      student: Student;
      activities: any[];
      assessments: any[];
    }>(`/api/student/${studentId}`);
  }

  async getStudentCourses(studentId: number) {
    return this.request<{ courses: any[] }>(`/api/student/${studentId}/courses`);
  }

  async getCourseMaterials(studentId: number) {
    return this.request<{ materials: CourseMaterial[] }>(`/api/student/${studentId}/materials`);
  }

  // Chat endpoints
  async sendMessage(studentId: number, message: string, conversationContext?: string) {
    return this.request<{ response: string; context: string }>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        student_id: studentId,
        message,
        conversation_context: conversationContext,
      }),
    });
  }

  async getChatHistory(studentId: number, limit: number = 10) {
    return this.request<{ history: ChatMessage[] }>(`/api/student/${studentId}/chat-history?limit=${limit}`);
  }

  async clearChatHistory(studentId: number) {
    return this.request<{ success: boolean }>(`/api/student/${studentId}/chat-history`, {
      method: 'DELETE',
    });
  }

  // Advice endpoint
  async getAdvice(studentId: number) {
    return this.request<any>('/api/advice', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId }),
    });
  }
}

export const api = new APIClient();

