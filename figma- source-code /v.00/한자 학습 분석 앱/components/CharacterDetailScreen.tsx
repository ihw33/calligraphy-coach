import { useState } from 'react';
import { ArrowLeft, Volume2, Camera, Star, BookOpen, Eye } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { cn } from './ui/utils';

interface CharacterDetailScreenProps {
  character?: string;
  onBack: () => void;
  onNavigateToCamera: () => void;
}

const characterData = {
  '中': {
    character: '中',
    pronunciation: 'jung',
    meaning: '가운데, 중앙',
    strokeCount: 4,
    difficulty: '초급',
    category: '기초한자',
    description: '가운데를 뜻하는 글자로, 세로로 긋는 획이 사각형을 관통하는 모양입니다. 동양 철학에서 중용의 개념을 나타내는 중요한 글자입니다.',
    etymology: '고대 중국에서 깃발이 바람에 날리는 모습을 본떠서 만든 글자입니다. 깃발이 중앙에 서 있어 중앙, 가운데라는 뜻이 되었습니다.',
    examples: [
      { word: '중국', meaning: '중국' },
      { word: '중심', meaning: '중심' },
      { word: '중간', meaning: '중간' },
      { word: '중요', meaning: '중요' }
    ],
    strokeOrder: [
      '세로획을 가운데서 위에서 아래로',
      '가로획을 위에서 왼쪽에서 오른쪽으로',
      '가로획을 가운데서 왼쪽에서 오른쪽으로',
      '가로획을 아래서 왼쪽에서 오른쪽으로'
    ],
    scriptTypes: [
      { type: '해서', example: '中' },
      { type: '행서', example: '中' },
      { type: '초서', example: '中' }
    ]
  }
};

export function CharacterDetailScreen({ 
  character = '中', 
  onBack, 
  onNavigateToCamera 
}: CharacterDetailScreenProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  
  const charData = characterData[character as keyof typeof characterData] || characterData['中'];

  const handlePlayAudio = () => {
    setIsPlaying(true);
    // Mock audio playback
    setTimeout(() => setIsPlaying(false), 3000);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '초급': return 'bg-accent-positive';
      case '중급': return 'bg-accent-warning';
      case '고급': return 'bg-accent-error';
      default: return 'bg-muted';
    }
  };

  return (
    <div className="flex-1 bg-background pb-24">
      {/* Header */}
      <div className="flex items-center justify-between p-4 pt-16 border-b border-border">
        <Button onClick={onBack} variant="ghost" size="sm">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="font-bold">글자 상세</h1>
        <Button
          onClick={handlePlayAudio}
          variant="ghost" 
          size="sm"
          className={cn(
            "relative",
            isPlaying && "text-primary"
          )}
        >
          <Volume2 className={cn("h-5 w-5", isPlaying && "animate-pulse")} />
          {isPlaying && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full animate-ping"></div>
          )}
        </Button>
      </div>

      <div className="p-4 space-y-6">
        {/* Character Display */}
        <Card className="border-0 shadow-lg bg-gradient-to-br from-primary/5 to-primary/10">
          <CardContent className="p-8 text-center">
            <div className="text-8xl font-serif text-ink-strong mb-4 leading-none">
              {charData.character}
            </div>
            
            <div className="flex items-center justify-center space-x-4 mb-4">
              <Badge 
                className={cn(
                  "text-sm px-3 py-1 text-white",
                  getDifficultyColor(charData.difficulty)
                )}
              >
                {charData.difficulty}
              </Badge>
              <span className="text-lg font-medium text-ink-base">
                {charData.pronunciation}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsFavorite(!isFavorite)}
                className="p-1"
              >
                <Star className={cn(
                  "h-5 w-5",
                  isFavorite ? "text-accent-warning fill-current" : "text-muted-foreground"
                )} />
              </Button>
            </div>

            <p className="text-lg text-ink-base mb-4">{charData.meaning}</p>
            
            <div className="flex justify-center space-x-3">
              <Button 
                onClick={onNavigateToCamera}
                className="flex-1 max-w-xs"
              >
                <Camera className="h-4 w-4 mr-2" />
                연습하기
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Character Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <BookOpen className="h-5 w-5" />
              <span>글자 정보</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">획수</p>
                <p className="font-medium">{charData.strokeCount}획</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">분류</p>
                <p className="font-medium">{charData.category}</p>
              </div>
            </div>
            <Separator />
            <div>
              <p className="text-sm text-muted-foreground mb-2">설명</p>
              <p className="text-sm leading-relaxed">{charData.description}</p>
            </div>
          </CardContent>
        </Card>

        {/* Etymology */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">어원과 유래</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{charData.etymology}</p>
          </CardContent>
        </Card>

        {/* Stroke Order */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center space-x-2">
              <Eye className="h-5 w-5" />
              <span>획순</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {charData.strokeOrder.map((stroke, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-muted rounded-lg">
                <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-medium flex-shrink-0">
                  {index + 1}
                </div>
                <p className="text-sm">{stroke}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Usage Examples */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">활용 예시</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {charData.examples.map((example, index) => (
                <div key={index} className="p-3 bg-muted rounded-lg">
                  <p className="font-medium text-base mb-1">{example.word}</p>
                  <p className="text-sm text-muted-foreground">{example.meaning}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Script Types */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">서체별 모습</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex justify-around items-center">
              {charData.scriptTypes.map((script, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-serif mb-2">{script.example}</div>
                  <p className="text-sm text-muted-foreground">{script.type}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}