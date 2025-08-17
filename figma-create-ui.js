const WebSocket = require('ws');

// Figma에서 표시되는 최신 채널 ID를 여기에 입력
const CHANNEL = process.argv[2] || 'mwi6eu0c';

const ws = new WebSocket('ws://localhost:3055');

let messageId = 1;

function sendCommand(command, params) {
    const message = {
        id: `msg-${messageId++}`,
        type: 'message',
        channel: CHANNEL,
        message: {
            id: `msg-${messageId}`,
            command: command,
            params: { ...params, commandId: `cmd-${messageId}` }
        }
    };
    
    console.log(`📤 Sending: ${command}`);
    ws.send(JSON.stringify(message));
}

ws.on('open', () => {
    console.log('✅ Connected to WebSocket');
    
    // 채널 가입
    ws.send(JSON.stringify({
        type: 'join',
        channel: CHANNEL
    }));
    
    // UI 생성 명령들
    setTimeout(() => {
        // 헤더 텍스트 추가
        sendCommand('create_text', {
            x: 20,
            y: 40,
            text: '서예 교실',
            fontSize: 32,
            parentId: '6:2'
        });
    }, 2000);
    
    setTimeout(() => {
        // 서브텍스트 추가  
        sendCommand('create_text', {
            x: 20,
            y: 75,
            text: 'AI와 함께하는 한자 학습',
            fontSize: 16,
            parentId: '6:2'
        });
    }, 3000);
    
    setTimeout(() => {
        // 메뉴 버튼 1
        sendCommand('create_rectangle', {
            x: 20,
            y: 140,
            width: 170,
            height: 170,
            name: '학습하기 버튼',
            parentId: '6:2'
        });
    }, 4000);
    
    setTimeout(() => {
        // 메뉴 버튼 2
        sendCommand('create_rectangle', {
            x: 200,
            y: 140,
            width: 170,
            height: 170,
            name: '연습하기 버튼',
            parentId: '6:2'
        });
    }, 5000);
    
    setTimeout(() => {
        console.log('✨ UI 생성 완료!');
        process.exit(0);
    }, 7000);
});

ws.on('message', (data) => {
    const msg = data.toString();
    if (msg.includes('result')) {
        console.log('✅ Success:', msg.substring(0, 100));
    }
});

ws.on('error', (error) => {
    console.error('❌ Error:', error);
});

console.log(`🎨 Creating UI in Figma - Channel: ${CHANNEL}`);