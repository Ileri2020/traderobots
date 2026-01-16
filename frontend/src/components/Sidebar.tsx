import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
    Home,
    TrendingUp,
    Cpu,
    LayoutDashboard,
    MessageSquare,
    User,
    Settings,
    Menu,
    LogOut,
    Shield,
    Store,
    Users,
    Activity,
    CheckCircle2,
    XCircle,
    Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';

import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import axios from 'axios';

const SidebarContent = ({ setOpen }: { setOpen?: (open: boolean) => void }) => {
    const navigate = useNavigate();
    const userString = localStorage.getItem('user');
    const user = userString ? JSON.parse(userString) : null;
    
    const [hasAccounts, setHasAccounts] = useState(false);
    const [mt5Status, setMt5Status] = useState<'idle' | 'checking' | 'connected' | 'error'>('idle');
    const [showMt5Dialog, setShowMt5Dialog] = useState(false);
    const [mt5Details, setMt5Details] = useState<any>(null);

    const navItems = [
        { icon: Home, label: 'Feed', path: '/' },
        { icon: TrendingUp, label: 'Trades', path: '/trades' },
        { icon: Cpu, label: 'Create Robot', path: '/robots' },
        { icon: Store, label: 'Marketplace', path: '/marketplace' },
        { icon: Users, label: 'Social', path: '/social' },
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: MessageSquare, label: 'Chat', path: '/chat' },
        { icon: Shield, label: 'Admin', path: '/admin', roles: ['admin', 'moderator'] },
    ];

    // Check if user has MT5 accounts
    useEffect(() => {
        const checkAccounts = async () => {
            if (!user) return;
            try {
                const response = await axios.get('/api/accounts/');
                setHasAccounts(response.data && response.data.length > 0);
            } catch (error) {
                console.error('Failed to check accounts:', error);
            }
        };
        checkAccounts();
    }, [user]);

    const handleMt5Initialize = async () => {
        setMt5Status('checking');
        setShowMt5Dialog(true);
        
        try {
            // Check current MT5 status
            const statusResponse = await axios.get('/api/accounts/mt5/status/');
            
            if (statusResponse.data.connected) {
                setMt5Status('connected');
                setMt5Details(statusResponse.data);
                toast.success('MT5 Terminal Connected!', {
                    description: `Account: ${statusResponse.data.login || 'Connected'}`
                });
            } else {
                // Try to reconnect
                const reconnectResponse = await axios.post('/api/accounts/mt5/reconnect/');
                
                if (reconnectResponse.data.status === 'RECONNECTED') {
                    setMt5Status('connected');
                    setMt5Details(reconnectResponse.data.health);
                    toast.success('MT5 Terminal Initialized!', {
                        description: 'Connection established successfully'
                    });
                } else {
                    throw new Error(reconnectResponse.data.error || 'Connection failed');
                }
            }
        } catch (error: any) {
            setMt5Status('error');
            const errorMsg = error.response?.data?.error || error.message || 'Failed to initialize MT5';
            toast.error('MT5 Connection Failed', {
                description: errorMsg
            });
            setMt5Details({ error: errorMsg });
        }
    };

    const handleLogout = async () => {
        try {
            await axios.post('/api/users/logout/');
            localStorage.removeItem('user');
            toast.success('Logged out successfully');
            navigate('/login');
        } catch (error) {
            localStorage.removeItem('user');
            navigate('/login');
        }
    };

    return (
        <div className="flex flex-col h-full py-4">
            <div className="flex items-center gap-3 px-4 mb-10">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                    <TrendingUp className="text-primary-foreground w-6 h-6" />
                </div>
                <h1 className="text-xl font-bold tracking-tighter">TRADEROBOTS</h1>
            </div>

            <nav className="flex-1 flex flex-col gap-2 px-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        onClick={() => setOpen?.(false)}
                        className={({ isActive }) => cn(
                            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                            isActive
                                ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* MT5 Initialize Button */}
            {user && hasAccounts && (
                <div className="px-2 mb-4">
                    <Button
                        onClick={handleMt5Initialize}
                        disabled={mt5Status === 'checking'}
                        className="w-full justify-start gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg"
                    >
                        {mt5Status === 'checking' ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : mt5Status === 'connected' ? (
                            <CheckCircle2 className="w-5 h-5" />
                        ) : (
                            <Activity className="w-5 h-5" />
                        )}
                        <span className="font-medium">
                            {mt5Status === 'checking' ? 'Connecting...' : 
                             mt5Status === 'connected' ? 'MT5 Connected' : 
                             'Initialize MT5'}
                        </span>
                    </Button>
                </div>
            )}

            <div className="mt-auto flex flex-col gap-2 border-t border-border pt-6 px-2">
                <NavLink to="/profile" onClick={() => setOpen?.(false)} className="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:text-foreground">
                    <User className="w-5 h-5" />
                    <span className="font-medium">Profile</span>
                </NavLink>
                <NavLink to="/settings" onClick={() => setOpen?.(false)} className="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:text-foreground">
                    <Settings className="w-5 h-5" />
                    <span className="font-medium">Settings</span>
                </NavLink>
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-4 py-3 text-destructive hover:bg-destructive/10 rounded-xl transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">Logout</span>
                </button>
            </div>

            {user && (
                <div className="mt-8 mx-4 p-4 bg-primary/5 rounded-2xl border border-primary/10">
                    <p className="text-xs text-center text-muted-foreground">
                        @{user.username}
                    </p>
                </div>
            )}

            {/* MT5 Status Dialog */}
            <Dialog open={showMt5Dialog} onOpenChange={setShowMt5Dialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            {mt5Status === 'checking' && <Loader2 className="w-5 h-5 animate-spin" />}
                            {mt5Status === 'connected' && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                            {mt5Status === 'error' && <XCircle className="w-5 h-5 text-red-600" />}
                            MT5 Terminal Status
                        </DialogTitle>
                        <DialogDescription>
                            {mt5Status === 'checking' && 'Initializing MT5 terminal connection...'}
                            {mt5Status === 'connected' && 'Successfully connected to MT5 terminal'}
                            {mt5Status === 'error' && 'Failed to connect to MT5 terminal'}
                        </DialogDescription>
                    </DialogHeader>
                    
                    {mt5Details && mt5Status === 'connected' && (
                        <div className="space-y-3 mt-4">
                            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                                <span className="text-sm text-muted-foreground">Account</span>
                                <span className="font-medium">{mt5Details.login}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                                <span className="text-sm text-muted-foreground">Balance</span>
                                <span className="font-medium">${mt5Details.balance?.toFixed(2) || '0.00'}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                                <span className="text-sm text-muted-foreground">Equity</span>
                                <span className="font-medium">${mt5Details.equity?.toFixed(2) || '0.00'}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                                <span className="text-sm text-muted-foreground">Trading Allowed</span>
                                <span className={cn(
                                    "font-medium",
                                    mt5Details.can_trade ? "text-green-600" : "text-red-600"
                                )}>
                                    {mt5Details.can_trade ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>
                    )}
                    
                    {mt5Details && mt5Status === 'error' && (
                        <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                            <p className="text-sm text-destructive">{mt5Details.error}</p>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
};

const Sidebar = () => {
    const [open, setOpen] = useState(false);

    return (
        <>
            {/* Mobile Nav */}
            <div className="lg:hidden fixed top-4 left-4 z-50">
                <Sheet open={open} onOpenChange={setOpen}>
                    <SheetTrigger asChild>
                        <Button variant="outline" size="icon" className="shadow-md bg-background/80 backdrop-blur">
                            <Menu className="h-5 w-5" />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="w-64 p-0">
                        <SidebarContent setOpen={setOpen} />
                    </SheetContent>
                </Sheet>
            </div>

            {/* Desktop Sidebar */}
            <aside className="hidden lg:flex w-64 bg-card border-r border-border h-screen sticky top-0 flex-col">
                <SidebarContent />
            </aside>
        </>
    );
};

export default Sidebar;
