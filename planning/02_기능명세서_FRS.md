# 📘 기능 요구사항 명세서 (FRS)
## Functional Requirements Specification

### 프로젝트명: 서예마스터 (Calligraphy Master)
### 버전: 1.0
### 작성일: 2025-08-14

---

## 1. 시스템 개요

### 1.1 시스템 아키텍처

```
┌─────────────────────────────────────────────┐
│                 Frontend (React)             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │   UI    │ │  State  │ │   API   │       │
│  │Component│ │ Manager │ │ Client  │       │
│  └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────┬───────────────────────┘
                      │ REST API
┌─────────────────────┴───────────────────────┐
│           Backend (Python/FastAPI)           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Analysis │ │   ML    │ │Database │       │
│  │ Engine  │ │ Models  │ │  Layer  │       │
│  └─────────┘ └─────────┘ └─────────┘       │
└──────────────────────────────────────────────┘
```

### 1.2 모듈 구성

| 모듈명 | 설명 | 기술 스택 |
|--------|------|-----------|
| Web Client | 웹 기반 UI | React, TypeScript, Tailwind |
| Mobile Client | 모바일 앱 | React Native |
| API Gateway | API 라우팅 및 인증 | FastAPI, JWT |
| Analysis Core | 이미지 분석 엔진 | OpenCV, scikit-image |
| ML Service | 기계학습 모델 | TensorFlow, PyTorch |
| Data Service | 데이터 저장/조회 | PostgreSQL, Redis |

---

## 2. 상세 기능 명세

### 2.1 사용자 관리 (User Management)

#### 2.1.1 회원가입 (FR-USR-001)

**기능 설명**: 새로운 사용자 계정 생성

**입력 데이터**:
```json
{
  "email": "string",
  "password": "string",
  "nickname": "string",
  "birthYear": "number",
  "learningLevel": "beginner|intermediate|advanced"
}
```

**처리 로직**:
1. 이메일 중복 검사
2. 비밀번호 강도 검증 (8자 이상, 특수문자 포함)
3. 이메일 인증 발송
4. 계정 생성 및 초기 프로필 설정

**출력 데이터**:
```json
{
  "userId": "uuid",
  "accessToken": "jwt_token",
  "refreshToken": "jwt_token",
  "profile": {
    "nickname": "string",
    "level": 1,
    "exp": 0
  }
}
```

**예외 처리**:
- `EMAIL_ALREADY_EXISTS`: 이메일 중복
- `WEAK_PASSWORD`: 비밀번호 규칙 미충족
- `INVALID_EMAIL`: 이메일 형식 오류

#### 2.1.2 로그인 (FR-USR-002)

**기능 설명**: 사용자 인증 및 세션 생성

**입력 데이터**:
```json
{
  "email": "string",
  "password": "string",
  "deviceId": "string"
}
```

**처리 로직**:
1. 이메일/비밀번호 검증
2. 디바이스 등록/확인
3. JWT 토큰 생성
4. 마지막 로그인 시간 업데이트

**보안 요구사항**:
- 5회 실패 시 15분 잠금
- 2FA 옵션 제공
- 토큰 만료: Access(1시간), Refresh(30일)

### 2.2 이미지 분석 (Image Analysis)

#### 2.2.1 기본 분석 (FR-ANA-001)

**기능 설명**: 한자 이미지의 기본 점수 분석

**입력 데이터**:
```json
{
  "image": "base64_string",
  "characterId": "string",
  "analysisMode": "basic|detailed|full"
}
```

**처리 단계**:

##### Step 1: 전처리
```python
def preprocess_image(image):
    # 1. 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. 노이즈 제거
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # 3. 이진화
    _, binary = cv2.threshold(denoised, 0, 255, 
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. 윤곽선 검출
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)
    
    return binary, contours
```

##### Step 2: 특징 추출
```python
def extract_features(binary_image):
    features = {
        'margin_ratio': calculate_margin_ratio(binary_image),
        'stroke_angles': detect_stroke_angles(binary_image),
        'center_alignment': calculate_center_alignment(binary_image),
        'shape_similarity': calculate_shape_similarity(binary_image),
        'guide_adherence': calculate_guide_adherence(binary_image)
    }
    return features
```

##### Step 3: 점수 계산
```python
def calculate_scores(features, reference_features):
    scores = {}
    weights = {
        'margin': 0.15,
        'angle': 0.20,
        'center': 0.25,
        'shape': 0.25,
        'guide': 0.15
    }
    
    for key in features:
        scores[key] = compare_feature(features[key], 
                                     reference_features[key])
    
    final_score = sum(scores[k] * weights[k] for k in scores)
    return scores, final_score
```

