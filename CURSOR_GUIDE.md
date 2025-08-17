# 📚 Calligraphy Coach 프로젝트 가이드 (Cursor용)

## 🎯 프로젝트 정보
- **프로젝트명**: Calligraphy Coach (캘리그라피 코치)
- **설명**: AI 기반 한자/한글 서예 학습 앱
- **GitHub**: https://github.com/ihw33/calligraphy-coach
- **로컬 경로**: `/Users/m4_macbook/calligraphy-coach`

## 📁 프로젝트 구조
```
/calligraphy-coach
├── mobile/                 # React Native 앱 (아직 개발 전)
├── backend/               # FastAPI 서버 (main.py 있음)
├── ai_engine/             # Python AI 분석 엔진 (완성됨)
│   └── analysis/          # 25개 분석 모듈
├── figma-source-code/     # Figma 디자인 코드
├── 디자인 소스코드/        # FigmaMake가 만든 UI 컴포넌트
│   ├── App.tsx           # 메인 앱 파일
│   └── components/ui/    # UI 컴포넌트들
└── docs/                  # 프로젝트 문서

```

## 🎨 디자인 시스템
```javascript
const colors = {
  primary: '#1A1A1A',     // 먹색
  secondary: '#8B4513',   // 붓 손잡이색
  accent: '#DC143C',      // 인주색
  background: '#F5F5DC',  // 화선지색
}
```

## ✅ 완료된 작업
1. **AI 엔진**: 서예 분석 시스템 완성 (Python)
   - 중봉 상태 추적
   - 붓 압력/속도 분석
   - 획 평가 시스템

2. **백엔드**: FastAPI 기본 구조
   - `/analyze/upload` - 이미지 분석 API
   - `/characters` - 학습 가능한 한자 목록
   - `/user/progress` - 사용자 진도

3. **UI 컴포넌트**: FigmaMake로 생성된 컴포넌트들
   - shadcn/ui 기반
   - TypeScript + Tailwind CSS

## 🚀 다음 작업 (mobile 앱 개발)

### 1. 네비게이션 설정
```typescript
// React Navigation 설치 필요
npm install @react-navigation/native @react-navigation/bottom-tabs
```

### 2. 주요 화면 생성
- `HomeScreen.tsx` - 홈 화면 (서예 교실)
- `LearningScreen.tsx` - 학습 화면
- `CameraScreen.tsx` - 카메라 촬영
- `AnalysisScreen.tsx` - AI 분석 결과
- `ProgressScreen.tsx` - 진도 확인

### 3. 백엔드 연동
```typescript
const API_URL = 'http://localhost:8000';

// 이미지 업로드 및 분석
const analyzeImage = async (imageUri: string) => {
  const formData = new FormData();
  formData.append('user_image', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  });
  
  const response = await fetch(`${API_URL}/analyze/upload`, {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
};
```

## 💡 ChatGPT-5에게 요청할 예시

### 홈 화면 생성
```
Create HomeScreen.tsx for Calligraphy Coach app:
- Use existing components from 디자인 소스코드/components/ui
- Korean title "서예 교실"
- 4 menu cards: 학습하기, 연습하기, 카메라, 진도확인
- Use our color theme (#1A1A1A, #F5F5DC, #DC143C)
- Add navigation to other screens
```

### 카메라 기능
```
Create camera functionality:
- Use react-native-image-picker
- Allow photo capture and gallery selection
- Send to backend API for analysis
- Show loading state while processing
```

### AI 결과 화면
```
Create analysis result screen:
- Display score and grade (A-F)
- Show visual feedback overlay
- Korean feedback messages
- Improvement suggestions
- Save to progress history
```

## 🔧 개발 명령어

### 모바일 앱 실행
```bash
cd mobile
npm install  # 처음 한 번만
npm start    # Metro 번들러 시작

# 새 터미널에서
npm run ios      # iOS 시뮬레이터
npm run android  # Android 에뮬레이터
```

### 백엔드 서버 실행
```bash
cd backend
python main.py  # 또는 uvicorn main:app --reload
```

## 📱 테스트 계정
- 아직 없음 (로그인 기능 추가 예정)

## 🔗 참고 자료
- React Native: https://reactnative.dev
- FastAPI: https://fastapi.tiangolo.com
- 프로젝트 요약: `/docs/PROJECT_SUMMARY.md`

---

**시작하기**: Cursor AI Chat (`Cmd + L`)에서 위 예시 프롬프트를 사용하여 개발을 시작하세요!