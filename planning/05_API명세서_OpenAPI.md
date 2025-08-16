# 🔌 API 명세서 (OpenAPI)
## API Specification Document

### 프로젝트명: 서예마스터 (Calligraphy Master)
### 버전: 1.0
### 작성일: 2025-08-14
### API Version: v1
### Base URL: `https://api.calligraphy-master.com/v1`

---

## 1. API 개요

### 1.1 인증 방식
- **Type**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer {token}`
- **Token 유효기간**: 
  - Access Token: 1시간
  - Refresh Token: 30일

### 1.2 응답 형식
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2025-08-14T10:30:00Z",
  "traceId": "abc123-def456"
}
```

### 1.3 에러 응답
```json
{
  "success": false,
  "error": {
    "code": 1001,
    "message": "Invalid credentials",
    "details": "The email or password is incorrect",
    "field": "password"
  },
  "timestamp": "2025-08-14T10:30:00Z",
  "traceId": "abc123-def456"
}
```

### 1.4 HTTP 상태 코드
| 코드 | 의미 | 사용 예시 |
|------|------|-----------|
| 200 | OK | 성공적인 GET, PUT |
| 201 | Created | 성공적인 POST |
| 204 | No Content | 성공적인 DELETE |
| 400 | Bad Request | 잘못된 요청 형식 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 429 | Too Many Requests | Rate limit 초과 |
| 500 | Internal Server Error | 서버 오류 |

---

## 2. 인증 API

### 2.1 회원가입
**POST** `/auth/register`

#### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "nickname": "민수",
  "birthYear": 2010,
  "learningLevel": "beginner"
}
```

#### Response (201)
```json
{
  "success": true,
  "data": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "민수",
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 3600
  }
}
```

#### Validation Rules
- `email`: Valid email format, unique
- `password`: Min 8 chars, 1 uppercase, 1 number, 1 special char
- `nickname`: 2-20 characters
- `birthYear`: 1900-current year
- `learningLevel`: enum ["beginner", "intermediate", "advanced"]

---

### 2.2 로그인
**POST** `/auth/login`

#### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "deviceId": "device-uuid-12345"
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "profile": {
      "nickname": "민수",
      "level": 5,
      "exp": 1250,
      "currentStreak": 7
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 3600
  }
}
```

---

### 2.3 토큰 갱신
**POST** `/auth/refresh`

