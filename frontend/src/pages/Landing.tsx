import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
    Image as ImageIcon,
    Video,
    MessageSquare,
    Heart,
    Share2,
    TrendingUp,
    Zap,
    Cpu
} from 'lucide-react';

interface Post {
    id: number;
    user_name: string;
    content: string;
    likes_count: number;
    comments_count: number;
    media_urls?: string[];
    comments?: Array<{
        id: number;
        user_name: string;
        content: string;
        created_at: string;
    }>;
    created_at: string;
}

interface Robot {
    id: string;
    name?: string;
    user_name: string;
    symbol: string;
    win_rate: number;
    method: string;
}

const Landing = () => {
    const navigate = useNavigate();
    const [posts, setPosts] = useState<Post[]>([]);
    const [trendingRobots, setTrendingRobots] = useState<Robot[]>([]);
    const [postContent, setPostContent] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [commentTexts, setCommentTexts] = useState<{ [key: number]: string }>({});
    const userString = localStorage.getItem('user');

    useEffect(() => {
        fetchPosts();
        fetchTrendingRobots();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await axios.get('/api/social/posts/');
            if (Array.isArray(response.data)) {
                setPosts(response.data);
            } else {
                setPosts([]);
                console.error('API Error: Posts response is not an array', response.data);
            }
        } catch (error) {
            console.error('Error fetching posts:', error);
            setPosts([]);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchTrendingRobots = async () => {
        try {
            const response = await axios.get('/api/robots/');
            setTrendingRobots(response.data.slice(0, 3));
        } catch (error) {
            console.error('Error fetching robots:', error);
        }
    };

    const handleCreatePost = async () => {
        if (!postContent.trim()) return;
        try {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            await axios.post('/api/social/posts/', {
                content: postContent,
                user: user.id
            });
            setPostContent('');
            fetchPosts();
            toast.success('Insight posted!');
        } catch (error) {
            toast.error('Failed to post insight');
        }
    };

    const handleLike = async (postId: number) => {
        try {
            await axios.post(`/api/social/posts/${postId}/like/`);
            fetchPosts();
        } catch (error) {
            toast.error('Failed to like post');
        }
    };

    const handleComment = async (postId: number) => {
        const text = commentTexts[postId];
        if (!text?.trim()) return;
        try {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            await axios.post('/api/social/posts/comment/', {
                post: postId,
                content: text,
                user: user.id
            });
            setCommentTexts(prev => ({ ...prev, [postId]: '' }));
            fetchPosts();
            toast.success('Comment added!');
        } catch (error) {
            toast.error('Failed to add comment');
        }
    };

    return (
        <div className="flex flex-col gap-8 p-4 md:p-8 max-w-7xl mx-auto">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight">Social Feed</h1>
                    <p className="text-muted-foreground">Stay updated with the latest AI trading insights.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        className="gap-2"
                        onClick={() => toast.info('AI Daily Market Summary: Bullish on JPY/CNY pairs. Neutral on EUR.')}
                    >
                        <TrendingUp className="h-4 w-4" /> Market Summary
                    </Button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Main Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    {/* Create Post Card */}
                    {userString ? (
                        <Card className="border-primary/10 bg-primary/5 shadow-none group">
                            <CardContent className="pt-6">
                                <div className="flex gap-4">
                                    <Avatar className="h-10 w-10 border border-primary/20">
                                        <AvatarFallback className="bg-primary/10 text-primary font-bold">U</AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1 space-y-4">
                                        <Textarea
                                            placeholder="Analyze the markets or share your results..."
                                            value={postContent}
                                            onChange={(e) => setPostContent(e.target.value)}
                                            className="min-h-[100px] bg-background/50 border-none focus-visible:ring-1 focus-visible:ring-primary/30 resize-none text-base"
                                        />
                                        <div className="flex items-center justify-between pt-2">
                                            <div className="flex gap-1">
                                                <Button variant="ghost" size="sm" className="h-9 px-3 gap-2 text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all">
                                                    <ImageIcon className="h-4 w-4" />
                                                    <span className="text-xs font-bold">Chart</span>
                                                </Button>
                                                <Button variant="ghost" size="sm" className="h-9 px-3 gap-2 text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all">
                                                    <Video className="h-4 w-4" />
                                                    <span className="text-xs font-bold">Stream</span>
                                                </Button>
                                            </div>
                                            <Button
                                                onClick={handleCreatePost}
                                                className="h-9 px-6 rounded-full font-bold shadow-lg shadow-primary/20 bg-primary hover:scale-105 transition-transform"
                                            >
                                                Post Insight
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ) : (
                        <Card className="border-dashed bg-muted/20">
                            <CardContent className="py-10 text-center space-y-4">
                                <p className="text-sm text-muted-foreground">Join the community to share your trading insights.</p>
                                <Button onClick={() => navigate('/login')} size="sm" className="font-bold">Login to Post</Button>
                            </CardContent>
                        </Card>
                    )}

                    {/* Posts List */}
                    {isLoading ? (
                        <div className="flex justify-center p-12">
                            <Zap className="animate-pulse h-8 w-8 text-primary" />
                        </div>
                    ) : (
                        posts.map((post) => (
                            <Card key={post.id} className="border-border/60 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300 overflow-hidden">
                                <CardHeader className="flex flex-row items-start gap-4 pb-4">
                                    <Avatar className="h-12 w-12 border-2 border-background shadow-sm">
                                        <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${post.user_name}`} />
                                        <AvatarFallback>{post.user_name[0]}</AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h3 className="font-bold text-lg leading-none">{post.user_name}</h3>
                                                <p className="text-xs text-muted-foreground mt-1">@{post.user_name.toLowerCase()} • {new Date(post.created_at).toLocaleTimeString()}</p>
                                            </div>
                                            <Badge variant="secondary" className="bg-green-500/10 text-green-500 border-none">EARLY ACCESS</Badge>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <p className="text-base text-card-foreground leading-relaxed">
                                        {post.content}
                                    </p>
                                    {post.media_urls && post.media_urls.length > 0 && (
                                        <div className="aspect-video bg-muted rounded-2xl border border-border/50 flex items-center justify-center overflow-hidden">
                                            <img src={post.media_urls[0]} alt="Post media" className="object-cover w-full h-full" />
                                        </div>
                                    )}
                                </CardContent>
                                <CardFooter className="pt-0 flex flex-col items-start gap-4">
                                    <div className="flex items-center gap-6 w-full h-10 border-t border-border/50 pt-4 mt-2">
                                        <Button
                                            onClick={() => handleLike(post.id)}
                                            variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-red-500 hover:bg-red-500/5 transition-all"
                                        >
                                            <Heart className="h-4 w-4" />
                                            <span className="text-xs font-bold">{post.likes_count}</span>
                                        </Button>
                                        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-primary hover:bg-primary/5 transition-all">
                                            <MessageSquare className="h-4 w-4" />
                                            <span className="text-xs font-bold">{post.comments?.length || 0}</span>
                                        </Button>
                                        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground hover:text-primary hover:bg-primary/5 transition-all">
                                            <Share2 className="h-4 w-4" />
                                            <span className="text-xs font-bold">Share</span>
                                        </Button>
                                    </div>

                                    <div className="w-full space-y-3 pt-2">
                                        {post.comments?.map((comment: any) => (
                                            <div key={comment.id} className="flex gap-2 text-sm bg-muted/30 p-2 rounded-xl">
                                                <span className="font-bold text-xs">{comment.user_name}:</span>
                                                <span className="text-muted-foreground text-xs">{comment.content}</span>
                                            </div>
                                        ))}
                                        <div className="flex items-center gap-2 w-full pt-2">
                                            <Input
                                                placeholder="Add a comment..."
                                                className="h-8 text-xs bg-muted/50 border-none rounded-lg"
                                                value={commentTexts[post.id] || ''}
                                                onChange={(e) => setCommentTexts(prev => ({ ...prev, [post.id]: e.target.value }))}
                                                onKeyDown={(e) => e.key === 'Enter' && handleComment(post.id)}
                                            />
                                            <Button size="sm" className="h-8 px-3 text-[10px] font-bold" onClick={() => handleComment(post.id)}>Reply</Button>
                                        </div>
                                    </div>
                                </CardFooter>
                            </Card>
                        ))
                    )}
                </div>

                {/* Sidebar Widgets */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
                        <CardHeader>
                            <CardTitle className="text-xl flex items-center gap-2">
                                <Cpu className="h-5 w-5 text-primary" /> Trending Robots
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-4">
                            {trendingRobots.length > 0 ? trendingRobots.map((robot) => (
                                <div
                                    key={robot.id}
                                    className="flex justify-between items-center p-3 rounded-xl hover:bg-background/80 transition-all cursor-pointer border border-transparent hover:border-border group shadow-sm bg-card/50"
                                >
                                    <div className="flex flex-col">
                                        <span className="font-bold group-hover:text-primary transition-colors">{robot.name || `Robot ${robot.symbol}`}</span>
                                        <span className="text-[10px] text-muted-foreground uppercase">{robot.symbol}</span>
                                    </div>
                                    <Badge className="bg-green-500/10 text-green-500 border-none">+{robot.win_rate}%</Badge>
                                </div>
                            )) : (
                                <p className="text-xs text-muted-foreground text-center py-4">No robots active yet.</p>
                            )}
                        </CardContent>
                        <CardFooter>
                            <Button variant="link" onClick={() => navigate('/robots')} className="text-xs text-primary font-bold p-0">Explore All Strategies →</Button>
                        </CardFooter>
                    </Card>

                    <Card className="bg-card">
                        <CardHeader>
                            <CardTitle className="text-lg">Robot of the Week</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col items-center text-center gap-4">
                                <div className="p-4 bg-primary rounded-3xl shadow-xl shadow-primary/20">
                                    <Zap className="h-10 w-10 text-primary-foreground fill-primary-foreground" />
                                </div>
                                <div>
                                    <h4 className="font-black text-xl italic tracking-tighter uppercase">GOLDEN EYE AI</h4>
                                    <p className="text-xs text-muted-foreground mt-1">Specialized in XAUUSD Mean Reversion</p>
                                </div>
                                <Button className="w-full h-11 rounded-xl font-bold">Copy Strategy</Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default Landing;
