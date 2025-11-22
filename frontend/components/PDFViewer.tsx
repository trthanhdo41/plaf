/**
 * PDF Viewer Component for MIT OCW Lecture Notes
 * Displays PDF slides inline or provides download link
 */

import { FileText, Download, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PDFViewerProps {
    pdfUrl: string;
    title?: string;
}

export default function PDFViewer({ pdfUrl, title = "Lecture Notes" }: PDFViewerProps) {
    return (
        <div className="w-full h-full flex flex-col bg-gray-900">
            {/* Header */}
            <div className="bg-gray-800 border-b border-gray-700 p-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FileText className="w-6 h-6 text-blue-400" />
                        <div>
                            <h3 className="text-white font-semibold">{title}</h3>
                            <p className="text-xs text-gray-400">MIT OpenCourseWare Lecture Slides</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(pdfUrl, '_blank')}
                            className="border-gray-600 text-gray-300 hover:bg-gray-700"
                        >
                            <ExternalLink className="w-4 h-4 mr-2" />
                            Open in New Tab
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                const link = document.createElement('a');
                                link.href = pdfUrl;
                                link.download = `${title}.pdf`;
                                link.click();
                            }}
                            className="border-gray-600 text-gray-300 hover:bg-gray-700"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                        </Button>
                    </div>
                </div>
            </div>

            {/* PDF Viewer */}
            <div className="flex-1 relative">
                <iframe
                    src={`${pdfUrl}#view=FitH`}
                    className="w-full h-full"
                    title={title}
                />
                {/* Fallback for browsers that don't support PDF embedding */}
                <div className="absolute bottom-4 right-4">
                    <div className="bg-gray-800/90 backdrop-blur-sm border border-gray-700 rounded-lg p-3 text-sm text-gray-300">
                        <p>PDF not displaying?{' '}
                            <a
                                href={pdfUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300 underline"
                            >
                                Open directly
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
