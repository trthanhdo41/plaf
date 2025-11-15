'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { 
  ThumbsUp, 
  ThumbsDown, 
  Star,
  MessageSquare,
  TrendingUp,
  CheckCircle
} from 'lucide-react';

interface InterventionFeedbackProps {
  interventionId: number;
  interventionType: string;
  onFeedbackSubmitted?: () => void;
}

export default function InterventionFeedback({ 
  interventionId, 
  interventionType, 
  onFeedbackSubmitted 
}: InterventionFeedbackProps) {
  const [rating, setRating] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { toast } = useToast();

  const handleRatingClick = (value: number) => {
    setRating(value);
  };

  const handleQuickFeedback = async (effectiveness: number, response: string) => {
    setIsSubmitting(true);
    
    try {
      const response_data = await fetch('/api/interventions/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intervention_id: interventionId,
          effectiveness: effectiveness,
          student_response: response,
          outcome: effectiveness >= 4 ? 'positive' : effectiveness >= 3 ? 'neutral' : 'negative'
        })
      });

      if (response_data.ok) {
        setIsSubmitted(true);
        toast({
          variant: "success",
          title: "Feedback Submitted",
          description: "Thank you for helping us improve our interventions!",
        });
        onFeedbackSubmitted?.();
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to submit feedback. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">Feedback submitted successfully!</span>
          </div>
          <p className="text-sm text-green-600 mt-1">
            Your input helps us provide better support for all students.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-blue-200 bg-blue-50">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-blue-600" />
          How helpful was this intervention?
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Quick Rating Buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleQuickFeedback(5, 'very_helpful')}
              disabled={isSubmitting}
              className="flex items-center gap-1 text-green-600 border-green-200 hover:bg-green-50"
            >
              <ThumbsUp className="w-3 h-3" />
              Very Helpful
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleQuickFeedback(3, 'somewhat_helpful')}
              disabled={isSubmitting}
              className="flex items-center gap-1 text-blue-600 border-blue-200 hover:bg-blue-50"
            >
              <Star className="w-3 h-3" />
              Somewhat
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleQuickFeedback(1, 'not_helpful')}
              disabled={isSubmitting}
              className="flex items-center gap-1 text-red-600 border-red-200 hover:bg-red-50"
            >
              <ThumbsDown className="w-3 h-3" />
              Not Helpful
            </Button>
          </div>

          {/* Intervention Type Badge */}
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {interventionType.replace('_', ' ').toUpperCase()}
            </Badge>
            <span className="text-xs text-gray-500">
              ID: {interventionId}
            </span>
          </div>

          <p className="text-xs text-gray-600">
            Your feedback helps our AI learn and provide better support for future students.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}