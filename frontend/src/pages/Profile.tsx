import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    User as UserIcon,
    CreditCard,
    Settings,
    Plus,
    Trash2,
    RefreshCw
} from 'lucide-react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

const Profile = () => {
    const [accounts, setAccounts] = useState<any[]>([]);
    const [robots, setRobots] = useState<any[]>([]);
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // New account form state
    const [accNum, setAccNum] = useState('');
    const [accPass, setAccPass] = useState('');
    const [accServer, setAccServer] = useState('');

    useEffect(() => {
        fetchProfileData();
    }, []);

    const fetchProfileData = async () => {
        try {
            const [accRes, robotRes] = await Promise.all([
                axios.get('/api/accounts/'),
                axios.get('/api/robots/')
            ]);
            setAccounts(accRes.data);
            setRobots(robotRes.data);
        } catch (error) {
            console.error('Error fetching profile data:', error);
        }
    };

    const handleConnectAccount = async () => {
        try {
            await axios.post('/api/accounts/', {
                account_number: accNum,
                password: accPass,
                server: accServer,
                mode: 'demo' // Default for now
            });
            toast.success('Account linked successfully!');
            fetchProfileData();
            setAccNum('');
            setAccPass('');
            setAccServer('');
        } catch (error) {
            toast.error('Failed to link account. check credentials.');
        }
    };

    const handleDeleteAccount = async (id: number) => {
        if (!confirm('Are you sure you want to disconnect this account?')) return;
        try {
            await axios.delete(`/api/accounts/${id}/`);
            toast.success('Account disconnected');
            fetchProfileData();
        } catch (error) {
            toast.error('Failed to disconnect account');
        }
    };

    return (
        <div className="p-4 md:p-8 flex flex-col gap-8 max-w-4xl mx-auto">
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-foreground">User Profile</h1>
                <p className="text-muted-foreground">Manage your personal settings and MT5 trading accounts.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left: User Info */}
                <div className="md:col-span-1 flex flex-col gap-6">
                    <Card className="overflow-hidden border-border/60">
                        <div className="h-24 bg-gradient-to-r from-primary to-primary/60" />
                        <CardContent className="relative pt-12 pb-6 px-6">
                            <div className="absolute -top-12 left-6 w-20 h-20 rounded-2xl bg-card border-4 border-card shadow-xl flex items-center justify-center overflow-hidden">
                                <UserIcon className="w-10 h-10 text-muted-foreground" />
                            </div>
                            <div className="flex flex-col gap-1">
                                <h2 className="text-xl font-bold italic">@{user.username || 'Guest'}</h2>
                                <p className="text-sm text-muted-foreground">{user.email}</p>
                            </div>
                            <div className="mt-6 flex flex-col gap-2">
                                <Badge variant="secondary" className="w-fit bg-primary/10 text-primary border-none">{user.role || 'Member'}</Badge>
                                <p className="text-sm mt-2 text-muted-foreground italic">Quantitative trading enthusiast powered by AI.</p>
                            </div>
                        </CardContent>
                        <CardFooter className="border-t bg-muted/30 px-6 py-4">
                            <Button
                                variant="outline"
                                className="w-full gap-2 font-bold h-10"
                                onClick={() => toast.info('Profile editing will be available in the next update.')}
                            >
                                <Settings className="h-4 w-4" /> Edit Profile
                            </Button>
                        </CardFooter>
                    </Card>

                    <Card className="border-border/60">
                        <CardHeader>
                            <CardTitle className="text-lg">Network Activity</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Total Robots</span>
                                <span className="font-bold">{robots.length}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground">Successful Trades</span>
                                <span className="font-bold text-green-500">{(robots.reduce((acc, r) => acc + r.win_rate, 0) / (robots.length || 1)).toFixed(1)}%</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Right: MT5 Accounts */}
                <div className="md:col-span-2 flex flex-col gap-6">
                    <Card className="border-border/60">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div>
                                <CardTitle>Trading Accounts</CardTitle>
                                <CardDescription>Link and manage your Metatrader 5 accounts.</CardDescription>
                            </div>
                            <Dialog>
                                <DialogTrigger asChild>
                                    <Button size="sm" className="gap-2 font-bold h-10">
                                        <Plus className="h-4 w-4" /> Add Account
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="glass-premium border-primary/20">
                                    <DialogHeader>
                                        <DialogTitle>Link MT5 Account</DialogTitle>
                                        <DialogDescription>Enter your Metatrader 5 credentials to sync your account balance and trades.</DialogDescription>
                                    </DialogHeader>
                                    <div className="grid gap-4 py-4">
                                        <div className="grid gap-2">
                                            <Label htmlFor="acc-num">Account Number</Label>
                                            <Input
                                                id="acc-num"
                                                placeholder="e.g. 100690024"
                                                value={accNum}
                                                onChange={(e) => setAccNum(e.target.value)}
                                            />
                                        </div>
                                        <div className="grid gap-2">
                                            <Label htmlFor="acc-pass">Master Password</Label>
                                            <Input
                                                id="acc-pass"
                                                type="password"
                                                value={accPass}
                                                onChange={(e) => setAccPass(e.target.value)}
                                            />
                                        </div>
                                        <div className="grid gap-2">
                                            <Label htmlFor="acc-server">Server</Label>
                                            <Input
                                                id="acc-server"
                                                placeholder="e.g. XMGlobal-MT5 5"
                                                value={accServer}
                                                onChange={(e) => setAccServer(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <DialogFooter>
                                        <Button className="w-full h-11 font-bold" onClick={handleConnectAccount}>Connect MT5 Account</Button>
                                    </DialogFooter>
                                </DialogContent>
                            </Dialog>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-4">
                            {accounts.length > 0 ? accounts.map((acc) => (
                                <div
                                    key={acc.id}
                                    className={cn(
                                        "p-4 rounded-xl border transition-all flex flex-col gap-4",
                                        acc.mode === 'REAL' ? "border-primary bg-primary/5" : "border-border bg-card"
                                    )}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className={cn(
                                                "w-10 h-10 rounded-lg flex items-center justify-center",
                                                acc.mode === 'REAL' ? "bg-amber-500/10 text-amber-500" : "bg-blue-500/10 text-blue-500"
                                            )}>
                                                <CreditCard className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <h4 className="font-bold flex items-center gap-2">
                                                    #{acc.account_number}
                                                    <Badge variant="outline" className="text-[10px] h-4 px-1">{acc.mode}</Badge>
                                                </h4>
                                                <p className="text-xs text-muted-foreground uppercase">{acc.server_name || 'MT5 CLOUD'}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm font-extrabold">${acc.balance.toLocaleString()}</p>
                                            <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tighter">EQUITY</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4 pt-2 border-t border-border/50">
                                        <div className="flex-1 flex flex-col gap-1">
                                            <Label className="text-[10px] uppercase text-muted-foreground font-black">Default Lot Size</Label>
                                            <div className="flex items-center gap-2">
                                                <Input
                                                    type="number"
                                                    defaultValue="0.01"
                                                    className="h-8 w-20 text-xs bg-muted/30 border-none"
                                                    step="0.01"
                                                />
                                                <Button size="icon" variant="ghost" className="h-8 w-8 text-primary hover:bg-primary/10">
                                                    <RefreshCw className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                className="text-destructive h-9 w-9 p-0 hover:bg-destructive/10"
                                                onClick={() => handleDeleteAccount(acc.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )) : (
                                <div className="text-center py-12 border-2 border-dashed border-border rounded-2xl opacity-40">
                                    <p className="italic text-sm">No trading accounts linked yet.</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="border-destructive/20 bg-destructive/5 overflow-hidden">
                        <CardHeader>
                            <CardTitle className="text-destructive font-black uppercase italic tracking-tighter">Danger Zone</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Button
                                variant="destructive"
                                className="w-fit font-bold h-11 px-8 rounded-xl shadow-lg shadow-destructive/20 transition-transform active:scale-95"
                                onClick={() => toast.error('Account deletion requires administrative review. Please contact support.')}
                            >
                                Delete My Global Account
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default Profile;
