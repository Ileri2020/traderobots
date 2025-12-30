import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    CardFooter
} from '@/components/ui/card';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { ArrowUpRight, ArrowDownRight, Activity, Wallet, BarChart3, Bell, RefreshCw, Zap } from 'lucide-react';
import { toast } from 'sonner';

const Dashboard = () => {
    const [accounts, setAccounts] = useState<any[]>([]);
    const [robots, setRobots] = useState<any[]>([]);
    const [tradeLogs, setTradeLogs] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSyncing, setIsSyncing] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [accRes, robotRes, logRes] = await Promise.all([
                axios.get('/api/accounts/'),
                axios.get('/api/robots/'),
                axios.get('/api/logs/')
            ]);
            setAccounts(accRes.data);
            setRobots(robotRes.data);
            setTradeLogs(logRes.data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            toast.error('Failed to load dashboard data');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSync = async () => {
        setIsSyncing(true);
        try {
            await axios.get('/api/accounts/sync/');
            toast.success('Accounts synced with MT5');
            fetchData();
        } catch (error) {
            toast.error('Sync failed. Ensure MT5 is running.');
        } finally {
            setIsSyncing(false);
        }
    };

    const [isStopping, setIsStopping] = useState<{ [key: string]: boolean }>({});

    const handleStopRobot = async (robotId: string) => {
        setIsStopping(prev => ({ ...prev, [robotId]: true }));
        try {
            await axios.patch(`/api/robots/${robotId}/`, { is_active: false });
            toast.success('Robot execution paused');
            fetchData();
        } catch (error) {
            toast.error('Failed to stop robot');
        } finally {
            setIsStopping(prev => ({ ...prev, [robotId]: false }));
        }
    };

    const mainAccount = accounts[0] || { balance: 0, equity: 0, mode: 'OFFLINE' };

    return (
        <div className="flex flex-col gap-8 p-4 md:p-8 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight">Trading Dashboard</h1>
                    <p className="text-muted-foreground mt-1">Real-time performance of your automated strategies.</p>
                </div>
                <div className="flex items-center gap-3 bg-muted/50 p-1.5 rounded-2xl border border-border">
                    <div className="px-4 py-1.5 bg-background rounded-xl border border-border shadow-sm">
                        <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest block">Account Mode</span>
                        <span className={cn(
                            "text-xs font-bold flex items-center gap-1.5",
                            mainAccount.mode === 'LIVE' ? "text-red-500" : "text-green-500"
                        )}>
                            <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", mainAccount.mode === 'LIVE' ? "bg-red-500" : "bg-green-500")} />
                            {mainAccount.mode}
                        </span>
                    </div>
                    <Button
                        size="sm"
                        onClick={handleSync}
                        disabled={isSyncing}
                        className="rounded-xl px-4 font-bold shadow-lg shadow-primary/20 gap-2"
                    >
                        <RefreshCw className={cn("h-4 w-4", isSyncing && "animate-spin")} />
                        {isSyncing ? "Syncing..." : "Sync MT5"}
                    </Button>
                </div>
            </header>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'Total Balance', value: `$${mainAccount.balance.toLocaleString()}`, sub: '+2.4% today', icon: Wallet, trend: 'up' },
                    { label: 'Equity', value: `$${mainAccount.equity.toLocaleString()}`, sub: '99.4% margin', icon: Activity, trend: 'up' },
                    { label: 'Active Robots', value: robots.length.toString(), sub: 'Running...', icon: BarChart3, trend: 'up' },
                    { label: 'MT5 Accounts', value: accounts.length.toString(), sub: 'Connected', icon: Activity, trend: 'up' }
                ].map((stat, i) => (
                    <Card key={i} className="border-border/60 bg-card/50 backdrop-blur-sm overflow-hidden relative">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{stat.label}</CardTitle>
                            <stat.icon className="h-4 w-4 text-primary opacity-70" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold tracking-tight">{stat.value}</div>
                            <div className={cn(
                                "flex items-center gap-1 text-[11px] font-bold mt-2",
                                stat.trend === 'up' ? "text-green-500" : "text-destructive"
                            )}>
                                {stat.trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                                {stat.sub}
                            </div>
                        </CardContent>
                        <div className="absolute top-0 right-0 p-2 opacity-5">
                            <stat.icon className="h-16 w-16" />
                        </div>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active Robots */}
                <Card className="lg:col-span-2 border-border/60">
                    <CardHeader className="flex flex-row items-center justify-between pb-6">
                        <div>
                            <CardTitle>Your Fleet</CardTitle>
                            <CardDescription>Status of your AI trading algorithms.</CardDescription>
                        </div>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="overflow-x-auto">
                            <Table>
                                <TableHeader className="bg-muted/50">
                                    <TableRow>
                                        <TableHead className="px-6 py-4">ROBOT NAME</TableHead>
                                        <TableHead>PAIR</TableHead>
                                        <TableHead>WIN RATE</TableHead>
                                        <TableHead>METHOD</TableHead>
                                        <TableHead className="text-right px-6">ACTION</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {robots.length > 0 ? robots.map((robot) => (
                                        <TableRow key={robot.id} className="hover:bg-muted/20 transition-colors">
                                            <TableCell className="px-6 py-4">
                                                <div className="flex flex-col">
                                                    <span className="font-bold">Bot {robot.symbol}</span>
                                                    <span className="text-[10px] text-muted-foreground font-mono">ID: {robot.id?.toString().slice(0, 8)}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="font-mono font-bold text-xs">{robot.symbol}</TableCell>
                                            <TableCell>
                                                <div className="flex flex-col gap-1.5 w-24">
                                                    <div className="flex justify-between text-[10px] font-bold">
                                                        <span>Win Rate</span>
                                                        <span>{robot.win_rate}%</span>
                                                    </div>
                                                    <Progress value={robot.win_rate} className="h-1" />
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge className="font-mono font-bold bg-primary/10 text-primary border-none uppercase">
                                                    {robot.method}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-right px-6">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="text-destructive font-bold hover:bg-destructive/10"
                                                    onClick={() => handleStopRobot(robot.id)}
                                                    disabled={isStopping[robot.id]}
                                                >
                                                    {isStopping[robot.id] ? "STOPPING..." : "STOP"}
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    )) : (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-12 text-muted-foreground italic">
                                                No robots created yet. Head over to the Robots page!
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </CardContent>
                </Card>

                {/* Recent Notifications / Trades */}
                <Card className="lg:col-span-1 border-border/60">
                    <CardHeader className="pb-4">
                        <div className="flex items-center justify-between">
                            <CardTitle>Trade Logs</CardTitle>
                            <Bell className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <CardDescription>Latest executions across all robots.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-6">
                        {isLoading ? (
                            <Zap className="animate-pulse h-8 w-8 text-primary mx-auto" />
                        ) : (
                            tradeLogs.length > 0 ? tradeLogs.slice(0, 5).map((log) => (
                                <div key={log.id} className="flex items-start gap-4 pb-4 border-b border-border last:border-0 last:pb-0">
                                    <div className={cn(
                                        "p-2 rounded-lg",
                                        log.action === 'BUY' ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                                    )}>
                                        {log.action === 'BUY' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                                    </div>
                                    <div className="flex flex-col flex-1">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm font-extrabold uppercase">{log.action} {log.symbol}</span>
                                            <span className="text-[10px] font-bold text-muted-foreground">{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-0.5">Exec: @ {log.price} • Profit: ${log.profit}</p>
                                    </div>
                                </div>
                            )) : (
                                <p className="text-center text-xs text-muted-foreground italic py-8">No recent trades executed.</p>
                            )
                        )}
                    </CardContent>
                    <CardFooter className="pt-0 border-t-0">
                        <Button
                            variant="outline"
                            className="w-full text-xs font-bold text-muted-foreground h-9"
                            onClick={() => toast.info('Full audit log feature coming soon to Pro users.')}
                        >
                            View Full Audit Log
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
};

export default Dashboard;
