'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  BookOpen, 
  MessageCircle, 
  GraduationCap,
  BarChart,
  LogOut,
  Menu,
  Search,
  PlayCircle,
  FileText,
  Link2,
  Clock,
  ArrowLeft,
  X
} from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { api, Student, CourseMaterial, Course } from '@/lib/api';
import Link from 'next/link';

export default function CoursesPage() {
  const router = useRouter();
  const [student, setStudent] = useState<Student | null>(null);
  const [materials, setMaterials] = useState<CourseMaterial[]>([]);
  const [filteredMaterials, setFilteredMaterials] = useState<CourseMaterial[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedMaterial, setSelectedMaterial] = useState<CourseMaterial | null>(null);
  const [imageErrors, setImageErrors] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const storedStudent = localStorage.getItem('student');
    if (!storedStudent) {
      router.push('/');
      return;
    }

    const studentData = JSON.parse(storedStudent);
    setStudent(studentData);
    loadMaterials(studentData.id_student);
    loadCourses();
  }, [router]);

  useEffect(() => {
    filterMaterials();
  }, [searchTerm, selectedType, materials]);

  const loadMaterials = async (studentId: number) => {
    try {
      const data = await api.getCourseMaterials(studentId);
      setMaterials(data.materials || []);
      setFilteredMaterials(data.materials || []);
    } catch (error) {
      console.error('Failed to load materials:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCourses = async () => {
    try {
      const data = await api.getAllCourses();
      setCourses(data.courses || []);
    } catch (error) {
      console.error('Failed to load courses:', error);
    }
  };

  const filterMaterials = () => {
    let filtered = materials;

    if (selectedType !== 'all') {
      filtered = filtered.filter(m => m.activity_type === selectedType);
    }

    if (searchTerm) {
      filtered = filtered.filter(m => 
        m.code_module.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.activity_type.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredMaterials(filtered);
  };

  const handleLogout = () => {
    localStorage.removeItem('student');
    router.push('/');
  };

  const getActivityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'video':
      case 'oucontent':
        return <PlayCircle className="w-5 h-5" />;
      case 'resource':
      case 'page':
        return <FileText className="w-5 h-5" />;
      case 'url':
      case 'externalquiz':
        return <Link2 className="w-5 h-5" />;
      default:
        return <BookOpen className="w-5 h-5" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'video':
      case 'oucontent':
        return 'bg-blue-100 text-blue-700';
      case 'resource':
      case 'page':
        return 'bg-green-100 text-green-700';
      case 'url':
      case 'externalquiz':
        return 'bg-purple-100 text-purple-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const activityTypes = Array.from(new Set(materials.map(m => m.activity_type)));

  if (loading || !student) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading course materials...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <img src="/study.png" alt="PLAF" className="w-10 h-10 rounded-lg object-cover" />
              <span className="text-xl font-bold text-gray-900">PLAF</span>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <BarChart className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
              <Link href="/dashboard/courses" className="flex items-center gap-2 text-blue-600 font-medium">
                <BookOpen className="w-5 h-5" />
                <span>My Courses</span>
              </Link>
              <Link href="/dashboard/chat" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <MessageCircle className="w-5 h-5" />
                <span>AI Advisor</span>
              </Link>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-3">
                <Avatar>
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    {student.first_name[0]}{student.last_name[0]}
                  </AvatarFallback>
                </Avatar>
                <div className="text-sm">
                  <div className="font-semibold text-gray-900">{student.first_name} {student.last_name}</div>
                  <div className="text-gray-500">{student.email}</div>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
                <Menu className="w-5 h-5" />
              </Button>
            </div>
          </div>

          {menuOpen && (
            <div className="md:hidden py-4 border-t">
              <div className="flex flex-col gap-2">
                <Link href="/dashboard" className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg">
                  <BarChart className="w-5 h-5" />
                  <span>Dashboard</span>
                </Link>
                <Link href="/dashboard/courses" className="flex items-center gap-2 px-4 py-3 text-blue-600 bg-blue-50 rounded-lg font-medium">
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
        {/* Header */}
        <div className="mb-8">
          <Link href="/dashboard">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-blue-600" />
            Course Materials
          </h1>
          <p className="text-gray-600">Access your learning resources and activities</p>
        </div>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  placeholder="Search materials..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 h-11"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={selectedType === 'all' ? 'default' : 'outline'}
                  onClick={() => setSelectedType('all')}
                >
                  All
                </Button>
                {activityTypes.slice(0, 4).map((type) => (
                  <Button
                    key={type}
                    variant={selectedType === type ? 'default' : 'outline'}
                    onClick={() => setSelectedType(type)}
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Courses Section */}
        {courses.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Courses</h2>
            <p className="text-gray-600 mb-6">Start learning with our interactive courses</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course) => (
                <Card 
                  key={course.id} 
                  className="group hover:shadow-xl transition-all duration-300 cursor-pointer border-2 hover:border-blue-500 overflow-hidden flex flex-col h-full"
                >
                  <div className="relative h-48 overflow-hidden flex-shrink-0">
                    {/* Gradient background - always visible */}
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500"></div>
                    
                    {/* Image - only if URL exists and no error */}
                    {course.thumbnail_url && !imageErrors[course.id] ? (
                      <img 
                        src={course.thumbnail_url} 
                        alt={course.title}
                        className="relative w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 z-10"
                        onError={() => {
                          setImageErrors(prev => ({ ...prev, [course.id]: true }));
                        }}
                        loading="lazy"
                      />
                    ) : (
                      /* Icon and category - only when no image or image failed */
                      <div className="relative w-full h-full flex flex-col items-center justify-center text-white z-10">
                        <GraduationCap className="w-16 h-16 opacity-90 mb-2 drop-shadow-lg" />
                        <p className="text-sm font-semibold opacity-95 drop-shadow">{course.category || 'Course'}</p>
                      </div>
                    )}
                    
                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all pointer-events-none z-20"></div>
                  </div>
                  
                  <div className="flex flex-col flex-grow">
                    <CardHeader className="pb-3 flex-shrink-0">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200">
                          {course.category || 'Course'}
                        </Badge>
                        <Badge variant="secondary">
                          {course.level || 'All Levels'}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg group-hover:text-blue-600 transition-colors line-clamp-2 min-h-[3.5rem]">
                        {course.title}
                      </CardTitle>
                      <CardDescription className="line-clamp-3 mt-2 min-h-[4.5rem]">
                        {course.description}
                      </CardDescription>
                    </CardHeader>
                    
                    <CardContent className="pt-0 flex flex-col flex-grow">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-4 flex-shrink-0">
                        <div className="flex items-center gap-2">
                          <GraduationCap className="w-4 h-4" />
                          <span>{course.instructor_name || 'Instructor'}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{course.duration_hours || 0}h</span>
                        </div>
                      </div>
                      
                      <div className="mt-auto">
                        <Link href={`/dashboard/courses/${course.id}`}>
                          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                            Start Learning →
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Course Materials Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-blue-600" />
            Course Materials
          </h2>
          <p className="text-gray-600 mb-6">Access your learning resources and activities</p>
        </div>

        {/* Materials Grid - Udemy Style */}
        {filteredMaterials.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMaterials.map((material) => (
              <Card 
                key={material.id_site} 
                className="group hover:shadow-xl transition-all duration-300 cursor-pointer border-2 hover:border-blue-500"
                onClick={() => setSelectedMaterial(material)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between mb-3">
                    <div className={`p-3 rounded-lg group-hover:scale-110 transition-transform ${getActivityColor(material.activity_type)}`}>
                      {getActivityIcon(material.activity_type)}
                    </div>
                    <Badge variant="outline" className="group-hover:bg-blue-50 group-hover:text-blue-600">
                      {material.activity_type}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                    {material.code_module}
                  </CardTitle>
                  <CardDescription className="group-hover:text-gray-700">
                    {material.code_presentation}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 group-hover:text-blue-600" />
                      <span className="group-hover:text-gray-900">
                        {material.week_from && material.week_to 
                          ? `Week ${material.week_from}-${material.week_to}`
                          : 'Available now'}
                      </span>
                    </div>
                  </div>
                  <Button 
                    className="w-full group-hover:bg-blue-600 group-hover:text-white transition-colors" 
                    variant="outline"
                  >
                    View Details →
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-16 text-center">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No materials found</h3>
              <p className="text-gray-600">
                {searchTerm || selectedType !== 'all' 
                  ? 'Try adjusting your filters' 
                  : 'Materials will appear here once you enroll in a course'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Material Detail Modal */}
      <Dialog open={!!selectedMaterial} onOpenChange={() => setSelectedMaterial(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3 text-2xl">
              <div className={`p-3 rounded-lg ${selectedMaterial && getActivityColor(selectedMaterial.activity_type)}`}>
                {selectedMaterial && getActivityIcon(selectedMaterial.activity_type)}
              </div>
              {selectedMaterial?.code_module} - {selectedMaterial?.activity_type}
            </DialogTitle>
            <DialogDescription>
              Course: {selectedMaterial?.code_presentation}
            </DialogDescription>
          </DialogHeader>

          {selectedMaterial && (
            <div className="space-y-6 py-4">
              {/* Material Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="text-sm font-semibold text-gray-500">Activity Type</div>
                  <Badge variant="outline" className="text-sm">
                    {selectedMaterial.activity_type}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="text-sm font-semibold text-gray-500">Availability</div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="w-4 h-4" />
                    {selectedMaterial.week_from && selectedMaterial.week_to 
                      ? `Week ${selectedMaterial.week_from} - ${selectedMaterial.week_to}`
                      : 'Available now'}
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="p-4 bg-gray-50 rounded-lg border">
                <h3 className="font-semibold mb-2">About this material</h3>
                <p className="text-gray-700">
                  This {selectedMaterial.activity_type.toLowerCase()} is part of the {selectedMaterial.code_module} course 
                  for {selectedMaterial.code_presentation} presentation.
                  {selectedMaterial.week_from && ` Available from week ${selectedMaterial.week_from}.`}
                </p>
              </div>

              {/* Activity Type Info */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-900 mb-2">Learning Activity</h3>
                <p className="text-blue-700 text-sm">
                  {selectedMaterial.activity_type === 'oucontent' && 
                    'Interactive course content with videos, readings, and exercises.'}
                  {selectedMaterial.activity_type === 'resource' && 
                    'Downloadable course materials and supplementary resources.'}
                  {selectedMaterial.activity_type === 'url' && 
                    'External web resources to support your learning.'}
                  {selectedMaterial.activity_type === 'externalquiz' && 
                    'External assessment to test your understanding.'}
                  {selectedMaterial.activity_type === 'page' && 
                    'Course information page with important details.'}
                  {selectedMaterial.activity_type === 'forumng' && 
                    'Discussion forum to interact with peers and instructors.'}
                  {selectedMaterial.activity_type === 'glossary' && 
                    'Key terms and definitions for the course.'}
                  {selectedMaterial.activity_type === 'homepage' && 
                    'Course homepage with overview and navigation.'}
                  {!['oucontent', 'resource', 'url', 'externalquiz', 'page', 'forumng', 'glossary', 'homepage'].includes(selectedMaterial.activity_type) &&
                    'Learning material to support your course objectives.'}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end pt-4">
                <Button variant="outline" onClick={() => setSelectedMaterial(null)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

