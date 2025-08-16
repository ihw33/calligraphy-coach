import { useState } from 'react';
import { 
  User, 
  Bell, 
  Camera, 
  Palette, 
  Globe, 
  HelpCircle, 
  Info, 
  LogOut, 
  ChevronRight,
  Moon,
  Sun,
  Volume2
} from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Switch } from './ui/switch';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { cn } from './ui/utils';

const settingsData = {
  user: {
    name: '김서예',
    email: 'kim.seoye@email.com',
    level: '중급',
    totalScore: 8750,
    practiceCount: 127
  },
  notifications: {
    dailyReminder: true,
    practiceGoal: true,
    achievements: false,
    weeklyReport: true
  },
  camera: {
    guideOpacity: 70,
    autoFocus: true,
    flashlight: false,
    soundFeedback: true
  },
  appearance: {
    darkMode: false,
    language: '한국어',
    fontSize: '보통'
  }
};

export function SettingsScreen() {
  const [notifications, setNotifications] = useState(settingsData.notifications);
  const [camera, setCamera] = useState(settingsData.camera);
  const [appearance, setAppearance] = useState(settingsData.appearance);

  const updateNotification = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const updateCamera = (key: string, value: boolean) => {
    setCamera(prev => ({ ...prev, [key]: value }));
  };

  const updateAppearance = (key: string, value: boolean) => {
    setAppearance(prev => ({ ...prev, [key]: value }));
  };

  const SettingItem = ({ 
    icon, 
    title, 
    description, 
    action, 
    onClick 
  }: { 
    icon: React.ReactNode;
    title: string;
    description?: string;
    action?: React.ReactNode;
    onClick?: () => void;
  }) => (
    <div 
      className={cn(
        "flex items-center justify-between py-4",
        onClick && "cursor-pointer hover:bg-muted/50 px-4 -mx-4 rounded-lg transition-colors"
      )}
      onClick={onClick}
    >
      <div className="flex items-center space-x-3">
        <div className="text-muted-foreground">{icon}</div>
        <div>
          <p className="font-medium text-ink-strong">{title}</p>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {action}
    </div>
  );

  return (
    <div className="flex-1 bg-background pb-4 overflow-y-auto">
      {/* Header */}
      <div className="px-4 pt-16 pb-6 bg-background">
        <h1 className="text-2xl font-bold text-ink-strong mb-6">설정</h1>
      </div>

      <div className="px-4 space-y-6">
        {/* User Profile */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4 mb-4">
              <Avatar className="w-16 h-16">
                <AvatarImage src="" alt="프로필" />
                <AvatarFallback className="bg-primary text-primary-foreground text-lg">
                  김
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h2 className="text-lg font-bold text-ink-strong mb-1">
                  {settingsData.user.name}
                </h2>
                <p className="text-sm text-muted-foreground mb-2">
                  {settingsData.user.email}
                </p>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary" className="text-xs">
                    {settingsData.user.level}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {settingsData.user.practiceCount}회 연습
                  </span>
                </div>
              </div>
            </div>
            <Button variant="outline" className="w-full">
              프로필 편집
            </Button>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <h3 className="font-bold text-ink-strong mb-4 flex items-center space-x-2">
              <Bell className="h-5 w-5" />
              <span>알림</span>
            </h3>
            
            <div className="space-y-1">
              <SettingItem
                icon={<Bell className="h-5 w-5" />}
                title="일일 연습 알림"
                description="매일 정해진 시간에 연습 알림을 받습니다"
                action={
                  <Switch
                    checked={notifications.dailyReminder}
                    onCheckedChange={(value) => updateNotification('dailyReminder', value)}
                  />
                }
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<HelpCircle className="h-5 w-5" />}
                title="연습 목표 달성"
                description="목표 달성 시 알림을 받습니다"
                action={
                  <Switch
                    checked={notifications.practiceGoal}
                    onCheckedChange={(value) => updateNotification('practiceGoal', value)}
                  />
                }
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<User className="h-5 w-5" />}
                title="성과 및 업적"
                description="새로운 성과나 업적 달성 시 알림"
                action={
                  <Switch
                    checked={notifications.achievements}
                    onCheckedChange={(value) => updateNotification('achievements', value)}
                  />
                }
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<Info className="h-5 w-5" />}
                title="주간 리포트"
                description="매주 학습 진행 상황 요약 리포트"
                action={
                  <Switch
                    checked={notifications.weeklyReport}
                    onCheckedChange={(value) => updateNotification('weeklyReport', value)}
                  />
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Camera Settings */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <h3 className="font-bold text-ink-strong mb-4 flex items-center space-x-2">
              <Camera className="h-5 w-5" />
              <span>카메라</span>
            </h3>
            
            <div className="space-y-1">
              <SettingItem
                icon={<Camera className="h-5 w-5" />}
                title="자동 초점"
                description="촬영 시 자동으로 초점을 맞춥니다"
                action={
                  <Switch
                    checked={camera.autoFocus}
                    onCheckedChange={(value) => updateCamera('autoFocus', value)}
                  />
                }
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<Volume2 className="h-5 w-5" />}
                title="사운드 피드백"
                description="촬영 시 셔터음을 재생합니다"
                action={
                  <Switch
                    checked={camera.soundFeedback}
                    onCheckedChange={(value) => updateCamera('soundFeedback', value)}
                  />
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <h3 className="font-bold text-ink-strong mb-4 flex items-center space-x-2">
              <Palette className="h-5 w-5" />
              <span>화면 설정</span>
            </h3>
            
            <div className="space-y-1">
              <SettingItem
                icon={appearance.darkMode ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                title="다크 모드"
                description="어두운 테마로 변경합니다"
                action={
                  <Switch
                    checked={appearance.darkMode}
                    onCheckedChange={(value) => updateAppearance('darkMode', value)}
                  />
                }
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<Globe className="h-5 w-5" />}
                title="언어"
                description={appearance.language}
                action={<ChevronRight className="h-5 w-5 text-muted-foreground" />}
                onClick={() => {}}
              />
            </div>
          </CardContent>
        </Card>

        {/* Help & Support */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <h3 className="font-bold text-ink-strong mb-4 flex items-center space-x-2">
              <HelpCircle className="h-5 w-5" />
              <span>도움말 및 지원</span>
            </h3>
            
            <div className="space-y-1">
              <SettingItem
                icon={<HelpCircle className="h-5 w-5" />}
                title="사용 가이드"
                description="앱 사용법을 확인하세요"
                action={<ChevronRight className="h-5 w-5 text-muted-foreground" />}
                onClick={() => {}}
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<Info className="h-5 w-5" />}
                title="앱 정보"
                description="버전 1.0.0"
                action={<ChevronRight className="h-5 w-5 text-muted-foreground" />}
                onClick={() => {}}
              />
              <Separator className="my-2" />
              <SettingItem
                icon={<User className="h-5 w-5" />}
                title="문의하기"
                description="개발팀에 문의나 제안하기"
                action={<ChevronRight className="h-5 w-5 text-muted-foreground" />}
                onClick={() => {}}
              />
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="space-y-1">
              <SettingItem
                icon={<LogOut className="h-5 w-5 text-destructive" />}
                title="로그아웃"
                onClick={() => {}}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}