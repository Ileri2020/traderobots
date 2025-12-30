import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { TrendingUp } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await axios.post('/api/users/register/', {
                username,
                email,
                password
            });
            toast.success('Account created! Please log in.');
            navigate('/login');
        } catch (error: any) {
            toast.error(error.response?.data?.error || 'Signup failed');
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
                    <p className="text-muted-foreground">Join the future of AI trading</p>
                </div>

                <Card className="border-border/60 shadow-2xl glass-premium">
                    <CardHeader>
                        <CardTitle>Create Account</CardTitle>
                        <CardDescription>Join 50,000+ traders worldwide.</CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSignup}>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="username">Username</Label>
                                <Input
                                    id="username"
                                    placeholder="choose_username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="your@email.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="min 8 characters"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="flex flex-col gap-4">
                            <Button type="submit" className="w-full h-11 font-bold" disabled={isLoading}>
                                {isLoading ? "Creating Account..." : "Create Account"}
                            </Button>
                            <div className="text-sm text-center text-muted-foreground">
                                Already have an account? <Link to="/login" className="text-primary font-bold hover:underline">Sign In</Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default Signup;
