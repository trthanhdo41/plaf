'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, XCircle, Clock, Trophy, AlertCircle } from 'lucide-react';

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  explanation?: string;
}

interface QuizProps {
  quizId: number;
  lessonId: number;
  studentId: number;
  questions: QuizQuestion[];
  title: string;
  passingScore: number;
  timeLimit?: number; // in minutes
  onComplete: (score: number, passed: boolean) => void;
}

export default function QuizPlayer({
  quizId,
  lessonId,
  studentId,
  questions,
  title,
  passingScore,
  timeLimit,
  onComplete
}: QuizProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(timeLimit ? timeLimit * 60 : null);
  const [quizStarted, setQuizStarted] = useState(false);

  // Timer countdown
  useEffect(() => {
    if (quizStarted && timeLeft !== null && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev && prev <= 1) {
            handleSubmitQuiz();
            return 0;
          }
          return prev ? prev - 1 : null;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [quizStarted, timeLeft]);

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: answerIndex
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.correct_answer) {
        correct++;
      }
    });
    return (correct / questions.length) * 100;
  };

  const handleSubmitQuiz = async () => {
    const finalScore = calculateScore();
    const passed = finalScore >= passingScore;
    
    setScore(finalScore);
    setShowResults(true);

    // Save quiz result to database
    try {
      const response = await fetch(`/api/quiz/${quizId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          lesson_id: lessonId,
          answers: selectedAnswers,
          score: finalScore,
          passed: passed,
          time_taken: timeLimit ? (timeLimit * 60 - (timeLeft || 0)) : null
        }),
      });

      if (response.ok) {
        onComplete(finalScore, passed);
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getAnswerStatus = (questionIndex: number, answerIndex: number) => {
    if (!showResults) return '';
    
    const question = questions[questionIndex];
    const selectedAnswer = selectedAnswers[questionIndex];
    
    if (answerIndex === question.correct_answer) {
      return 'correct';
    } else if (answerIndex === selectedAnswer && answerIndex !== question.correct_answer) {
      return 'incorrect';
    }
    return '';
  };

  if (!quizStarted) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-6 h-6 text-yellow-500" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Questions:</strong> {questions.length}
            </div>
            <div>
              <strong>Passing Score:</strong> {passingScore}%
            </div>
            {timeLimit && (
              <div>
                <strong>Time Limit:</strong> {timeLimit} minutes
              </div>
            )}
            <div>
              <strong>Attempts:</strong> Unlimited
            </div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Instructions:</h4>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Read each question carefully</li>
              <li>• Select the best answer for each question</li>
              <li>• You can navigate between questions</li>
              <li>• Submit when you're ready</li>
              {timeLimit && <li>• Quiz will auto-submit when time runs out</li>}
            </ul>
          </div>
          
          <Button 
            onClick={() => setQuizStarted(true)}
            className="w-full"
            size="lg"
          >
            Start Quiz
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (showResults) {
    const passed = score >= passingScore;
    
    return (
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {passed ? (
              <CheckCircle2 className="w-6 h-6 text-green-500" />
            ) : (
              <XCircle className="w-6 h-6 text-red-500" />
            )}
            Quiz Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <div className={`text-4xl font-bold ${passed ? 'text-green-600' : 'text-red-600'}`}>
              {score.toFixed(1)}%
            </div>
            <div className={`text-lg ${passed ? 'text-green-600' : 'text-red-600'}`}>
              {passed ? '🎉 Congratulations! You passed!' : '😔 You need to score at least ' + passingScore + '% to pass'}
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {Object.keys(selectedAnswers).filter(key => 
                  selectedAnswers[parseInt(key)] === questions[parseInt(key)].correct_answer
                ).length}
              </div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {questions.length - Object.keys(selectedAnswers).filter(key => 
                  selectedAnswers[parseInt(key)] === questions[parseInt(key)].correct_answer
                ).length}
              </div>
              <div className="text-sm text-gray-600">Incorrect</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">
                {questions.length}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
          
          {/* Review Answers */}
          <div className="space-y-4">
            <h4 className="font-semibold">Review Your Answers:</h4>
            {questions.map((question, qIndex) => (
              <div key={qIndex} className="border rounded-lg p-4">
                <div className="font-medium mb-2">
                  {qIndex + 1}. {question.question}
                </div>
                <div className="space-y-2">
                  {question.options.map((option, oIndex) => {
                    const status = getAnswerStatus(qIndex, oIndex);
                    return (
                      <div
                        key={oIndex}
                        className={`p-2 rounded flex items-center gap-2 ${
                          status === 'correct' ? 'bg-green-100 text-green-800' :
                          status === 'incorrect' ? 'bg-red-100 text-red-800' :
                          'bg-gray-50'
                        }`}
                      >
                        {status === 'correct' && <CheckCircle2 className="w-4 h-4" />}
                        {status === 'incorrect' && <XCircle className="w-4 h-4" />}
                        <span>{option}</span>
                      </div>
                    );
                  })}
                </div>
                {question.explanation && (
                  <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                    <strong>Explanation:</strong> {question.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div className="flex gap-2">
            <Button 
              onClick={() => window.location.reload()}
              variant="outline"
              className="flex-1"
            >
              Retake Quiz
            </Button>
            <Button 
              onClick={() => {
                console.log('Continue button clicked!', { score, passed });
                onComplete(score, passed);
              }}
              className="flex-1"
            >
              Continue
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const question = questions[currentQuestion];

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>
            Question {currentQuestion + 1} of {questions.length}
          </CardTitle>
          {timeLeft !== null && (
            <div className={`flex items-center gap-2 ${timeLeft < 300 ? 'text-red-600' : 'text-gray-600'}`}>
              <Clock className="w-4 h-4" />
              {formatTime(timeLeft)}
            </div>
          )}
        </div>
        <Progress value={progress} className="w-full" />
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="text-lg font-medium">
          {question.question}
        </div>
        
        <div className="space-y-3">
          {question.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(currentQuestion, index)}
              className={`w-full p-4 text-left border rounded-lg transition-colors ${
                selectedAnswers[currentQuestion] === index
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  selectedAnswers[currentQuestion] === index
                    ? 'border-blue-500 bg-blue-500'
                    : 'border-gray-300'
                }`}>
                  {selectedAnswers[currentQuestion] === index && (
                    <div className="w-full h-full rounded-full bg-white scale-50"></div>
                  )}
                </div>
                <span>{option}</span>
              </div>
            </button>
          ))}
        </div>
        
        <div className="flex justify-between">
          <Button
            onClick={handlePreviousQuestion}
            disabled={currentQuestion === 0}
            variant="outline"
          >
            Previous
          </Button>
          
          <div className="flex gap-2">
            {currentQuestion === questions.length - 1 ? (
              <Button
                onClick={handleSubmitQuiz}
                disabled={Object.keys(selectedAnswers).length < questions.length}
                className="bg-green-600 hover:bg-green-700"
              >
                Submit Quiz
              </Button>
            ) : (
              <Button
                onClick={handleNextQuestion}
                disabled={selectedAnswers[currentQuestion] === undefined}
              >
                Next
              </Button>
            )}
          </div>
        </div>
        
        {Object.keys(selectedAnswers).length < questions.length && (
          <div className="flex items-center gap-2 text-amber-600 text-sm">
            <AlertCircle className="w-4 h-4" />
            Please answer all questions before submitting
          </div>
        )}
      </CardContent>
    </Card>
  );
}
