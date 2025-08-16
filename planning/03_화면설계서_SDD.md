# 📱 화면 설계서 (SDD)
## Screen Design Document

### 프로젝트명: 서예마스터 (Calligraphy Master)
### 버전: 1.0
### 작성일: 2025-08-14

---

## 1. 디자인 시스템

### 1.1 색상 팔레트

```css
/* Primary Colors */
--primary: #FF6B35        /* 주황 - 액션, CTA */
--primary-dark: #E55A2B   /* 진한 주황 */
--primary-light: #FF8A5B  /* 연한 주황 */

/* Neutral Colors */
--background: #FFFFFF     /* 배경 */
--surface: #F8F9FA       /* 카드 배경 */
--border: #E1E8ED        /* 테두리 */

/* Text Colors */
--ink-strong: #1A1D1F    /* 제목 */
--ink-base: #272B30      /* 본문 */
--ink-light: #6C7680     /* 보조 텍스트 */
--muted: #99A1A8         /* 비활성 */

/* Status Colors */
--success: #10B981       /* 성공, 우수 */
--warning: #F59E0B       /* 경고, 보통 */
--error: #EF4444         /* 오류, 부족 */
--info: #3B82F6          /* 정보 */

/* Gradient */
--gradient-primary: linear-gradient(135deg, #FF6B35 0%, #FF8A5B 100%);
```

### 1.2 타이포그래피

```css
/* Font Family */
--font-sans: 'Pretendard', -apple-system, sans-serif;
--font-serif: 'Noto Serif KR', serif;  /* 한자 표시용 */

/* Font Sizes */
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 30px;
--text-4xl: 36px;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 1.3 간격 시스템

```css
/* Spacing Scale */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
```

---

## 2. 화면 구조

### 2.1 레이아웃 템플릿

```
┌─────────────────────────┐
│     Status Bar (44px)    │
├─────────────────────────┤
│     Header (56px)        │
├─────────────────────────┤
│                         │
│     Content Area        │
│     (Scrollable)        │
│                         │
├─────────────────────────┤
│   Tab Bar (56px)        │
└─────────────────────────┘
```

### 2.2 반응형 브레이크포인트

| 구분 | 너비 | 대상 기기 |
|------|------|-----------|
| Mobile | 320-767px | 스마트폰 |
| Tablet | 768-1023px | 태블릿 |
| Desktop | 1024px+ | 데스크톱 |

---

## 3. 주요 화면 상세

### 3.1 홈 화면 (Home Screen)

#### 와이어프레임
```
┌─────────────────────────┐
│  🔔  서예마스터  👤     │
├─────────────────────────┤
│                         │
│  안녕하세요, 민수님!     │
│  오늘도 함께 연습해요    │
│                         │
│ ┌─────────────────────┐ │
│ │   오늘의 한자        │ │
│ │      大              │ │
│ │   큰 대              │ │
│ └─────────────────────┘ │
│                         │
│  최근 학습 ─────────    │
│ ┌───┐ ┌───┐ ┌───┐     │
│ │ 中 │ │ 小 │ │ 人 │     │
│ │85점│ │92점│ │78점│     │
│ └───┘ └───┘ └───┘     │
│                         │
│ ┌─────────────────────┐ │
│ │   📷 연습 시작       │ │
│ └─────────────────────┘ │
│                         │
│  학습 통계 ─────────    │
│  [████████░░] 80%       │
│  이번 주 목표 달성률     │
│                         │
├─────────────────────────┤
│  🏠  📚  📷  📊  ⚙️    │
└─────────────────────────┘
```

#### 컴포넌트 명세

| 컴포넌트 | 타입 | 설명 |
|----------|------|------|
| Header | Navigation | 알림, 프로필 접근 |
| Welcome Card | Card | 개인화된 인사말 |
| Today's Character | Card | 오늘의 학습 한자 |
| Recent Practice | Horizontal List | 최근 연습 기록 |
| Quick Start | Button | 카메라 화면 이동 |
| Weekly Progress | Progress Bar | 주간 목표 진도 |
| Tab Bar | Navigation | 하단 네비게이션 |

### 3.2 카메라 화면 (Camera Screen)

#### 와이어프레임
```
┌─────────────────────────┐
│  ←   촬영하기    💡     │
├─────────────────────────┤
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │                 │    │
│  │    카메라       │    │
│  │    프리뷰       │    │
│  │                 │    │
│  │   ┌─┬─┬─┐      │    │
│  │   ├─┼─┼─┤      │    │
│  │   ├─┼─┼─┤      │    │
│  │   └─┴─┴─┘      │    │
│  │  (가이드라인)   │    │
│  │                 │    │
│  └─────────────────┘    │
│                         │
│  선택한 한자: 中         │
│                         │
│  ┌───────────────────┐  │
│  │   🖼️  갤러리      │  │
│  └───────────────────┘  │
│                         │
│     ◉ 촬영             │
│                         │
└─────────────────────────┘
```

#### 인터랙션 명세

| 액션 | 트리거 | 결과 |
|------|--------|------|
| 촬영 | 셔터 버튼 탭 | 사진 촬영 → 분석 시작 |
| 갤러리 | 갤러리 버튼 탭 | 이미지 선택 화면 |
| 가이드 토글 | 가이드 아이콘 탭 | 격자 표시/숨김 |
| 플래시 | 플래시 아이콘 탭 | 플래시 켜기/끄기 |
| 뒤로가기 | 백 버튼 탭 | 이전 화면 |

### 3.3 분석 중 화면 (Analysis Loading)

#### 와이어프레임
```
┌─────────────────────────┐
│                         │
│                         │
│                         │
│      ⊙ ⊙ ⊙             │
│                         │
│    분석 중입니다...      │
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │   [스켈레톤     │    │
│  │    애니메이션]  │    │
│  │                 │    │
│  └─────────────────┘    │
│                         │
│  획 분석 ████░░░░░░     │
│  압력 추정 ██░░░░░░░    │
│  비교 분석 ░░░░░░░░░    │
│                         │
│                         │
│                         │
└─────────────────────────┘
```

### 3.4 평가 결과 화면 (Evaluation Result)

#### 와이어프레임
```
┌─────────────────────────┐
│  ←   평가 결과    📤    │
├─────────────────────────┤
│                         │
│  ┌─────────────────┐    │
│  │      中         │    │
│  │                 │    │
│  │   C+    76.2    │    │
│  │         점      │    │
│  │      +8점↑      │    │
│  └─────────────────┘    │
│                         │
│  세부 평가 ─────────    │
│  여백    ████████░░ 82  │
│  각도    ███████░░░ 74  │
│  중심    █████████░ 95  │
│  형태    ██████░░░░ 63  │
│  가이드  ██████░░░░ 68  │
│                         │
│  개선 제안 ─────────    │
│  • 가로획 길이 늘리기   │
│  • 좌우 균형 맞추기     │
│                         │
│ ┌──────┐ ┌──────┐      │
│ │재도전│ │ 저장 │      │
│ └──────┘ └──────┘      │
└─────────────────────────┘
```

#### 컴포넌트 상세

**점수 카드 (Score Card)**
```jsx
<Card gradient="primary">
  <Character size="xl" />
  <ScoreBadge grade="C+" />
  <Score value={76.2} unit="점" />
  <Improvement value="+8" />
