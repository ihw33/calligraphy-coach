# Calligraphy Coach - 프로젝트 구조

## 📁 디렉토리 구조

```
calligraphy-coach/
│
├── 📱 frontend/              # 프론트엔드 (React Native / Flutter)
│   ├── mobile/              # 모바일 앱 (iOS/Android)
│   └── web/                 # 웹앱 (React)
│
├── 🔧 backend/               # 백엔드 서버
│   ├── api/                 # API 엔드포인트
│   ├── models/              # 데이터 모델
│   └── services/            # 비즈니스 로직
│
├── 🧠 ai_engine/             # AI 분석 엔진
│   ├── analysis/            # 서예 분석 모듈
│   ├── evaluation/          # 평가 시스템
│   └── recommendation/      # 개선 추천 시스템
│
├── 🎨 design/                # 디자인 리소스
│   ├── figma/               # Figma 파일
│   ├── assets/              # 이미지, 아이콘
│   └── style_guide/         # 스타일 가이드
│
├── 📝 docs/                  # 문서
│   ├── api/                 # API 문서
│   ├── planning/            # 기획 문서
│   └── technical/           # 기술 문서
│
├── 🧪 tests/                 # 테스트
│   ├── unit/                # 단위 테스트
│   ├── integration/         # 통합 테스트
│   └── e2e/                 # E2E 테스트
│
├── 🚀 deployment/            # 배포 설정
│   ├── docker/              # Docker 설정
│   ├── kubernetes/          # K8s 설정
│   └── ci_cd/               # CI/CD 파이프라인
│
└── 📊 data/                  # 데이터
    ├── samples/             # 샘플 이미지
    ├── models/              # 학습된 모델
    └── datasets/            # 데이터셋
```

## 🛠 기술 스택

### Frontend
- **Mobile**: React Native / Flutter
- **Web**: React + TypeScript
- **State Management**: Redux / MobX
- **UI Framework**: Material-UI / Tailwind CSS

### Backend
- **Server**: Node.js / Python FastAPI
- **Database**: PostgreSQL + Redis
- **Storage**: AWS S3 / Google Cloud Storage
- **Queue**: RabbitMQ / Redis Queue

### AI/ML
- **Framework**: TensorFlow / PyTorch
- **Image Processing**: OpenCV
- **Analysis**: scikit-image, NumPy

### Infrastructure
- **Cloud**: AWS / Google Cloud
- **Container**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## 🎯 주요 기능

1. **서예 분석**
   - 실시간 획 분석
   - 중봉 상태 추적
   - 압력/속도 추정

2. **평가 시스템**
   - 다차원 점수 체계
   - 등급 시스템 (A-F)
   - 진도 추적

3. **학습 관리**
   - 맞춤형 커리큘럼
   - 단계별 학습
   - 성과 분석

4. **소셜 기능**
   - 작품 공유
   - 선생님 피드백
   - 커뮤니티