#### Request
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 3600
  }
}
```

---

### 2.4 로그아웃
**POST** `/auth/logout`

#### Headers
```
Authorization: Bearer {token}
```

#### Request
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Response (204)
No content

---

## 3. 분석 API

### 3.1 기본 분석
**POST** `/analysis/basic`

#### Headers
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

#### Request (multipart/form-data)
```
image: [binary file]
characterId: "中"
sessionId: "550e8400-e29b-41d4-a716-446655440000" (optional)
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "analysisId": "660e8400-e29b-41d4-a716-446655440000",
    "character": "中",
    "scores": {
      "overall": 81.5,
      "margin": 85,
      "angle": 78,
      "center": 92,
      "shape": 71,
      "guide": 82
    },
    "grade": "B+",
    "improvement": 8.5,
    "processingTime": 1234,
    "imageUrls": {
      "original": "https://cdn.example.com/images/original/xxx.jpg",
      "processed": "https://cdn.example.com/images/processed/xxx.jpg"
    },
    "feedback": [
      "가로획 길이를 10% 늘려보세요",
      "세로획 중심 정렬이 우수합니다"
    ]
  }
}
```

---

### 3.2 스켈레톤 분석
**POST** `/analysis/skeleton`

#### Request (multipart/form-data)
```
image: [binary file]
characterId: "中"
includeVisualization: true
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "analysisId": "770e8400-e29b-41d4-a716-446655440000",
    "skeleton": {
      "strokeCount": 4,
      "keyPoints": {
        "endpoints": [[120, 50], [120, 200], [50, 125], [190, 125]],
        "junctions": [[120, 125]]
      },
      "strokeAngles": [90, 90, 0, 0],
      "averageAngle": 45,
      "thicknessProfile": {
        "average": 12.5,
        "uniformity": 0.85,
        "variations": [11, 12, 13, 12, 14]
      }
    },
    "structuralScore": 88.5,
    "visualizationUrl": "https://cdn.example.com/skeleton/xxx.png"
  }
}
```

---

### 3.3 다이나믹스 분석
**POST** `/analysis/dynamics`

#### Request (multipart/form-data)
```
image: [binary file]
characterId: "中"
referenceId: "ref_001" (optional)
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "analysisId": "880e8400-e29b-41d4-a716-446655440000",
    "dynamics": {
      "pressure": {
        "profile": [
          {"position": [50, 125], "value": 0.8, "status": "normal"},
          {"position": [120, 125], "value": 0.95, "status": "high"},
          {"position": [190, 125], "value": 0.6, "status": "low"}
        ],
        "average": 0.78,
        "peaks": 3,
        "consistency": 0.72
      },
      "speed": {
        "profile": [
          {"position": [50, 125], "value": 1.2, "status": "fast"},
          {"position": [120, 125], "value": 0.8, "status": "normal"},
          {"position": [190, 125], "value": 0.9, "status": "normal"}
        ],
        "average": 0.97,
        "consistency": 0.85
      },
      "strokeOrder": [1, 2, 3, 4],
      "estimatedDuration": 2.3
    },
    "heatmapUrl": "https://cdn.example.com/heatmap/xxx.png",
    "annotatedImageUrl": "https://cdn.example.com/annotated/xxx.png"
  }
}
```

---

### 3.4 비교 분석
**POST** `/analysis/compare`

#### Request
```json
{
  "userImageId": "880e8400-e29b-41d4-a716-446655440000",
  "referenceId": "ref_001",
  "comparisonMode": "detailed"
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "comparisonId": "990e8400-e29b-41d4-a716-446655440000",
    "similarity": {
      "overall": 78.5,
      "structural": 82.3,
      "stylistic": 74.7
    },
    "differences": {
      "pressure": [
        {"area": [120, 50, 140, 70], "difference": 0.3, "suggestion": "압력을 줄이세요"},
        {"area": [100, 120, 140, 130], "difference": -0.2, "suggestion": "압력을 높이세요"}
      ],
      "speed": [
        {"area": [50, 125, 80, 135], "difference": 0.5, "suggestion": "천천히 쓰세요"}
      ],
      "shape": {
        "hausdorffDistance": 12.5,
        "problematicAreas": 2
      }
    },
    "overlayImageUrl": "https://cdn.example.com/overlay/xxx.png",
    "sideBySideUrl": "https://cdn.example.com/comparison/xxx.png"
  }
}
```

---

### 3.5 분석 결과 조회
**GET** `/analysis/{analysisId}`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "analysisId": "660e8400-e29b-41d4-a716-446655440000",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "character": "中",
    "analysisType": "full",
    "scores": {...},
    "skeleton": {...},
    "dynamics": {...},
    "comparison": {...},
    "images": {
      "original": "url",
      "skeleton": "url",
      "heatmap": "url",
      "annotated": "url",
      "overlay": "url"
    },
    "createdAt": "2025-08-14T10:30:00Z"
  }
}
```

---

## 4. 학습 관리 API

### 4.1 학습 세션 시작
**POST** `/learning/sessions/start`

#### Request
```json
{
  "characterId": "中",
  "sessionType": "practice"
}
```

#### Response (201)
```json
{
  "success": true,
  "data": {
    "sessionId": "aa0e8400-e29b-41d4-a716-446655440000",
    "characterId": "中",
    "sessionType": "practice",
    "startedAt": "2025-08-14T10:30:00Z",
    "characterInfo": {
      "symbol": "中",
      "meaning": "가운데 중",
      "strokeCount": 4,
      "difficulty": 1
    }
  }
}
```

