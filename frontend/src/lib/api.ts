import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

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
};
