import { useState } from 'react';
import { Search, Filter, Book, User, Star } from 'lucide-react';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { cn } from './ui/utils';

const scriptTypes = [
  { id: 'seal', name: '전서', description: '篆書' },
  { id: 'regular', name: '해서', description: '楷書' },
  { id: 'running', name: '행서', description: '行書' },
  { id: 'cursive', name: '초서', description: '草書' },
  { id: 'clerical', name: '예서', description: '隸書' }
];

const calligraphyBooks = {
  seal: [
    { id: 1, title: '천자문', author: '주흥사', dynasty: '북주', difficulty: '초급', characters: 1000, favorite: false },
    { id: 2, title: '석고문', author: '이사', dynasty: '진', difficulty: '중급', characters: 800, favorite: true },
    { id: 3, title: '태산각석', author: '이사', dynasty: '진', difficulty: '고급', characters: 222, favorite: false }
  ],
  regular: [
    { id: 4, title: '구성궁예천비', author: '구양순', dynasty: '당', difficulty: '중급', characters: 1200, favorite: true },
    { id: 5, title: '안씨가묘비', author: '안진경', dynasty: '당', difficulty: '고급', characters: 1500, favorite: false },
    { id: 6, title: '다보탑비', author: '안진경', dynasty: '당', difficulty: '중급', characters: 900, favorite: true },
    { id: 7, title: '황보탄비', author: '구양순', dynasty: '당', difficulty: '고급', characters: 1100, favorite: false }
  ],
  running: [
    { id: 8, title: '난정서', author: '왕희지', dynasty: '동진', difficulty: '고급', characters: 324, favorite: true },
    { id: 9, title: '성교서', author: '왕희지', dynasty: '동진', difficulty: '중급', characters: 461, favorite: false },
    { id: 10, title: '조맹부첩', author: '조맹부', dynasty: '원', difficulty: '중급', characters: 600, favorite: true }
  ],
  cursive: [
    { id: 11, title: '십칠첩', author: '왕희지', dynasty: '동진', difficulty: '고급', characters: 280, favorite: false },
    { id: 12, title: '회소첩', author: '회소', dynasty: '당', difficulty: '중급', characters: 350, favorite: true },
    { id: 13, title: '자서첩', author: '장욱', dynasty: '당', difficulty: '고급', characters: 420, favorite: false }
  ],
  clerical: [
    { id: 14, title: '조전비', author: '미상', dynasty: '한', difficulty: '중급', characters: 1800, favorite: true },
    { id: 15, title: '예기비', author: '미상', dynasty: '한', difficulty: '고급', characters: 1200, favorite: false },
    { id: 16, title: '장천비', author: '미상', dynasty: '한', difficulty: '초급', characters: 800, favorite: false }
  ]
};

const authors = [
  { id: 'wangxizhi', name: '왕희지', period: '동진' },
  { id: 'yanzhengqing', name: '안진경', period: '당' },
  { id: 'ouyangxun', name: '구양순', period: '당' },
  { id: 'zhaomengfu', name: '조맹부', period: '원' },
  { id: 'lisi', name: '이사', period: '진' }
];

interface LibraryScreenProps {
  onBack?: () => void;
  onCharacterSelect?: (character: string) => void;
}

