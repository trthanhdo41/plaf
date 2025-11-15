'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  AlertTriangle, 
  TrendingDown, 
  TrendingUp, 
  Clock, 
  Target,
  BookOpen,
  Activity
} from 'lucide-react';

interface RiskFactor {
  factor: string;
  impact: number;
  description: string;
  recommendation: string;
  icon: React.ReactNode;
}

interface RiskExplanationProps {
  student: any;
}

export default function RiskExplanation({ student }: RiskExplanationProps) {
  const riskPercentage = (student.risk_probability || 0) * 100;
  const isAtRisk = riskPercentage >= 50;
  
  // Generate SHAP-like explanations based on student data
  const generateRiskFactors = (): RiskFactor[] => {
    const factors: RiskFactor[] = [];
    
    // Low average score factor
    if (student.avg_score && student.avg_score < 70) {
      factors.push({
        factor: 'Low Average Score',
        impact: Math.max(0, (70 - student.avg_score) / 70 * 100),
        description: `Current score: ${student.avg_score}% (Below 70% threshold)`,
        recommendation: 'Focus on improving assessment performance',
        icon: <TrendingDown className="w-4 h-4 text-red-500" />
      });
    }
    
    // Low engagement factor
    if (student.num_days_active && student.num_days_active < 30) {
      factors.push({
        factor: 'Low Engagement',
        impact: Math.max(0, (30 - student.num_days_active) / 30 * 100),
        description: `Active ${student.num_days_active} days (Below 30 days threshold)`,
        recommendation: 'Increase regular study schedule and platform engagement',
        icon: <Clock className="w-4 h-4 text-orange-500" />
      });
    }
    
    // Low activity factor
    if (student.total_clicks && student.total_clicks < 500) {
      factors.push({
        factor: 'Limited Activity',
        impact: Math.max(0, (500 - student.total_clicks) / 500 * 100),
        description: `${student.total_clicks} interactions (Below 500 threshold)`,
        recommendation: 'Engage more with course materials and resources',
        icon: <Activity className="w-4 h-4 text-yellow-500" />
      });
    }
    
    // Positive factors
    if (student.avg_score && student.avg_score >= 80) {
      factors.push({
        factor: 'Strong Performance',
        impact: -((student.avg_score - 80) / 20 * 30), // Negative impact = positive factor
        description: `Excellent score: ${student.avg_score}%`,
        recommendation: 'Continue current study approach',
        icon: <TrendingUp className="w-4 h-4 text-green-500" />
      });
    }
    
    if (student.num_days_active && student.num_days_active >= 40) {
      factors.push({
        factor: 'High Engagement',
        impact: -((student.num_days_active - 40) / 20 * 25),
        description: `Very active: ${student.num_days_active} days`,
        recommendation: 'Maintain consistent engagement',
        icon: <Target className="w-4 h-4 text-green-500" />
      });
    }
    
    return factors.sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
  };
  
  const riskFactors = generateRiskFactors();
  
  // Generate DiCE-like counterfactuals
  const generateCounterfactuals = () => {
    const counterfactuals = [];
    
    if (student.avg_score && student.avg_score < 70) {
      const targetScore = 75;
      const improvement = targetScore - student.avg_score;
      counterfactuals.push({
        scenario: 'Improve Assessment Performance',
        change: `Increase average score by ${improvement.toFixed(1)} points to ${targetScore}%`,
        impact: 'Risk level would decrease by ~25%',
        action: 'Focus on quiz preparation and assignment quality'
      });
    }
    
    if (student.num_days_active && student.num_days_active < 30) {
      const targetDays = 35;
      const increase = targetDays - student.num_days_active;
      counterfactuals.push({
        scenario: 'Increase Engagement',
        change: `Add ${increase} more active days (target: ${targetDays} days)`,
        impact: 'Risk level would decrease by ~20%',
        action: 'Establish daily study routine and regular platform visits'
      });
    }
    
    if (student.total_clicks && student.total_clicks < 1000) {
      const targetClicks = 1200;
      const increase = targetClicks - student.total_clicks;
      counterfactuals.push({
        scenario: 'Boost Activity Level',
        change: `Increase interactions by ${increase} clicks`,
        impact: 'Risk level would decrease by ~15%',
        action: 'Explore more course materials, videos, and resources'
      });
    }
    
    return counterfactuals;
  };
  
  const counterfactuals = generateCounterfactuals();
  
  return (
    <div className="space-y-6">
      {/* Risk Factors Analysis (SHAP-like) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Risk Factors Analysis
          </CardTitle>
          <p className="text-sm text-gray-600">
            AI-powered analysis of factors contributing to your risk level
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {riskFactors.map((factor, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {factor.icon}
                    <span className="font-medium">{factor.factor}</span>
                  </div>
                  <Badge variant={factor.impact > 0 ? "destructive" : "default"}>
                    {factor.impact > 0 ? '+' : ''}{factor.impact.toFixed(1)}%
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-2">{factor.description}</p>
                <div className="mb-2">
                  <Progress 
                    value={Math.abs(factor.impact)} 
                    className={`h-2 ${factor.impact > 0 ? 'bg-red-100' : 'bg-green-100'}`}
                  />
                </div>
                <p className="text-xs text-blue-600 font-medium">
                  💡 {factor.recommendation}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Counterfactual Scenarios (DiCE-like) */}
      {counterfactuals.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              Improvement Scenarios
            </CardTitle>
            <p className="text-sm text-gray-600">
              What-if scenarios to reduce your risk level
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {counterfactuals.map((scenario, index) => (
                <div key={index} className="border rounded-lg p-4 bg-blue-50">
                  <h4 className="font-medium text-blue-900 mb-2">{scenario.scenario}</h4>
                  <div className="space-y-2 text-sm">
                    <p><strong>Change:</strong> {scenario.change}</p>
                    <p><strong>Expected Impact:</strong> <span className="text-green-600">{scenario.impact}</span></p>
                    <p><strong>Action Plan:</strong> {scenario.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}