---

### 4.2 학습 세션 종료
**POST** `/learning/sessions/{sessionId}/complete`

#### Request
```json
{
  "totalAttempts": 5,
  "bestScore": 85.5
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "sessionId": "aa0e8400-e29b-41d4-a716-446655440000",
    "duration": 300,
    "totalAttempts": 5,
    "bestScore": 85.5,
    "averageScore": 78.2,
    "improvement": 12.3,
    "experienceGained": 50,
    "achievements": [
      {
        "id": "ach_001",
        "name": "첫 걸음",
        "description": "첫 한자 완성"
      }
    ]
  }
}
```

---

### 4.3 학습 진도 조회
**GET** `/learning/progress`

#### Query Parameters
- `period`: "daily" | "weekly" | "monthly" | "all"
- `limit`: number (default: 10)

#### Response (200)
```json
{
  "success": true,
  "data": {
    "summary": {
      "totalCharactersLearned": 25,
      "totalPracticeTime": 3600,
      "averageScore": 82.5,
      "currentStreak": 7,
      "longestStreak": 15
    },
    "characterProgress": [
      {
        "characterId": "中",
        "character": "中",
        "masteryLevel": 85,
        "totalAttempts": 12,
        "bestScore": 95,
        "averageScore": 87.5,
        "lastPracticed": "2025-08-13T15:30:00Z"
      }
    ],
    "weeklyStats": {
      "practicedays": [true, true, true, false, true, false, false],
      "scores": [85, 87, 90, 0, 92, 0, 0],
      "timeSpent": [20, 25, 30, 0, 35, 0, 0]
    }
  }
}
```

---

### 4.4 학습 기록
**GET** `/learning/history`

#### Query Parameters
- `page`: number (default: 1)
- `limit`: number (default: 20)
- `characterId`: string (optional)
- `startDate`: ISO 8601 date (optional)
- `endDate`: ISO 8601 date (optional)

#### Response (200)
```json
{
  "success": true,
  "data": {
    "total": 127,
    "page": 1,
    "limit": 20,
    "history": [
      {
        "attemptId": "bb0e8400-e29b-41d4-a716-446655440000",
        "character": "中",
        "score": 85,
        "grade": "B+",
        "improvement": 5,
        "duration": 45,
        "createdAt": "2025-08-14T09:30:00Z",
        "imageUrl": "https://cdn.example.com/attempts/xxx.jpg"
      }
    ]
  }
}
```

---

### 4.5 추천 한자
**GET** `/learning/recommendations`

#### Query Parameters
- `count`: number (default: 3)
- `difficulty`: "easy" | "medium" | "hard" | "auto"

