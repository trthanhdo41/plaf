'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  Clock,
  Target,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

interface JourneyEvent {
  date: string;
  type: 'risk_change' | 'intervention' | 'performance' | 'engagement';
  title: string;
  description: string;
  impact: 'positive' | 'negative' | 'neutral';
  value?: number;
}

interface StudentJourneyProps {
  student: any;
}

export default function StudentJourney({ student }: StudentJourneyProps) {
  // Generate mock journey data based on student info
  const generateJourneyEvents = (): JourneyEvent[] => {
    const events: JourneyEvent[] = [];
    const now = new Date();
    
    // Initial enrollment
    events.push({
      date: new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      type: 'engagement',
      title: 'Course Enrollment',
      description: `Started ${student.code_module || 'DDD'} course`,
      impact: 'positive'
    });
    
    // Early engagement period
    if (student.num_days_active >= 20) {
      events.push({
        date: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000).toISOString(),
        type: 'engagement',
        title: 'Strong Early Engagement',
        description: 'Consistent daily activity detected',
        impact: 'positive',
        value: 85
      });
    }
    
    // Performance milestone
    if (student.avg_score >= 70) {
      events.push({
        date: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        type: 'performance',
        title: 'Good Academic Performance',
        description: `Achieved ${student.avg_score}% average score`,
        impact: 'positive',
        value: student.avg_score
      });
    }
    
    // Risk detection
    if (student.risk_probability >= 0.7) {
      events.push({
        date: new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        type: 'risk_change',
        title: 'High Risk Detected',
        description: 'AI system identified potential academic challenges',
        impact: 'negative',
        value: student.risk_probability * 100
      });
      
      // Intervention triggered
      events.push({
        date: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        type: 'intervention',
        title: 'Proactive Intervention Triggered',
        description: 'Personalized support recommendations provided',
        impact: 'positive'
      });
    }
    
    // Recent activity
    if (student.total_clicks >= 1000) {
      events.push({
        date: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        type: 'engagement',
        title: 'High Platform Engagement',
        description: `Reached ${student.total_clicks} total interactions`,
        impact: 'positive',
        value: student.total_clicks
      });
    }
    
    return events.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  };

  const journeyEvents = generateJourneyEvents();
  
  const getEventIcon = (type: string, impact: string) => {
    switch (type) {
      case 'risk_change':
        return impact === 'negative' ? 
          <AlertTriangle className="w-4 h-4 text-red-500" /> :
          <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'intervention':
        return <Target className="w-4 h-4 text-blue-500" />;
      case 'performance':
        return impact === 'positive' ? 
          <TrendingUp className="w-4 h-4 text-green-500" /> :
          <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'engagement':
        return <Clock className="w-4 h-4 text-purple-500" />;
      default:
        return <Calendar className="w-4 h-4 text-gray-500" />;
    }
  };
  
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive': return 'border-green-200 bg-green-50';
      case 'negative': return 'border-red-200 bg-red-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-600" />
          Student Journey Timeline
        </CardTitle>
        <p className="text-sm text-gray-600">
          Track your academic progress and interventions over time
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {journeyEvents.map((event, index) => (
            <div key={index} className={`border rounded-lg p-4 ${getImpactColor(event.impact)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {getEventIcon(event.type, event.impact)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm">{event.title}</h4>
                      <Badge variant="outline" className="text-xs">
                        {event.type.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{event.description}</p>
                    {event.value && (
                      <p className="text-xs font-medium">
                        Value: {event.type === 'risk_change' ? `${event.value.toFixed(1)}%` : 
                               event.type === 'performance' ? `${event.value}%` :
                               event.value.toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(event.date).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
          
          {journeyEvents.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No journey events recorded yet</p>
              <p className="text-sm">Events will appear as you engage with the platform</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}