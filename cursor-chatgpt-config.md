# Cursor + ChatGPT-5 연동 가이드

## 🚀 빠른 설정

### 1️⃣ Cursor Settings 열기
```
Cmd + , → Features → AI
```

### 2️⃣ Model Provider 설정
1. **Model**: `GPT-4` 또는 `Custom`
2. **Provider**: `OpenAI`
3. **API Key**: OpenAI API 키 입력

### 3️⃣ Custom Model 추가 (ChatGPT-5 시뮬레이션)
Settings.json에 추가:
```json
{
  "cursor.ai.customModels": [
    {
      "name": "ChatGPT-5",
      "provider": "openai",
      "model": "gpt-4-turbo-preview",
      "temperature": 0.8,
      "maxTokens": 4000
    }
  ]
}
```

### 4️⃣ Cursor Chat에서 사용
- `Cmd + L`: AI Chat 열기
- `@ChatGPT-5` 또는 모델 선택 드롭다운에서 선택

## 💡 유용한 프롬프트

### React Native 컴포넌트 생성
```
@ChatGPT-5 Create a React Native component for the Calligraphy Coach home screen with:
- Header with title "서예 교실"
- 4 menu buttons (학습하기, 연습하기, 카메라, 진도)
- Bottom navigation
- Use TypeScript and styled-components
```

### Figma 디자인을 코드로 변환
```
@ChatGPT-5 Convert this Figma design to React Native:
- Frame: 390x844 (iPhone 14)
- Background: #F5F5DC
- Header: #1A1A1A
- Generate responsive code with proper styling
```

### AI 엔진 연동
```
@ChatGPT-5 Create an API integration for:
- Image upload to FastAPI backend
- Call Python AI analysis engine
- Display results in React Native
- Handle loading states and errors
```

## 🔗 API 키 설정

### 방법 1: 환경 변수
```bash
export OPENAI_API_KEY="sk-..."
```

### 방법 2: Cursor 설정
1. Settings → AI → OpenAI
2. API Key 입력란에 직접 입력

### 방법 3: .env 파일
```
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
```

## 📁 프로젝트 구조와 연동

ChatGPT-5에게 프로젝트 컨텍스트 제공:
```
Our project structure:
/calligraphy-coach
  /mobile (React Native)
  /backend (FastAPI)
  /ai_engine (Python AI)
  /figma-source-code (Designs)
```

## 🎯 작업 흐름

1. **디자인 확인**: Figma에서 디자인 확인
2. **코드 생성**: ChatGPT-5로 컴포넌트 생성
3. **테스트**: React Native 앱에서 확인
4. **수정**: ChatGPT-5와 함께 개선

## ⚡ 단축키

- `Cmd + K`: Inline AI (코드 수정)
- `Cmd + L`: AI Chat (대화)
- `Cmd + Shift + L`: AI Panel
- `Tab`: AI 제안 수락

## 🔧 트러블슈팅

### API 키 오류
- OpenAI 대시보드에서 키 확인
- 사용량 한도 확인
- 결제 정보 확인

### 모델 선택 안됨
- Cursor 재시작
- Settings 재설정
- 캐시 클리어: `Cmd + Shift + P` → "Clear Cache"