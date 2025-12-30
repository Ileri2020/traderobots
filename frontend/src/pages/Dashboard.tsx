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
import {
    ArrowUpRight,
    ArrowDownRight,
    Activity,
    Wallet,
    BarChart3,
    Bell,
    RefreshCw,
    Zap,
    TrendingUp,
    Code
} from 'lucide-react';
import { toast } from 'sonner';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";


const Dashboard = () => {
    const [accounts, setAccounts] = useState<any[]>([]);
    const [robots, setRobots] = useState<any[]>([]);
    const [tradeLogs, setTradeLogs] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSyncing, setIsSyncing] = useState(false);

    // New State for Robot Control
    const [selectedRobot, setSelectedRobot] = useState<any>(null);
    const [showTradeModal, setShowTradeModal] = useState(false);
    const [tradeConfig, setTradeConfig] = useState({ lot: 0.1, sl: 300, tp: 600 });
    const [isDeploying, setIsDeploying] = useState(false);

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

    const handleAutoTrade = async () => {
        if (!selectedRobot || !accounts[0]) return;
        setIsDeploying(true);
        try {
            await axios.post(`/api/robots/${selectedRobot.id}/deploy/`, {
                account_id: accounts[0].id,
                lot: tradeConfig.lot,
                sl: tradeConfig.sl,
                tp: tradeConfig.tp
            });
            toast.success("Order Placed Successfully!", {
                description: `Bot ${selectedRobot.symbol} is now executing with ${tradeConfig.lot} lot.`
            });
            setShowTradeModal(false);
            fetchData();
        } catch (error: any) {
            const msg = error.response?.data?.error || "Failed to execute trade on MT5.";
            toast.error("MT5 Execution Failed", { description: msg });
        } finally {
            setIsDeploying(false);
        }
    };

    const handleCopyCode = (type: 'mql5' | 'python') => {
        if (!selectedRobot) return;
        const code = type === 'mql5' ? selectedRobot.mql5_code : selectedRobot.python_code;
        if (code) {
            navigator.clipboard.writeText(code);
            toast.success(`${type.toUpperCase()} Code copied!`);
        } else {
            toast.error("Code not generated yet. Deploy robot first.");
        }
    };

    const mainAccount = accounts[0] || { balance: 0, equity: 0, mode: 'OFFLINE' };

    // Dynamic Calculations
    const pointValue = 1.0; // Simplified average point value per lot
    const estProfit = tradeConfig.lot * tradeConfig.tp * pointValue;
    const estLoss = tradeConfig.lot * tradeConfig.sl * pointValue;
    const projectedProfitBalance = mainAccount.balance + estProfit;
    const projectedLossBalance = mainAccount.balance - estLoss;

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
                                                <div className="flex justify-end gap-2">
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        className="font-bold border-primary/20 text-primary hover:bg-primary/10"
                                                        onClick={() => {
                                                            setSelectedRobot(robot);
                                                            setTradeConfig({ lot: robot.lot || 0.1, sl: robot.sl || 300, tp: robot.tp || 600 });
                                                            setShowTradeModal(true);
                                                        }}
                                                    >
                                                        OPEN CONTROLLER
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="text-destructive font-bold hover:bg-destructive/10"
                                                        onClick={() => handleStopRobot(robot.id)}
                                                        disabled={isStopping[robot.id]}
                                                    >
                                                        {isStopping[robot.id] ? "STOPPING..." : "STOP"}
                                                    </Button>
                                                </div>
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

            {/* Robot Control Modal */}
            <Dialog open={showTradeModal} onOpenChange={setShowTradeModal}>
                <DialogContent className="sm:max-w-xl border-primary/20 bg-background/95 backdrop-blur-xl">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-2xl font-black italic tracking-tighter uppercase">
                            <TrendingUp className="h-6 w-6 text-primary" />
                            Robot Controller
                        </DialogTitle>
                        <DialogDescription className="font-medium">
                            Configure parameters for <span className="text-primary font-bold">Bot {selectedRobot?.symbol}</span>
                        </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-6 py-4">
                        <div className="flex gap-4 p-4 bg-muted/30 rounded-2xl border border-border/50">
                            <div className="flex-1 space-y-1">
                                <span className="text-[10px] text-muted-foreground font-black tracking-widest uppercase">Target Win Rate</span>
                                <p className="text-xl font-bold text-green-500">{selectedRobot?.win_rate}%</p>
                            </div>
                            <Separator orientation="vertical" className="h-10" />
                            <div className="flex-1 space-y-1">
                                <span className="text-[10px] text-muted-foreground font-black tracking-widest uppercase">Base Currency</span>
                                <p className="text-xl font-bold">{selectedRobot?.symbol}</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div className="grid gap-2">
                                <Label className="text-[11px] font-bold uppercase">Volume (Lot)</Label>
                                <Input
                                    type="number"
                                    step="0.01"
                                    className="font-bold h-11"
                                    value={tradeConfig.lot}
                                    onChange={e => setTradeConfig({ ...tradeConfig, lot: parseFloat(e.target.value) })}
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label className="text-[11px] font-bold uppercase text-destructive">Stop Loss (pts)</Label>
                                <Input
                                    type="number"
                                    className="font-bold h-11 border-destructive/20 focus-visible:ring-destructive"
                                    value={tradeConfig.sl}
                                    onChange={e => setTradeConfig({ ...tradeConfig, sl: parseInt(e.target.value) })}
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label className="text-[11px] font-bold uppercase text-green-500">Take Profit (pts)</Label>
                                <Input
                                    type="number"
                                    className="font-bold h-11 border-green-500/20 focus-visible:ring-green-500"
                                    value={tradeConfig.tp}
                                    onChange={e => setTradeConfig({ ...tradeConfig, tp: parseInt(e.target.value) })}
                                />
                            </div>
                        </div>

                        {/* Balance Projection */}
                        <div className="space-y-3 p-4 bg-primary/5 rounded-2xl border border-primary/10">
                            <div className="flex items-center justify-between text-xs font-bold">
                                <span>CURRENT BALANCE:</span>
                                <span>${mainAccount.balance.toLocaleString()}</span>
                            </div>
                            <Separator />
                            <div className="grid grid-cols-2 gap-4 pt-1">
                                <div className="space-y-1">
                                    <span className="text-[9px] font-black text-green-600 tracking-wider">PROJECTED GAIN</span>
                                    <p className="text-sm font-bold text-green-500">+${estProfit.toFixed(2)}</p>
                                    <p className="text-[10px] text-muted-foreground font-medium">New Bal: ${projectedProfitBalance.toLocaleString()}</p>
                                </div>
                                <div className="space-y-1 text-right">
                                    <span className="text-[9px] font-black text-destructive tracking-wider">PROJECTED RISK</span>
                                    <p className="text-sm font-bold text-destructive">-${estLoss.toFixed(2)}</p>
                                    <p className="text-[10px] text-muted-foreground font-medium">New Bal: ${projectedLossBalance.toLocaleString()}</p>
                                </div>
                            </div>
                        </div>

                        {/* Source Code Options */}
                        <div className="grid grid-cols-2 gap-3">
                            <Button variant="outline" className="h-10 text-xs font-bold gap-2" onClick={() => handleCopyCode('mql5')}>
                                <Code className="h-4 w-4" /> COPY MQL5
                            </Button>
                            <Button variant="outline" className="h-10 text-xs font-bold gap-2" onClick={() => handleCopyCode('python')}>
                                <TrendingUp className="h-4 w-4" /> COPY PYTHON
                            </Button>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            className="w-full h-12 font-black italic tracking-tighter uppercase text-lg animate-pulse hover:animate-none"
                            disabled={isDeploying || !accounts[0]}
                            onClick={handleAutoTrade}
                        >
                            {isDeploying ? "Launching Order..." : "Auto-Place to MT5"}
                            <Zap className="ml-2 h-5 w-5 fill-current" />
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default Dashboard;
