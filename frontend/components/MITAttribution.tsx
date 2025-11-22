/**
 * MIT OpenCourseWare Attribution Component
 * Displays proper attribution and licensing information for MIT OCW content
 */

import { ExternalLink } from 'lucide-react';

interface MITAttributionProps {
  mitCourseId?: string;
  compact?: boolean;
}

export default function MITAttribution({ mitCourseId, compact = false }: MITAttributionProps) {
  if (compact) {
    return (
      <div className="px-4 py-2 bg-gray-800 border-t border-gray-700">
        <p className="text-xs text-gray-400">
          📚 Content based on{' '}
          <a 
            href="https://ocw.mit.edu" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
          >
            MIT OpenCourseWare
            <ExternalLink className="w-3 h-3" />
          </a>
          {mitCourseId && (
            <span> ({mitCourseId})</span>
          )}
        </p>
      </div>
    );
  }

  return (
    <div className="mt-6 p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-white mb-2">
            Content Attribution
          </h4>
          <div className="text-sm text-gray-300 space-y-2">
            <p>
              This course incorporates materials from{' '}
              <a 
                href="https://ocw.mit.edu" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
              >
                MIT OpenCourseWare
                <ExternalLink className="w-3 h-3" />
              </a>
              {mitCourseId && (
                <span> (Course {mitCourseId})</span>
              )}, which is made available under a{' '}
              <a 
                href="https://creativecommons.org/licenses/by-nc-sa/4.0/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 hover:underline inline-flex items-center gap-1"
              >
                Creative Commons BY-NC-SA 4.0 license
                <ExternalLink className="w-3 h-3" />
              </a>.
            </p>
            <p className="text-xs text-gray-400">
              <span className="font-medium">License:</span> You are free to share and adapt this material for non-commercial purposes with proper attribution.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
