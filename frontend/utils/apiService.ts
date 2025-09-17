import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DependencyGraph {
  dependency_graph: {
    nodes: Array<{
      id: string;
      name?: string;
      group: number;
      type: string;
      size: number;
    }>;
    links: Array<{
      source: string;
      target: string;
      value: number;
    }>;
  };
}

export interface GitHubAnalysisRequest {
  repo_url: string;
  service: 'gemini' | 'nebius';
  max_files: number;
  include_patterns: string[];
}

export interface AnalysisResponse {
  job_id: string;
  status: string;
  message?: string;
}

export interface AnalysisStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  // Summary information
  summary?: {
    total_files: number;
    critical_issues: number;
    total_issues: number;
    code_quality_score: number;
  };
  // Severity distribution for charts
  severity_distribution?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  // Issues list
  issues?: Array<{
    id: string;
    category: string;
    severity: string;
    title: string;
    description: string;
    file: string;
    line?: number;
    message: string;
    suggestion?: string;
    impact_score?: number;
  }>;
  // Dependency graph data
  dependency_graph?: {
    nodes: Array<{
      id: string;
      name?: string;
      group: number;
      type: string;
      size: number;
    }>;
    links: Array<{
      source: string;
      target: string;
      value: number;
    }>;
  };
}

export interface DependencyGraph {
  dependency_graph: {
    nodes: Array<{
      id: string;
      name?: string;
      group: number;
      type: string;
      size: number;
    }>;
    links: Array<{
      source: string;
      target: string;
      value: number;
    }>;
  };
}

class ApiService {
  private axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  });

  // GitHub Repository Analysis
  async analyzeGitHubRepo(request: GitHubAnalysisRequest): Promise<AnalysisResponse> {
    const response = await this.axiosInstance.post('/api/analyze/github', request);
    return response.data;
  }

  // File Upload Analysis
  async uploadFiles(files: File[]): Promise<AnalysisResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.axiosInstance.post('/api/analyze/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Get Analysis Status
  async getAnalysisStatus(jobId: string): Promise<AnalysisStatus> {
    const response = await this.axiosInstance.get(`/api/status/${jobId}?include_details=true`);
    return response.data;
  }

  // Get Dependency Graph
  async getDependencyGraph(jobId: string): Promise<DependencyGraph> {
    const response = await this.axiosInstance.get(`/api/graph/${jobId}`);
    return response.data;
  }

  // Generate Report
  async generateReport(jobId: string, format: 'json' | 'html' | 'md'): Promise<Blob> {
    const response = await this.axiosInstance.post('/api/report', {
      job_id: jobId,
      format
    }, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; services: Record<string, boolean> }> {
    const response = await this.axiosInstance.get('/api/health');
    return response.data;
  }
}

export const apiService = new ApiService();