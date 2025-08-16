import { Search, ChevronRight, Star, Clock } from 'lucide-react';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';

const recentEvaluations = [
  { id: 1, character: '中', score: 76, date: '2024-01-15', level: 'intermediate' },
  { id: 2, character: '書', score: 84, date: '2024-01-14', level: 'advanced' },
  { id: 3, character: '道', score: 68, date: '2024-01-13', level: 'beginner' },
  { id: 4, character: '法', score: 91, date: '2024-01-12', level: 'advanced' },
];

const favoriteCharacters = [
  { id: 1, character: '愛', category: '상용한자', difficulty: '고급' },
  { id: 2, character: '和', category: '기초한자', difficulty: '초급' },
  { id: 3, character: '美', category: '상용한자', difficulty: '중급' },
  { id: 4, character: '心', category: '기초한자', difficulty: '초급' },
];

interface HomeScreenProps {
  onNavigateToCamera: () => void;
  onNavigateToLibrary: () => void;
  onCharacterSelect?: (character: string) => void;
}

export function HomeScreen({ onNavigateToCamera, onNavigateToLibrary, onCharacterSelect }: HomeScreenProps) {
  return (
    <div className="flex-1 bg-background pb-4 overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-16 pb-6 bg-background">
        <h1 className="text-2xl font-bold text-ink-strong mb-6">붓글씨 결구 평가</h1>
        
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="한자를 검색하세요"
            className="pl-12 h-12 rounded-xl border-0 bg-muted text-base"
          />
        </div>
      </div>

      <div className="px-4 space-y-6">
        {/* Quick Action */}
        <Card className="border-2 border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-ink-strong">오늘의 연습</h3>
                <p className="text-sm text-muted-foreground mt-1">가이드를 보며 글자를 써보세요</p>
              </div>
              <div className="text-4xl font-serif">中</div>
            </div>
            <button
              onClick={onNavigateToCamera}
              className="w-full bg-primary text-primary-foreground py-3 rounded-xl font-medium hover:bg-primary/90 transition-colors"
            >
              가이드 켜고 촬영하기
            </button>
          </CardContent>
        </Card>

        {/* Recent Evaluations */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-ink-strong">최근 평가</h2>
            <button
              onClick={() => {}}
              className="flex items-center text-sm text-primary font-medium"
            >
              더보기
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {recentEvaluations.map((item) => (
              <Card 
                key={item.id} 
                className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onCharacterSelect && onCharacterSelect(item.character)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-2xl font-serif text-ink-strong">{item.character}</div>
                    <Badge 
                      variant={item.score >= 80 ? "default" : item.score >= 60 ? "secondary" : "outline"}
                      className="text-xs"
                    >
                      {item.score}점
                    </Badge>
                  </div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Clock className="h-3 w-3 mr-1" />
                    {item.date}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Favorite Characters */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-ink-strong">즐겨찾기</h2>
            <button
              onClick={onNavigateToLibrary}
              className="flex items-center text-sm text-primary font-medium"
            >
              더보기
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {favoriteCharacters.map((item) => (
              <Card 
                key={item.id} 
                className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onCharacterSelect && onCharacterSelect(item.character)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-2xl font-serif text-ink-strong">{item.character}</div>
                    <Star className="h-4 w-4 text-accent-warning fill-current" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">{item.category}</p>
                    <Badge variant="outline" className="text-xs">
                      {item.difficulty}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}