</Card>
```

**세부 점수 (Detail Scores)**
```jsx
<ScoreBar 
  label="여백"
  value={82}
  color="chart-1"
  icon="margin"
/>
```

### 3.5 상세 분석 화면 (Detailed Analysis)

#### 탭 구조
```
┌─────────────────────────┐
│  ←   상세 분석          │
├─────────────────────────┤
│ [스켈레톤][압력][비교]  │
├─────────────────────────┤
│                         │
│   (선택된 탭 내용)      │
│                         │
└─────────────────────────┘
```

#### 스켈레톤 탭
```
│  스켈레톤 분석          │
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │   [스켈레톤     │    │
│  │    이미지]      │    │
│  │                 │    │
│  └─────────────────┘    │
│                         │
│  획 정보 ───────────    │
│  • 총 4획 감지          │
│  • 평균 각도: 87.3°     │
│  • 굵기 균일도: 85%     │
│                         │
│  주요 특징점 ────────   │
│  • 교차점: 1개          │
│  • 끝점: 4개            │
```

#### 압력 분석 탭
```
│  압력/속도 분석         │
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │   [히트맵       │    │
│  │    이미지]      │    │
│  │                 │    │
│  └─────────────────┘    │
│                         │
│  압력 분포 ─────────    │
│  🔴 과도: 2곳           │
│  🟠 부족: 1곳           │
│  🟢 적절: 85%           │
│                         │
│  속도 패턴 ─────────    │
│  [그래프]               │
```

### 3.6 학습 기록 화면 (History)

#### 와이어프레임
```
┌─────────────────────────┐
│      학습 기록          │
├─────────────────────────┤
│                         │
│  이번 주 ───────────    │
│  [월][화][수][목][금]   │
│   ✓   ✓   ✓   -   -    │
│                         │
│  통계 ──────────────    │
│  총 연습: 127회         │
│  평균 점수: 82.5점      │
│  최고 점수: 95점        │
│                         │
│  최근 연습 ─────────    │
│ ┌─────────────────────┐ │
│ │ 中  2024.08.14      │ │
│ │     85점  C+        │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ 大  2024.08.13      │ │
│ │     92점  A-        │ │
│ └─────────────────────┘ │
│                         │
└─────────────────────────┘
```

---

## 4. 컴포넌트 라이브러리

### 4.1 버튼 (Buttons)

```jsx
// Primary Button
<Button variant="primary" size="lg" fullWidth>
  연습 시작
</Button>

// Secondary Button  
<Button variant="secondary" size="md">
  <Icon name="retry" /> 재도전
</Button>

// Ghost Button
<Button variant="ghost" size="sm">
  <Icon name="back" />
