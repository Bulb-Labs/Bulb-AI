export const development: Config = {
    environment: 'development',
    llm: {
        claude: {
            apiKey: process.env.CLAUDE_API_KEY || '',
            model: 'claude-3-opus-20240229',
            temperature: 0.7
        },
        gpt4: {
            apiKey: process.env.OPENAI_API_KEY || '',
            model: 'gpt-4-turbo-preview',
            temperature: 0.7
        },
        gemini: {
            apiKey: process.env.GEMINI_API_KEY || '',
            model: 'gemini-pro',
            temperature: 0.7
        }
    },
    network: {
        websocket: {
            url: 'ws://localhost:8080',
            reconnectAttempts: 5,
            reconnectDelay: 1000,
            heartbeatInterval: 30000
        },
        webrtc: {
            enabled: false,
            iceServers: [
                { urls: ['stun:stun.l.google.com:19302'] }
            ]
        }
    },
    engine: {
        targetFPS: 60,
        debug: true,
        maxAgents: 10,
        tickRate: 20
    }
};