#### Response (200)
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "characterId": "大",
        "character": "大",
        "reason": "기초 한자 학습 필요",
        "difficulty": 1,
        "estimatedScore": 75,
        "benefits": [
          "기본 획 연습",
          "균형 감각 향상"
        ]
      },
      {
        "characterId": "小",
        "character": "小",
        "reason": "대칭 구조 연습",
        "difficulty": 1,
        "estimatedScore": 80
      }
    ],
    "learningPath": {
      "currentLevel": 5,
      "nextMilestone": "기초 한자 마스터",
      "progress": 65,
      "estimatedDays": 7
    }
  }
}
```

---

## 5. 한자 정보 API

### 5.1 한자 목록
**GET** `/characters`

#### Query Parameters
- `category`: "basic" | "intermediate" | "advanced"
- `difficulty`: 1-10
- `search`: string
- `page`: number
- `limit`: number

#### Response (200)
```json
{
  "success": true,
  "data": {
    "total": 100,
    "characters": [
      {
        "id": "中",
        "character": "中",
        "pinyin": "zhōng",
        "koreanReading": "중",
        "meaning": "가운데, 중심",
        "strokeCount": 4,
        "difficulty": 1,
        "category": "basic"
      }
    ]
  }
}
```

---

### 5.2 한자 상세 정보
**GET** `/characters/{characterId}`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "id": "中",
    "character": "中",
    "pinyin": "zhōng",
    "koreanReading": "중",
    "meaningKo": "가운데, 중심",
    "meaningEn": "middle, center",
    "strokeCount": 4,
    "strokeOrder": [
      {"stroke": 1, "path": "M60,50 L60,200", "type": "vertical"},
      {"stroke": 2, "path": "M40,75 L80,75", "type": "horizontal"},
      {"stroke": 3, "path": "M40,175 L80,175", "type": "horizontal"},
      {"stroke": 4, "path": "M40,50 L80,50 L80,200 L40,200 Z", "type": "box"}
    ],
    "radical": "丨",
    "components": ["丨", "口"],
    "difficulty": 1,
    "category": "basic",
    "referenceImages": [
      {
        "id": "ref_001",
        "type": "standard",
        "style": "해서",
        "url": "https://cdn.example.com/references/中_standard.jpg"
      }
    ],
    "relatedCharacters": ["央", "中", "串"],
    "exampleWords": ["中心", "中國", "中間"]
  }
}
```

---

## 6. 사용자 API

### 6.1 프로필 조회
**GET** `/users/profile`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "nickname": "민수",
    "profileImageUrl": "https://cdn.example.com/profiles/xxx.jpg",
    "level": 5,
    "experiencePoints": 1250,
    "nextLevelExp": 2000,
    "totalPracticeTime": 7200,
    "totalCharactersLearned": 25,
    "currentStreak": 7,
    "longestStreak": 15,
    "achievements": 12,
    "joinedAt": "2025-07-01T00:00:00Z"
  }
}
```

---

### 6.2 프로필 수정
**PUT** `/users/profile`

#### Request
```json
{
  "nickname": "서예고수",
  "birthYear": 2010,
  "learningLevel": "intermediate"
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "message": "프로필이 업데이트되었습니다"
  }
}
```

---

### 6.3 설정 조회
**GET** `/users/settings`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "theme": "light",
    "language": "ko",
    "notifications": {
      "enabled": true,
      "dailyReminder": "09:00",
      "achievementAlerts": true,
      "weeklyReport": true
    },
    "practice": {
      "weeklyGoal": 5,
      "autoSave": true,
      "showGuidelines": true,
      "hapticFeedback": true,
      "soundEffects": true
    },
    "privacy": {
      "publicProfile": true,
      "showInLeaderboard": true,
      "shareProgress": false
    }
  }
}
```

---

### 6.4 설정 변경
**PATCH** `/users/settings`

#### Request
```json
{
  "theme": "dark",
  "notifications.dailyReminder": "21:00",
  "practice.weeklyGoal": 7
}
```

#### Response (200)
```json
{
  "success": true,
  "data": {
    "message": "설정이 업데이트되었습니다"
  }
}
```

---

## 7. 목표 및 업적 API

