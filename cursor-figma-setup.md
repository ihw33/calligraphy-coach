# Cursor + Figma MCP 설정 가이드

## 1. Figma MCP 설치 (Terminal에서)

```bash
# Figma MCP 설치
npm install -g @figma/claude-talk-to-figma-mcp

# 또는 로컬 설치
npm install @figma/claude-talk-to-figma-mcp
```

## 2. Cursor 설정

### 방법 1: Cursor Settings UI
1. Cursor 열기
2. `Cmd + ,` (Settings)
3. Features → AI → MCP Servers
4. "Add MCP Server" 클릭
5. 다음 정보 입력:
   - Name: `figma`
   - Command: `npx`
   - Arguments: `@figma/claude-talk-to-figma-mcp`

### 방법 2: 설정 파일 직접 수정
`~/Library/Application Support/Cursor/User/mcp-settings.json` 파일 생성:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["@figma/claude-talk-to-figma-mcp"],
      "env": {
        "WEBSOCKET_URL": "ws://localhost:3055"
      }
    }
  }
}
```

## 3. Figma Desktop App 설정

1. Figma Desktop App 열기
2. 우측 상단 프로필 → Settings
3. Beta features 활성화
4. Developer mode 활성화

## 4. WebSocket 서버 실행

터미널에서:
```bash
# WebSocket 서버 시작
npx @figma/claude-talk-to-figma-mcp start
```

## 5. Cursor에서 사용하기

### AI Chat (Cmd + L)에서:
```
@figma connect to channel kjmu80tt
@figma create frame "Mobile App" with size 390x844
@figma add text "서예 교실" at position 195,100
```

### 주요 명령어:
- `@figma connect to channel [ID]` - Figma 연결
- `@figma create frame` - 프레임 생성
- `@figma add [element]` - 요소 추가
- `@figma get design tokens` - 디자인 토큰 가져오기
- `@figma export components` - 컴포넌트 내보내기

## 6. 프로젝트별 설정 (.cursorrules)

이미 설정됨:
- WebSocket: ws://localhost:3055
- Channel: kjmu80tt
- Design System 정의됨

## 7. 테스트

1. Cursor에서 프로젝트 열기:
```bash
cursor /Users/m4_macbook/calligraphy-coach
```

2. AI Chat에서:
```
@figma connect to channel kjmu80tt
@figma 현재 디자인 파일의 컴포넌트를 보여줘
```

## 문제 해결

### WebSocket 연결 안됨
- Figma Desktop App 재시작
- WebSocket 서버 재시작
- 포트 3055가 사용 중인지 확인

### MCP 명령어 인식 안됨
- Cursor 재시작
- MCP 설정 파일 확인
- npm 패키지 재설치

### Figma 권한 오류
- Figma 파일 편집 권한 확인
- Developer mode 활성화 확인