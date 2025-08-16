import { useState } from 'react';
import { ArrowLeft, RotateCcw, Image as ImageIcon, Settings, HelpCircle } from 'lucide-react';
import { Slider } from './ui/slider';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { cn } from './ui/utils';

interface CameraScreenProps {
  onBack: () => void;
  onCapture: () => void;
}

const alignmentModes = [
  { id: 'center', label: '중심', description: '글자 중심점 정렬' },
  { id: 'frame', label: '테두리', description: '글자 외곽선 정렬' },
  { id: 'auto', label: '자동', description: 'AI 자동 정렬' }
];

export function CameraScreen({ onBack, onCapture }: CameraScreenProps) {
  const [guideOpacity, setGuideOpacity] = useState([70]);
  const [alignmentMode, setAlignmentMode] = useState('center');
  const [showTip, setShowTip] = useState(true);

  return (
    <div className="absolute inset-0 bg-black z-50">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 pt-12 bg-gradient-to-b from-black/50 to-transparent">
        <Button
          onClick={onBack}
          variant="ghost"
          size="sm"
          className="text-white hover:bg-white/20"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/20"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Camera Preview Area */}
      <div className="relative flex-1 bg-gray-900 flex items-center justify-center h-full">
        {/* Mock camera preview */}
        <div className="w-full h-full bg-gray-800 relative">
          {/* Guide Overlay */}
          <div 
            className="absolute inset-0 flex items-center justify-center"
            style={{ opacity: guideOpacity[0] / 100 }}
          >
            <svg
              width="320"
              height="320"
              viewBox="0 0 320 320"
              className="text-primary"
            >
              {/* Outer guide frame */}
              <rect
                x="40"
                y="40"
                width="240"
                height="240"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                rx="8"
                strokeDasharray="8,4"
              />
              
              {/* Inner character box */}
              <rect
                x="80"
                y="80"
                width="160"
                height="160"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                rx="4"
              />
              
              {/* Center cross lines */}
              <line 
                x1="160" y1="80" 
                x2="160" y2="240" 
                stroke="currentColor" 
                strokeWidth="1" 
                strokeDasharray="3,3" 
              />
              <line 
                x1="80" y1="160" 
                x2="240" y2="160" 
                stroke="currentColor" 
                strokeWidth="1" 
                strokeDasharray="3,3" 
              />
              
              {/* Extended grid lines */}
              <line x1="0" y1="160" x2="80" y2="160" stroke="currentColor" strokeWidth="1" strokeDasharray="2,4" opacity="0.5" />
              <line x1="240" y1="160" x2="320" y2="160" stroke="currentColor" strokeWidth="1" strokeDasharray="2,4" opacity="0.5" />
              <line x1="160" y1="0" x2="160" y2="80" stroke="currentColor" strokeWidth="1" strokeDasharray="2,4" opacity="0.5" />
              <line x1="160" y1="240" x2="160" y2="320" stroke="currentColor" strokeWidth="1" strokeDasharray="2,4" opacity="0.5" />
              
              {/* Center alignment guides */}
              {alignmentMode === 'center' && (
                <>
                  <circle cx="160" cy="160" r="6" fill="currentColor" />
                  <circle cx="160" cy="160" r="40" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="2,2" opacity="0.7" />
                  <circle cx="160" cy="160" r="80" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="2,2" opacity="0.4" />
                </>
              )}
              
              {/* Frame alignment guides */}
              {alignmentMode === 'frame' && (
                <>
                  <rect x="100" y="100" width="120" height="120" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="2,2" opacity="0.7" />
                  <rect x="120" y="120" width="80" height="80" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="2,2" opacity="0.5" />
                </>
              )}
              
              {/* Auto mode indicator */}
              {alignmentMode === 'auto' && (
                <>
                  <circle cx="160" cy="160" r="4" fill="currentColor" />
                  <circle cx="160" cy="160" r="20" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="1,1" />
                </>
              )}
            </svg>
          </div>

          {/* Corner markers for paper alignment */}
          <div className="absolute inset-6">
            {/* Top-left corner */}
            <div className="absolute top-0 left-0 w-8 h-8">
              <div className="w-6 h-1 bg-white/60 absolute top-0 left-0"></div>
              <div className="w-1 h-6 bg-white/60 absolute top-0 left-0"></div>
            </div>
            {/* Top-right corner */}
            <div className="absolute top-0 right-0 w-8 h-8">
              <div className="w-6 h-1 bg-white/60 absolute top-0 right-0"></div>
              <div className="w-1 h-6 bg-white/60 absolute top-0 right-0"></div>
            </div>
            {/* Bottom-left corner */}
            <div className="absolute bottom-0 left-0 w-8 h-8">
              <div className="w-6 h-1 bg-white/60 absolute bottom-0 left-0"></div>
              <div className="w-1 h-6 bg-white/60 absolute bottom-0 left-0"></div>
            </div>
            {/* Bottom-right corner */}
            <div className="absolute bottom-0 right-0 w-8 h-8">
              <div className="w-6 h-1 bg-white/60 absolute bottom-0 right-0"></div>
              <div className="w-1 h-6 bg-white/60 absolute bottom-0 right-0"></div>
            </div>
          </div>

          {/* Reference character */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-white/30 text-center">
              <div className="text-7xl font-serif mb-2 leading-none">中</div>
              <p className="text-sm">가이드에 맞춰 글자를 작성하세요</p>
            </div>
          </div>
        </div>

        {/* Help Tip */}
        {showTip && (
          <div className="absolute top-24 left-4 right-4">
            <Card className="bg-black/80 border-white/20">
              <CardContent className="p-3">
                <div className="flex items-start space-x-2">
                  <HelpCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                  <div className="text-white text-sm">
                    <p>가이드 테두리에 용지를 맞춰주세요</p>
                  </div>
                  <Button
                    onClick={() => setShowTip(false)}
                    variant="ghost"
                    size="sm"
                    className="text-white/60 hover:text-white p-0 h-auto ml-auto"
                  >
                    ✕
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Guide Opacity Control */}
      <div className="absolute top-24 left-4 right-4 z-10">
        <div className="bg-black/50 rounded-lg p-3 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white text-sm font-medium">가이드 투명도</span>
            <Badge variant="secondary" className="text-xs">
              {guideOpacity[0]}%
            </Badge>
          </div>
          <Slider
            value={guideOpacity}
            onValueChange={setGuideOpacity}
            max={100}
            step={10}
            className="w-full"
          />
        </div>
      </div>

      {/* Alignment Mode Selector */}
      <div className="absolute top-40 left-4 right-4 z-10">
        <div className="bg-black/50 rounded-lg p-3 backdrop-blur-sm">
          <p className="text-white text-sm font-medium mb-3">정렬 모드</p>
          <div className="flex space-x-2">
            {alignmentModes.map((mode) => (
              <button
                key={mode.id}
                onClick={() => setAlignmentMode(mode.id)}
                className={cn(
                  "flex-1 p-2 rounded-lg text-xs transition-colors",
                  alignmentMode === mode.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-white/20 text-white hover:bg-white/30"
                )}
              >
                <div className="font-medium">{mode.label}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 z-10 p-6 pb-8 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex items-center justify-between">
          {/* Retake */}
          <Button
            variant="ghost"
            size="lg"
            className="text-white hover:bg-white/20 flex flex-col items-center space-y-1"
          >
            <RotateCcw className="h-6 w-6" />
            <span className="text-xs">재촬영</span>
          </Button>

          {/* Shutter */}
          <button
            onClick={onCapture}
            className="w-16 h-16 rounded-full bg-white border-4 border-white shadow-lg hover:scale-105 transition-transform active:scale-95"
          >
            <div className="w-full h-full rounded-full bg-red-500" />
          </button>

          {/* Gallery */}
          <Button
            variant="ghost"
            size="lg"
            className="text-white hover:bg-white/20 flex flex-col items-center space-y-1"
          >
            <ImageIcon className="h-6 w-6" />
            <span className="text-xs">갤러리</span>
          </Button>
        </div>
      </div>
    </div>
  );
}