### 7.1 목표 목록
**GET** `/goals`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "activeGoals": [
      {
        "goalId": "goal_001",
        "name": "주간 연습",
        "description": "일주일에 5일 연습하기",
        "type": "weekly",
        "targetValue": 5,
        "currentValue": 3,
        "progress": 60,
        "deadline": "2025-08-18T23:59:59Z",
        "reward": 100
      }
    ],
    "completedGoals": [
      {
        "goalId": "goal_002",
        "name": "첫 한자 마스터",
        "completedAt": "2025-08-10T15:30:00Z",
        "reward": 50
      }
    ]
  }
}
```

---

### 7.2 목표 설정
**POST** `/goals`

#### Request
```json
{
  "goalType": "custom",
  "name": "한자 10개 마스터",
  "targetValue": 10,
  "deadline": "2025-09-01T00:00:00Z"
}
```

#### Response (201)
```json
{
  "success": true,
  "data": {
    "goalId": "goal_003",
    "message": "목표가 설정되었습니다"
  }
}
```

---

### 7.3 업적 목록
**GET** `/achievements`

#### Response (200)
```json
{
  "success": true,
  "data": {
    "earned": [
      {
        "achievementId": "ach_001",
        "name": "첫 발걸음",
        "description": "첫 한자 연습 완료",
        "iconUrl": "https://cdn.example.com/achievements/first_step.png",
        "earnedAt": "2025-08-01T10:00:00Z",
        "points": 10
      }
    ],
    "available": [
      {
        "achievementId": "ach_002",
        "name": "연습의 달인",
        "description": "100개 한자 연습",
        "progress": 25,
        "targetValue": 100,
        "points": 100
      }
    ],
    "totalPoints": 250
  }
}
```

---

## 8. 리더보드 API

### 8.1 리더보드 조회
**GET** `/leaderboard`

#### Query Parameters
- `type`: "score" | "streak" | "mastery" | "practice_time"
- `period`: "daily" | "weekly" | "monthly" | "all_time"
- `limit`: number (default: 20)

#### Response (200)
```json
{
  "success": true,
  "data": {
    "type": "score",
    "period": "weekly",
    "userRank": 15,
    "userScore": 850,
    "leaderboard": [
      {
        "rank": 1,
        "userId": "user_001",
        "nickname": "서예마스터",
        "profileImageUrl": "url",
        "score": 2450,
        "level": 12,
        "change": 0
      },
      {
        "rank": 2,
        "userId": "user_002",
        "nickname": "한자왕",
        "profileImageUrl": "url",
        "score": 2380,
        "level": 11,
        "change": 1
      }
    ]
  }
}
```

---

## 9. WebSocket API

### 9.1 연결
```javascript
const ws = new WebSocket('wss://api.calligraphy-master.com/v1/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'AUTH',
    token: 'Bearer eyJhbGciOiJIUzI1NiIs...'
  }));
};
```

### 9.2 실시간 분석
```javascript
// 클라이언트 → 서버
{
  "type": "ANALYZE_FRAME",
  "data": {
    "sessionId": "session_123",
    "frame": "base64_image_data",
    "characterId": "中",
    "timestamp": 1234567890
  }
}

// 서버 → 클라이언트
{
  "type": "ANALYSIS_PROGRESS",
  "data": {
    "sessionId": "session_123",
    "progress": 45,
    "stage": "skeleton_extraction"
  }
}

// 서버 → 클라이언트 (완료)
{
  "type": "ANALYSIS_COMPLETE",
  "data": {
    "sessionId": "session_123",
    "score": 85,
    "feedback": "압력을 조금 더 일정하게",
    "problemAreas": [
      {"x": 120, "y": 50, "issue": "pressure_high"}
    ]
  }
}
```

### 9.3 실시간 협업
```javascript
// 방 참가
{
  "type": "JOIN_ROOM",
  "data": {
    "roomId": "room_123",
    "role": "student"
  }
}

// 실시간 피드백
{
  "type": "TEACHER_FEEDBACK",
  "data": {
    "studentId": "user_123",
    "feedback": "세로획을 더 곧게 써보세요",
    "annotation": {
      "type": "arrow",
      "from": [100, 100],
      "to": [100, 200]
    }
  }
}
```

---

## 10. Rate Limiting

### 10.1 제한 정책
| 엔드포인트 | 제한 | 윈도우 |
|------------|------|--------|
| /auth/* | 10 requests | 1분 |
| /analysis/* | 100 requests | 1시간 |
| /learning/* | 500 requests | 1시간 |
| 기타 | 1000 requests | 1시간 |

### 10.2 Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1628856000
```

---

## 11. 에러 코드