</Button>
```

**버튼 상태**
- Default
- Hover (Desktop)
- Pressed
- Disabled
- Loading

### 4.2 카드 (Cards)

```jsx
// Basic Card
<Card>
  <CardHeader>
    <CardTitle>제목</CardTitle>
  </CardHeader>
  <CardContent>
    내용
  </CardContent>
</Card>

// Gradient Card
<Card gradient="primary">
  <CardContent centered>
    <Score value={85} />
  </CardContent>
</Card>
```

### 4.3 입력 컴포넌트 (Input Components)

```jsx
// Text Input
<Input 
  label="이메일"
  type="email"
  placeholder="example@email.com"
  error="올바른 이메일을 입력하세요"
/>

// Select
<Select 
  label="난이도"
  options={levels}
  defaultValue="beginner"
/>

// Slider
<Slider 
  min={0}
  max={100}
  value={75}
  onChange={handleChange}
/>
```

### 4.4 피드백 컴포넌트 (Feedback)

```jsx
// Progress Bar
<Progress value={75} max={100} />

// Badge
<Badge variant="success">A+</Badge>
<Badge variant="warning">개선 필요</Badge>

// Toast
<Toast 
  type="success"
  message="저장되었습니다"
  duration={3000}
/>

// Modal
<Modal 
  isOpen={isOpen}
  onClose={handleClose}
  title="확인"
>
  <p>정말 삭제하시겠습니까?</p>
</Modal>
```

---

## 5. 애니메이션 및 전환

### 5.1 페이지 전환

```css
/* Slide Transition */
.page-enter {
  transform: translateX(100%);
}
.page-enter-active {
  transform: translateX(0);
  transition: transform 300ms ease-out;
}

/* Fade Transition */
.fade-enter {
  opacity: 0;
}
.fade-enter-active {
  opacity: 1;
  transition: opacity 200ms ease-in;
}
```

### 5.2 마이크로 인터랙션

| 요소 | 애니메이션 | 지속시간 |
|------|------------|----------|
| 버튼 클릭 | Scale(0.95) | 100ms |
| 카드 호버 | Shadow 증가 | 200ms |
| 점수 표시 | Count Up | 1000ms |
| 로딩 | Pulse | 1500ms |
| 스켈레톤 | Draw Path | 2000ms |

### 5.3 제스처

| 제스처 | 액션 | 피드백 |
|--------|------|--------|
| Swipe Left/Right | 이미지 전환 | Slide 애니메이션 |
| Pinch | 이미지 확대/축소 | Smooth scale |
| Long Press | 옵션 메뉴 | Haptic feedback |
| Pull to Refresh | 새로고침 | Loading spinner |

---

## 6. 접근성 (Accessibility)

### 6.1 색상 대비

| 조합 | 대비율 | WCAG 레벨 |
|------|--------|-----------|
| 텍스트/배경 | 7.2:1 | AAA |
| 버튼/배경 | 4.8:1 | AA |
| 비활성/배경 | 3.1:1 | AA |

### 6.2 터치 타겟

- 최소 크기: 44x44px (iOS), 48x48dp (Android)
- 간격: 최소 8px
- 확장 가능한 히트 영역

### 6.3 스크린 리더

```jsx
<Button 
  aria-label="카메라로 한자 촬영하기"
  role="button"
>
  <Icon name="camera" aria-hidden="true" />
  촬영
</Button>
```

---

## 7. 다크 모드

### 7.1 색상 매핑

```css
/* Light Mode */
--background: #FFFFFF;
--text: #1A1D1F;
--surface: #F8F9FA;

/* Dark Mode */
[data-theme="dark"] {
  --background: #1A1D1F;
  --text: #F8F9FA;
  --surface: #272B30;
}
```

### 7.2 이미지 처리

```jsx
// 다크모드 대응 이미지
<Image 
  src="logo.png"
  darkSrc="logo-dark.png"
  alt="서예마스터"
/>
```

---

## 8. 성능 최적화

### 8.1 이미지 최적화

- WebP 포맷 우선 사용
- Lazy Loading 적용
- 적응형 이미지 (srcset)
- 썸네일 프리로딩

### 8.2 애니메이션 최적화

```css
/* GPU 가속 사용 */
.animated {
  will-change: transform;
  transform: translateZ(0);
}

/* 60fps 유지 */
.smooth {
  animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 9. 플랫폼별 고려사항

### 9.1 iOS

- Safe Area 대응
- Notch/Dynamic Island 고려
- iOS 고유 제스처 충돌 방지
- SF Symbols 사용

### 9.2 Android

- Material Design 가이드라인
- Back 버튼 처리
- 다양한 화면 비율 대응
- Vector Drawable 사용

### 9.3 Web

- 반응형 레이아웃
- 키보드 네비게이션
- 브라우저 호환성
- PWA 지원

---

## 10. 프로토타입 링크

- **Figma 디자인**: [링크]
- **Interactive Prototype**: [링크]
- **Component Storybook**: [링크]

---

*이 문서는 개발 진행에 따라 업데이트됩니다.*