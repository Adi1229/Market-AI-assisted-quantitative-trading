"use client";

import { Bell, Search, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function Header() {
  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-border bg-background px-6">
      <div className="flex items-center flex-1">
        <div className="relative w-96 max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search instruments, strategies..."
            className="w-full bg-muted pl-9 shadow-none border-transparent focus-visible:ring-1"
          />
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <Badge variant="outline" className="h-6 font-mono bg-green-500/10 text-green-500 border-green-500/20">
          ● SYSTEM: OPERATIONAL
        </Badge>
        
        <Badge variant="outline" className="h-6 font-mono bg-blue-500/10 text-blue-500 border-blue-500/20" title="LIVE trading is hard-blocked">
          EXECUTION: PAPER ONLY (LIVE LOCKED)
        </Badge>

        <Button variant="ghost" size="icon" className="relative text-muted-foreground">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
        </Button>
        
        <Button variant="ghost" size="icon" className="text-muted-foreground rounded-full bg-muted">
          <User className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