export function LibraryScreen({ onBack, onCharacterSelect }: LibraryScreenProps) {
  const [activeScript, setActiveScript] = useState('regular');
  const [selectedAuthor, setSelectedAuthor] = useState<string | null>(null);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredBooks = calligraphyBooks[activeScript as keyof typeof calligraphyBooks]?.filter(book => {
    const matchesAuthor = !selectedAuthor || book.author.includes(selectedAuthor);
    const matchesFavorite = !showFavoritesOnly || book.favorite;
    const matchesSearch = !searchQuery || book.title.includes(searchQuery) || book.author.includes(searchQuery);
    return matchesAuthor && matchesFavorite && matchesSearch;
  }) || [];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '초급': return 'bg-accent-positive';
      case '중급': return 'bg-accent-warning';
      case '고급': return 'bg-accent-error';
      default: return 'bg-muted';
    }
  };

  const handleCharacterClick = (character: string) => {
    if (onCharacterSelect) {
      onCharacterSelect(character);
    }
  };

  return (
    <div className="flex-1 bg-background pb-4 overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-16 pb-6 bg-background">
        <h1 className="text-2xl font-bold text-ink-strong mb-6">법첩 라이브러리</h1>
        
        {/* Search Bar */}
        <div className="relative mb-4">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            placeholder="법첩이나 작가를 검색하세요"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 h-12 rounded-xl border-0 bg-muted text-base"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-3 mb-4">
          <Button
            variant={showFavoritesOnly ? "default" : "outline"}
            size="sm"
            onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
            className="flex items-center space-x-2"
          >
            <Star className={cn("h-4 w-4", showFavoritesOnly && "fill-current")} />
            <span>즐겨찾기</span>
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            className="flex items-center space-x-2"
          >
            <Filter className="h-4 w-4" />
            <span>필터</span>
          </Button>
        </div>
      </div>

      {/* Script Type Tabs */}
      <div className="px-4">
        <Tabs value={activeScript} onValueChange={setActiveScript} className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-6">
            {scriptTypes.map((script) => (
              <TabsTrigger
                key={script.id}
                value={script.id}
                className="flex flex-col items-center p-2 text-xs"
              >
                <span className="font-medium">{script.name}</span>
                <span className="text-xs text-muted-foreground">{script.description}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Author Filter Tags */}
          <div className="mb-4">
            <p className="text-sm font-medium text-ink-strong mb-3">작가별 필터</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedAuthor === null ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedAuthor(null)}
                className="text-xs"
              >
                전체
              </Button>
              {authors.map((author) => (
                <Button
                  key={author.id}
                  variant={selectedAuthor === author.name ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedAuthor(selectedAuthor === author.name ? null : author.name)}
                  className="text-xs flex items-center space-x-1"
                >
                  <User className="h-3 w-3" />
                  <span>{author.name}</span>
                  <span className="text-muted-foreground">({author.period})</span>
                </Button>
              ))}
            </div>
          </div>

          {/* Book List */}
          <TabsContent value={activeScript} className="space-y-4">
            {filteredBooks.length === 0 ? (
              <div className="text-center py-12">
                <Book className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-medium text-ink-strong mb-2">검색 결과가 없습니다</p>
                <p className="text-sm text-muted-foreground">다른 조건으로 검색해보세요</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredBooks.map((book) => (
                  <Card key={book.id} className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-bold text-ink-strong text-lg">{book.title}</h3>
                            {book.favorite && (
                              <Star className="h-4 w-4 text-accent-warning fill-current" />
                            )}
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                            <span className="flex items-center space-x-1">
                              <User className="h-3 w-3" />
                              <span>{book.author}</span>
                            </span>
                            <span>{book.dynasty}</span>
                            <span>{book.characters}자</span>
                          </div>
                        </div>
                        <Badge
                          className={cn(
                            "text-xs text-white",
                            getDifficultyColor(book.difficulty)
                          )}
                        >
                          {book.difficulty}
                        </Badge>
                      </div>
                      
                      {/* Sample Characters */}
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex justify-center space-x-4 text-2xl font-serif text-ink-strong">
                          <span 
                            className="cursor-pointer hover:text-primary transition-colors"
                            onClick={() => handleCharacterClick('永')}
                          >
                            永
                          </span>
                          <span 
                            className="cursor-pointer hover:text-primary transition-colors"
                            onClick={() => handleCharacterClick('和')}
                          >
                            和
                          </span>
                          <span 
                            className="cursor-pointer hover:text-primary transition-colors"
                            onClick={() => handleCharacterClick('雅')}
                          >
                            雅
                          </span>
                          <span 
                            className="cursor-pointer hover:text-primary transition-colors"
                            onClick={() => handleCharacterClick('正')}
                          >
                            正
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}