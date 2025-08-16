# 📚 Calligraphy Coach 세션 가이드

## 🔄 세션 관리 체계

### 현재 세션
- **세션명**: calligraphy-coach-01
- **시작일**: 2025년 8월 16일
- **역할**: 개발 구현
- **GitHub 중심**: 모든 작업은 GitHub 레포지토리를 통해 동기화

## 🎯 세션별 역할 분담

### Claude Desktop (기획 세션)
- 기획 문서 작성
- 사용자 요구사항 정의
- 화면 설계
- GitHub Issues 관리

### calligraphy-coach-01 (개발 세션)
- 코드 구현
- 테스트 작성
- API 개발
- GitHub 커밋/푸시

### Figma (디자인 세션)
- UI/UX 디자인
- 컴포넌트 설계
- 스타일 가이드
- 에셋 제작

## 📋 GitHub 워크플로우

### 1. 작업 시작
```bash
# 최신 코드 받기
git pull origin main

# 작업 브랜치 생성 (선택사항)
git checkout -b feature/새기능
```

### 2. 작업 중
```bash
# 수시로 저장
git add .
git commit -m "작업 내용"
git push origin main
```

### 3. 세션 종료
```bash
# 모든 변경사항 푸시
git add -A
git commit -m "session: calligraphy-coach-01 작업 완료"
git push origin main
```

## 🔗 주요 링크

### GitHub
- 레포지토리: https://github.com/ihw33/calligraphy-coach
- Issues: https://github.com/ihw33/calligraphy-coach/issues
- Projects: https://github.com/ihw33/calligraphy-coach/projects

### 핵심 문서
- 프로젝트 요약: `/docs/PROJECT_SUMMARY.md`
- 기획 문서: `/planning/`
- 기술 문서: `/docs/technical/`

## 💬 세션 간 소통

### 새 세션 시작 시
1. GitHub에서 최신 상태 확인
2. `docs/PROJECT_SUMMARY.md` 읽기
3. 이전 세션의 커밋 로그 확인
4. Issues 확인

### 작업 인계 시
1. 모든 코드 커밋 & 푸시
2. 작업 내용 문서화
3. 다음 작업 TODO 작성
4. Issue 업데이트

## 📝 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드 업무, 패키지 매니저 설정
session: 세션 작업 완료
```

## 🚀 다음 세션 예정 작업

### calligraphy-coach-02
- React Native 앱 초기 설정
- 기본 화면 구성

### calligraphy-coach-03
- FastAPI 서버 구축
- 이미지 업로드 API

### calligraphy-coach-04
- AI 엔진 연동
- 실시간 분석 기능

---

*이 문서는 세션 관리를 위한 가이드입니다. 각 세션은 이 문서를 참고하여 작업을 진행합니다.*