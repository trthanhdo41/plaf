'use client';

import { useState, useEffect, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, RotateCcw, RotateCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';

interface VideoPlayerProps {
  videoUrl: string;
  lessonId: number;
  studentId: number;
  onProgressUpdate: (watchTime: number, duration: number, percentage: number) => void;
  onComplete: () => void;
  initialWatchTime?: number;
}

// Helper function to extract YouTube video ID from various URL formats
const getYouTubeVideoId = (url: string): string | null => {
  if (!url) return null;
  
  const patterns = [
    // youtube.com/watch?v=VIDEO_ID
    /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
    // youtu.be/VIDEO_ID
    /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    // youtube.com/embed/VIDEO_ID
    /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    // youtube.com/watch?.*v=VIDEO_ID
    /youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match && match[1]) {
      return match[1];
    }
  }
  
  return null;
};

export default function VideoPlayer({
  videoUrl,
  lessonId,
  studentId,
  onProgressUpdate,
  onComplete,
  initialWatchTime = 0
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(initialWatchTime);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [watchedTime, setWatchedTime] = useState(initialWatchTime);
  const [watchedSegments, setWatchedSegments] = useState<Set<number>>(new Set());
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Track progress every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (videoRef.current && isPlaying) {
        const current = videoRef.current.currentTime;
        const total = videoRef.current.duration;
        
        // Mark this second as watched
        const currentSecond = Math.floor(current);
        setWatchedSegments(prev => new Set([...prev, currentSecond]));
        
        // Calculate total watched time (unique segments)
        const totalWatched = watchedSegments.size + 1;
        setWatchedTime(totalWatched);
        
        // Calculate percentage
        const percentage = total > 0 ? (totalWatched / total) * 100 : 0;
        
        // Update progress
        onProgressUpdate(totalWatched, total, percentage);
        
        // Auto-complete if watched 80%
        if (percentage >= 80) {
          onComplete();
        }
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isPlaying, watchedSegments, onProgressUpdate, onComplete]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
      // Resume from last watched position
      videoRef.current.currentTime = initialWatchTime;
    }
  };

  const handleSeek = (value: number[]) => {
    if (videoRef.current) {
      const newTime = (value[0] / 100) * duration;
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0] / 100;
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !isMuted;
      videoRef.current.muted = newMuted;
      setIsMuted(newMuted);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const skip = (seconds: number) => {
    if (videoRef.current) {
      const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const watchPercentage = duration > 0 ? (watchedTime / duration) * 100 : 0;

  const videoId = getYouTubeVideoId(videoUrl);
  const embedUrl = videoId ? `https://www.youtube.com/embed/${videoId}?controls=1&rel=0&modestbranding=1&fs=1&cc_load_policy=0&iv_load_policy=3&autohide=0` : null;
  
  // Debug logging
  console.log('Video URL:', videoUrl);
  console.log('Extracted Video ID:', videoId);
  console.log('Embed URL:', embedUrl);

  return (
    <div className="relative bg-black rounded-lg overflow-hidden group">
      {embedUrl ? (
        <iframe
          className="w-full aspect-video"
          src={embedUrl}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="YouTube Video Player"
        />
      ) : videoUrl && videoUrl.includes('youtube') ? (
        // Fallback: Use original URL if it's YouTube but ID extraction failed
        <iframe
          className="w-full aspect-video"
          src={videoUrl.replace('watch?v=', 'embed/').split('&')[0] + '?controls=1'}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title="YouTube Video Player"
        />
      ) : (
        <video
          ref={videoRef}
          className="w-full aspect-video"
          src={videoUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onEnded={() => {
            setIsPlaying(false);
            if (watchPercentage >= 80) onComplete();
          }}
        />
      )}
      
      {/* Controls Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="absolute bottom-0 left-0 right-0 p-4 space-y-3">
          {/* Progress Bar */}
          <div className="space-y-1">
            <Slider
              value={[duration > 0 ? (currentTime / duration) * 100 : 0]}
              onValueChange={handleSeek}
              className="w-full"
              max={100}
              step={0.1}
            />
            <div className="flex justify-between text-xs text-white">
              <span>{formatTime(currentTime)}</span>
              <span className="text-green-400">
                Watched: {watchPercentage.toFixed(1)}% 
                {watchPercentage >= 80 && ' ✓'}
              </span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
          
          {/* Control Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => skip(-10)}
                className="text-white hover:bg-white/20"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={togglePlay}
                className="text-white hover:bg-white/20"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => skip(10)}
                className="text-white hover:bg-white/20"
              >
                <RotateCw className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleMute}
                className="text-white hover:bg-white/20"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </Button>
              
              <div className="w-20">
                <Slider
                  value={[isMuted ? 0 : volume * 100]}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                />
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleFullscreen}
                className="text-white hover:bg-white/20"
              >
                <Maximize className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Play Button Overlay */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Button
            variant="ghost"
            size="lg"
            onClick={togglePlay}
            className="w-16 h-16 rounded-full bg-white/20 hover:bg-white/30 text-white"
          >
            <Play className="w-8 h-8 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
