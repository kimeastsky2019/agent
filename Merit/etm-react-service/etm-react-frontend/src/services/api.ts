import axios, { AxiosInstance, AxiosError } from 'axios';

export interface Scenario {
  id: number;
  title: string;
  area_code: string;
  end_year: number;
  created_at: string;
  updated_at: string;
}

export interface GQueryResult {
  present: number;
  future: number;
  unit: string;
}

export interface ScenarioInput {
  area_code: string;
  end_year: number;
  title?: string;
}

export interface InputUpdate {
  [key: string]: number;
}

export interface Area {
  code: string;
  name: string;
  [key: string]: unknown;
}

export interface Input {
  key: string;
  name: string;
  [key: string]: unknown;
}

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class ETMAPIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = '/dt/api/v3') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds timeout
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        return this.handleError(error);
      }
    );
  }

  private handleError(error: AxiosError): Promise<never> {
    if (error.code === 'ECONNABORTED') {
      throw new APIError(
        'Request timeout. Please check your connection and try again.',
        undefined,
        error
      );
    }

    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as { error?: string; errors?: Record<string, string[]> };
      
      // Handle validation errors (422, 400, etc.)
      if (data.errors && typeof data.errors === 'object') {
        const errorMessages = Object.entries(data.errors)
          .map(([field, messages]) => {
            const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            return `${fieldName}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
          })
          .join('; ');
        
        throw new APIError(
          errorMessages || `API Error (${status}): Validation failed`,
          status,
          error
        );
      }
      
      const message =
        data.error ||
        error.message ||
        'An error occurred';

      throw new APIError(
        `API Error (${status}): ${message}`,
        status,
        error
      );
    } else if (error.request) {
      // Request was made but no response received
      throw new APIError(
        'Network error. Please check your connection and try again.',
        undefined,
        error
      );
    } else {
      // Something else happened
      throw new APIError(
        error.message || 'An unexpected error occurred',
        undefined,
        error
      );
    }
  }

  // Scenario Management
  async createScenario(input: ScenarioInput): Promise<Scenario> {
    const response = await this.client.post('/scenarios', {
      scenario: input,
    });
    return response.data;
  }

  async getScenario(scenarioId: number): Promise<Scenario> {
    const response = await this.client.get(`/scenarios/${scenarioId}`);
    return response.data;
  }

  async updateScenario(
    scenarioId: number,
    userValues: InputUpdate
  ): Promise<Scenario> {
    const response = await this.client.put(`/scenarios/${scenarioId}`, {
      scenario: {
        user_values: userValues,
      },
    });
    return response.data;
  }

  async deleteScenario(scenarioId: number): Promise<void> {
    await this.client.delete(`/scenarios/${scenarioId}`);
  }

  // Query Results - Use dashboard endpoint which includes gquery results
  async getGQuery(
    scenarioId: number,
    gqueryKey: string
  ): Promise<GQueryResult> {
    const batchResults = await this.getBatchGQueries(scenarioId, [gqueryKey]);
    return batchResults[gqueryKey] || { present: 0, future: 0, unit: 'unknown' };
  }

  async getBatchGQueries(
    scenarioId: number,
    gqueryKeys: string[]
  ): Promise<Record<string, GQueryResult>> {
    if (gqueryKeys.length === 0) {
      return {};
    }
    
    try {
      // Use dashboard endpoint with gqueries as query parameters
      const queryParams = gqueryKeys
        .map((key) => `gqueries[]=${encodeURIComponent(key)}`)
        .join('&');
      
      const response = await this.client.put(
        `/scenarios/${scenarioId}/dashboard?${queryParams}`
      );
      const dashboard = response.data;
      
      const results: Record<string, GQueryResult> = {};
      
      // Dashboard response structure: { scenario: {...}, gqueries: {...} }
      if (dashboard && dashboard.gqueries) {
        gqueryKeys.forEach((key) => {
          const gquery = dashboard.gqueries[key];
          if (gquery) {
            // Handle different response formats
            if (typeof gquery === 'object') {
              results[key] = {
                present: gquery.present || gquery.value || 0,
                future: gquery.future || gquery.value || 0,
                unit: gquery.unit || 'unknown',
              };
            } else if (typeof gquery === 'number') {
              results[key] = {
                present: gquery,
                future: gquery,
                unit: 'unknown',
              };
            } else {
              results[key] = { present: 0, future: 0, unit: 'unknown' };
            }
          } else {
            results[key] = { present: 0, future: 0, unit: 'unknown' };
          }
        });
      } else {
        // Fallback: return default values
        gqueryKeys.forEach((key) => {
          results[key] = { present: 0, future: 0, unit: 'unknown' };
        });
      }
      
      return results;
    } catch (error) {
      console.error('Failed to fetch batch gqueries:', error);
      // Return default values for all keys
      const results: Record<string, GQueryResult> = {};
      gqueryKeys.forEach((key) => {
        results[key] = { present: 0, future: 0, unit: 'unknown' };
      });
      return results;
    }
  }

  // Available Areas
  async getAreas(): Promise<Area[]> {
    const response = await this.client.get('/areas');
    return response.data as Area[];
  }

  // Input Definitions
  async getInputs(): Promise<Input[]> {
    const response = await this.client.get('/inputs');
    return response.data as Input[];
  }

  // List Scenarios
  async listScenarios(): Promise<Scenario[]> {
    const response = await this.client.get('/scenarios');
    // Handle pagination response format
    if (response.data && typeof response.data === 'object') {
      if (Array.isArray(response.data)) {
        return response.data as Scenario[];
      }
      // Handle pagination format: { data: [...], meta: {...} }
      if (response.data.data && Array.isArray(response.data.data)) {
        return response.data.data as Scenario[];
      }
      // Handle collection format: { scenarios: [...] }
      if (response.data.scenarios && Array.isArray(response.data.scenarios)) {
        return response.data.scenarios as Scenario[];
      }
    }
    return [];
  }
}

// Singleton instance
const apiClient = new ETMAPIClient();

export default apiClient;