### 11.1 인증 에러 (1xxx)
| 코드 | 메시지 | 설명 |
|------|--------|------|
| 1001 | Invalid credentials | 잘못된 이메일/비밀번호 |
| 1002 | Token expired | 토큰 만료 |
| 1003 | Invalid token | 유효하지 않은 토큰 |
| 1004 | Account locked | 계정 잠금 (5회 실패) |
| 1005 | Email not verified | 이메일 미인증 |

### 11.2 분석 에러 (2xxx)
| 코드 | 메시지 | 설명 |
|------|--------|------|
| 2001 | Invalid image format | 지원하지 않는 이미지 형식 |
| 2002 | Image too large | 이미지 크기 초과 (10MB) |
| 2003 | Character not found | 인식할 수 없는 한자 |
| 2004 | Analysis failed | 분석 실패 |
| 2005 | Processing timeout | 처리 시간 초과 |

### 11.3 데이터 에러 (3xxx)
| 코드 | 메시지 | 설명 |
|------|--------|------|
| 3001 | Resource not found | 리소스 없음 |
| 3002 | Duplicate entry | 중복 데이터 |
| 3003 | Invalid data format | 잘못된 데이터 형식 |
| 3004 | Storage limit exceeded | 저장 공간 초과 |

---

## 12. SDK 예제

### 12.1 JavaScript/TypeScript
```typescript
import { CalligraphyMasterAPI } from '@calligraphy-master/sdk';

const api = new CalligraphyMasterAPI({
  apiKey: 'your-api-key',
  baseURL: 'https://api.calligraphy-master.com/v1'
});

// 로그인
const { data } = await api.auth.login({
  email: 'user@example.com',
  password: 'password123'
});

// 이미지 분석
const analysis = await api.analysis.analyze({
  image: imageFile,
  characterId: '中',
  mode: 'full'
});

console.log(`점수: ${analysis.scores.overall}`);
```

### 12.2 Python
```python
from calligraphy_master import CalligraphyMasterAPI

api = CalligraphyMasterAPI(
    api_key='your-api-key',
    base_url='https://api.calligraphy-master.com/v1'
)

# 로그인
auth = api.auth.login(
    email='user@example.com',
    password='password123'
)

# 이미지 분석
with open('character.jpg', 'rb') as f:
    analysis = api.analysis.analyze(
        image=f,
        character_id='中',
        mode='full'
    )

print(f"점수: {analysis['scores']['overall']}")
```

### 12.3 Swift (iOS)
```swift
import CalligraphyMasterSDK

let api = CalligraphyMasterAPI(
    apiKey: "your-api-key",
    baseURL: "https://api.calligraphy-master.com/v1"
)

// 로그인
api.auth.login(email: "user@example.com", password: "password123") { result in
    switch result {
    case .success(let auth):
        print("로그인 성공: \(auth.userId)")
    case .failure(let error):
        print("에러: \(error)")
    }
}

// 이미지 분석
api.analysis.analyze(image: imageData, characterId: "中") { result in
    if let analysis = try? result.get() {
        print("점수: \(analysis.scores.overall)")
    }
}
```

---

## 13. 테스트 환경

### 13.1 Sandbox URL
```
https://sandbox-api.calligraphy-master.com/v1
```

### 13.2 테스트 계정
```json
{
  "email": "test@example.com",
  "password": "Test1234!",
  "apiKey": "test_pk_1234567890abcdef"
}
```

### 13.3 Postman Collection
[Download Postman Collection](https://api.calligraphy-master.com/docs/postman.json)

---

## 14. 변경 이력

### v1.0.0 (2025-08-14)
- 초기 API 릴리즈
- 기본 인증 및 분석 기능
- 학습 관리 API

### v1.1.0 (예정)
- GraphQL 지원
- Batch API 추가
- 고급 필터링 옵션

---

*이 문서는 지속적으로 업데이트됩니다.*
*최신 버전: https://api.calligraphy-master.com/docs*