**출력 데이터**:
```json
{
  "analysisId": "uuid",
  "timestamp": "ISO8601",
  "scores": {
    "margin": 85,
    "angle": 78,
    "center": 92,
    "shape": 71,
    "guide": 83
  },
  "finalScore": 81.8,
  "grade": "B+",
  "processingTime": 1.23
}
```

#### 2.2.2 스켈레톤 분석 (FR-ANA-002)

**기능 설명**: 글자의 골격 구조 분석

**처리 알고리즘**:

```python
class SkeletonAnalyzer:
    def analyze(self, binary_image):
        # 1. 스켈레톤 추출
        skeleton = skeletonize(binary_image)
        
        # 2. 교차점 및 끝점 검출
        keypoints = self.detect_keypoints(skeleton)
        
        # 3. 획 분리
        strokes = self.separate_strokes(skeleton, keypoints)
        
        # 4. 각 획 분석
        stroke_analysis = []
        for stroke in strokes:
            analysis = {
                'angle': self.calculate_angle(stroke),
                'length': self.calculate_length(stroke),
                'curvature': self.calculate_curvature(stroke),
                'thickness': self.measure_thickness(stroke, binary_image)
            }
            stroke_analysis.append(analysis)
        
        return {
            'skeleton': skeleton,
            'keypoints': keypoints,
            'strokes': stroke_analysis,
            'structural_score': self.calculate_structure_score(stroke_analysis)
        }
```

#### 2.2.3 압력/속도 추정 (FR-ANA-003)

**기능 설명**: 붓 압력과 속도 추정

**압력 추정 알고리즘**:
```python
def estimate_pressure(binary_image, skeleton):
    # Distance Transform으로 굵기 측정
    dist_transform = cv2.distanceTransform(binary_image, cv2.DIST_L2, 5)
    
    # 스켈레톤 경로 따라 샘플링
    pressure_profile = []
    for point in skeleton_path:
        thickness = dist_transform[point] * 2
        
        # 압력 = f(굵기, 농도, 번짐)
        pressure = calculate_pressure(thickness, density, blur)
        pressure_profile.append({
            'position': point,
            'pressure': pressure,
            'thickness': thickness
        })
    
    return pressure_profile
```

**속도 추정 알고리즘**:
```python
def estimate_speed(skeleton_path, pressure_profile):
    speed_profile = []
    
    for i in range(1, len(skeleton_path)):
        # 연속 점 간 거리
        distance = euclidean_distance(skeleton_path[i-1], skeleton_path[i])
        
        # 압력 변화율
        pressure_change = abs(pressure_profile[i] - pressure_profile[i-1])
        
        # 속도 = f(거리, 압력변화)
        # 빠른 움직임 = 긴 거리, 적은 압력 변화
        speed = distance / (1 + pressure_change * 0.1)
        
        speed_profile.append({
            'position': skeleton_path[i],
            'speed': speed
        })
    
    return speed_profile
```

### 2.3 비교 분석 (Comparison Analysis)

#### 2.3.1 교본 비교 (FR-CMP-001)

**기능 설명**: 사용자 글자와 교본 비교

**비교 메트릭**:

```python
class ComparisonAnalyzer:
    def compare(self, user_image, reference_image):
        results = {}
        
        # 1. 구조 유사도 (Structural Similarity)
        results['ssim'] = structural_similarity(user_image, reference_image)
        
        # 2. 형태 거리 (Shape Distance)
        user_contour = get_contour(user_image)
        ref_contour = get_contour(reference_image)
        results['hausdorff'] = hausdorff_distance(user_contour, ref_contour)
        
        # 3. 모멘트 비교 (Moment Comparison)
        user_moments = cv2.moments(user_image)
        ref_moments = cv2.moments(reference_image)
        results['moment_diff'] = compare_moments(user_moments, ref_moments)
        
        # 4. 히스토그램 비교
        results['histogram'] = cv2.compareHist(
            cv2.calcHist([user_image], [0], None, [256], [0,256]),
            cv2.calcHist([reference_image], [0], None, [256], [0,256]),
            cv2.HISTCMP_CORREL
        )
        
        return results
```

#### 2.3.2 주석 생성 (FR-CMP-002)

**기능 설명**: 분석 결과를 이미지에 시각화

**주석 타입**:

