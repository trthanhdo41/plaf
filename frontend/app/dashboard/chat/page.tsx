'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  MessageCircle, 
  GraduationCap,
  BarChart,
  LogOut,
  Menu,
  Send,
  ArrowLeft,
  Trash2,
  Bot,
  User,
  Sparkles
} from 'lucide-react';
import { api, Student, ChatMessage } from '@/lib/api';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

export default function ChatPage() {
  const router = useRouter();
  const [student, setStudent] = useState<Student | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const storedStudent = localStorage.getItem('student');
    if (!storedStudent) {
      router.push('/');
      return;
    }

    const studentData = JSON.parse(storedStudent);
    setStudent(studentData);
    loadChatHistory(studentData.id_student);
  }, [router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async (studentId: number) => {
    try {
      const data = await api.getChatHistory(studentId, 50);
      setMessages(data.history || []);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || !student || sending) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setSending(true);

    // Show user message immediately (optimistic update)
    const tempUserMessage: ChatMessage = {
      student_id: student.id_student,
      message: userMessage,
      response: '', // Will be filled when AI responds
      timestamp: new Date().toISOString(),
    };
    setMessages([...messages, tempUserMessage]);

    // Build conversation context from recent messages
    const conversationContext = messages
      .slice(-3)
      .map(m => `Student: ${m.message}\nAdvisor: ${m.response}`)
      .join('\n');

    try {
      const result = await api.sendMessage(student.id_student, userMessage, conversationContext);

      // Reload chat history to get the complete message with AI response
      await loadChatHistory(student.id_student);
    } catch (error: any) {
      console.error('Failed to send message:', error);
      alert('Failed to send message: ' + (error.message || 'Unknown error'));
      // Remove the temporary message on error
      await loadChatHistory(student.id_student);
    } finally {
      setSending(false);
    }
  };

  const handleClearHistory = async () => {
    if (!student) return;
    
    if (!confirm('Are you sure you want to clear your chat history?')) return;

    try {
      await api.clearChatHistory(student.id_student);
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
      alert('Failed to clear chat history');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('student');
    router.push('/');
  };

  if (loading || !student) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Advisor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <img src="/study.png" alt="PLAF" className="w-10 h-10 rounded-lg object-cover" />
              <span className="text-xl font-bold text-gray-900">PLAF</span>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <BarChart className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
              <Link href="/dashboard/courses" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <BookOpen className="w-5 h-5" />
                <span>My Courses</span>
              </Link>
              <Link href="/dashboard/chat" className="flex items-center gap-2 text-blue-600 font-medium">
                <MessageCircle className="w-5 h-5" />
                <span>AI Advisor</span>
              </Link>
            </div>

            <div className="flex items-center gap-4">
              <Link href="/dashboard/profile" className="hidden md:flex items-center gap-3 hover:opacity-80 transition-opacity" title="View Profile">
                <Avatar className="cursor-pointer">
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    {student.first_name[0]}{student.last_name[0]}
                  </AvatarFallback>
                </Avatar>
                <div className="text-sm">
                  <div className="font-semibold text-gray-900">{student.first_name} {student.last_name}</div>
                  <div className="text-gray-500">{student.email}</div>
                </div>
              </Link>
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
                <Menu className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {menuOpen && (
            <div className="md:hidden py-4 border-t">
              <div className="flex flex-col gap-2">
                <Link href="/dashboard" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BarChart className="w-5 h-5" />
                  <span>Dashboard</span>
                </Link>
                <Link href="/dashboard/courses" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BookOpen className="w-5 h-5" />
                  <span>My Courses</span>
                </Link>
                <Link href="/dashboard/chat" className="flex items-center gap-2 px-4 py-3 text-blue-600 bg-blue-50 rounded-lg font-medium">
                  <MessageCircle className="w-5 h-5" />
                  <span>AI Advisor</span>
                </Link>
                <Link href="/dashboard/profile" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <User className="w-5 h-5" />
                  <span>My Profile</span>
                </Link>
                <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg w-full text-left">
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-4 py-8 flex flex-col max-w-6xl">
        {/* Header */}
        <div className="mb-6">
          <Link href="/dashboard">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                AI Academic Advisor
                <Badge variant="secondary" className="text-sm">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Online
                </Badge>
              </h1>
              <p className="text-gray-600">Get personalized academic support and guidance 24/7</p>
            </div>
            {messages.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleClearHistory}>
                <Trash2 className="w-4 h-4 mr-2" />
                Clear History
              </Button>
            )}
          </div>
        </div>

        {/* Chat Container */}
        <Card className="flex-1 flex flex-col">
          {/* Context Info Banner */}
          {messages.length > 0 && (
            <div className="border-b bg-blue-50 px-6 py-3">
              <div className="flex items-center gap-2 text-sm text-blue-800">
                <Sparkles className="w-4 h-4" />
                <p>
                  <strong>Context:</strong> I remember our previous {messages.length} conversation{messages.length > 1 ? 's' : ''}. 
                  I can refer to our earlier discussions to provide more personalized advice.
                </p>
              </div>
            </div>
          )}
          
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6" style={{ maxHeight: 'calc(100vh - 400px)' }}>
            {messages.length === 0 ? (
              <div className="text-center py-16">
                <div className="w-32 h-32 mx-auto mb-6">
                  <img src="/chatbot.jpg" alt="AI Advisor" className="w-full h-full object-cover rounded-full" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Start a Conversation</h3>
                <p className="text-gray-600 max-w-md mx-auto mb-8 text-base">
                  Ask me anything about your courses, study strategies, assignments, or academic concerns. I'm here to help you succeed!
                </p>
                <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
                  {[
                    "How can I improve my grades?",
                    "What are my upcoming deadlines?",
                    "I'm struggling with time management",
                    "Explain this concept to me"
                  ].map((suggestion, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      size="sm"
                      onClick={() => setInputMessage(suggestion)}
                      className="text-sm"
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, idx) => (
                  <div key={idx} className="space-y-4">
                    {/* User Message */}
                    <div className="flex items-start gap-3 justify-end">
                      <div className="flex-1 max-w-2xl">
                        <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-2xl rounded-tr-sm p-4 shadow-sm">
                          <p className="text-sm leading-relaxed">{msg.message}</p>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-right">
                          {msg.timestamp && formatDistanceToNow(new Date(msg.timestamp), { addSuffix: true })}
                        </p>
                      </div>
                      <Avatar className="w-9 h-9">
                        <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white text-sm">
                          <User className="w-5 h-5" />
                        </AvatarFallback>
                      </Avatar>
                    </div>

                    {/* AI Response */}
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-full overflow-hidden flex-shrink-0">
                        <img src="/chatbot.jpg" alt="AI Advisor" className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-1 max-w-2xl">
                        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm p-4 shadow-sm">
                          {msg.response ? (
                            <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{msg.response}</p>
                          ) : (
                            <div className="flex items-center gap-2 text-gray-500">
                              <div className="flex gap-1">
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                              </div>
                              <span className="text-sm">AI is thinking...</span>
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          AI Advisor • {msg.timestamp && formatDistanceToNow(new Date(msg.timestamp), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t bg-gray-50 p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message here..."
                disabled={sending}
                className="flex-1 h-12 bg-white"
                autoFocus
              />
              <Button 
                type="submit" 
                disabled={!inputMessage.trim() || sending}
                size="lg"
                className="px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Send className="w-5 h-5" />
              </Button>
            </form>
            <p className="text-xs text-gray-500 mt-2 text-center">
              AI Advisor uses advanced language models to provide personalized academic support
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}

