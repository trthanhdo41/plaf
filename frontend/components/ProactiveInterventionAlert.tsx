'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  MessageCircle, 
  BookOpen, 
  TrendingUp, 
  X,
  Lightbulb,
  Target,
  Clock
} from 'lucide-react';
import { Student } from '@/lib/api';
import Link from 'next/link';
import InterventionFeedback from './InterventionFeedback';

interface ProactiveInterventionAlertProps {
  student: Student;
  onDismiss?: () => void;
}

interface InterventionLog {
  id: number;
  intervention_type: string;
  created_at: string;
}

interface InterventionStrategy {
  id: string;
  title: string;
  description: string;
  action: string;
  actionLink: string;
  icon: React.ReactNode;
  priority: 'high' | 'medium' | 'low';
  riskFactors: string[];
}

export default function ProactiveInterventionAlert({ student, onDismiss }: ProactiveInterventionAlertProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<InterventionStrategy | null>(null);
  const [interventionLog, setInterventionLog] = useState<InterventionLog | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  
  const riskPercentage = (student.risk_probability || 0) * 100;
  const isHighRisk = riskPercentage >= 70;
  const isMediumRisk = riskPercentage >= 40 && riskPercentage < 70;
  
  // Generate intervention strategies based on student data
  const generateInterventionStrategies = (): InterventionStrategy[] => {
    const strategies: InterventionStrategy[] = [];
    
    // Critical Risk Interventions (>85%)
    if (riskPercentage >= 85) {
      strategies.push({
        id: 'emergency-protocol',
        title: 'URGENT: Emergency Academic Support',
        description: 'Critical risk detected. Immediate intervention required to prevent academic failure.',
        action: 'Get Emergency Help',
        actionLink: '/dashboard/chat',
        icon: <AlertTriangle className="w-5 h-5" />,
        priority: 'critical',
        riskFactors: ['Critical risk level', 'Emergency intervention needed', 'Academic failure risk']
      });
      
      strategies.push({
        id: 'human-advisor-urgent',
        title: 'Human Advisor Notification Sent',
        description: 'Academic advisor has been automatically notified for immediate support.',
        action: 'Contact Advisor',
        actionLink: '/dashboard/chat',
        icon: <MessageCircle className="w-5 h-5" />,
        priority: 'critical',
        riskFactors: ['Human intervention required', 'Advisor notification']
      });
    }
    // High Risk Interventions (70-85%)
    else if (isHighRisk) {
      strategies.push({
        id: 'urgent-advisor',
        title: 'Immediate AI Advisor Support',
        description: 'Your risk level is high. Get immediate personalized guidance from our AI advisor.',
        action: 'Chat Now',
        actionLink: '/dashboard/chat',
        icon: <MessageCircle className="w-5 h-5" />,
        priority: 'high',
        riskFactors: ['High risk probability', 'Needs immediate attention']
      });
      
      if ((student.avg_score || 0) < 50) {
        strategies.push({
          id: 'study-plan',
          title: 'Intensive Study Plan',
          description: 'Your scores need improvement. Access targeted learning materials and practice tests.',
          action: 'View Materials',
          actionLink: '/dashboard/courses',
          icon: <BookOpen className="w-5 h-5" />,
          priority: 'high',
          riskFactors: ['Low average score', 'Performance concerns']
        });
      }
      
      if ((student.num_days_active || 0) < 30) {
        strategies.push({
          id: 'engagement-boost',
          title: 'Engagement Recovery Program',
          description: 'Low activity detected. Let\'s create a schedule to get you back on track.',
          action: 'Get Schedule',
          actionLink: '/dashboard/chat',
          icon: <Clock className="w-5 h-5" />,
          priority: 'high',
          riskFactors: ['Low engagement', 'Infrequent activity']
        });
      }
    }
    
    // Medium Risk Interventions
    if (isMediumRisk) {
      strategies.push({
        id: 'preventive-support',
        title: 'Preventive Academic Support',
        description: 'You\'re showing some risk factors. Let\'s address them before they become issues.',
        action: 'Get Support',
        actionLink: '/dashboard/chat',
        icon: <Lightbulb className="w-5 h-5" />,
        priority: 'medium',
        riskFactors: ['Moderate risk level', 'Early intervention recommended']
      });
      
      strategies.push({
        id: 'performance-review',
        title: 'Performance Review & Tips',
        description: 'Review your progress and get personalized study tips to improve your outcomes.',
        action: 'Review Progress',
        actionLink: '/dashboard/chat',
        icon: <TrendingUp className="w-5 h-5" />,
        priority: 'medium',
        riskFactors: ['Performance monitoring', 'Improvement opportunities']
      });
    }
    
    return strategies;
  };

  const interventionStrategies = generateInterventionStrategies();
  
  useEffect(() => {
    // Show alert if student has risk factors and hasn't dismissed recently
    const lastDismissed = localStorage.getItem(`intervention_dismissed_${student.id_student}`);
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
    
    if (interventionStrategies.length > 0 && (!lastDismissed || parseInt(lastDismissed) < oneDayAgo)) {
      setIsVisible(true);
      setSelectedStrategy(interventionStrategies[0]); // Select highest priority strategy
      
      // Log intervention trigger
      triggerIntervention();
    }
  }, [student.id_student, interventionStrategies.length]);

  const triggerIntervention = async () => {
    try {
      const response = await fetch('/api/interventions/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: student.id_student,
          intervention_type: 'proactive_alert',
          risk_level: isHighRisk ? 'high' : 'medium',
          triggered_by: 'auto_system',
          metadata: {
            risk_percentage: riskPercentage,
            strategies: interventionStrategies.map(s => s.id)
          }
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setInterventionLog({
          id: data.intervention_id,
          intervention_type: 'proactive_alert',
          created_at: new Date().toISOString()
        });
        
        // Show feedback after 10 seconds
        setTimeout(() => setShowFeedback(true), 10000);
      }
    } catch (error) {
      console.error('Failed to log intervention:', error);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    localStorage.setItem(`intervention_dismissed_${student.id_student}`, Date.now().toString());
    onDismiss?.();
  };

  const getRiskLevelInfo = () => {
    if (isHighRisk) {
      return {
        level: 'Critical Risk',
        color: 'bg-red-50 border-red-200',
        textColor: 'text-red-700',
        badgeVariant: 'destructive' as const,
        urgency: 'Immediate action recommended'
      };
    }
    if (isMediumRisk) {
      return {
        level: 'Moderate Risk',
        color: 'bg-orange-50 border-orange-200',
        textColor: 'text-orange-700',
        badgeVariant: 'secondary' as const,
        urgency: 'Early intervention suggested'
      };
    }
    return {
      level: 'Low Risk',
      color: 'bg-green-50 border-green-200',
      textColor: 'text-green-700',
      badgeVariant: 'default' as const,
      urgency: 'Continue current progress'
    };
  };

  if (!isVisible || interventionStrategies.length === 0) {
    return null;
  }

  const riskInfo = getRiskLevelInfo();

  return (
    <Card className={`border-l-4 ${riskInfo.color} animate-slide-in-top shadow-lg`}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white rounded-full shadow-sm">
              <AlertTriangle className={`w-6 h-6 ${isHighRisk ? 'text-red-600' : 'text-orange-600'}`} />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-lg">Proactive Academic Support</h3>
                <Badge variant={riskInfo.badgeVariant}>
                  {riskInfo.level}
                </Badge>
              </div>
              <p className={`text-sm ${riskInfo.textColor}`}>
                {riskInfo.urgency} • Risk Level: {Math.round(riskPercentage)}%
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={handleDismiss}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {selectedStrategy && (
          <div className="bg-white rounded-lg p-4 border border-gray-100 mb-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                {selectedStrategy.icon}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-1">
                  {selectedStrategy.title}
                </h4>
                <p className="text-gray-600 text-sm mb-3">
                  {selectedStrategy.description}
                </p>
                
                {/* Risk Factors */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {selectedStrategy.riskFactors.map((factor, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {factor}
                    </Badge>
                  ))}
                </div>

                <Link href={selectedStrategy.actionLink}>
                  <Button 
                    size="sm" 
                    className={`${isHighRisk ? 'bg-red-600 hover:bg-red-700' : 'bg-orange-600 hover:bg-orange-700'} text-white`}
                  >
                    {selectedStrategy.action}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Additional Strategies */}
        {interventionStrategies.length > 1 && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Additional Support Options:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {interventionStrategies.slice(1).map((strategy) => (
                <Link key={strategy.id} href={strategy.actionLink}>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full justify-start h-auto py-2 px-3"
                  >
                    <div className="flex items-center gap-2">
                      {strategy.icon}
                      <span className="text-xs">{strategy.title}</span>
                    </div>
                  </Button>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Intervention Feedback */}
        {showFeedback && interventionLog && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <InterventionFeedback
              interventionId={interventionLog.id}
              interventionType={interventionLog.intervention_type}
              onFeedbackSubmitted={() => setShowFeedback(false)}
            />
          </div>
        )}

        {/* Auto-generated Insights */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-start gap-2">
            <Lightbulb className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-500">
              This intervention was automatically generated based on your learning patterns and risk factors. 
              Our AI continuously monitors your progress to provide timely support.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}