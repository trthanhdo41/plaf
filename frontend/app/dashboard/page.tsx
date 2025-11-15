'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  BookOpen, 
  MessageCircle, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  BarChart,
  GraduationCap,
  Target,
  Activity,
  LogOut,
  Menu,
  Trophy,
  User
} from 'lucide-react';
import { api, Student } from '@/lib/api';
import Link from 'next/link';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer, PolarAngleAxis, BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import ProactiveInterventionAlert from '@/components/ProactiveInterventionAlert';
import RiskExplanation from '@/components/RiskExplanation';
import StudentJourney from '@/components/StudentJourney';
import InterventionPlan from '@/components/InterventionPlan';
import NotificationCenter from '@/components/NotificationCenter';

// Custom hook for animating numbers
function useCountUp(end: number, duration: number = 2000, startOnMount: boolean = false) {
  const [count, setCount] = useState(0);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    if (!startOnMount || hasStarted) return;
    
    setHasStarted(true);
    let startTime: number | null = null;
    const startValue = 0;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * end));

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };

    requestAnimationFrame(animate);
  }, [end, duration, startOnMount, hasStarted]);

  return count;
}

export default function DashboardPage() {
  const router = useRouter();
  const [student, setStudent] = useState<Student | null>(null);
  const [activities, setActivities] = useState<any[]>([]);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const [startAnimation, setStartAnimation] = useState(false);

  // Calculate values with safe defaults
  const riskPercentage = student ? (student.risk_probability || 0) * 100 : 0;
  const isAtRisk = student ? (student.is_at_risk || riskPercentage > 50) : false;
  const avgScore = student?.avg_score || 0;
  const daysActive = student?.num_days_active || 0;
  const totalClicks = student?.total_clicks || 0;
  const passRate = (student as any)?.pass_rate || 0;
  const quizCompleted = (student as any)?.quiz_completed || 0;

  // Animated counters - must be called unconditionally
  const animatedRisk = useCountUp(riskPercentage, 2000, startAnimation);
  const animatedScore = useCountUp(avgScore, 2000, startAnimation);
  const animatedDays = useCountUp(daysActive, 1800, startAnimation);
  const animatedClicks = useCountUp(totalClicks, 2200, startAnimation);
  const animatedPassRate = useCountUp(passRate, 2000, startAnimation);
  const animatedQuizCompleted = useCountUp(quizCompleted, 1500, startAnimation);

  useEffect(() => {
    // Get student from localStorage
    const storedStudent = localStorage.getItem('student');
    if (!storedStudent) {
      router.push('/');
      return;
    }

    const studentData = JSON.parse(storedStudent);
    setStudent(studentData);

    // Fetch detailed student data
    loadStudentData(studentData.id_student);
  }, [router]);

  const loadStudentData = async (studentId: number) => {
    try {
      const data = await api.getStudent(studentId);
      setActivities(data.activities || []);
      setAssessments(data.assessments || []);
    } catch (error) {
      console.error('Failed to load student data:', error);
    } finally {
      setLoading(false);
      // Start animations after data is loaded
      setTimeout(() => setStartAnimation(true), 100);
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
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  const getRiskColor = () => {
    if (riskPercentage >= 70) return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'destructive' };
    if (riskPercentage >= 40) return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', badge: 'warning' };
    return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', badge: 'success' };
  };

  const riskColor = getRiskColor();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <img src="/study.png" alt="PLAF" className="w-10 h-10 rounded-lg object-cover" />
              <span className="text-xl font-bold text-gray-900">PLAF</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="flex items-center gap-2 text-blue-600 font-medium">
                <BarChart className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
              <Link href="/dashboard/courses" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <BookOpen className="w-5 h-5" />
                <span>My Courses</span>
              </Link>
              <Link href="/dashboard/chat" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <MessageCircle className="w-5 h-5" />
                <span>AI Advisor</span>
              </Link>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <NotificationCenter student={student} />
              <Link href="/dashboard/profile" className="hidden md:flex items-center gap-3 hover:opacity-80 transition-opacity">
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

          {/* Mobile Menu */}
          {menuOpen && (
            <div className="md:hidden py-4 border-t">
              <div className="flex flex-col gap-2">
                <Link href="/dashboard" className="flex items-center gap-2 px-4 py-3 text-blue-600 bg-blue-50 rounded-lg font-medium">
                  <BarChart className="w-5 h-5" />
                  <span>Dashboard</span>
                </Link>
                <Link href="/dashboard/courses" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BookOpen className="w-5 h-5" />
                  <span>My Courses</span>
                </Link>
                <Link href="/dashboard/chat" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <MessageCircle className="w-5 h-5" />
                  <span>AI Advisor</span>
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Banner */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            Welcome back, {student.first_name}!
            <User className="w-8 h-8 text-blue-600" />
          </h1>
          <p className="text-gray-600">
            Here's your learning progress and personalized insights
          </p>
        </div>

        {/* Proactive Intervention Alert */}
        <div className="mb-6">
          <ProactiveInterventionAlert student={student} />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          {/* Risk Level Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Risk Level</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">{Math.round(animatedRisk)}%</div>
                <TrendingUp className={`w-8 h-8 ${riskColor.text} animate-bounce-slow`} />
              </div>
              <div className="relative h-2 mb-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`absolute top-0 left-0 h-full ${isAtRisk ? 'bg-red-600' : 'bg-green-600'} transition-all duration-2000 ease-out`}
                  style={{ width: `${startAnimation ? Math.round(animatedRisk) : 0}%` }}
                />
              </div>
              <Badge variant={riskColor.badge as any} className="text-xs animate-fade-in">
                {isAtRisk ? 'Needs Attention' : 'On Track'}
              </Badge>
            </CardContent>
          </Card>

          {/* Average Score Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Average Score</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">{avgScore > 0 ? animatedScore.toFixed(1) : 'N/A'}</div>
                <Target className="w-8 h-8 text-blue-600 animate-pulse" />
              </div>
              <div className="relative h-2 mb-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-2000 ease-out"
                  style={{ width: `${startAnimation ? animatedScore : 0}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 animate-fade-in">
                {avgScore >= 70 ? 'Excellent performance!' : avgScore >= 50 ? 'Good progress' : 'Keep improving'}
              </p>
            </CardContent>
          </Card>

          {/* Days Active Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Days Active</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">{animatedDays}</div>
                <Clock className="w-8 h-8 text-green-600 animate-spin-slow" />
              </div>
              <p className="text-sm text-gray-600 mt-2 animate-fade-in">
                {daysActive > 50 ? 'Great consistency!' : 'Stay engaged!'}
              </p>
            </CardContent>
          </Card>

          {/* Total Engagement Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Total Engagement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">{animatedClicks.toLocaleString()}</div>
                <Activity className="w-8 h-8 text-purple-600 animate-ping-slow" />
              </div>
              <p className="text-sm text-gray-600 mt-2 animate-fade-in">
                {totalClicks > 1000 ? 'Highly engaged!' : 'Keep it up!'}
              </p>
            </CardContent>
          </Card>

          {/* Pass Rate Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Pass Rate</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">
                  {quizCompleted > 0 ? `${Math.round(animatedPassRate)}%` : 'N/A'}
                </div>
                <CheckCircle className="w-8 h-8 text-green-600 animate-pulse" />
              </div>
              <div className="relative h-2 mb-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-2000 ease-out"
                  style={{ width: `${startAnimation && quizCompleted > 0 ? animatedPassRate : 0}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 animate-fade-in">
                {quizCompleted === 0 ? 'No quizzes yet' : passRate >= 70 ? 'Great job!' : 'Keep trying!'}
              </p>
            </CardContent>
          </Card>

          {/* Quiz Completed Card */}
          <Card className="transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription>Quiz Completed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <div className="text-3xl font-bold animate-fade-in">{animatedQuizCompleted}</div>
                <Trophy className="w-8 h-8 text-yellow-500 animate-bounce" />
              </div>
              <p className="text-sm text-gray-600 mt-2 animate-fade-in">
                {quizCompleted === 0 ? 'Start a quiz!' : `${quizCompleted} quiz${quizCompleted !== 1 ? 'zes' : ''} done`}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Risk Gauge Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                Academic Risk Level
              </CardTitle>
              <CardDescription>Your current risk assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <ResponsiveContainer width="100%" height={300}>
                  <RadialBarChart 
                    cx="50%" 
                    cy="50%" 
                    innerRadius="60%" 
                    outerRadius="90%" 
                    barSize={20}
                    data={[{ name: 'Risk', value: animatedRisk, fill: isAtRisk ? '#ef4444' : '#22c55e' }]}
                    startAngle={180}
                    endAngle={0}
                  >
                    <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                    <RadialBar
                      background
                      dataKey="value"
                      cornerRadius={10}
                      isAnimationActive={false}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center" style={{ top: '20%' }}>
                  <div className="text-center">
                    <div className="text-5xl font-bold text-gray-900 mb-1">
                      {Math.round(animatedRisk)}%
                    </div>
                    <div className="text-sm text-gray-500 font-medium">
                      Risk Level
                    </div>
                  </div>
                </div>
              </div>
              <div className="text-center mt-4">
                <div className="flex justify-center">
                  <Badge variant={isAtRisk ? "destructive" : "default"} className="text-sm flex items-center gap-1">
                    {isAtRisk ? (
                      <>
                        <AlertTriangle className="w-3 h-3" />
                        Needs Attention
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-3 h-3" />
                        On Track
                      </>
                    )}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {isAtRisk 
                    ? 'Consider talking to your AI Advisor for personalized support'
                    : 'Great job! Keep up the good work'
                  }
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Activity Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Weekly Activity
              </CardTitle>
              <CardDescription>Your engagement over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={[
                  { week: 'Week 1', clicks: Math.floor(totalClicks * 0.15) },
                  { week: 'Week 2', clicks: Math.floor(totalClicks * 0.20) },
                  { week: 'Week 3', clicks: Math.floor(totalClicks * 0.25) },
                  { week: 'Week 4', clicks: Math.floor(totalClicks * 0.40) },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="week" tick={{ fill: '#6b7280' }} />
                  <YAxis tick={{ fill: '#6b7280' }} />
                  <Tooltip 
                    contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                    labelStyle={{ color: '#111827', fontWeight: 'bold' }}
                  />
                  <Bar 
                    dataKey="clicks" 
                    fill="#8b5cf6" 
                    radius={[8, 8, 0, 0]}
                    isAnimationActive={true}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  />
                </RechartsBarChart>
              </ResponsiveContainer>
              <div className="text-center mt-4">
                <p className="text-sm text-gray-600">
                  Total: <span className="font-semibold text-gray-900">{totalClicks.toLocaleString()}</span> interactions
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Risk Explanation Section */}
        {isAtRisk && (
          <div className="mb-8">
            <RiskExplanation student={student} />
          </div>
        )}

        {/* Intervention Plan Section */}
        {isAtRisk && (
          <div className="mb-8">
            <InterventionPlan 
              student={student} 
              riskFactors={[]} 
              strategies={[]} 
            />
          </div>
        )}

        {/* Student Journey Timeline */}
        <div className="mb-8">
          <StudentJourney student={student} />
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Assessments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Recent Assessments
              </CardTitle>
              <CardDescription>Your latest assignment results</CardDescription>
            </CardHeader>
            <CardContent>
              {assessments.length > 0 ? (
                <div className="space-y-3">
                  {assessments.slice(0, 5).map((assessment, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">Assessment {assessment.id_assessment}</div>
                        <div className="text-sm text-gray-600">Score: {assessment.score || 'Pending'}</div>
                      </div>
                      <Badge variant={assessment.score >= 70 ? 'default' : 'secondary'}>
                        {assessment.score >= 70 ? 'Pass' : 'Review'}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No assessments yet</p>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Access your learning tools</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Link href="/dashboard/courses">
                  <Button variant="outline" className="w-full justify-start h-auto py-4" size="lg">
                    <BookOpen className="w-5 h-5 mr-3 text-blue-600" />
                    <div className="text-left flex-1">
                      <div className="font-semibold">Browse Course Materials</div>
                      <div className="text-sm text-gray-600">Access readings, videos, and resources</div>
                    </div>
                  </Button>
                </Link>

                <Link href="/dashboard/chat">
                  <Button variant="outline" className="w-full justify-start h-auto py-4" size="lg">
                    <MessageCircle className="w-5 h-5 mr-3 text-purple-600" />
                    <div className="text-left flex-1">
                      <div className="font-semibold">Chat with AI Advisor</div>
                      <div className="text-sm text-gray-600">Get personalized academic support 24/7</div>
                    </div>
                  </Button>
                </Link>

                <Button variant="outline" className="w-full justify-start h-auto py-4" size="lg">
                  <TrendingUp className="w-5 h-5 mr-3 text-green-600" />
                  <div className="text-left flex-1">
                    <div className="font-semibold">View Progress Analytics</div>
                    <div className="text-sm text-gray-600">Detailed insights into your performance</div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

