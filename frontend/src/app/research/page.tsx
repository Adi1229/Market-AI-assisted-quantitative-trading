"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { 
  Play, Pause, Square, AlertCircle, TrendingUp, CheckCircle, XCircle
} from 'lucide-react';

interface Session {
  id: string;
  name: string;
  status: string;
  starting_capital: number;
  current_capital: number;
  execution_mode: string;
}

interface DailyReport {
  date: string;
  portfolio_value: number;
  daily_pnl: number;
  daily_return_pct: number;
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  message: string;
}

export default function ResearchDashboard() {
  const [session, setSession] = useState<Session | null>(null);
  const [report, setReport] = useState<DailyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [sessionData, reportData] = await Promise.all([
        api.getCurrentSession().catch(() => null),
        api.getDailyReport().catch(() => null)
      ]);

      if (sessionData && sessionData.status !== "NO_SESSION") {
        setSession(sessionData);
      } else {
        setSession(null);
      }

      if (reportData) {
        setReport(reportData);
      }
      setError(null);
    } catch (e) {
      console.error(e);
      setError("Unable to load research data");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: 'start' | 'pause' | 'resume' | 'end') => {
    try {
      if (action === 'start') {
        await api.manageSession({ action, name: 'Ops Session' });
      } else if (session) {
        await api.manageSession({ action });
      }
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return <div className="p-8 flex h-full items-center justify-center">Loading Research Dashboard...</div>;
  }
  
  if (error) {
    return <div className="p-8 flex h-full items-center justify-center text-destructive font-semibold">{error}</div>;
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Paper Trading Operations</h1>
        <p className="text-muted-foreground">Manage active paper sessions and monitor strategy intelligence.</p>
      </div>

      {/* Session Controls */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold mb-1">Session Status: {session ? session.status : 'INACTIVE'}</h2>
            {session && <p className="text-sm text-muted-foreground">ID: {session.id}</p>}
          </div>
          <div className="flex space-x-4">
            {!session || session.status === 'COMPLETED' ? (
              <button 
                onClick={() => handleAction('start')}
                className="flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                <Play className="w-4 h-4 mr-2" /> Start Session
              </button>
            ) : (
              <>
                {session.status === 'ACTIVE' ? (
                  <button 
                    onClick={() => handleAction('pause')}
                    className="flex items-center px-4 py-2 bg-yellow-500/10 text-yellow-500 rounded-md hover:bg-yellow-500/20 transition-colors"
                  >
                    <Pause className="w-4 h-4 mr-2" /> Pause
                  </button>
                ) : (
                  <button 
                    onClick={() => handleAction('resume')}
                    className="flex items-center px-4 py-2 bg-primary/10 text-primary rounded-md hover:bg-primary/20 transition-colors"
                  >
                    <Play className="w-4 h-4 mr-2" /> Resume
                  </button>
                )}
                <button 
                  onClick={() => handleAction('end')}
                  className="flex items-center px-4 py-2 bg-destructive/10 text-destructive rounded-md hover:bg-destructive/20 transition-colors"
                >
                  <Square className="w-4 h-4 mr-2" /> End
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Daily Report */}
      {report && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Daily Report (UTC)</h2>
          {report.message === 'INSUFFICIENT SAMPLE SIZE' ? (
            <div className="flex items-center p-4 bg-yellow-500/10 text-yellow-500 rounded-md border border-yellow-500/20">
              <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
              <div>
                <p className="font-medium">Insufficient Sample Size</p>
                <p className="text-sm opacity-90">Only {report.total_trades} trades executed today. Statistically significant reporting requires minimum 3 trades.</p>
              </div>
            </div>
          ) : report.message === 'NO TRADES TODAY' ? (
            <div className="flex items-center p-4 bg-muted text-muted-foreground rounded-md border border-border">
              <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
              <div>
                <p className="font-medium">No Trades Executed Today</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-6">
              <div className="p-4 bg-background rounded-md border border-border">
                <p className="text-sm text-muted-foreground mb-1">Daily PnL</p>
                <p className={`text-2xl font-bold ${report.daily_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${report.daily_pnl.toFixed(2)}
                </p>
              </div>
              <div className="p-4 bg-background rounded-md border border-border">
                <p className="text-sm text-muted-foreground mb-1">Return</p>
                <p className={`text-2xl font-bold ${report.daily_return_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {report.daily_return_pct.toFixed(2)}%
                </p>
              </div>
              <div className="p-4 bg-background rounded-md border border-border">
                <p className="text-sm text-muted-foreground mb-1">Win Rate</p>
                <p className="text-2xl font-bold">
                  {(report.win_rate * 100).toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-background rounded-md border border-border">
                <p className="text-sm text-muted-foreground mb-1">Total Trades</p>
                <p className="text-2xl font-bold">{report.total_trades}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Placeholder for Advanced Analytics (Phase 14 integration point) */}
      <div className="grid grid-cols-2 gap-8">
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Signal Funnel</h2>
          <div className="flex items-center justify-center h-48 text-muted-foreground border-2 border-dashed border-border rounded-md">
            Data Collection in Progress
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">AI Effectiveness</h2>
          <div className="flex items-center justify-center h-48 text-muted-foreground border-2 border-dashed border-border rounded-md">
            Data Collection in Progress
          </div>
        </div>
      </div>
    </div>
  );
}
