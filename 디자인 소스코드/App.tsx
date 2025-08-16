import { useState } from 'react';
import { Home, Library, Camera, History, Settings } from 'lucide-react';
import { TabNavigation } from './components/TabNavigation';
import { HomeScreen } from './components/HomeScreen';
import { CameraScreen } from './components/CameraScreen';
import { EvaluationScreen } from './components/EvaluationScreen';
import { LibraryScreen } from './components/LibraryScreen';
import { CharacterDetailScreen } from './components/CharacterDetailScreen';
import { HistoryScreen } from './components/HistoryScreen';
import { SettingsScreen } from './components/SettingsScreen';
import { PhoneFrame } from './components/PhoneFrame';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [currentScreen, setCurrentScreen] = useState('home');
  const [selectedCharacter, setSelectedCharacter] = useState<string>('中');

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setCurrentScreen(tab);
  };

  const navigateToCamera = () => {
    setCurrentScreen('camera');
    setActiveTab('camera');
  };

  const navigateToEvaluation = () => {
    setCurrentScreen('evaluation');
  };

  const navigateToCharacterDetail = (character: string) => {
    setSelectedCharacter(character);
    setCurrentScreen('characterDetail');
  };

  const navigateBack = () => {
    setCurrentScreen('home');
    setActiveTab('home');
  };

  const navigateBackToLibrary = () => {
    setCurrentScreen('library');
    setActiveTab('library');
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'camera':
        return (
          <CameraScreen
            onBack={navigateBack}
            onCapture={navigateToEvaluation}
          />
        );
      case 'evaluation':
        return (
          <EvaluationScreen
            onBack={navigateBack}
            onRetry={navigateToCamera}
            onSave={navigateBack}
          />
        );
      case 'library':
        return (
          <LibraryScreen 
            onCharacterSelect={navigateToCharacterDetail}
          />
        );
      case 'characterDetail':
        return (
          <CharacterDetailScreen
            character={selectedCharacter}
            onBack={navigateBackToLibrary}
            onNavigateToCamera={navigateToCamera}
          />
        );
      case 'history':
        return (
          <HistoryScreen />
        );
      case 'settings':
        return (
          <SettingsScreen />
        );
      default:
        return (
          <HomeScreen
            onNavigateToCamera={navigateToCamera}
            onNavigateToLibrary={() => handleTabChange('library')}
            onCharacterSelect={navigateToCharacterDetail}
          />
        );
    }
  };

  const appContent = (
    <div className="h-full flex flex-col bg-background font-sans relative">
      <div className="flex-1 overflow-hidden">
        {renderScreen()}
      </div>
      {currentScreen !== 'camera' && currentScreen !== 'evaluation' && currentScreen !== 'characterDetail' && (
        <div className="relative z-10 bg-background border-t border-border">
          <div className="flex items-center justify-around px-2 py-2 pb-4">
            {[
              { id: 'home', label: '홈', icon: 'Home' },
              { id: 'library', label: '라이브러리', icon: 'Library' },
              { id: 'camera', label: '촬영', icon: 'Camera', isPrimary: true },
              { id: 'history', label: '히스토리', icon: 'History' },
              { id: 'settings', label: '설정', icon: 'Settings' },
            ].map(({ id, label, icon, isPrimary }) => (
              <button
                key={id}
                onClick={() => handleTabChange(id)}
                className={`flex flex-col items-center justify-center min-h-[48px] px-3 py-2 rounded-lg transition-colors hover:bg-muted active:scale-95 ${
                  isPrimary 
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90' 
                    : activeTab === id 
                      ? 'text-primary bg-primary/10' 
                      : 'text-muted-foreground'
                }`}
              >
                <div className={`mb-1 ${isPrimary ? 'w-6 h-6' : 'w-5 h-5'}`}>
                  {icon === 'Home' && <Home className="w-full h-full" />}
                  {icon === 'Library' && <Library className="w-full h-full" />}
                  {icon === 'Camera' && <Camera className="w-full h-full" />}
                  {icon === 'History' && <History className="w-full h-full" />}
                  {icon === 'Settings' && <Settings className="w-full h-full" />}
                </div>
                <span className={`text-xs leading-none ${isPrimary ? 'font-medium' : ''}`}>
                  {label}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <PhoneFrame>
      {appContent}
    </PhoneFrame>
  );
}