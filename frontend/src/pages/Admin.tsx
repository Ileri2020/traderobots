import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import {
    Users as UsersIcon,
    Cpu,
    CreditCard,
    FileText,
    Search,
    Plus,
    Trash2,
    Edit,
    BarChart3,
    ShieldAlert
} from 'lucide-react';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from '@/components/ui/card';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table';
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger
} from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';

const Admin = () => {
    const [stats, setStats] = useState<any[]>([]);
    const [users, setUsers] = useState<any[]>([]);
    const [robots, setRobots] = useState<any[]>([]);
    const [accounts, setAccounts] = useState<any[]>([]);
    const [posts, setPosts] = useState<any[]>([]);

    useEffect(() => {
        fetchAdminData();
    }, []);

    const fetchAdminData = async () => {
        try {
            const [userRes, robotRes, accRes, postRes] = await Promise.all([
                axios.get('/api/users/'),
                axios.get('/api/robots/'),
                axios.get('/api/accounts/'),
                axios.get('/api/social/posts/')
            ]);

            setUsers(userRes.data);
            setRobots(robotRes.data);
            setAccounts(accRes.data);
            setPosts(postRes.data);

            setStats([
                { title: 'Total Users', value: userRes.data.length.toString(), change: '+12%', icon: UsersIcon },
                { title: 'Active Robots', value: robotRes.data.length.toString(), change: '+5%', icon: Cpu },
                { title: 'MT5 Accounts', value: accRes.data.length.toString(), change: '+18%', icon: CreditCard },
                { title: 'Social Posts', value: postRes.data.length.toString(), change: '+24%', icon: FileText },
            ]);
        } catch (error) {
            console.error('Error fetching admin data:', error);
        }
    };

    const handleDelete = async (type: string, id: number) => {
        if (!confirm(`Are you sure you want to delete this ${type.slice(0, -1)}?`)) return;
        try {
            const endpoint = type === 'posts' ? `social/${type}` : type;
            await axios.delete(`/api/${endpoint}/${id}/`);
            toast.success('Deleted successfully');
            fetchAdminData();
        } catch (error) {
            toast.error('Failed to delete');
        }
    };

    const handleEdit = (type: string, row: any) => {
        toast.info(`Editing ${type} ${row.id} - Not yet implemented in this view.`);
    };

    const chartData = [
        { name: 'Mon', visits: 400, trades: 240, users: 24 },
        { name: 'Tue', visits: 300, trades: 139, users: 13 },
        { name: 'Wed', visits: 200, trades: 980, users: 98 },
        { name: 'Thu', visits: 278, trades: 390, users: 39 },
        { name: 'Fri', visits: 189, trades: 480, users: 48 },
        { name: 'Sat', visits: 239, trades: 380, users: 38 },
        { name: 'Sun', visits: 349, trades: 430, users: 43 },
    ];

    return (
        <div className="p-4 md:p-8 flex flex-col gap-8 max-w-7xl mx-auto">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tighter flex items-center gap-2">
                        <ShieldAlert className="text-primary h-8 w-8" />
                        ADMIN CONSOLE
                    </h1>
                    <p className="text-muted-foreground mt-1">Manage the core underlying data of the Traderobots ecosystem.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="gap-2 font-bold h-10">
                        <BarChart3 className="h-4 w-4" /> Export Stats
                    </Button>
                    <Button onClick={fetchAdminData} className="gap-2 font-bold h-10">
                        <Plus className="h-4 w-4" /> Sync Database
                    </Button>
                </div>
            </header>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat, i) => (
                    <Card key={i} className="border-border/50 bg-card/50 backdrop-blur-sm">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                            <stat.icon className="h-4 w-4 text-primary" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stat.value}</div>
                            <p className="text-xs text-green-500 font-medium mt-1">{stat.change} from last month</p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Tabs defaultValue="analytics" className="w-full">
                <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5 h-auto gap-1 p-1 bg-muted/50 rounded-xl">
                    <TabsTrigger value="analytics" className="py-2 rounded-lg">Analytics</TabsTrigger>
                    <TabsTrigger value="users" className="py-2 rounded-lg">Users</TabsTrigger>
                    <TabsTrigger value="robots" className="py-2 rounded-lg">Robots</TabsTrigger>
                    <TabsTrigger value="accounts" className="py-2 rounded-lg">Accounts</TabsTrigger>
                    <TabsTrigger value="posts" className="py-2 rounded-lg">Posts</TabsTrigger>
                </TabsList>

                <TabsContent value="analytics" className="space-y-4 py-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <Card className="border-border/60">
                            <CardHeader>
                                <CardTitle>User Growth & Activity</CardTitle>
                                <CardDescription>Tracking daily active users and interactions.</CardDescription>
                            </CardHeader>
                            <CardContent className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                        <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                                        <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                                        />
                                        <Area type="monotone" dataKey="visits" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorVisits)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                        <Card className="border-border/60">
                            <CardHeader>
                                <CardTitle>Trading Volume</CardTitle>
                                <CardDescription>Total trades executed by robots over time.</CardDescription>
                            </CardHeader>
                            <CardContent className="h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                        <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                                        <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                                        />
                                        <Bar dataKey="trades" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="users" className="py-4">
                    <CRUDTable
                        title="Users"
                        description="Manage user accounts and roles."
                        columns={['username', 'email', 'is_staff']}
                        data={users}
                        onDelete={(id) => handleDelete('users', id)}
                        onEdit={(row) => handleEdit('users', row)}
                    />
                </TabsContent>

                <TabsContent value="robots" className="py-4">
                    <CRUDTable
                        title="Robots"
                        description="Monitor and manage active trading robots."
                        columns={['symbol', 'method', 'win_rate', 'user_name']}
                        data={robots}
                        onDelete={(id) => handleDelete('robots', id)}
                        onEdit={(row) => handleEdit('robots', row)}
                    />
                </TabsContent>

                <TabsContent value="accounts" className="py-4">
                    <CRUDTable
                        title="MT5 Accounts"
                        description="View linked Metatrader 5 accounts."
                        columns={['account_number', 'mode', 'balance']}
                        data={accounts}
                        onDelete={(id) => handleDelete('accounts', id)}
                        onEdit={(row) => handleEdit('accounts', row)}
                    />
                </TabsContent>

                <TabsContent value="posts" className="py-4">
                    <CRUDTable
                        title="Social Posts"
                        description="Moderation for the social feed."
                        columns={['user_name', 'content', 'likes_count', 'created_at']}
                        data={posts}
                        onDelete={(id) => handleDelete('posts', id)}
                        onEdit={(row) => handleEdit('posts', row)}
                    />
                </TabsContent>
            </Tabs>
        </div>
    );
};

