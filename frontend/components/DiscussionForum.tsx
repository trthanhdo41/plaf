'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle, 
  ThumbsUp, 
  ThumbsDown, 
  Reply, 
  Send, 
  User,
  Clock,
  Pin,
  CheckCircle
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ForumPost {
  id: number;
  title: string;
  content: string;
  author: string;
  author_id: number;
  created_at: string;
  updated_at: string;
  likes?: number;
  dislikes?: number;
  replies_count?: number;
  is_pinned?: boolean;
  is_solved?: boolean;
  tags?: string[];
}

interface ForumReply {
  id: number;
  post_id: number;
  content: string;
  author?: string;
  author_id?: number;
  student_id?: number;
  first_name?: string;
  last_name?: string;
  created_at: string;
  likes?: number;
  dislikes?: number;
  is_solution?: boolean;
}

interface DiscussionForumProps {
  lessonId: number;
  studentId: number;
  studentName: string;
}

export default function DiscussionForum({ lessonId, studentId, studentName }: DiscussionForumProps) {
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [selectedPost, setSelectedPost] = useState<ForumPost | null>(null);
  const [replies, setReplies] = useState<ForumReply[]>([]);
  const [showNewPostForm, setShowNewPostForm] = useState(false);
  const [newPostTitle, setNewPostTitle] = useState('');
  const [newPostContent, setNewPostContent] = useState('');
  const [newReplyContent, setNewReplyContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [userVotes, setUserVotes] = useState<Record<number, string>>({});

  useEffect(() => {
    loadPosts();
    loadUserVotes();
  }, [lessonId]);

  const loadUserVotes = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/lessons/${lessonId}/user-votes/${studentId}`);
      if (response.ok) {
        const data = await response.json();
        setUserVotes(data.votes || {});
      }
    } catch (error) {
      console.error('Failed to load user votes:', error);
    }
  };

  const loadPosts = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/lessons/${lessonId}/forum`);
      if (response.ok) {
        const data = await response.json();
        setPosts(data.posts || []);
      }
    } catch (error) {
      console.error('Failed to load posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadReplies = async (postId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/forum/posts/${postId}/replies`);
      if (response.ok) {
        const data = await response.json();
        setReplies(data.replies || []);
      }
    } catch (error) {
      console.error('Failed to load replies:', error);
    }
  };

  const handleCreatePost = async () => {
    if (!newPostTitle.trim() || !newPostContent.trim()) {
      alert('Please fill in both title and content');
      return;
    }

    console.log('Creating post:', { lessonId, studentId, studentName, title: newPostTitle });
    
    const apiUrl = `http://localhost:8000/api/lessons/${lessonId}/forum`;
    console.log('API URL:', apiUrl);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newPostTitle,
          content: newPostContent,
          author_id: studentId,
          author: studentName
        }),
      });

      console.log('Forum API response:', response.status, response.statusText);

      if (response.ok) {
        const result = await response.json();
        console.log('Post created successfully:', result);
        setNewPostTitle('');
        setNewPostContent('');
        setShowNewPostForm(false);
        loadPosts();
      } else {
        const errorText = await response.text();
        console.error('Failed to create post:', response.status, errorText);
        alert(`Failed to create post: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to create post:', error);
      alert('Network error: Failed to create post');
    }
  };

  const handleCreateReply = async (postId: number) => {
    if (!newReplyContent.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/api/forum/posts/${postId}/replies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newReplyContent,
          author_id: studentId,
          author: studentName
        }),
      });

      if (response.ok) {
        setNewReplyContent('');
        loadReplies(postId);
        loadPosts(); // Refresh to update reply count
      }
    } catch (error) {
      console.error('Failed to create reply:', error);
    }
  };

  const handleVote = async (postId: number, type: 'like' | 'dislike') => {
    console.log(`Voting ${type} on post ${postId}, current vote:`, userVotes[postId]);
    console.log('All user votes:', userVotes);
    
    try {
      const response = await fetch(`http://localhost:8000/api/forum/posts/${postId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          vote_type: type
        }),
      });

      if (response.ok) {
        // Update user vote state
        const currentVote = userVotes[postId];
        if (currentVote === type) {
          // Remove vote (unlike/undislike)
          setUserVotes(prev => {
            const newVotes = { ...prev };
            delete newVotes[postId];
            return newVotes;
          });
        } else {
          // Add/change vote
          setUserVotes(prev => {
            const newVotes = { ...prev, [postId]: type };
            console.log('Updated user votes:', newVotes);
            return newVotes;
          });
        }
        
        loadPosts();
        // Refresh selected post if it's the one being voted on
        if (selectedPost && selectedPost.id === postId) {
          // Reload the selected post with updated vote counts
          const response = await fetch(`http://localhost:8000/api/lessons/${lessonId}/forum`);
          if (response.ok) {
            const data = await response.json();
            const updatedPost = data.posts.find((p: any) => p.id === postId);
            if (updatedPost) {
              setSelectedPost({
                ...updatedPost,
                tags: updatedPost.tags || [],
                likes: updatedPost.likes || 0,
                dislikes: updatedPost.dislikes || 0,
                replies_count: updatedPost.replies_count || 0
              });
            }
          }
          loadReplies(postId);
        }
      }
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  const handleSelectPost = (post: ForumPost) => {
    // Add default values for missing fields
    const postWithDefaults = {
      ...post,
      tags: post.tags || [],
      likes: post.likes || 0,
      dislikes: post.dislikes || 0,
      replies_count: post.replies_count || 0
    };
    setSelectedPost(postWithDefaults);
    loadReplies(post.id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (selectedPost) {
    return (
      <div className="space-y-6">
        {/* Back to forum */}
        <Button 
          variant="outline" 
          onClick={() => setSelectedPost(null)}
          className="mb-4 !bg-gray-800 !text-white !border-gray-600 hover:!bg-gray-700 hover:!text-white hover:!border-gray-500 transition-colors"
        >
          ← Back to Forum
        </Button>

        {/* Post Detail */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  {selectedPost.is_pinned && <Pin className="w-4 h-4 text-yellow-500" />}
                  {selectedPost.is_solved && <CheckCircle className="w-4 h-4 text-green-500" />}
                  <CardTitle className="text-xl">{selectedPost.title}</CardTitle>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Avatar className="w-6 h-6">
                      <AvatarFallback className="text-xs">
                        {selectedPost.author.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <span>{selectedPost.author}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatDistanceToNow(new Date(selectedPost.created_at), { addSuffix: true })}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleVote(selectedPost.id, 'like')}
                  className={`flex items-center gap-1 ${
                    userVotes[selectedPost.id] === 'like' 
                      ? 'text-blue-600 bg-blue-50' 
                      : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  <ThumbsUp className="w-4 h-4" />
                  {selectedPost.likes || 0}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleVote(selectedPost.id, 'dislike')}
                  className={`flex items-center gap-1 ${
                    userVotes[selectedPost.id] === 'dislike' 
                      ? 'text-red-600 bg-red-50' 
                      : 'text-gray-600 hover:text-red-600'
                  }`}
                >
                  <ThumbsDown className="w-4 h-4" />
                  {selectedPost.dislikes || 0}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <p className="whitespace-pre-wrap">{selectedPost.content}</p>
            </div>
            {selectedPost.tags && selectedPost.tags.length > 0 && (
              <div className="flex gap-2 mt-4">
                {selectedPost.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary">{tag}</Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Replies */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            Replies ({replies.length})
          </h3>
          
          {replies.map((reply) => (
            <Card key={reply.id} className={reply.is_solution ? 'border-green-500' : ''}>
              <CardContent className="pt-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="text-sm">
                        {(reply.first_name || reply.author || 'U').charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-medium">
                        {reply.first_name && reply.last_name 
                          ? `${reply.first_name} ${reply.last_name}`
                          : reply.author || 'Unknown User'
                        }
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                      </div>
                    </div>
                    {reply.is_solution && (
                      <Badge className="bg-green-500">Solution</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex items-center gap-1"
                    >
                      <ThumbsUp className="w-3 h-3" />
                      {reply.likes}
                    </Button>
                  </div>
                </div>
                <p className="whitespace-pre-wrap">{reply.content}</p>
              </CardContent>
            </Card>
          ))}

          {/* New Reply Form */}
          <Card>
            <CardContent className="pt-4">
              <div className="space-y-3">
                <textarea
                  placeholder="Write your reply..."
                  value={newReplyContent}
                  onChange={(e) => setNewReplyContent(e.target.value)}
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                />
                <Button 
                  onClick={() => handleCreateReply(selectedPost.id)}
                  disabled={!newReplyContent.trim()}
                  className="flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Post Reply
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Discussion Forum</h2>
        <Button 
          onClick={() => setShowNewPostForm(true)}
          className="flex items-center gap-2"
        >
          <MessageCircle className="w-4 h-4" />
          New Discussion
        </Button>
      </div>

      {/* New Post Form */}
      {showNewPostForm && (
        <Card>
          <CardHeader>
            <CardTitle>Start a New Discussion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              type="text"
              placeholder="Discussion title..."
              value={newPostTitle}
              onChange={(e) => setNewPostTitle(e.target.value)}
              className="w-full p-3 border rounded-lg"
            />
            <textarea
              placeholder="What would you like to discuss?"
              value={newPostContent}
              onChange={(e) => setNewPostContent(e.target.value)}
              className="w-full p-3 border rounded-lg resize-none"
              rows={4}
            />
            <div className="flex gap-2">
              <Button 
                onClick={handleCreatePost}
                disabled={!newPostTitle.trim() || !newPostContent.trim()}
              >
                Create Discussion
              </Button>
              <Button 
                variant="outline"
                onClick={() => {
                  setShowNewPostForm(false);
                  setNewPostTitle('');
                  setNewPostContent('');
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Posts List */}
      <div className="space-y-4">
        {posts.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-600 mb-2">No discussions yet</h3>
              <p className="text-gray-500 mb-4">Be the first to start a discussion about this lesson!</p>
              <Button onClick={() => setShowNewPostForm(true)}>
                Start Discussion
              </Button>
            </CardContent>
          </Card>
        ) : (
          posts.map((post) => (
            <Card 
              key={post.id} 
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleSelectPost(post)}
            >
              <CardContent className="pt-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {post.is_pinned && <Pin className="w-4 h-4 text-yellow-500" />}
                      {post.is_solved && <CheckCircle className="w-4 h-4 text-green-500" />}
                      <h3 className="font-semibold text-lg">{post.title}</h3>
                    </div>
                    <p className="text-gray-600 mb-3 line-clamp-2">{post.content}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        {post.author}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}
                      </div>
                      <div className="flex items-center gap-1">
                        <Reply className="w-4 h-4" />
                        {post.replies_count || 0} replies
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleVote(post.id, 'like');
                      }}
                      className={`flex items-center gap-1 ${
                        userVotes[post.id] === 'like' 
                          ? 'text-blue-600 bg-blue-50' 
                          : 'text-gray-600 hover:text-blue-600'
                      }`}
                    >
                      <ThumbsUp className="w-4 h-4" />
                      {post.likes || 0}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleVote(post.id, 'dislike');
                      }}
                      className={`flex items-center gap-1 ${
                        userVotes[post.id] === 'dislike' 
                          ? 'text-red-600 bg-red-50' 
                          : 'text-gray-600 hover:text-red-600'
                      }`}
                    >
                      <ThumbsDown className="w-4 h-4" />
                      {post.dislikes || 0}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
