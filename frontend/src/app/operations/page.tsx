"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { 
  Server, Activity, ShieldAlert, CheckCircle, XCircle, Clock
} from 'lucide-react';

interface SystemStatus {
  market_open: boolean;
  market_status: string;
  unresolved_incidents: number;
  providers_error: number;
}

interface Incident {
  id: string;
  timestamp: string;
  severity: string;
  category: string;
  instrument: string | null;
  provider: string | null;
  message: string;
}

export default function OperationsDashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statusData, incidentsData] = await Promise.all([
        api.getOperationsStatus().catch(() => null),
        api.getIncidents().catch(() => null)
      ]);

      if (statusData) setStatus(statusData);
      if (incidentsData) setIncidents(incidentsData);
      setError(null);
    } catch (e) {
      console.error(e);
      setError("Unable to load operations data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 flex h-full items-center justify-center">Loading Operations Center...</div>;
  if (error) return <div className="p-8 flex h-full items-center justify-center text-destructive font-semibold">{error}</div>;

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Operations Center</h1>
        <p className="text-muted-foreground">Monitor system health, market status, and operational reliability.</p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-muted-foreground mb-4">
            <Clock className="w-5 h-5" />
            <h2 className="font-semibold">Market Status</h2>
          </div>
          <p className={`text-2xl font-bold ${status?.market_open ? 'text-green-500' : 'text-yellow-500'}`}>
            {status?.market_status || 'UNKNOWN'}
          </p>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-muted-foreground mb-4">
            <Server className="w-5 h-5" />
            <h2 className="font-semibold">Provider Health</h2>
          </div>
          <p className={`text-2xl font-bold ${status?.providers_error === 0 ? 'text-green-500' : 'text-red-500'}`}>
            {status?.providers_error === 0 ? 'ALL HEALTHY' : `${status?.providers_error} ERRORS`}
          </p>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-muted-foreground mb-4">
            <ShieldAlert className="w-5 h-5" />
            <h2 className="font-semibold">Active Incidents</h2>
          </div>
          <p className={`text-2xl font-bold ${status?.unresolved_incidents === 0 ? 'text-green-500' : 'text-red-500'}`}>
            {status?.unresolved_incidents || 0}
          </p>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-muted-foreground mb-4">
            <CheckCircle className="w-5 h-5" />
            <h2 className="font-semibold">Execution Mode</h2>
          </div>
          <p className="text-2xl font-bold text-blue-500">
            PAPER ONLY
          </p>
          <p className="text-xs text-muted-foreground mt-1">Live execution is HARD LOCKED</p>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4">Recent Incidents</h2>
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="px-6 py-3 font-medium">Timestamp</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Category</th>
                <th className="px-6 py-3 font-medium">Message</th>
              </tr>
            </thead>
            <tbody>
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-4 text-center text-muted-foreground">
                    No active incidents.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr key={inc.id} className="border-t border-border border-b-border last:border-b-0">
                    <td className="px-6 py-4 whitespace-nowrap">
                      {new Date(inc.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        inc.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-500' :
                        inc.severity === 'ERROR' ? 'bg-red-500/20 text-red-500' :
                        inc.severity === 'WARNING' ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-blue-500/20 text-blue-500'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium">{inc.category}</td>
                    <td className="px-6 py-4 text-muted-foreground">{inc.message}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
