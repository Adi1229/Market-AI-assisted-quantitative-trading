"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Play, TrendingUp, AlertTriangle, Briefcase, Hash, Activity } from "lucide-react";

export default function BacktestingPage() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    strategy_id: "",
    symbol: "RELIANCE",
    start_date: "2020-01-01",
    end_date: "2023-01-01",
    initial_capital: 100000,
  });

  useEffect(() => {
    api.getStrategies().then(data => {
      setStrategies(data);
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, strategy_id: data[0].id }));
      }
    });
  }, []);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.runBacktest({
        ...formData,
        start_date: formData.start_date + "T00:00:00",
        end_date: formData.end_date + "T00:00:00",
        parameters: {}
      });
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Backtesting Engine</h2>
        <p className="text-muted-foreground">
          Validate quantitative strategies chronologically against historical data.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Setup your backtest run</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleRunBacktest} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Strategy</label>
                <select 
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={formData.strategy_id}
                  onChange={e => setFormData({...formData, strategy_id: e.target.value})}
                  required
                >
                  <option value="" disabled>Select a strategy</option>
                  {strategies.map(s => (
                    <option key={s.id} value={s.id} className="text-foreground bg-background">{s.name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Symbol</label>
                <Input 
                  value={formData.symbol} 
                  onChange={e => setFormData({...formData, symbol: e.target.value})} 
                  required 
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Start Date</label>
                <Input 
                  type="date" 
                  value={formData.start_date} 
                  onChange={e => setFormData({...formData, start_date: e.target.value})} 
                  required 
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">End Date</label>
                <Input 
                  type="date" 
                  value={formData.end_date} 
                  onChange={e => setFormData({...formData, end_date: e.target.value})} 
                  required 
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Initial Capital</label>
                <Input 
                  type="number" 
                  value={formData.initial_capital} 
                  onChange={e => setFormData({...formData, initial_capital: Number(e.target.value)})} 
                  required 
                />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Running..." : <><Play className="mr-2 h-4 w-4" /> Run Backtest</>}
              </Button>

              {error && (
                <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                  {error}
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        <div className="md:col-span-2 space-y-6">
          <Card className="h-full min-h-[400px]">
            <CardHeader>
              <CardTitle>Results</CardTitle>
              <CardDescription>
                {result ? `Backtest completed for ${result.symbol} using ${result.strategy_id}` : "Run a backtest to view results"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Total Return</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {(result.total_return * 100).toFixed(2)}%
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">CAGR</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {(result.cagr * 100).toFixed(2)}%
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
                      <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {result.sharpe_ratio.toFixed(2)}
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
                      <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-destructive">
                        -{(result.max_drawdown * 100).toFixed(2)}%
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                      <Briefcase className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {(result.win_rate * 100).toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
                      <Hash className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {result.total_trades}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="flex h-full min-h-[300px] items-center justify-center text-muted-foreground font-semibold">
                  NO BACKTEST RESULT
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
