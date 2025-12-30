import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Heart, MessageCircle, Send, ImagePlus, User, ShieldAlert } from 'lucide-react';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const Social = () => {
    const [posts, setPosts] = useState<any[]>([]);
    const [newPost, setNewPost] = useState('');
    const [errorDialog, setErrorDialog] = useState({ open: false, title: '', description: '' });
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await axios.get('/api/social/posts/');
            setPosts(response.data);
        } catch (error) {
            console.error('Error fetching posts:', error);
            setErrorDialog({
                open: true,
                title: 'Data Load Error',
                description: 'Unable to retrieve community posts.'
            });
        }
    };

    const handleCreatePost = async () => {
        if (!newPost.trim()) return;
        try {
            await axios.post('/api/social/posts/', {
                content: newPost,
                user: user.id
            });
            setNewPost('');
            toast.success('Post created successfully!');
            fetchPosts();
        } catch (error: any) {
            const msg = error.response?.data?.error || 'Failed to create post';
            setErrorDialog({
                open: true,
                title: 'Post Failed',
                description: msg
            });
        }
    };

    const handleLikePost = async (postId: number) => {
        try {
            await axios.post(`/api/social/posts/${postId}/like/`);
            fetchPosts();
        } catch (error) {
            console.error('Error liking post:', error);
        }
    };

    const handleCommentPost = async (postId: number) => {
        const content = prompt('Enter your comment:');
        if (!content) return;
        try {
            await axios.post('/api/social/posts/comment/', {
                post: postId,
                content
            });
            toast.success('Comment added!');
            fetchPosts();
        } catch (error) {
            toast.error('Failed to add comment');
        }
    };

    return (
        <div className="p-4 md:p-8 max-w-4xl mx-auto flex flex-col gap-6">
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">Community Feed</h1>
                <p className="text-muted-foreground">Connect with traders worldwide and share your trading journey.</p>
            </header>

            {/* Create Post */}
            <Card className="border-border/60 shadow-sm">
                <CardHeader className="pb-4">
                    <div className="flex items-start gap-4">
                        <Avatar className="h-10 w-10 border border-border">
                            <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`} />
                            <AvatarFallback><User className="h-5 w-5" /></AvatarFallback>
                        </Avatar>
                        <div className="flex-1 flex flex-col gap-3">
                            <Textarea
                                placeholder="Share your trading insights, strategies, or questions..."
                                value={newPost}
                                onChange={(e) => setNewPost(e.target.value)}
                                className="min-h-[100px] resize-none bg-muted/30 border-border focus-visible:ring-primary/20"
                            />
                            <div className="flex justify-between items-center">
                                <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
                                    <ImagePlus className="h-4 w-4" />
                                    Add Media
                                </Button>
                                <Button
                                    onClick={handleCreatePost}
                                    disabled={!newPost.trim()}
                                    className="gap-2 font-bold shadow-lg shadow-primary/20"
                                    size="sm"
                                >
                                    <Send className="h-4 w-4" />
                                    Post
                                </Button>
                            </div>
                        </div>
                    </div>
                </CardHeader>
            </Card>

            {/* Posts Feed */}
            <div className="flex flex-col gap-4">
                {posts.length > 0 ? posts.map((post) => (
                    <Card key={post.id} className="border-border/60 shadow-sm hover:shadow-md transition-all">
                        <CardContent className="p-6">
                            <div className="flex items-start gap-4">
                                <Avatar className="h-12 w-12 border border-border">
                                    <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${post.user_name}`} />
                                    <AvatarFallback>{post.user_name?.[0]}</AvatarFallback>
                                </Avatar>
                                <div className="flex-1 flex flex-col gap-3">
                                    <div className="flex flex-col gap-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold">@{post.user_name}</span>
                                            <span className="text-xs text-muted-foreground">
                                                {new Date(post.created_at).toLocaleDateString()} • {new Date(post.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                    </div>
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>

                                    {/* Media */}
                                    {post.media_urls && post.media_urls.length > 0 && (
                                        <div className="grid grid-cols-2 gap-2 mt-2">
                                            {post.media_urls.map((url: string, idx: number) => (
                                                <img key={idx} src={url} alt="Post media" className="rounded-lg border border-border" />
                                            ))}
                                        </div>
                                    )}

                                    {/* Actions */}
                                    <div className="flex items-center gap-6 pt-3 border-t border-border/50">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="gap-2 hover:bg-red-500/10 hover:text-red-500 transition-colors"
                                            onClick={() => handleLikePost(post.id)}
                                        >
                                            <Heart className="h-4 w-4" />
                                            <span className="font-bold">{post.likes_count || 0}</span>
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="gap-2 hover:bg-blue-500/10 hover:text-blue-500 transition-colors"
                                            onClick={() => handleCommentPost(post.id)}
                                        >
                                            <MessageCircle className="h-4 w-4" />
                                            <span className="font-bold">{post.comments?.length || 0}</span>
                                        </Button>
                                    </div>

                                    {/* Comments */}
                                    {post.comments && post.comments.length > 0 && (
                                        <div className="flex flex-col gap-3 pt-3 border-t border-border/30 mt-2">
                                            {post.comments.map((comment: any) => (
                                                <div key={comment.id} className="flex items-start gap-3 bg-muted/30 p-3 rounded-xl">
                                                    <Avatar className="h-8 w-8 border border-border">
                                                        <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${comment.user_name}`} />
                                                        <AvatarFallback>{comment.user_name?.[0]}</AvatarFallback>
                                                    </Avatar>
                                                    <div className="flex-1 flex flex-col gap-1">
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-sm font-bold">@{comment.user_name}</span>
                                                            <span className="text-[10px] text-muted-foreground">
                                                                {new Date(comment.created_at).toLocaleDateString()}
                                                            </span>
                                                        </div>
                                                        <p className="text-xs leading-relaxed">{comment.content}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )) : (
                    <Card className="border-border/60 border-dashed">
                        <CardContent className="flex flex-col items-center justify-center py-16 opacity-40">
                            <MessageCircle className="h-12 w-12 mb-4" />
                            <p className="text-sm italic">No posts yet. Be the first to share something!</p>
                        </CardContent>
                    </Card>
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
        </div >
    );
};

export default Social;
