import { useState } from 'react';
import { Calendar, TrendingUp, Award, Clock, Filter, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { cn } from './ui/utils';

const historyData = {
  stats: {
    totalPractices: 127,
    averageScore: 78.5,
    bestScore: 94,
    streakDays: 12,
    totalCharacters: 45
  },
  recentPractices: [
    { id: 1, character: '中', score: 76.2, date: '2024-01-15', time: '14:30', difficulty: '초급', improvements: '+8점' },
    { id: 2, character: '書', score: 84.1, date: '2024-01-15', time: '14:15', difficulty: '고급', improvements: '+12점' },
    { id: 3, character: '道', score: 68.5, date: '2024-01-14', time: '19:20', difficulty: '중급', improvements: '-3점' },
    { id: 4, character: '法', score: 91.2, date: '2024-01-14', time: '19:05', difficulty: '고급', improvements: '+15점' },
    { id: 5, character: '心', score: 82.7, date: '2024-01-13', time: '16:45', difficulty: '초급', improvements: '+5점' },
    { id: 6, character: '和', score: 75.3, date: '2024-01-13', time: '16:30', difficulty: '중급', improvements: '+2점' },
  ],
  weeklyProgress: [
    { day: '월', score: 75, practices: 3 },
    { day: '화', score: 78, practices: 4 },
    { day: '수', score: 82, practices: 2 },
    { day: '목', score: 79, practices: 5 },
    { day: '금', score: 85, practices: 3 },
    { day: '토', score: 88, practices: 4 },
    { day: '일', score: 84, practices: 3 },
  ],
  achievements: [
    { id: 1, title: '첫 연습', description: '첫 글자 연습 완료', icon: '🎯', unlocked: true, date: '2024-01-10' },
    { id: 2, title: '연속 학습자', description: '7일 연속 연습 달성', icon: '🔥', unlocked: true, date: '2024-01-12' },
    { id: 3, title: '정확도 마스터', description: '90점 이상 5회 달성', icon: '🎖️', unlocked: true, date: '2024-01-14' },
    { id: 4, title: '서예 입문자', description: '20개 글자 연습 완료', icon: '✍️', unlocked: true, date: '2024-01-13' },
    { id: 5, title: '완벽주의자', description: '95점 이상 달성', icon: '💎', unlocked: false, progress: 85 },
    { id: 6, title: '한 달 챌린지', description: '30일 연속 연습', icon: '👑', unlocked: false, progress: 40 },
  ]
};

export function HistoryScreen() {
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [activeTab, setActiveTab] = useState('recent');

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-accent-positive';
    if (score >= 70) return 'text-accent-warning';
    return 'text-accent-error';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-accent-positive';
    if (score >= 70) return 'bg-accent-warning';
    return 'bg-accent-error';
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
    <div className="flex-1 bg-background pb-4 overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-16 pb-6 bg-background">
        <h1 className="text-2xl font-bold text-ink-strong mb-6">학습 히스토리</h1>
        
        {/* Period Filter */}
        <div className="flex space-x-2 mb-4">
          {[
            { id: 'week', label: '이번 주' },
            { id: 'month', label: '이번 달' },
            { id: 'all', label: '전체' }
          ].map((period) => (
            <Button
              key={period.id}
              variant={selectedPeriod === period.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedPeriod(period.id)}
              className="text-xs"
            >
              {period.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="px-4">
        {/* Stats Overview */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <Card className="border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-ink-strong mb-1">
                {historyData.stats.totalPractices}
              </div>
              <div className="text-xs text-muted-foreground flex items-center justify-center">
                <Clock className="h-3 w-3 mr-1" />
                총 연습 횟수
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-accent-warning mb-1">
                {historyData.stats.averageScore}
              </div>
              <div className="text-xs text-muted-foreground flex items-center justify-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                평균 점수
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-accent-positive mb-1">
                {historyData.stats.bestScore}
              </div>
              <div className="text-xs text-muted-foreground flex items-center justify-center">
                <Award className="h-3 w-3 mr-1" />
                최고 점수
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-primary mb-1">
                {historyData.stats.streakDays}
              </div>
              <div className="text-xs text-muted-foreground flex items-center justify-center">
                <Calendar className="h-3 w-3 mr-1" />
                연속 학습일
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="recent">최근 기록</TabsTrigger>
            <TabsTrigger value="progress">주간 진행도</TabsTrigger>
            <TabsTrigger value="achievements">성과</TabsTrigger>
          </TabsList>

          {/* Recent Practices */}
          <TabsContent value="recent" className="space-y-3">
            {historyData.recentPractices.map((practice) => (
              <Card key={practice.id} className="border-0 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl font-serif">{practice.character}</div>
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={cn("font-bold", getScoreColor(practice.score))}>
                            {practice.score}점
                          </span>
                          <Badge 
                            variant={practice.improvements.startsWith('+') ? "default" : "secondary"}
                            className="text-xs"
                          >
                            {practice.improvements}
                          </Badge>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {practice.date} • {practice.time}
                        </div>
                      </div>
                    </div>
                    <Badge 
                      className={cn(
                        "text-xs text-white",
                        getDifficultyColor(practice.difficulty)
                      )}
                    >
                      {practice.difficulty}
                    </Badge>
                  </div>
                  <Progress value={practice.score} className="h-2" />
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Weekly Progress */}
          <TabsContent value="progress" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>주간 평균 점수</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {historyData.weeklyProgress.map((day) => (
                    <div key={day.day} className="flex items-center space-x-4">
                      <div className="w-8 text-sm font-medium">{day.day}</div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">{day.score}점</span>
                          <span className="text-xs text-muted-foreground">
                            {day.practices}회 연습
                          </span>
                        </div>
                        <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className={cn(
                              "h-full rounded-full transition-all",
                              getScoreBg(day.score)
                            )}
                            style={{ width: `${day.score}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Achievements */}
          <TabsContent value="achievements" className="space-y-3">
            {historyData.achievements.map((achievement) => (
              <Card 
                key={achievement.id} 
                className={cn(
                  "border-0 shadow-sm",
                  achievement.unlocked ? "bg-gradient-to-r from-primary/5 to-primary/10" : "opacity-60"
                )}
              >
                <CardContent className="p-4">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-medium text-ink-strong">{achievement.title}</h3>
                        {achievement.unlocked && (
                          <Badge variant="outline" className="text-xs text-accent-positive border-accent-positive">
                            달성
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {achievement.description}
                      </p>
                      {achievement.unlocked ? (
                        <p className="text-xs text-muted-foreground">
                          달성일: {achievement.date}
                        </p>
                      ) : (
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span>진행도</span>
                            <span>{achievement.progress}%</span>
                          </div>
                          <Progress value={achievement.progress} className="h-2" />
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}