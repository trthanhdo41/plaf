'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { 
  CheckCircle, 
  AlertCircle, 
  User, 
  Mail, 
  Lock, 
  UserPlus,
  LogIn,
  Lightbulb,
  MessageCircle,
  BarChart3,
  Users,
  Clock,
  Award
} from 'lucide-react';
import { api } from '@/lib/api';

export default function LandingPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerFirstName, setRegisterFirstName] = useState('');
  const [registerLastName, setRegisterLastName] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await api.login(loginEmail, loginPassword);
      
      if (result.success) {
        toast({
          variant: "success",
          title: "Login Successful",
          description: "Welcome back! Redirecting to your dashboard...",
        });
        localStorage.setItem('student', JSON.stringify(result.student));
        setTimeout(() => router.push('/dashboard'), 1500);
      } else {
        toast({
          variant: "destructive",
          title: "Login Failed",
          description: "Please check your credentials and try again.",
        });
      }
    } catch (err: any) {
      console.error('Login error:', err);
      toast({
        variant: "destructive",
        title: "Login Error",
        description: err.message || 'Invalid email or password. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await api.register(
        registerEmail,
        registerPassword,
        registerFirstName,
        registerLastName
      );
      
      if (result.success) {
        toast({
          variant: "success",
          title: "Account Created",
          description: "Welcome to PLAF! Redirecting to your dashboard...",
        });
        localStorage.setItem('student', JSON.stringify(result.student));
        setTimeout(() => router.push('/dashboard'), 1500);
      }
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "Registration Failed",
        description: err.message || 'Please check your information and try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section with Background Image */}
      <div 
        className="relative bg-cover bg-center min-h-[600px] flex items-center"
        style={{
          backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920&q=80)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Hero Text */}
            <div className="text-white space-y-6">
              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                Learn without limits
              </h1>
              <p className="text-xl text-gray-200">
                Start, switch, or advance your career with AI-powered learning analytics. 
                Get personalized insights and academic support 24/7.
              </p>
              <div className="flex flex-wrap gap-4 pt-4">
                <div className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20 flex items-center gap-2">
                  <Users className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-2xl font-bold">32,000+</div>
                    <div className="text-sm text-gray-200">Students Tracked</div>
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20 flex items-center gap-2">
                  <Award className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-2xl font-bold">85%</div>
                    <div className="text-sm text-gray-200">Prediction Accuracy</div>
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/20 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-2xl font-bold">24/7</div>
                    <div className="text-sm text-gray-200">AI Support</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Login/Register Card */}
            <Card className="bg-white p-8 shadow-2xl">
              <Tabs defaultValue="login" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger value="login">Log In</TabsTrigger>
                  <TabsTrigger value="register">Sign Up</TabsTrigger>
                </TabsList>
                
                {/* Login Tab */}
                <TabsContent value="login">
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="login-email">Email</Label>
                      <Input
                        id="login-email"
                        type="email"
                        placeholder="Enter your email"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-12"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="login-password">Password</Label>
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="Enter your password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-12"
                      />
                    </div>

                    <Button 
                      type="submit" 
                      className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-semibold"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Logging in...
                        </>
                      ) : (
                        <>
                          <LogIn className="w-4 h-4 mr-2" />
                          Log In
                        </>
                      )}
                    </Button>

                    <div className="pt-4 border-t text-center">
                      <p className="text-sm text-gray-600 mb-2">
                        <strong>Demo Account:</strong>
                      </p>
                      <p className="text-xs text-gray-500 font-mono mb-2">
                        student650515@ou.ac.uk / demo123
                      </p>
                      <button
                        type="button"
                        onClick={() => {
                          setLoginEmail('student650515@ou.ac.uk');
                          setLoginPassword('demo123');
                          toast({
                            title: "Demo Credentials Filled",
                            description: "You can now click 'Log In' to access the demo account.",
                          });
                        }}
                        className="text-xs text-purple-600 hover:text-purple-700 underline"
                      >
                        Click to fill demo credentials
                      </button>
                    </div>
                  </form>
                </TabsContent>
                
                {/* Register Tab */}
                <TabsContent value="register">
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="register-firstname">First Name</Label>
                        <Input
                          id="register-firstname"
                          type="text"
                          placeholder="First name"
                          value={registerFirstName}
                          onChange={(e) => setRegisterFirstName(e.target.value)}
                          required
                          disabled={isLoading}
                          className="h-12"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="register-lastname">Last Name</Label>
                        <Input
                          id="register-lastname"
                          type="text"
                          placeholder="Last name"
                          value={registerLastName}
                          onChange={(e) => setRegisterLastName(e.target.value)}
                          required
                          disabled={isLoading}
                          className="h-12"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="register-email">Email</Label>
                      <Input
                        id="register-email"
                        type="email"
                        placeholder="Enter your email"
                        value={registerEmail}
                        onChange={(e) => setRegisterEmail(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-12"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="register-password">Password</Label>
                      <Input
                        id="register-password"
                        type="password"
                        placeholder="Create a password"
                        value={registerPassword}
                        onChange={(e) => setRegisterPassword(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-12"
                      />
                    </div>

                    <Button 
                      type="submit" 
                      className="w-full h-12 bg-purple-600 hover:bg-purple-700 text-white font-semibold"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Creating Account...
                        </>
                      ) : (
                        <>
                          <UserPlus className="w-4 h-4 mr-2" />
                          Sign Up
                        </>
                      )}
                    </Button>
                  </form>
                </TabsContent>
              </Tabs>
            </Card>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-gray-50 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              A broad selection of courses
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Choose from over 100 learning materials with AI-powered insights to help you succeed
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Feature Card 1 */}
            <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
              <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                <Lightbulb className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">AI-Powered Insights</h3>
              <p className="text-gray-600 leading-relaxed">
                Get personalized recommendations and early risk detection to stay on track with your learning goals.
              </p>
            </div>

            {/* Feature Card 2 */}
            <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <MessageCircle className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">24/7 AI Advisor</h3>
              <p className="text-gray-600 leading-relaxed">
                Chat with our intelligent advisor anytime for academic support, study tips, and personalized guidance.
              </p>
            </div>

            {/* Feature Card 3 */}
            <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
              <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Track Your Progress</h3>
              <p className="text-gray-600 leading-relaxed">
                Monitor your performance with detailed analytics and visualizations of your learning journey.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-purple-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Transform your learning journey with AI
          </h2>
          <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
            Join thousands of students using PLAF to achieve their academic goals
          </p>
          <Button 
            size="lg" 
            className="bg-white text-purple-600 hover:bg-gray-100 font-semibold h-14 px-8 text-lg"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Get Started Today
          </Button>
        </div>
      </div>
    </div>
  );
}
