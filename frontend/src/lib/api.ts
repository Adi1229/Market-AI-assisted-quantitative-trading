import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Market
  getInstruments: () => apiClient.get('/instruments').then(res => res.data),
  
  // Strategies
  getStrategies: () => apiClient.get('/strategies').then(res => res.data),
  getStrategy: (id: string) => apiClient.get(`/strategies/${id}`).then(res => res.data),
  activateStrategy: (id: string) => apiClient.post(`/strategies/${id}/activate`).then(res => res.data),
  deactivateStrategy: (id: string) => apiClient.post(`/strategies/${id}/deactivate`).then(res => res.data),
  
  // Portfolio
  getPortfolioSummary: () => apiClient.get('/portfolio/summary').then(res => res.data),
  getPositions: () => apiClient.get('/portfolio/positions').then(res => res.data),
  getOrders: () => apiClient.get('/portfolio/orders').then(res => res.data),
  
  // Signals & Opportunities
  getOpportunities: () => apiClient.get('/opportunities').then(res => res.data),
  approveOpportunity: (id: string, currentPrice: number) => 
    apiClient.post(`/opportunities/${id}/approve`, { current_price: currentPrice }).then(res => res.data),
  ignoreOpportunity: (id: string, currentPrice: number) => 
    apiClient.post(`/opportunities/${id}/ignore`, { current_price: currentPrice }).then(res => res.data),
    
  // Mock Opportunity Generator
  generateMockOpportunity: () => apiClient.post('/test/generate_mock_opportunity').then(res => res.data),
  
  // Backtesting
  runBacktest: (data: any) => apiClient.post('/backtests', data).then(res => res.data),

  // Operations
  getOperationsStatus: () => apiClient.get('/operations/status').then(res => res.data),
  getOperationsHealth: () => apiClient.get('/operations/health').then(res => res.data),
  getProvidersHealth: () => apiClient.get('/operations/providers').then(res => res.data),
  getMarketDataHealth: () => apiClient.get('/operations/market-data').then(res => res.data),
  getHeartbeats: () => apiClient.get('/operations/heartbeat').then(res => res.data),
  getIncidents: (resolved = false) => apiClient.get(`/operations/incidents?resolved=${resolved}`).then(res => res.data),
  
  // Research
  getResearchSummary: () => apiClient.get('/research/summary').then(res => res.data),
  getCurrentSession: () => apiClient.get('/research/sessions/current').then(res => res.data),
  getDailyReport: () => apiClient.get('/research/daily-report').then(res => res.data),
  manageSession: (data: any) => apiClient.post('/research/sessions', data).then(res => res.data),
  
  // Experiments
  getExperiments: () => apiClient.get('/experiments').then(res => res.data),
  getExperiment: (id: string) => apiClient.get(`/experiments/${id}`).then(res => res.data),
  createExperiment: (data: any) => apiClient.post('/experiments', data).then(res => res.data),
};
