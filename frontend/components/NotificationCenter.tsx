'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { 
  Bell, 
  BellRing,
  AlertTriangle,
  TrendingUp,
  Calendar,
  CheckCircle,
  X,
  Settings
} from 'lucide-react';

interface Notification {
  id: string;
  type: 'risk_change' | 'intervention_reminder' | 'progress_update' | 'system_alert';
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
}

interface NotificationCenterProps {
  student: any;
}

export default function NotificationCenter({ student }: NotificationCenterProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const { toast } = useToast();
  
  const riskPercentage = (student.risk_probability || 0) * 100;
  
  // Generate notifications based on student data
  useEffect(() => {
    const generateNotifications = (): Notification[] => {
      const notifs: Notification[] = [];
      const now = new Date();
      
      // Risk change notification
      if (riskPercentage >= 85) {
        notifs.push({
          id: 'risk-critical',
          type: 'risk_change',
          title: 'Critical Risk Level Detected',
          message: `Your risk level has reached ${riskPercentage.toFixed(1)}%. Immediate action recommended.`,
          priority: 'high',
          timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000), // 2 hours ago
          read: false,
          actionUrl: '/dashboard/chat'
        });
      } else if (riskPercentage >= 70) {
        notifs.push({
          id: 'risk-high',
          type: 'risk_change',
          title: 'High Risk Level Alert',
          message: `Your risk level is ${riskPercentage.toFixed(1)}%. Consider seeking additional support.`,
          priority: 'medium',
          timestamp: new Date(now.getTime() - 6 * 60 * 60 * 1000), // 6 hours ago
          read: false,
          actionUrl: '/dashboard/chat'
        });
      }
      
      // Intervention reminder
      if (riskPercentage >= 50) {
        notifs.push({
          id: 'intervention-reminder',
          type: 'intervention_reminder',
          title: 'Intervention Follow-up',
          message: 'How are you progressing with the recommended study strategies?',
          priority: 'medium',
          timestamp: new Date(now.getTime() - 24 * 60 * 60 * 1000), // 1 day ago
          read: false,
          actionUrl: '/dashboard'
        });
      }
      
      // Progress update
      if (student.avg_score >= 80) {
        notifs.push({
          id: 'progress-positive',
          type: 'progress_update',
          title: 'Excellent Performance!',
          message: `Great job! Your average score of ${student.avg_score}% shows strong academic performance.`,
          priority: 'low',
          timestamp: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
          read: true
        });
      }
      
      // Engagement reminder
      if (student.num_days_active < 30) {
        notifs.push({
          id: 'engagement-low',
          type: 'system_alert',
          title: 'Increase Your Engagement',
          message: 'Regular platform engagement helps improve learning outcomes. Try to visit daily!',
          priority: 'medium',
          timestamp: new Date(now.getTime() - 12 * 60 * 60 * 1000), // 12 hours ago
          read: false,
          actionUrl: '/dashboard/courses'
        });
      }
      
      // Weekly check-in
      notifs.push({
        id: 'weekly-checkin',
        type: 'system_alert',
        title: 'Weekly Progress Check-in',
        message: 'Time for your weekly progress review. How has your learning been going?',
        priority: 'low',
        timestamp: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), // 1 week ago
        read: true,
        actionUrl: '/dashboard'
      });
      
      return notifs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    };
    
    const notifs = generateNotifications();
    setNotifications(notifs);
    setUnreadCount(notifs.filter(n => !n.read).length);
  }, [student, riskPercentage]);
  
  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };
  
  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
    setUnreadCount(0);
  };
  
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
    const notif = notifications.find(n => n.id === id);
    if (notif && !notif.read) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };
  
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'risk_change': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'progress_update': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'intervention_reminder': return <Calendar className="w-4 h-4 text-blue-500" />;
      case 'system_alert': return <Bell className="w-4 h-4 text-orange-500" />;
      default: return <Bell className="w-4 h-4 text-gray-500" />;
    }
  };
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'medium': return 'border-l-orange-500 bg-orange-50';
      case 'low': return 'border-l-blue-500 bg-blue-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
        className="relative"
      >
        {unreadCount > 0 ? (
          <BellRing className="w-5 h-5 text-orange-600" />
        ) : (
          <Bell className="w-5 h-5" />
        )}
        {unreadCount > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs p-0"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Button>
      
      {/* Notification Panel */}
      {isOpen && (
        <Card className="absolute right-0 top-12 w-96 max-h-96 overflow-hidden shadow-lg z-50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">Notifications</CardTitle>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                    Mark all read
                  </Button>
                )}
                <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-80 overflow-y-auto">
            {notifications.length > 0 ? (
              <div className="space-y-1">
                {notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`border-l-4 p-3 hover:bg-gray-50 cursor-pointer ${getPriorityColor(notif.priority)} ${
                      !notif.read ? 'bg-opacity-100' : 'bg-opacity-50'
                    }`}
                    onClick={() => {
                      markAsRead(notif.id);
                      if (notif.actionUrl) {
                        window.location.href = notif.actionUrl;
                      }
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-2 flex-1">
                        {getNotificationIcon(notif.type)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className={`text-sm font-medium ${!notif.read ? 'text-gray-900' : 'text-gray-600'}`}>
                              {notif.title}
                            </h4>
                            {!notif.read && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            )}
                          </div>
                          <p className={`text-xs mt-1 ${!notif.read ? 'text-gray-700' : 'text-gray-500'}`}>
                            {notif.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {notif.timestamp.toLocaleDateString()} {notif.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeNotification(notif.id);
                        }}
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No notifications</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}