# 📝 Calligraphy Coach

> AI 기반 서예 학습 플랫폼 - 한자와 한글 서예를 체계적으로 배우세요

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![React Native](https://img.shields.io/badge/React%20Native-0.72+-green.svg)](https://reactnative.dev)

## 🎯 프로젝트 소개

Calligraphy Coach는 AI 기술을 활용하여 서예 학습을 돕는 혁신적인 플랫폼입니다. 
실시간 획 분석, 붓 움직임 추적, 맞춤형 피드백을 통해 누구나 쉽게 서예를 배울 수 있습니다.

### 핵심 기능

- 🔍 **실시간 서예 분석**: 획순, 굵기, 각도, 균형 등 다차원 분석
- 🎯 **중봉 상태 추적**: 붓이 바로 세워졌는지 실시간 모니터링
- 📊 **상세한 평가 시스템**: 5개 평가 항목, A-F 등급 체계
- 📈 **진도 추적**: 개인별 학습 진도 및 성과 분석
- 🎓 **맞춤형 커리큘럼**: AI 기반 개인 맞춤 학습 계획
- 📱 **크로스 플랫폼**: iOS, Android, 웹 지원

## 🚀 시작하기

### 필요 조건

- Python 3.8+
- Node.js 16+
- OpenCV 4.5+
- React Native CLI

### 설치

```bash
# 저장소 클론
git clone https://github.com/ihw33/calligraphy-coach.git
cd calligraphy-coach

# AI 엔진 의존성 설치
pip install -r requirements.txt

# 프론트엔드 의존성 설치
cd frontend/mobile
npm install

# iOS 설정 (Mac only)
cd ios && pod install
```

### 실행

```bash
# AI 분석 서버 실행
python ai_engine/server.py

# 모바일 앱 실행
npm run ios     # iOS
npm run android # Android

# 웹앱 실행
cd frontend/web
npm start
```

## 📊 주요 분석 기능

### 1. 구조 분석
- 획순 정확도
- 획 간격 균일성
- 전체 균형도
- 좌우 대칭성

### 2. 붓 움직임 분석
- 붓 궤적 추적
- 압력 변화 추정
- 속도 변화 감지
- 꺾임 부분 처리

### 3. 중봉 상태 분석
- 붓 수직 상태 확인
- 좌우 대칭성 평가
- 먹 농도 분포 분석
- 운필 일관성 체크

## 🎨 스크린샷

### 분석 화면
![Analysis](docs/screenshots/analysis.png)

### 평가 리포트
![Report](docs/screenshots/report.png)

### 학습 진도
![Progress](docs/screenshots/progress.png)

## 🛠 기술 스택

- **Frontend**: React Native, TypeScript, Redux
- **Backend**: Python FastAPI, Node.js
- **AI/ML**: TensorFlow, OpenCV, scikit-image
- **Database**: PostgreSQL, Redis
- **Cloud**: AWS/Google Cloud
- **Design**: Figma

## 📁 프로젝트 구조

```
calligraphy-coach/
├── frontend/          # 프론트엔드 앱
├── backend/           # 백엔드 서버
├── ai_engine/         # AI 분석 엔진
├── design/            # 디자인 리소스
├── docs/              # 문서
├── tests/             # 테스트
└── deployment/        # 배포 설정
```

## 🤝 기여하기

프로젝트에 기여하고 싶으시다면:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 팀

- **개발**: AI Development Team
- **기획**: Claude Desktop
- **디자인**: Figma Design Team

## 📞 문의

- GitHub Issues: [https://github.com/ihw33/calligraphy-coach/issues](https://github.com/ihw33/calligraphy-coach/issues)
- Email: contact@calligraphy-coach.com

---

Made with ❤️ by Calligraphy Coach Team