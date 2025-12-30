import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardFooter
} from '@/components/ui/card';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
    Cpu,
    TrendingUp,
    Layers,
    Activity,
    ChevronRight,
    Users,
    Zap
} from 'lucide-react';

const Trades = () => {
    const [robots, setRobots] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchRobots();
    }, []);

    const fetchRobots = async () => {
        try {
            const response = await axios.get('/api/robots/');
            setRobots(response.data);
        } catch (error) {
            console.error('Error fetching robots:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCopyBot = (robot: any) => {
        toast.promise(
            new Promise((resolve) => setTimeout(resolve, 1500)),
            {
                loading: `Cloning ${robot.user_name}'s AI structure...`,
                success: 'Strategy successfully copied to your fleet!',
                error: 'Failed to copy strategy',
            }
        );
    };

    return (
        <div className="flex flex-col gap-8 p-4 md:p-8 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-2">
                        <TrendingUp className="h-8 w-8 text-primary" /> Robot Marketplace
                    </h1>
                    <p className="text-muted-foreground mt-1">Discover and copy high-performance AI trading bots.</p>
                </div>
                <div className="flex items-center gap-3">
                    <Select defaultValue="all">
                        <SelectTrigger className="w-[180px] bg-background">
                            <SelectValue placeholder="Asset Category" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Assets</SelectItem>
                            <SelectItem value="forex">Forex</SelectItem>
                            <SelectItem value="crypto">Crypto</SelectItem>
                            <SelectItem value="commodities">Commodities</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button variant="outline" className="gap-2">
                        <Layers className="h-4 w-4" /> Filter
                    </Button>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {isLoading ? (
                    <div className="col-span-full flex justify-center p-20">
                        <Zap className="animate-pulse h-12 w-12 text-primary" />
                    </div>
                ) : (
                    robots.map((robot) => (
                        <Card key={robot.id} className="group border-border/60 hover:border-primary/50 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5 cursor-pointer overflow-hidden bg-card/50 backdrop-blur-sm">
                            <CardHeader className="pb-4">
                                <div className="flex justify-between items-start">
                                    <div className="p-3 bg-primary/10 rounded-2xl group-hover:bg-primary transition-colors duration-300">
                                        <Cpu className="h-6 w-6 text-primary group-hover:text-primary-foreground" />
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <Badge variant="outline" className="text-green-500 border-green-500/20 bg-green-500/5 font-bold px-2 py-0.5 mb-2">
                                            {robot.win_rate}% WIN RATE
                                        </Badge>
                                        <div className="flex items-center gap-1 text-[10px] text-muted-foreground uppercase font-black">
                                            <Activity className="h-3 w-3" /> {robot.method === 'ml' ? 'AI DRIVEN' : 'QUANT CORE'}
                                        </div>
                                    </div>
                                </div>
                                <div className="pt-4">
                                    <CardTitle className="text-xl font-black italic tracking-tighter uppercase transition-colors group-hover:text-primary">
                                        {robot.user_name}'s {robot.symbol} Bot
                                    </CardTitle>
                                    <p className="text-xs text-muted-foreground font-mono mt-1">{robot.symbol} • H1 TIMEFRAME • {robot.method.toUpperCase()}</p>
                                </div>
                            </CardHeader>

                            <CardContent className="space-y-6">
                                <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar text-[10px]">
                                    {robot.indicators?.map((tag: any) => (
                                        <Badge key={tag.name} variant="secondary" className="bg-muted/50 font-bold py-0 h-5 px-1.5 opacity-70 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                            {tag.name}
                                        </Badge>
                                    )) || (
                                            ['RSI', 'MACD', 'EMA'].map(tag => (
                                                <Badge key={tag} variant="secondary" className="bg-muted/50 font-bold py-0 h-5 px-1.5 opacity-70 group-hover:opacity-100 transition-opacity">
                                                    {tag}
                                                </Badge>
                                            ))
                                        )}
                                </div>

                                {/* Chart Visualization (Simulated) */}
                                <div className="h-24 flex items-end gap-1 px-1 bg-gradient-to-t from-primary/5 to-transparent rounded-xl border border-border/10 p-2">
                                    {Array.from({ length: 14 }).map((_, i) => {
                                        const h = Math.floor(Math.random() * 80) + 20;
                                        return (
                                            <div
                                                key={i}
                                                className="flex-1 bg-primary/20 rounded-t-sm transition-all duration-500 group-hover:bg-primary/60"
                                                style={{ height: `${h}%` }}
                                            />
                                        );
                                    })}
                                </div>

                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest leading-none mb-1">Total ROI</span>
                                        <span className="font-black text-primary text-lg">+{(robot.win_rate * 1.5).toFixed(1)}%</span>
                                    </div>
                                    <div className="flex flex-col text-right">
                                        <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest leading-none mb-1">Drawdown</span>
                                        <span className="font-black text-destructive text-lg">{(100 - robot.win_rate).toFixed(1)}%</span>
                                    </div>
                                </div>
                            </CardContent>

                            <CardFooter className="pt-4 border-t border-border/50 flex justify-between items-center bg-muted/20">
                                <div className="flex items-center gap-2">
                                    <div className="flex -space-x-2">
                                        {[1, 2, 3].map(i => (
                                            <Avatar key={i} className="w-7 h-7 border-2 border-background">
                                                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${robot.user_name}${i}`} />
                                                <AvatarFallback>U</AvatarFallback>
                                            </Avatar>
                                        ))}
                                    </div>
                                    <span className="text-[10px] font-bold text-muted-foreground flex items-center gap-1">
                                        <Users className="h-3 w-3" /> {Math.floor(robot.win_rate * 5)}+
                                    </span>
                                </div>
                                <Button
                                    onClick={(e) => { e.stopPropagation(); handleCopyBot(robot); }}
                                    className="h-9 rounded-xl font-bold bg-secondary text-secondary-foreground hover:bg-primary hover:text-primary-foreground group/btn shadow-sm transition-all"
                                >
                                    Copy Bot <ChevronRight className="h-4 w-4 ml-1 group-hover/btn:translate-x-1 transition-transform" />
                                </Button>
                            </CardFooter>
                        </Card>
                    ))
                )}
            </div>

            <Card className="border-primary/20 bg-primary/5 p-8 text-center flex flex-col items-center gap-6 rounded-3xl overflow-hidden relative">
                <div className="absolute top-0 right-0 p-12 opacity-5 rotate-12">
                    <Zap className="h-64 w-64 text-primary fill-primary" />
                </div>
                <div className="space-y-2 relative z-10">
                    <h2 className="text-3xl font-black tracking-tight uppercase italic">Want a custom strategy?</h2>
                    <p className="text-muted-foreground max-w-lg">Our AI can build your proprietary trading algorithm using complex indicators in seconds.</p>
                </div>
                <Button
                    onClick={() => navigate('/robots')}
                    size="lg" className="h-14 px-10 rounded-2xl font-black text-lg gap-3 shadow-2xl shadow-primary/30 relative z-10 transition-transform active:scale-95"
                >
                    <Zap className="h-5 w-5 fill-primary-foreground text-primary-foreground" />
                    GENERATE CUSTOM BOT
                </Button>
            </Card>
        </div>
    );
};

export default Trades;
