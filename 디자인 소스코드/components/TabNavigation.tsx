import { Home, Library, Camera, History, Settings } from 'lucide-react';
import { cn } from './ui/utils';

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'home', label: '홈', icon: Home },
  { id: 'library', label: '라이브러리', icon: Library },
  { id: 'camera', label: '촬영', icon: Camera, isPrimary: true },
  { id: 'history', label: '히스토리', icon: History },
  { id: 'settings', label: '설정', icon: Settings },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-background border-t border-border safe-area-pb">
      <div className="flex items-center justify-around px-2 py-2">
        {tabs.map(({ id, label, icon: Icon, isPrimary }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={cn(
              "flex flex-col items-center justify-center min-h-[48px] px-3 py-2 rounded-lg transition-colors",
              "hover:bg-muted active:scale-95",
              isPrimary && "bg-primary text-primary-foreground hover:bg-primary/90",
              activeTab === id && !isPrimary && "text-primary bg-primary/10",
              activeTab !== id && !isPrimary && "text-muted-foreground"
            )}
          >
            <Icon className={cn(
              "mb-1",
              isPrimary ? "h-6 w-6" : "h-5 w-5"
            )} />
            <span className={cn(
              "text-xs leading-none",
              isPrimary && "font-medium"
            )}>
              {label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}