interface CRUDTableProps {
    title: string;
    description: string;
    columns: string[];
    data: any[];
    onDelete: (id: number) => void;
    onEdit: (row: any) => void;
}

const CRUDTable = ({ title, description, columns, data, onDelete, onEdit }: CRUDTableProps) => {
    return (
        <Card className="border-border/60">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <div>
                    <CardTitle>{title}</CardTitle>
                    <CardDescription>{description}</CardDescription>
                </div>
                <div className="flex gap-2">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input type="search" placeholder="Search..." className="pl-8 w-[200px] h-9 bg-muted/30 border-none" />
                    </div>
                    <Button size="sm" className="gap-1 font-bold h-9">
                        <Plus className="h-4 w-4" /> Add New
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader className="bg-muted/30">
                        <TableRow>
                            {columns.map((col) => (
                                <TableHead key={col} className="uppercase text-[10px] font-black tracking-widest">{col.replace('_', ' ')}</TableHead>
                            ))}
                            <TableHead className="text-right uppercase text-[10px] font-black tracking-widest">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row) => (
                            <TableRow key={row.id} className="hover:bg-muted/10 transition-colors">
                                {columns.map((col) => (
                                    <TableCell key={col}>
                                        {col === 'Status' || col === 'mode' || col === 'is_staff' ? (
                                            <Badge variant={row[col] ? 'default' : 'secondary'} className="uppercase text-[9px] font-bold">
                                                {row[col]?.toString() || 'OFFLINE'}
                                            </Badge>
                                        ) : (
                                            <span className="text-sm">{row[col]}</span>
                                        )}
                                    </TableCell>
                                ))}
                                <TableCell className="text-right">
                                    <div className="flex justify-end gap-2">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 hover:bg-primary/10 hover:text-primary"
                                            onClick={() => onEdit(row)}
                                        >
                                            <Edit className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-destructive hover:bg-destructive/10"
                                            onClick={() => onDelete(row.id)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
};

export default Admin;