| 타입 | 표시 | 의미 |
|------|------|------|
| PRESSURE_HIGH | 🔴 빨간 점 | 과도한 압력 |
| PRESSURE_LOW | 🟠 주황 점 | 부족한 압력 |
| SPEED_FAST | ➡️ 긴 화살표 | 너무 빠름 |
| SPEED_SLOW | → 짧은 화살표 | 너무 느림 |
| PROBLEM_AREA | ⭕ 노란 원 | 주요 문제 |

### 2.4 학습 관리 (Learning Management)

#### 2.4.1 진도 추적 (FR-LRN-001)

**데이터 모델**:

```sql
-- 학습 세션
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    character_id VARCHAR(10),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_attempts INT,
    best_score DECIMAL(5,2),
    average_score DECIMAL(5,2)
);

-- 개별 시도
CREATE TABLE attempts (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES learning_sessions(id),
    attempt_number INT,
    score DECIMAL(5,2),
    analysis_data JSONB,
    image_url TEXT,
    created_at TIMESTAMP
);

-- 숙련도
CREATE TABLE mastery_levels (
    user_id UUID,
    character_id VARCHAR(10),
    mastery_level INT DEFAULT 0,
    total_practice_time INT DEFAULT 0,
    last_practiced TIMESTAMP,
    PRIMARY KEY (user_id, character_id)
);
```

#### 2.4.2 추천 시스템 (FR-LRN-002)

**추천 알고리즘**:

```python
class RecommendationEngine:
    def get_next_character(self, user_id):
        # 1. 사용자 학습 이력 조회
        history = get_learning_history(user_id)
        
        # 2. 약점 분석
        weaknesses = analyze_weaknesses(history)
        
        # 3. 난이도 곡선 계산
        difficulty_curve = calculate_difficulty_curve(user_id)
        
        # 4. 추천 점수 계산
        candidates = []
        for character in all_characters:
            score = 0
            
            # 약점 보완 가능성
            score += weakness_coverage_score(character, weaknesses)
            
            # 적절한 난이도
            score += difficulty_match_score(character, difficulty_curve)
            
            # 다양성
            score += diversity_score(character, history)
            
            # 시간 간격 (간격 반복 학습)
            score += spaced_repetition_score(character, history)
            
            candidates.append((character, score))
        
        # 5. 상위 3개 반환
        return sorted(candidates, key=lambda x: x[1], reverse=True)[:3]
```

### 2.5 데이터 관리 (Data Management)

#### 2.5.1 이미지 저장 (FR-DAT-001)

**저장 전략**:

```python
class ImageStorage:
    def save_image(self, user_id, image_data, metadata):
        # 1. 이미지 압축
        compressed = self.compress_image(image_data, quality=85)
        
        # 2. 파일명 생성
        filename = f"{user_id}/{uuid4()}.jpg"
        
        # 3. 메타데이터 추가
        metadata.update({
            'original_size': len(image_data),
            'compressed_size': len(compressed),
            'compression_ratio': len(compressed) / len(image_data)
        })
        
        # 4. S3 업로드
        s3_url = upload_to_s3(filename, compressed)
        
        # 5. DB 기록
        save_to_database({
            'user_id': user_id,
            'filename': filename,
            'url': s3_url,
            'metadata': metadata
        })
        
        # 6. 캐시 업데이트
        update_cache(user_id, s3_url)
        
        return s3_url
```

#### 2.5.2 데이터 동기화 (FR-DAT-002)

**동기화 프로토콜**:

```python
class DataSync:
    def sync_offline_data(self, user_id, offline_data):
        conflicts = []
        synced = []
        
        for item in offline_data:
            # 1. 충돌 검사
            server_version = get_server_version(item['id'])
            
            if server_version and server_version['updated_at'] > item['updated_at']:
                # 충돌 발생
                conflicts.append({
                    'local': item,
                    'server': server_version
                })
            else:
                # 2. 서버 업데이트
                update_server(item)
                synced.append(item['id'])
        
        # 3. 충돌 해결
        resolved = resolve_conflicts(conflicts, strategy='server_wins')
        
        return {
            'synced': synced,
            'conflicts': conflicts,
            'resolved': resolved
        }
```

---

## 3. API 명세

### 3.1 RESTful API 엔드포인트

#### 인증 관련

| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|-----------|
| POST | /api/auth/register | 회원가입 | ❌ |
| POST | /api/auth/login | 로그인 | ❌ |
| POST | /api/auth/refresh | 토큰 갱신 | ❌ |
| POST | /api/auth/logout | 로그아웃 | ✅ |
| GET | /api/auth/verify | 이메일 인증 | ❌ |

#### 분석 관련

| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|-----------|
| POST | /api/analysis/basic | 기본 분석 | ✅ |
| POST | /api/analysis/skeleton | 스켈레톤 분석 | ✅ |
| POST | /api/analysis/dynamics | 다이나믹스 분석 | ✅ |
| GET | /api/analysis/{id} | 분석 결과 조회 | ✅ |
| POST | /api/analysis/compare | 비교 분석 | ✅ |

#### 학습 관련

| Method | Endpoint | 설명 | 인증 필요 |
|--------|----------|------|-----------|
| GET | /api/learning/progress | 진도 조회 | ✅ |
| GET | /api/learning/history | 학습 이력 | ✅ |
| GET | /api/learning/recommend | 추천 한자 | ✅ |
| POST | /api/learning/goal | 목표 설정 | ✅ |
| GET | /api/learning/statistics | 통계 조회 | ✅ |

### 3.2 WebSocket API

#### 실시간 분석

```javascript
// 연결
ws.connect('/ws/analysis/{user_id}')

// 메시지 타입
{
    "type": "ANALYZE_FRAME",
    "data": {
        "frame": "base64_image",
        "characterId": "中"
    }
}

// 응답
{
    "type": "ANALYSIS_RESULT",
    "data": {
        "score": 85,
        "feedback": "압력을 조금 더 일정하게"
    }
}
```

---

## 4. 에러 처리

### 4.1 에러 코드 체계

| 코드 범위 | 카테고리 | 예시 |
|-----------|----------|------|
| 1000-1999 | 인증 | 1001: 잘못된 비밀번호 |
| 2000-2999 | 분석 | 2001: 이미지 형식 오류 |
| 3000-3999 | 데이터 | 3001: 저장 공간 부족 |
| 4000-4999 | 네트워크 | 4001: 연결 시간 초과 |
| 5000-5999 | 서버 | 5001: 내부 서버 오류 |

### 4.2 에러 응답 형식

```json
{
    "error": {
        "code": 2001,
        "message": "이미지 형식이 올바르지 않습니다",
        "details": "지원 형식: JPEG, PNG",
        "timestamp": "2025-08-14T10:30:00Z",
        "traceId": "abc123"
    }
}
```

---

## 5. 성능 요구사항

### 5.1 응답 시간

| 작업 | 목표 시간 | 최대 시간 |
|------|-----------|-----------|
| 기본 분석 | 1초 | 3초 |
| 스켈레톤 분석 | 2초 | 5초 |
| 비교 분석 | 1.5초 | 4초 |
| 이미지 업로드 | 2초 | 10초 |

### 5.2 처리량

- 동시 사용자: 1,000명
- 초당 요청: 100 RPS
- 일일 분석: 50,000건

---

## 6. 보안 요구사항

### 6.1 인증 및 권한

```python
# JWT 페이로드 구조
{
    "sub": "user_id",
    "email": "user@example.com",
    "roles": ["user"],
    "exp": 1234567890,
    "iat": 1234567890,
    "device_id": "device_uuid"
}
```

### 6.2 데이터 암호화

- 전송: TLS 1.3
- 저장: AES-256-GCM
- 비밀번호: bcrypt (cost=12)

---

## 7. 테스트 시나리오

### 7.1 단위 테스트

```python
def test_skeleton_extraction():
    # Given
    test_image = load_test_image('test_char.png')
    
    # When
    skeleton = extract_skeleton(test_image)
    
    # Then
    assert skeleton is not None
    assert skeleton.shape == test_image.shape
    assert np.sum(skeleton) > 0  # 스켈레톤 존재
    assert np.max(skeleton) == 255  # 이진 이미지
```

### 7.2 통합 테스트

```python
def test_full_analysis_flow():
    # 1. 이미지 업로드
    response = client.post('/api/analysis/basic', 
                          files={'image': test_image})
    assert response.status_code == 200
    
    # 2. 결과 조회
    analysis_id = response.json()['analysisId']
    result = client.get(f'/api/analysis/{analysis_id}')
    assert result.json()['finalScore'] > 0
    
    # 3. 비교 분석
    compare = client.post('/api/analysis/compare',
                         json={'userImageId': analysis_id,
                               'referenceId': 'ref_001'})
    assert compare.status_code == 200
```

---

## 8. 배포 요구사항

### 8.1 환경 구성

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dbname
  
  redis:
    image: redis:7
```

### 8.2 CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          npm test
          python -m pytest
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: |
          docker build -t app:latest .
          docker push registry/app:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/app
```

---

*이 문서는 개발 진행에 따라 업데이트됩니다.*