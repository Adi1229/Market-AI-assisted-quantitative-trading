"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Wallet, TrendingUp, AlertTriangle } from "lucide-react";

export default function PortfolioPage() {
  const [summary, setSummary] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [sumData, posData, ordData] = await Promise.all([
        api.getPortfolioSummary(),
        api.getPositions(),
        api.getOrders()
      ]);
      setSummary(sumData);
      setPositions(posData);
      setOrders(ordData);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load portfolio");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex h-full items-center justify-center">Loading portfolio...</div>;
  if (error) return <div className="flex h-full items-center justify-center text-destructive font-semibold">{error}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Paper Portfolio</h2>
        <p className="text-muted-foreground">
          Monitor your virtual holdings and execution history.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cash Balance</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${summary?.cash?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Available for trading</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Position Value</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(summary?.total_value - summary?.cash)?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Value of {summary?.open_positions} open positions</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Unrealized PnL</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${summary?.total_pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
              {summary?.total_pnl >= 0 ? "+" : ""}${summary?.total_pnl?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="positions" className="w-full">
        <TabsList>
          <TabsTrigger value="positions">Open Positions</TabsTrigger>
          <TabsTrigger value="orders">Order History</TabsTrigger>
        </TabsList>
        <TabsContent value="positions" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Current Holdings</CardTitle>
              <CardDescription>All active positions in your paper portfolio.</CardDescription>
            </CardHeader>
            <CardContent>
              {positions.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">No open positions</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Entry Price</TableHead>
                      <TableHead>Current Price</TableHead>
                      <TableHead className="text-right">Unrealized PnL</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {positions.map(pos => {
                      const isPositive = pos.unrealized_pnl >= 0;
                      return (
                        <TableRow key={pos.instrument_id}>
                          <TableCell className="font-bold">{pos.instrument_id}</TableCell>
                          <TableCell>{pos.quantity}</TableCell>
                          <TableCell>${pos.entry_price.toFixed(2)}</TableCell>
                          <TableCell>${pos.current_price.toFixed(2)}</TableCell>
                          <TableCell className={`text-right font-medium ${isPositive ? "text-green-500" : "text-red-500"}`}>
                            {isPositive ? "+" : ""}{pos.unrealized_pnl.toFixed(2)}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="orders" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
              <CardDescription>Past orders executed by the engine.</CardDescription>
            </CardHeader>
            <CardContent>
              {orders.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">No order history found</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Side</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Fill Price</TableHead>
                      <TableHead className="text-right">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orders.map(order => (
                      <TableRow key={order.order_id}>
                        <TableCell>{new Date(order.timestamp).toLocaleString()}</TableCell>
                        <TableCell className="font-bold">{order.instrument_id}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={order.direction === "BUY" ? "text-green-500" : "text-red-500"}>
                            {order.direction}
                          </Badge>
                        </TableCell>
                        <TableCell>{order.quantity}</TableCell>
                        <TableCell>${order.fill_price ? order.fill_price.toFixed(2) : "-"}</TableCell>
                        <TableCell className="text-right">
                          <Badge className="bg-green-500/10 text-green-500 border-green-500/20">{order.status}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
