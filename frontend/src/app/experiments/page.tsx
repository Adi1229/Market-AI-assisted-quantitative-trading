"use client";

import { useState, useEffect } from 'react';
import { 
  Beaker, Play, Square, Settings, ShieldAlert, BarChart2
} from 'lucide-react';

interface Experiment {
  experiment_id: string;
  name: string;
  start_time: string;
  starting_capital: number;
  execution_mode: string;
  data_provider: string;
  timeframe: string;
  status: string;
}

export default function ExperimentsDashboard() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/experiments');
      if (res.ok) {
        setExperiments(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const createExperiment = async () => {
    setCreating(true);
    try {
      const payload = {
        name: `Experiment-${new Date().toISOString().split('T')[0]}`,
        starting_capital: 100000.0,
        execution_mode: "PAPER",
        data_provider: "upstox",
        timeframe: "5m",
        watchlist: ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"],
        strategies: [
          { name: "MomentumStrategy", version: "1.0", params: { lookback: 20 } },
          { name: "MeanReversionStrategy", version: "1.0", params: { lookback: 20 } }
        ],
        decision_modes: ["STRATEGY_ONLY", "HYBRID"],
        risk_configuration: { max_position_size: 20000.0 },
        ai_provider: "mock"
      };

      const res = await fetch('http://localhost:8000/api/v1/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="p-8">Loading Experiments...</div>;

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Live Paper Experiments</h1>
          <p className="text-muted-foreground">Run statistically honest long-term paper trading tests.</p>
        </div>
        <button 
          onClick={createExperiment}
          disabled={creating}
          className="bg-blue-600 text-white px-4 py-2 rounded font-medium flex items-center space-x-2 disabled:opacity-50"
        >
          <Beaker className="w-5 h-5" />
          <span>{creating ? 'Creating...' : 'New Experiment'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {experiments.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground bg-card border border-border rounded-lg">
            No experiments found. Create one to begin.
          </div>
        ) : (
          experiments.map((exp) => (
            <div key={exp.experiment_id} className="bg-card border border-border rounded-lg p-6 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <h2 className="font-semibold text-lg">{exp.name}</h2>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    exp.status === 'ACTIVE' ? 'bg-green-500/20 text-green-500' :
                    exp.status === 'PLANNED' ? 'bg-blue-500/20 text-blue-500' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {exp.status}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Provider</span>
                    <span className="font-medium">{exp.data_provider} ({exp.timeframe})</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Mode</span>
                    <span className="font-bold text-blue-500">{exp.execution_mode}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Started</span>
                    <span>{new Date(exp.start_time).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-border flex justify-end space-x-2">
                <button className="text-muted-foreground hover:text-foreground p-2">
                  <BarChart2 className="w-5 h-5" />
                </button>
                <button className="text-muted-foreground hover:text-foreground p-2">
                  <Settings className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
