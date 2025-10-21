'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  MessageCircle, 
  BarChart,
  LogOut,
  Menu,
  User,
  Mail,
  MapPin,
  GraduationCap,
  Calendar,
  Award,
  TrendingUp
} from 'lucide-react';
import { Student } from '@/lib/api';
import Link from 'next/link';

export default function ProfilePage() {
  const router = useRouter();
  const [student, setStudent] = useState<Student | null>(null);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const storedStudent = localStorage.getItem('student');
    if (!storedStudent) {
      router.push('/');
      return;
    }

    const studentData = JSON.parse(storedStudent);
    setStudent(studentData);
    setLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('student');
    router.push('/');
  };

  if (loading || !student) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  const riskPercentage = (student.risk_probability || 0) * 100;
  const isAtRisk = student.is_at_risk || riskPercentage > 50;

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
              <Link href="/dashboard" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
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
              <div className="hidden md:flex items-center gap-3">
                <Avatar className="cursor-pointer">
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white font-semibold">
                    {student.first_name?.charAt(0)}{student.last_name?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900">{student.first_name} {student.last_name}</p>
                  <p className="text-xs text-gray-500">{student.email}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="hidden md:flex">
                <LogOut className="w-4 h-4" />
              </Button>

              {/* Mobile Menu Button */}
              <Button variant="ghost" size="sm" className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
                <Menu className="w-6 h-6" />
              </Button>
            </div>
          </div>

          {/* Mobile Menu */}
          {menuOpen && (
            <div className="md:hidden py-4 border-t">
              <div className="flex flex-col gap-2">
                <Link href="/dashboard" className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BarChart className="w-5 h-5" />
                  <span>Dashboard</span>
                </Link>
                <Link href="/dashboard/courses" className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BookOpen className="w-5 h-5" />
                  <span>My Courses</span>
                </Link>
                <Link href="/dashboard/chat" className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <MessageCircle className="w-5 h-5" />
                  <span>AI Advisor</span>
                </Link>
                <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg">
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <User className="w-8 h-8" />
            My Profile
          </h1>
          <p className="text-gray-600">View and manage your personal information</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Card */}
          <Card className="lg:col-span-1">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center">
                <Avatar className="w-24 h-24 mb-4">
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white text-3xl font-bold">
                    {student.first_name?.charAt(0)}{student.last_name?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">
                  {student.first_name} {student.last_name}
                </h2>
                <p className="text-gray-600 mb-4">{student.email}</p>
                <Badge variant={isAtRisk ? "destructive" : "default"} className="mb-4">
                  {isAtRisk ? '⚠️ At-Risk' : '✅ On Track'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Information Cards */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5 text-blue-600" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Mail className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-medium text-gray-900">{student.email}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Gender</p>
                      <p className="font-medium text-gray-900">{student.gender || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Region</p>
                      <p className="font-medium text-gray-900">{student.region || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Age Band</p>
                      <p className="font-medium text-gray-900">{student.age_band || 'Not specified'}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Academic Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-purple-600" />
                  Academic Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <BookOpen className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Course Module</p>
                      <p className="font-medium text-gray-900">{student.code_module}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Presentation</p>
                      <p className="font-medium text-gray-900">{student.code_presentation}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Award className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Education Level</p>
                      <p className="font-medium text-gray-900">{student.highest_education || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <TrendingUp className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Risk Level</p>
                      <p className={`font-medium ${isAtRisk ? 'text-red-600' : 'text-green-600'}`}>
                        {riskPercentage.toFixed(1)}% {isAtRisk ? '(At-Risk)' : '(On Track)'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <BarChart className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Study Credits</p>
                      <p className="font-medium text-gray-900">{student.studied_credits || 0}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-gray-400 mt-1" />
                    <div>
                      <p className="text-sm text-gray-500">Disability</p>
                      <p className="font-medium text-gray-900">{student.disability === 'Y' ? 'Yes' : 'No'}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Navigate to other sections</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Link href="/dashboard">
                    <Button variant="outline" className="w-full justify-start">
                      <BarChart className="w-4 h-4 mr-2" />
                      View Dashboard
                    </Button>
                  </Link>
                  <Link href="/dashboard/courses">
                    <Button variant="outline" className="w-full justify-start">
                      <BookOpen className="w-4 h-4 mr-2" />
                      Browse Courses
                    </Button>
                  </Link>
                  <Link href="/dashboard/chat">
                    <Button variant="outline" className="w-full justify-start">
                      <MessageCircle className="w-4 h-4 mr-2" />
                      AI Advisor
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

