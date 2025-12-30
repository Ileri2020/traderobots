import { useState } from 'react';
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
    Users
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import axios from 'axios';

const SidebarContent = ({ setOpen }: { setOpen?: (open: boolean) => void }) => {
    const navigate = useNavigate();
    const userString = localStorage.getItem('user');
    const user = userString ? JSON.parse(userString) : null;

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

            <div className="mt-8 mx-4 p-4 bg-primary/5 rounded-2xl border border-primary/10">
                <p className="text-xs text-center text-muted-foreground">
                    @{user?.username || 'trader_ceo'}
                </p>
            </div>
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
