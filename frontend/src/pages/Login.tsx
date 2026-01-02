import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp, Zap } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await axios.post('/api/users/login/', {
                username,
                password
            });
            localStorage.setItem('user', JSON.stringify(response.data));
            toast.success('Login successful!');
            navigate('/');
        } catch (error) {
            const err = error as any;
            const msg = err.response?.data?.error || 'Login failed';
            toast.error(msg);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSocialLogin = async (platform: 'google' | 'facebook') => {
        setIsLoading(true);
        try {
            const response = await axios.post(`/api/users/${platform}_login/`);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            toast.success(`${platform.charAt(0).toUpperCase() + platform.slice(1)} login successful!`);
            navigate('/');
        } catch (error) {
            const err = error as any;
            const msg = err.response?.data?.error || `${platform} login failed`;
            toast.error(msg);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-background p-4">
            <div className="w-full max-w-md space-y-8">
                <div className="flex flex-col items-center gap-2 text-center">
                    <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20">
                        <TrendingUp className="text-primary-foreground w-8 h-8" />
                    </div>
                    <h1 className="text-3xl font-black tracking-tighter uppercase">TRADEROBOTS</h1>
                    <p className="text-muted-foreground">Sign in to your AI trading account</p>
                </div>

                <Card className="border-border/60 shadow-2xl glass-premium">
                    <CardHeader>
                        <CardTitle>Welcome Back</CardTitle>
                        <CardDescription>Enter your credentials to access the platform.</CardDescription>
                    </CardHeader>
                    <form onSubmit={handleLogin}>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="username">Username</Label>
                                <Input
                                    id="username"
                                    placeholder="your_username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="flex flex-col gap-4">
                            <Button type="submit" className="w-full h-11 font-bold" disabled={isLoading}>
                                {isLoading ? "Signing in..." : "Sign In"}
                            </Button>
                            <div className="text-sm text-center text-muted-foreground">
                                Don't have an account? <Link to="/signup" className="text-primary font-bold hover:underline">Sign Up</Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>

                <div className="grid grid-cols-2 gap-4">
                    <Button
                        variant="outline"
                        className="h-11 font-bold gap-2"
                        onClick={() => handleSocialLogin('google')}
                        disabled={isLoading}
                    >
                        <Zap className="h-4 w-4" /> Google
                    </Button>
                    <Button
                        variant="outline"
                        className="h-11 font-bold gap-2"
                        onClick={() => handleSocialLogin('facebook')}
                        disabled={isLoading}
                    >
                        <Zap className="h-4 w-4" /> Facebook
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default Login;
