const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3055');
const channel = 'mwi6eu0c'; // 최신 채널

ws.on('open', () => {
    console.log('✅ WebSocket 연결 성공!');
    
    // 채널 연결
    ws.send(JSON.stringify({
        type: 'join',
        channel: channel
    }));
    
    setTimeout(() => {
        // 테스트 메시지
        ws.send(JSON.stringify({
            type: 'message',
            channel: channel,
            message: {
                command: 'get_selection',
                params: {}
            }
        }));
    }, 1000);
});

ws.on('message', (data) => {
    console.log('📨 메시지 수신:', data.toString());
});

ws.on('error', (error) => {
    console.error('❌ 에러:', error);
});

console.log(`🔌 Figma WebSocket 연결 테스트 - Channel: ${channel}`);