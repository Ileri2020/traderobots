import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Hash, Users, Star, Send, MessageSquare } from 'lucide-react';
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

const Chat = () => {
    const [groups, setGroups] = useState<any[]>([]);
    const [activeGroup, setActiveGroup] = useState<any>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
    const [newGroupName, setNewGroupName] = useState('');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        fetchGroups();
    }, []);

    useEffect(() => {
        if (activeGroup) {
            fetchMessages(activeGroup.id);
            const interval = setInterval(() => fetchMessages(activeGroup.id), 3000);
            return () => clearInterval(interval);
        }
    }, [activeGroup]);

    const fetchGroups = async () => {
        try {
            const response = await axios.get('/api/social/groups/');
            setGroups(response.data);
            if (response.data.length > 0 && !activeGroup) {
                setActiveGroup(response.data[0]);
            }
        } catch (error) {
            console.error('Error fetching groups:', error);
        }
    };

    const fetchMessages = async (groupId: number) => {
        try {
            const response = await axios.get(`/api/social/messages/?group_id=${groupId}`);
            setMessages(response.data);
        } catch (error) {
            console.error('Error fetching messages:', error);
        }
    };

    const handleSendMessage = async () => {
        if (!newMessage.trim() || !activeGroup) return;
        try {
            await axios.post('/api/social/messages/', {
                group: activeGroup.id,
                content: newMessage,
                sender: user.id
            });
            setNewMessage('');
            fetchMessages(activeGroup.id);
        } catch (error) {
            toast.error('Failed to send message');
        }
    };

    const handleJoinGroup = async (groupId: number) => {
        try {
            await axios.post(`/api/social/groups/${groupId}/join/`);
            toast.success('Joined group!');
            fetchGroups();
        } catch (error) {
            toast.error('Failed to join group');
        }
    };

    const handleCreateGroup = async () => {
        if (!newGroupName.trim()) return;
        try {
            const response = await axios.post('/api/social/groups/', {
                name: newGroupName,
            });
            toast.success('Community created!');
            setNewGroupName('');
            setIsCreateDialogOpen(false);
            fetchGroups();
            setActiveGroup(response.data);
        } catch (error) {
            toast.error('Failed to create community');
        }
    };

    return (
        <div className="flex h-[calc(100vh-100px)] gap-6 p-6 overflow-hidden">
            {/* Sidebar: Groups & Channels */}
            <div className="w-80 flex flex-col gap-6 bg-card rounded-2xl border border-border overflow-hidden shadow-sm">
                <div className="p-6 border-b border-border bg-muted/20">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Users className="h-5 w-5 text-primary" /> Communities
                    </h2>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    <div className="px-4 py-4">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest pl-2">Available Groups</span>
                        <div className="mt-2 flex flex-col gap-1">
                            {groups.map(group => (
                                <button
                                    key={group.id}
                                    onClick={() => setActiveGroup(group)}
                                    className={`p-3 text-left rounded-xl transition-all duration-200 flex flex-col gap-1 group ${activeGroup?.id === group.id ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20' : 'hover:bg-muted'}`}
                                >
                                    <div className="flex justify-between items-center w-full">
                                        <span className="font-bold">{group.name}</span>
                                        <Star className={`h-3 w-3 ${activeGroup?.id === group.id ? 'text-primary-foreground' : 'text-yellow-500'}`} />
                                    </div>
                                    <span className={`text-[10px] ${activeGroup?.id === group.id ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                                        {group.members?.length || 0} members
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-4 border-t border-border">
                    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                        <DialogTrigger asChild>
                            <Button variant="outline" className="w-full gap-2 text-xs font-bold h-10 border-dashed">
                                Create New Community +
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Establish New Community</DialogTitle>
                                <DialogDescription>Create a space for traders to discuss specific symbols or strategies.</DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="name">Community Name</Label>
                                    <Input
                                        id="name"
                                        placeholder="e.g. Gold Scalpers Elite"
                                        value={newGroupName}
                                        onChange={(e) => setNewGroupName(e.target.value)}
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button className="w-full" onClick={handleCreateGroup}>Create Community</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col bg-card rounded-2xl border border-border overflow-hidden shadow-sm relative">
                {activeGroup ? (
                    <>
                        <header className="p-6 border-b border-border flex justify-between items-center bg-muted/5">
                            <div className="flex items-center gap-4">
                                <div className="h-12 w-12 bg-primary/10 rounded-2xl flex items-center justify-center border border-primary/20">
                                    <Hash className="h-6 w-6 text-primary" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold">#{activeGroup.name.toLowerCase().replace(/\s+/g, '-')}</h3>
                                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                                        Active since {new Date(activeGroup.created_at || Date.now()).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                            <Button
                                variant="secondary"
                                size="sm"
                                className="font-bold h-9 bg-primary/10 text-primary hover:bg-primary hover:text-white transition-all"
                                onClick={() => handleJoinGroup(activeGroup.id)}
                            >
                                Join Community
                            </Button>
                        </header>

                        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 custom-scrollbar">
                            {messages.length > 0 ? messages.map((m) => (
                                <div key={m.id} className={`flex gap-4 ${m.sender === user.id ? 'flex-row-reverse' : ''}`}>
                                    <Avatar className="h-10 w-10 border border-border shadow-sm">
                                        <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${m.sender_name}`} />
                                        <AvatarFallback>{m.sender_name?.[0]}</AvatarFallback>
                                    </Avatar>
                                    <div className={`flex flex-col gap-1 max-w-[70%] ${m.sender === user.id ? 'items-end' : ''}`}>
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold text-sm">{m.sender === user.id ? 'You' : m.sender_name}</span>
                                            <span className="text-[10px] text-muted-foreground">{new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <p className={`text-sm p-3 rounded-2xl ${m.sender === user.id ? 'bg-primary text-primary-foreground rounded-tr-none shadow-md shadow-primary/10' : 'bg-muted/50 rounded-tl-none border border-border/50'}`}>
                                            {m.content}
                                        </p>
                                    </div>
                                </div>
                            )) : (
                                <div className="flex-1 flex flex-col items-center justify-center opacity-40 gap-4">
                                    <MessageSquare className="h-16 w-16" />
                                    <p className="font-bold italic">No messages yet. Be the first to start the conversation!</p>
                                </div>
                            )}
                        </div>

                        <div className="p-6 border-t border-border bg-muted/20">
                            <div className="bg-background border border-border p-2 pr-2 rounded-2xl flex items-center gap-2 shadow-inner focus-within:ring-2 ring-primary/20 transition-all">
                                <Input
                                    type="text"
                                    placeholder={`Message # ${activeGroup.name.toLowerCase()}`}
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                    className="flex-1 bg-transparent border-none focus-visible:ring-0 px-4 h-10 shadow-none text-base"
                                />
                                <Button
                                    size="icon"
                                    className="h-10 w-10 rounded-xl bg-primary text-white shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-all"
                                    onClick={handleSendMessage}
                                >
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center gap-6 opacity-30">
                        <Users className="h-24 w-24" />
                        <h2 className="text-2xl font-black italic tracking-tighter">SELECT A COMMUNITY</h2>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Chat;
