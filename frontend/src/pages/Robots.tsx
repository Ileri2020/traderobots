import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Bot, TrendingUp, Download, Star, Filter, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface Robot {
    id: string;
    symbol: string;
    method: string;
    win_rate: number;
    mql5_code?: string;
    indicators?: string[];
    risk_settings?: {
        lot: string;
        sl: number;
        tp: number;
    };
    user: string;
    created_at: string;
}

const Robots = () => {
    const [robots, setRobots] = useState<Robot[]>([]);
    const [filter, setFilter] = useState('all');
    const [sortBy, setSortBy] = useState('win_rate');
    const [errorDialog, setErrorDialog] = useState({ open: false, title: '', description: '' });

    useEffect(() => {
        fetchRobots();
    }, []);

    const fetchRobots = async () => {
        try {
            const response = await axios.get('/api/robots/');
            setRobots(response.data);
        } catch (error: any) {
            console.error('Error fetching robots:', error);
            setErrorDialog({
                open: true,
                title: 'Data Unavailable',
                description: 'Unable to load robot marketplace. Please check your connection.'
            });
        }
    };

    const handleDownloadRobot = (robot: Robot) => {
        if (!robot.mql5_code) {
            toast.error('MQL5 code not available for this robot');
            return;
        }
        const blob = new Blob([robot.mql5_code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${robot.symbol}_${robot.method}_${robot.id?.toString().slice(0, 8)}.mq5`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast.success('Robot downloaded successfully!');
    };

    const filteredRobots = robots
        .filter(r => filter === 'all' || r.method === filter)
        .sort((a, b) => {
            if (sortBy === 'win_rate') return b.win_rate - a.win_rate;
            if (sortBy === 'newest') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
            return 0;
        });

    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto flex flex-col gap-8">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                        <Bot className="h-8 w-8 text-primary" />
                        Trading Robots Marketplace
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        Discover and download AI-powered trading strategies created by our community.
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <Select value={filter} onValueChange={setFilter}>
                        <SelectTrigger className="w-40 font-bold">
                            <Filter className="h-4 w-4 mr-2" />
                            <SelectValue placeholder="Filter" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Methods</SelectItem>
                            <SelectItem value="winrate">Win-Rate</SelectItem>
                            <SelectItem value="ml">Machine Learning</SelectItem>
                        </SelectContent>
                    </Select>

                    <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger className="w-40 font-bold">
                            <TrendingUp className="h-4 w-4 mr-2" />
                            <SelectValue placeholder="Sort" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="win_rate">Top Rated</SelectItem>
                            <SelectItem value="newest">Newest First</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRobots.length > 0 ? filteredRobots.map((robot) => (
                    <Card key={robot.id} className="border-border/60 hover:shadow-xl transition-all duration-300 hover:border-primary/30 overflow-hidden group">
                        <CardHeader className="pb-4 bg-gradient-to-br from-primary/5 to-transparent border-b border-border/30">
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="p-3 bg-primary/10 rounded-2xl border border-primary/20 group-hover:scale-110 transition-transform">
                                        <Bot className="h-6 w-6 text-primary" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-lg font-bold">{robot.symbol}</CardTitle>
                                        <CardDescription className="text-xs font-mono">
                                            ID: {robot.id?.toString().slice(0, 8)}
                                        </CardDescription>
                                    </div>
                                </div>
                                <Badge
                                    className={cn(
                                        "font-bold uppercase text-[10px]",
                                        robot.method === 'ml' ? 'bg-purple-500/10 text-purple-500 border-purple-500/20' : 'bg-blue-500/10 text-blue-500 border-blue-500/20'
                                    )}
                                    variant="outline"
                                >
                                    {robot.method}
                                </Badge>
                            </div>
                        </CardHeader>

                        <CardContent className="pt-6 space-y-6">
                            {/* Win Rate */}
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Win Rate</span>
                                    <div className="flex items-center gap-1">
                                        <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />
                                        <span className="text-lg font-black">{robot.win_rate}%</span>
                                    </div>
                                </div>
                                <Progress value={robot.win_rate} className="h-2" />
                            </div>

                            {/* Indicators */}
                            <div className="space-y-2">
                                <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Indicators</span>
                                <div className="flex flex-wrap gap-2">
                                    {robot.indicators && robot.indicators.length > 0 ? (
                                        robot.indicators.map((indicator: string, idx: number) => (
                                            <Badge key={idx} variant="secondary" className="text-[10px] font-mono uppercase">
                                                {indicator}
                                            </Badge>
                                        ))
                                    ) : (
                                        <span className="text-xs italic text-muted-foreground">No indicators specified</span>
                                    )}
                                </div>
                            </div>

                            {/* Risk Settings */}
                            {robot.risk_settings && (
                                <div className="grid grid-cols-3 gap-3 bg-muted/30 p-3 rounded-xl">
                                    <div className="flex flex-col">
                                        <span className="text-[9px] uppercase text-muted-foreground font-bold">Lot</span>
                                        <span className="text-sm font-bold">{robot.risk_settings.lot || '0.01'}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[9px] uppercase text-muted-foreground font-bold">SL</span>
                                        <span className="text-sm font-bold text-red-500">{robot.risk_settings.sl || 30}</span>
                                    </div>
                                    <div className="flex flex-col">
                                        <span className="text-[9px] uppercase text-muted-foreground font-bold">TP</span>
                                        <span className="text-sm font-bold text-green-500">{robot.risk_settings.tp || 60}</span>
                                    </div>
                                </div>
                            )}

                            {/* Creator */}
                            <div className="flex items-center gap-2 pt-3 border-t border-border/30">
                                <Avatar className="h-6 w-6 border border-border">
                                    <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${robot.user}`} />
                                    <AvatarFallback className="text-[10px]">U</AvatarFallback>
                                </Avatar>
                                <span className="text-xs text-muted-foreground">
                                    Created {new Date(robot.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </CardContent>

                        <CardFooter className="pt-0">
                            <Button
                                onClick={() => handleDownloadRobot(robot)}
                                className="w-full font-bold gap-2 shadow-lg shadow-primary/20"
                                size="sm"
                            >
                                <Download className="h-4 w-4" />
                                Download MQL5
                            </Button>
                        </CardFooter>
                    </Card>
                )) : (
                    <div className="col-span-full">
                        <Card className="border-border/60 border-dashed">
                            <CardContent className="flex flex-col items-center justify-center py-20 opacity-40">
                                <Bot className="h-16 w-16 mb-4" />
                                <p className="text-sm italic">No robots found. Try adjusting your filters.</p>
                            </CardContent>
                        </Card>
                    </div>
                )}
            </div>

            {/* Error Alert Dialog */}
            <AlertDialog open={errorDialog.open} onOpenChange={(open) => setErrorDialog(prev => ({ ...prev, open }))}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle className="text-destructive flex items-center gap-2">
                            <ShieldAlert className="h-5 w-5" />
                            {errorDialog.title}
                        </AlertDialogTitle>
                        <AlertDialogDescription>
                            {errorDialog.description}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => setErrorDialog(prev => ({ ...prev, open: false }))}>
                            Understood
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
};

export default Robots;
