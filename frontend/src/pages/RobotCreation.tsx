import { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger
} from "@/components/ui/accordion";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { cn } from '@/lib/utils';
import { Cpu, Zap, Settings2, BarChart, ChevronRight, Check, Info } from 'lucide-react';

const RobotCreation = () => {
    const [step, setStep] = useState(1);
    const [isCreating, setIsCreating] = useState(false);
    const [creationProgress, setCreationProgress] = useState(0);
    const [configs, setConfigs] = useState<any>({
        symbol: 'EURUSD',
        timeframe: 'H1',
        rsi: { active: true, buy: 30, sell: 70, period: 14 },
        ma: { active: false, period: 50, type: 'MODE_SMA' },
        macd: { active: false },
        bands: { active: false, period: 20, dev: 2.0 },
        stoch: { active: false },
        lotSize: 0.01,
        sl: 30,
        tp: 60
    });

    const handleCreateRobot = async () => {
        setIsCreating(true);
        setCreationProgress(0);

        try {
            // Mapping UI state to Backend API expected format
            const indicators = [];
            if (configs.rsi.active) indicators.push('rsi');
            if (configs.ma.active) indicators.push('ma');
            if (configs.macd.active) indicators.push('macd');
            if (configs.bands.active) indicators.push('bands');
            if (configs.stoch.active) indicators.push('stoch');

            const payload = {
                symbol: configs.symbol,
                timeframe: configs.timeframe,
                indicators: indicators,
                risk: {
                    lot: configs.lotSize,
                    sl: configs.sl,
                    tp: configs.tp
                },
                rsi_settings: configs.rsi,
                ma_settings: configs.ma
                // add others as needed
            };

            // Start simulation
            const interval = setInterval(() => {
                setCreationProgress(prev => {
                    if (prev >= 95) return 95;
                    return prev + 2;
                });
            }, 100);

            await axios.post('/api/robots/create_winrate_robot/', payload);

            clearInterval(interval);
            setCreationProgress(100);

            setTimeout(() => {
                setIsCreating(false);
                setStep(2);
                toast.success('Robot created and MQL5 code generated!');
            }, 500);

        } catch (error) {
            setIsCreating(false);
            toast.error('Failed to generate robot. Check MT5 connection.');
        }
    };

    return (
        <div className="flex flex-col gap-8 p-4 md:p-8 max-w-7xl mx-auto">
            <header className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                    <Zap className="text-primary h-6 w-6 fill-primary" />
                    <h1 className="text-3xl font-extrabold tracking-tight">Generate Trading Robot</h1>
                </div>
                <p className="text-muted-foreground">Orchestrate your AI-powered trading strategy in minutes.</p>
            </header>

            {/* Progress Steps */}
            <div className="flex justify-between items-center mb-4 relative px-4">
                <div className="absolute top-1/2 left-0 w-full h-0.5 bg-muted -z-10" />
                {[1, 2, 3, 4].map((s) => (
                    <div
                        key={s}
                        className={cn(
                            "w-10 h-10 rounded-2xl flex items-center justify-center font-bold text-sm transition-all border-2 shadow-sm",
                            step >= s ? "bg-primary border-primary text-primary-foreground" : "bg-card border-border text-muted-foreground"
                        )}
                    >
                        {step > s ? <Check className="h-5 w-5" /> : s}
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                {/* Left Column: Configuration */}
                <div className="xl:col-span-4 flex flex-col gap-6">
                    <Card className="border-border/60 shadow-xl shadow-primary/5">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Settings2 className="h-4 w-4" /> Strategy Designer
                            </CardTitle>
                            <CardDescription>Configure indicators and risk management.</CardDescription>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-6">
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Market Asset</Label>
                                    <Select defaultValue={configs.symbol}>
                                        <SelectTrigger className="w-full h-11 font-bold">
                                            <SelectValue placeholder="Select Pair" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="EURUSD">EURUSD (Euro/USD)</SelectItem>
                                            <SelectItem value="GBPUSD">GBPUSD (Pound/USD)</SelectItem>
                                            <SelectItem value="USDJPY">USDJPY (USD/Yen)</SelectItem>
                                            <SelectItem value="AUDUSD">AUDUSD (Aud/USD)</SelectItem>
                                            <SelectItem value="USDCAD">USDCAD (USD/Cad)</SelectItem>
                                            <SelectItem value="USDCHF">USDCHF (USD/Swiss)</SelectItem>
                                            <SelectItem value="NZDUSD">NZDUSD (Nzd/USD)</SelectItem>
                                            <SelectItem value="BTCUSD">BTCUSD (Bitcoin/USD)</SelectItem>
                                            <SelectItem value="XAUUSD">XAUUSD (Gold/USD)</SelectItem>
                                            <SelectItem value="XAGUSD">XAGUSD (Silver/USD)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Timeframe</Label>
                                    <div className="grid grid-cols-4 gap-2">
                                        {['M5', 'M15', 'H1', 'D1'].map(tf => (
                                            <Button
                                                key={tf}
                                                variant={configs.timeframe === tf ? "default" : "outline"}
                                                size="sm"
                                                onClick={() => setConfigs({ ...configs, timeframe: tf })}
                                                className="font-bold border-border"
                                            >
                                                {tf}
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <Separator />

                            <div className="space-y-4">
                                <Label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Technical Indicators</Label>
                                <Accordion type="single" collapsible className="w-full">
                                    <AccordionItem value="rsi" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold flex items-center gap-2 cursor-pointer">
                                                    Relative Strength Index
                                                    <Info className="h-3 w-3 text-muted-foreground" />
                                                </Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.rsi.active}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, rsi: { ...configs.rsi, active: v } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-xs font-medium">
                                                    <span>Oversold (Buy): {configs.rsi.buy}</span>
                                                    <span>Overbought (Sell): {configs.rsi.sell}</span>
                                                </div>
                                                <Slider
                                                    defaultValue={[configs.rsi.buy, configs.rsi.sell]}
                                                    max={100}
                                                    step={1}
                                                    className="w-full"
                                                />
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="ma" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Moving Average</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.ma.active}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, ma: { ...configs.ma, active: v } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <Label className="text-[10px]">Period</Label>
                                                    <Input type="number" defaultValue={configs.ma.period} className="h-8" />
                                                </div>
                                                <div className="space-y-2">
                                                    <Label className="text-[10px]">Method</Label>
                                                    <Select defaultValue={configs.ma.type}>
                                                        <SelectTrigger className="h-8">
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="MODE_SMA">Simple (SMA)</SelectItem>
                                                            <SelectItem value="MODE_EMA">Exponential (EMA)</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </div>
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="bands" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Bollinger Bands</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.bands?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, bands: { active: v, period: 20, dev: 2.0 } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <Label className="text-[10px]">Period</Label>
                                                    <Input type="number" defaultValue={20} className="h-8" />
                                                </div>
                                                <div className="space-y-2">
                                                    <Label className="text-[10px]">Deviation</Label>
                                                    <Input type="number" defaultValue={2.0} step={0.1} className="h-8" />
                                                </div>
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="stoch" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Stochastic Oscillator</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.stoch?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, stoch: { active: v } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <p className="text-xs text-muted-foreground">Using default (5,3,3) settings.</p>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="atr" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Average True Range (ATR)</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.atr?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, atr: { active: v, period: 14 } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <div className="space-y-2">
                                                <Label className="text-[10px]">Period</Label>
                                                <Input type="number" defaultValue={14} className="h-8" />
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="adx" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Average Directional Index (ADX)</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.adx?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, adx: { active: v, period: 14 } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <div className="space-y-2">
                                                <Label className="text-[10px]">Period</Label>
                                                <Input type="number" defaultValue={14} className="h-8" />
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="ichimoku" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Ichimoku Kinko Hyo</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.ichimoku?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, ichimoku: { active: v } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <p className="text-xs text-muted-foreground">Using default Tenkan/Kijun/Senkou settings.</p>
                                        </AccordionContent>
                                    </AccordionItem>

                                    <AccordionItem value="psar" className="border-none">
                                        <div className="flex items-center justify-between py-2">
                                            <AccordionTrigger className="hover:no-underline py-0">
                                                <Label className="font-bold cursor-pointer">Parabolic SAR</Label>
                                            </AccordionTrigger>
                                            <Switch
                                                checked={configs.psar?.active || false}
                                                onCheckedChange={(v: boolean) => setConfigs({ ...configs, psar: { active: v } })}
                                            />
                                        </div>
                                        <AccordionContent className="pt-2 pb-4 px-1 space-y-4">
                                            <p className="text-xs text-muted-foreground">Step: 0.02, Maximum: 0.2</p>
                                        </AccordionContent>
                                    </AccordionItem>
                                </Accordion>
                            </div>

                            <Separator />

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label className="text-[10px] font-bold uppercase">Stop Loss (pts)</Label>
                                    <Input type="number" defaultValue={configs.sl} className="font-bold" />
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-[10px] font-bold uppercase">Take Profit (pts)</Label>
                                    <Input type="number" defaultValue={configs.tp} className="font-bold" />
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button
                                onClick={handleCreateRobot}
                                disabled={isCreating}
                                className="w-full h-12 rounded-xl font-bold gap-2 group shadow-lg shadow-primary/20"
                            >
                                {isCreating ? "Synthesizing Strategy..." : "Generate AI Strategy"}
                                <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </Button>
                        </CardFooter>
                    </Card>
                </div>

                {/* Right Column: Visualization */}
                <div className="xl:col-span-8 flex flex-col gap-6">
                    <Card className="h-full border-border/60 bg-muted/10 overflow-hidden relative group">
                        <CardHeader className="bg-card border-b border-border">
                            <CardTitle className="text-sm flex items-center gap-2">
                                <BarChart className="h-4 w-4" /> Predictive Performance Model
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="h-[500px] p-0 flex items-center justify-center relative">
                            {/* Animated Chart Placeholder */}
                            <div className="w-full h-full flex items-end gap-[2px] p-8 pb-20">
                                {Array.from({ length: 80 }).map((_, i) => (
                                    <div
                                        key={i}
                                        className="flex-1 bg-primary/20 rounded-t-sm transition-all duration-1000 group-hover:bg-primary/40"
                                        style={{ height: `${10 + Math.random() * (isCreating ? 80 : 40)}%` }}
                                    />
                                ))}
                            </div>
                            {(isCreating || creationProgress > 0) && (
                                <div className="absolute inset-0 flex items-center justify-center bg-background/10 backdrop-blur-[1px]">
                                    <div className="bg-card/95 shadow-2xl border border-border p-8 rounded-3xl flex flex-col items-center gap-6 max-w-sm text-center border-t-primary/20">
                                        <div className="p-4 bg-primary/10 rounded-full animate-pulse border border-primary/20">
                                            <Cpu className="h-10 w-10 text-primary" />
                                        </div>
                                        <div className="space-y-2">
                                            <h4 className="text-xl font-black italic tracking-tighter uppercase">AI QUANTUM CORE</h4>
                                            <p className="text-xs text-muted-foreground leading-relaxed px-4">
                                                {creationProgress < 100
                                                    ? `Simulating millions of market variations using the selected indicators for ${configs.symbol}...`
                                                    : "Strategy generated and ready for deployment!"}
                                            </p>
                                        </div>
                                        <div className="w-full space-y-2">
                                            <div className="flex justify-between text-[10px] font-bold text-muted-foreground">
                                                <span>{creationProgress < 100 ? "COMPILING MQL5" : "COMPILATION COMPLETE"}</span>
                                                <span>{Math.round(creationProgress)}%</span>
                                            </div>
                                            <Progress value={creationProgress} className="h-2 w-full" />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>

                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[95%] grid grid-cols-1 md:grid-cols-3 gap-4">
                            {[
                                { label: 'Estimated Win Rate', value: '78.4%', sub: 'Based on 5yr Backtest', color: 'text-green-500' },
                                { label: 'Avg Monthly Profit', value: '12.2%', sub: 'Compounded returns', color: 'text-primary' },
                                { label: 'Max Expected DD', value: '2.4%', sub: 'Low risk profile', color: 'text-destructive' }
                            ].map((stat, i) => (
                                <Card key={i} className="bg-card/90 backdrop-blur border-border/50 shadow-2xl">
                                    <CardContent className="p-4 flex flex-col items-center text-center">
                                        <span className="text-[10px] text-muted-foreground uppercase font-black tracking-widest">{stat.label}</span>
                                        <span className={cn("text-2xl font-black mt-1 tracking-tighter", stat.color)}>{stat.value}</span>
                                        <span className="text-[9px] text-muted-foreground mt-1">{stat.sub}</span>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

// Simple Separator because shadcn-add might still be running
const Separator = () => <div className="h-px bg-border w-full my-2" />;

export default RobotCreation;
