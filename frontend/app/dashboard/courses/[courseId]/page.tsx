'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api, Student, Course, Lesson, LessonProgress } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  ArrowLeft,
  Play,
  CheckCircle2,
  Circle,
  ChevronRight,
  Clock,
  Menu,
  X,
  GraduationCap,
} from 'lucide-react';

export default function CoursePlayerPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);

  const [student, setStudent] = useState<Student | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [progress, setProgress] = useState<Record<number, LessonProgress>>({});
  const [overallProgress, setOverallProgress] = useState(0);
  const [selectedLessonId, setSelectedLessonId] = useState<number | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedStudent = localStorage.getItem('student');
    if (!storedStudent) {
      router.push('/');
      return;
    }

    const studentData = JSON.parse(storedStudent);
    setStudent(studentData);
    loadCourseData(courseId, studentData.id_student);
  }, [courseId, router]);

  const loadCourseData = async (courseId: number, studentId: number) => {
    try {
      const data = await api.getCourseDetail(courseId, studentId);
      setCourse(data.course);
      const sortedLessons = (data.lessons || []).sort((a, b) => (a.lesson_order || 0) - (b.lesson_order || 0));
      setLessons(sortedLessons);
      setProgress(data.progress || {});
      setOverallProgress(data.overall_progress || 0);

      if (sortedLessons.length > 0 && !selectedLessonId) {
        const firstLesson = sortedLessons[0];
        setSelectedLessonId(firstLesson.id);
        setSelectedLesson(firstLesson);
      }
    } catch (error) {
      console.error('Failed to load course:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLessonSelect = async (lesson: Lesson) => {
    setSelectedLessonId(lesson.id);
    setSelectedLesson(lesson);

    try {
      const data = await api.getLessonDetail(courseId, lesson.id);
      setSelectedLesson(data.lesson);
    } catch (error) {
      console.error('Failed to load lesson:', error);
    }

    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  const handleCompleteLesson = async () => {
    if (!selectedLesson || !student) return;

    try {
      await api.updateProgress(
        courseId,
        student.id_student,
        selectedLesson.id,
        true,
        100
      );

      setProgress((prev) => ({
        ...prev,
        [selectedLesson.id]: {
          lesson_id: selectedLesson.id,
          completed: 1,
          progress_percent: 100,
          time_spent_minutes: (prev[selectedLesson.id]?.time_spent_minutes || 0) + 10,
        },
      }));

      await loadCourseData(courseId, student.id_student);
    } catch (error: any) {
      console.error('Failed to update progress:', error);
      alert('Failed to mark lesson as complete: ' + (error.message || 'Unknown error'));
    }
  };

  const getNextLesson = () => {
    if (!selectedLessonId || lessons.length === 0) return null;
    const currentIndex = lessons.findIndex((l) => l.id === selectedLessonId);
    return currentIndex < lessons.length - 1 ? lessons[currentIndex + 1] : null;
  };

  const getPreviousLesson = () => {
    if (!selectedLessonId || lessons.length === 0) return null;
    const currentIndex = lessons.findIndex((l) => l.id === selectedLessonId);
    return currentIndex > 0 ? lessons[currentIndex - 1] : null;
  };

  const handleNextLesson = () => {
    const next = getNextLesson();
    if (next) handleLessonSelect(next);
  };

  const handlePreviousLesson = () => {
    const prev = getPreviousLesson();
    if (prev) handleLessonSelect(prev);
  };

  const isLessonCompleted = (lessonId: number) => {
    return progress[lessonId]?.completed === 1;
  };

  const getLessonProgress = (lessonId: number) => {
    return progress[lessonId]?.progress_percent || 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading course...</p>
        </div>
      </div>
    );
  }

  if (!course || !student) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Course not found</p>
          <Button onClick={() => router.push('/dashboard/courses')}>
            Back to Courses
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Top Bar */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push('/dashboard/courses')}
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold line-clamp-1">{course.title}</h1>
              <p className="text-sm text-gray-400">Progress: {Math.round(overallProgress)}%</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden text-gray-400 hover:text-white"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>
        <div className="px-4 pb-2">
          <Progress value={overallProgress} className="h-2" />
        </div>
      </div>

      <div className="flex h-[calc(100vh-100px)]">
        {/* Sidebar - Lesson List */}
        <div
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } fixed md:sticky md:translate-x-0 top-[100px] left-0 h-[calc(100vh-100px)] w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto transition-transform duration-300 z-40`}
        >
          <div className="p-4">
            <div className="mb-4">
              <h2 className="text-sm font-semibold text-gray-400 uppercase mb-2">
                Course Content
              </h2>
              <p className="text-sm text-gray-500">
                {lessons.length} lessons • {Math.round(overallProgress)}% complete
              </p>
            </div>

            <div className="space-y-1">
              {lessons.map((lesson, index) => {
                const isCompleted = isLessonCompleted(lesson.id);
                const isSelected = selectedLessonId === lesson.id;
                const lessonProgress = getLessonProgress(lesson.id);

                return (
                  <button
                    key={lesson.id}
                    onClick={() => handleLessonSelect(lesson)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      isSelected
                        ? 'bg-blue-600 text-white'
                        : 'hover:bg-gray-700 text-gray-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        {isCompleted ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-gray-400">
                            {index + 1}
                          </span>
                          <span className="text-xs text-gray-400">{lesson.lesson_type}</span>
                        </div>
                        <p className="text-sm font-medium line-clamp-2">{lesson.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {lesson.duration_minutes && (
                            <span className="text-xs text-gray-400 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {lesson.duration_minutes}m
                            </span>
                          )}
                          {lessonProgress > 0 && lessonProgress < 100 && (
                            <div className="flex-1 max-w-24">
                              <Progress value={lessonProgress} className="h-1" />
                            </div>
                          )}
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          {selectedLesson ? (
            <div className="max-w-5xl mx-auto">
              {/* Video/Content Area */}
              <div className="bg-black aspect-video relative">
                {selectedLesson.video_url ? (
                  <iframe
                    src={selectedLesson.video_url}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <Play className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-400">No video available</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Lesson Content */}
              <div className="p-6 bg-gray-900">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 text-xs font-medium rounded bg-blue-600">
                        {selectedLesson.lesson_type}
                      </span>
                      {selectedLesson.duration_minutes && (
                        <span className="text-sm text-gray-400 flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {selectedLesson.duration_minutes} minutes
                        </span>
                      )}
                    </div>
                    <h2 className="text-2xl font-bold mb-2">{selectedLesson.title}</h2>
                  </div>
                  {isLessonCompleted(selectedLesson.id) ? (
                    <div className="flex items-center gap-2 text-green-500">
                      <CheckCircle2 className="w-5 h-5" />
                      <span className="text-sm font-medium">Completed</span>
                    </div>
                  ) : (
                    <Button onClick={handleCompleteLesson} className="bg-green-600 hover:bg-green-700">
                      Mark as Complete
                    </Button>
                  )}
                </div>

                {selectedLesson.content && (
                  <div className="prose prose-invert max-w-none mb-6">
                    <div
                      className="text-gray-300 leading-relaxed whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{ __html: selectedLesson.content }}
                    />
                  </div>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between pt-6 border-t border-gray-700 mt-6">
                  <Button
                    variant="outline"
                    onClick={handlePreviousLesson}
                    disabled={!getPreviousLesson()}
                    className="border-gray-600 text-gray-300 hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Previous
                  </Button>
                  <Button
                    onClick={handleNextLesson}
                    disabled={!getNextLesson()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next Lesson
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <GraduationCap className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">Select a lesson to begin</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
