"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, Play, Square, Settings2 } from "lucide-react";

export default function StrategyStudio() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const data = await api.getStrategies();
      setStrategies(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load strategies");
    } finally {
      setLoading(false);
    }
  };

  const toggleStrategy = async (id: string, currentStatus: string) => {
    try {
      if (currentStatus === "ACTIVE") {
        await api.deactivateStrategy(id);
      } else {
        await api.activateStrategy(id);
      }
      fetchStrategies();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="flex h-full items-center justify-center">Loading strategies...</div>;
  if (error) return <div className="flex h-full items-center justify-center text-destructive font-semibold">{error}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Strategy Studio</h2>
        <p className="text-muted-foreground">
          Manage quantitative strategies and execution engines.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {strategies.map(strat => (
          <Card key={strat.id} className="flex flex-col">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-xl">{strat.name}</CardTitle>
                <Badge variant={strat.status === "ACTIVE" ? "default" : "secondary"}>
                  {strat.status}
                </Badge>
              </div>
              <CardDescription>Version {strat.version}</CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <p className="text-sm text-muted-foreground">{strat.description}</p>
              
              <div className="mt-4 flex items-center space-x-2 text-sm">
                <Activity className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Status: </span>
                <span className="font-medium text-foreground">Operational</span>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between border-t border-border pt-4">
              <Button variant="outline" size="sm">
                <Settings2 className="mr-2 h-4 w-4" />
                Configure
              </Button>
              <Button 
                variant={strat.status === "ACTIVE" ? "destructive" : "default"}
                size="sm"
                onClick={() => toggleStrategy(strat.id, strat.status)}
              >
                {strat.status === "ACTIVE" ? (
                  <>
                    <Square className="mr-2 h-4 w-4" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Activate
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
