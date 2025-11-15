'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { 
  FileText, 
  Download, 
  Calendar,
  Target,
  CheckSquare,
  Clock,
  AlertTriangle,
  TrendingUp
} from 'lucide-react';

interface InterventionPlanProps {
  student: any;
  riskFactors: any[];
  strategies: any[];
}

interface ActionItem {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  timeframe: string;
  category: string;
}

export default function InterventionPlan({ student, riskFactors, strategies }: InterventionPlanProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();
  
  const riskPercentage = (student.risk_probability || 0) * 100;
  
  // Generate structured action plan
  const generateActionPlan = (): ActionItem[] => {
    const actions: ActionItem[] = [];
    
    // Immediate actions for critical risk
    if (riskPercentage >= 85) {
      actions.push({
        id: 'emergency-contact',
        title: 'Contact Academic Advisor Immediately',
        description: 'Schedule urgent meeting within 24 hours to discuss academic status and support options.',
        priority: 'high',
        timeframe: 'Within 24 hours',
        category: 'Emergency Support'
      });
      
      actions.push({
        id: 'course-load-review',
        title: 'Review Course Load',
        description: 'Consider reducing course load or requesting extensions to manage academic pressure.',
        priority: 'high',
        timeframe: 'Within 48 hours',
        category: 'Academic Planning'
      });
    }
    
    // Performance improvement actions
    if (student.avg_score < 70) {
      actions.push({
        id: 'study-schedule',
        title: 'Create Structured Study Schedule',
        description: 'Develop daily 2-3 hour study blocks focusing on weak areas identified in assessments.',
        priority: 'high',
        timeframe: 'This week',
        category: 'Study Strategy'
      });
      
      actions.push({
        id: 'assessment-review',
        title: 'Review Past Assessments',
        description: 'Analyze incorrect answers and seek clarification on challenging concepts.',
        priority: 'medium',
        timeframe: 'Next 3 days',
        category: 'Performance Analysis'
      });
    }
    
    // Engagement improvement actions
    if (student.num_days_active < 30) {
      actions.push({
        id: 'daily-engagement',
        title: 'Establish Daily Platform Engagement',
        description: 'Set goal to access learning platform daily for at least 30 minutes.',
        priority: 'medium',
        timeframe: 'Starting tomorrow',
        category: 'Engagement'
      });
      
      actions.push({
        id: 'resource-exploration',
        title: 'Explore Additional Resources',
        description: 'Access supplementary materials, videos, and practice exercises available on platform.',
        priority: 'medium',
        timeframe: 'This week',
        category: 'Resource Utilization'
      });
    }
    
    // Long-term strategies
    actions.push({
      id: 'progress-monitoring',
      title: 'Weekly Progress Check-ins',
      description: 'Monitor academic progress weekly and adjust strategies based on performance trends.',
      priority: 'low',
      timeframe: 'Ongoing',
      category: 'Monitoring'
    });
    
    return actions.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };
  
  const actionPlan = generateActionPlan();
  
  const generatePDFContent = () => {
    const content = `
PERSONALIZED ACADEMIC INTERVENTION PLAN
Generated: ${new Date().toLocaleDateString()}

STUDENT INFORMATION:
Name: ${student.first_name} ${student.last_name}
Email: ${student.email}
Course: ${student.code_module || 'N/A'}
Risk Level: ${riskPercentage.toFixed(1)}% (${riskPercentage >= 85 ? 'CRITICAL' : riskPercentage >= 70 ? 'HIGH' : riskPercentage >= 40 ? 'MEDIUM' : 'LOW'})

CURRENT ACADEMIC STATUS:
- Average Score: ${student.avg_score || 0}%
- Days Active: ${student.num_days_active || 0}
- Total Engagement: ${student.total_clicks || 0} interactions

IDENTIFIED RISK FACTORS:
${riskFactors.map(factor => `- ${factor.factor}: ${factor.description}`).join('\n')}

ACTION PLAN:
${actionPlan.map((action, index) => `
${index + 1}. ${action.title} [${action.priority.toUpperCase()} PRIORITY]
   Category: ${action.category}
   Timeframe: ${action.timeframe}
   Description: ${action.description}
`).join('\n')}

RECOMMENDED STRATEGIES:
${strategies.map((strategy, index) => `
${index + 1}. ${strategy.title}
   Description: ${strategy.description}
   Priority: ${strategy.priority}
`).join('\n')}

NEXT STEPS:
1. Review this plan with your academic advisor
2. Implement high-priority actions immediately
3. Monitor progress weekly
4. Adjust strategies based on outcomes

This plan was generated by PLAF AI system based on your learning analytics and risk assessment.
For additional support, contact your academic advisor or use the AI chatbot for real-time guidance.
    `;
    
    return content;
  };
  
  const handleDownloadPlan = async () => {
    setIsGenerating(true);
    
    try {
      const content = generatePDFContent();
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `intervention-plan-${student.first_name}-${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        variant: "success",
        title: "Plan Downloaded",
        description: "Your personalized intervention plan has been saved.",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Download Failed",
        description: "Unable to generate plan. Please try again.",
      });
    } finally {
      setIsGenerating(false);
    }
  };
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-orange-200 bg-orange-50';
      case 'low': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };
  
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'medium': return <Clock className="w-4 h-4 text-orange-600" />;
      case 'low': return <Target className="w-4 h-4 text-blue-600" />;
      default: return <CheckSquare className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Structured Intervention Plan
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              Personalized action plan based on your risk assessment
            </p>
          </div>
          <Button 
            onClick={handleDownloadPlan}
            disabled={isGenerating}
            className="flex items-center gap-2"
          >
            {isGenerating ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Download Plan
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Risk Summary */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">Risk Assessment Summary</h4>
              <Badge variant={riskPercentage >= 85 ? "destructive" : riskPercentage >= 70 ? "secondary" : "default"}>
                {riskPercentage.toFixed(1)}% Risk
              </Badge>
            </div>
            <p className="text-sm text-gray-600">
              {riskPercentage >= 85 ? 'CRITICAL: Immediate intervention required' :
               riskPercentage >= 70 ? 'HIGH: Urgent support needed' :
               riskPercentage >= 40 ? 'MEDIUM: Preventive measures recommended' :
               'LOW: Continue current approach'}
            </p>
          </div>
          
          {/* Action Items */}
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-green-600" />
              Action Plan ({actionPlan.length} items)
            </h4>
            
            {actionPlan.map((action, index) => (
              <div key={action.id} className={`border rounded-lg p-4 ${getPriorityColor(action.priority)}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getPriorityIcon(action.priority)}
                    <h5 className="font-medium text-sm">{action.title}</h5>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {action.category}
                    </Badge>
                    <Badge variant={action.priority === 'high' ? 'destructive' : action.priority === 'medium' ? 'secondary' : 'default'} className="text-xs">
                      {action.priority.toUpperCase()}
                    </Badge>
                  </div>
                </div>
                <p className="text-sm text-gray-700 mb-2">{action.description}</p>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Calendar className="w-3 h-3" />
                  <span>{action.timeframe}</span>
                </div>
              </div>
            ))}
          </div>
          
          {/* Plan Footer */}
          <div className="border-t pt-4 text-center">
            <p className="text-xs text-gray-500 mb-2">
              This plan was generated by PLAF AI system on {new Date().toLocaleDateString()}
            </p>
            <p className="text-xs text-gray-500">
              For additional support, contact your academic advisor or use the AI chatbot
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}