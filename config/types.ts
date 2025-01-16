export class NetworkManager {
    private socket: WebSocket | null = null;
    private messageQueue: NetworkMessage[] = [];
    private config: NetworkConfig;
    private reconnectAttempts: number = 0;
    private heartbeatInterval: number;
    private handlers: Map<string, Set<(data: any) => void>>;

    constructor(config: NetworkConfig) {
        this.config = config;
        this.handlers = new Map();
        this.heartbeatInterval = 0;
    }

    public async connect(): Promise<void> {
        if (this.socket?.readyState === WebSocket.OPEN) return;

        return new Promise((resolve, reject) => {
            try {
                this.socket = new WebSocket(this.config.url);

                this.socket.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.startHeartbeat();
                    this.flushMessageQueue();
                    resolve();
                };

                this.socket.onclose = () => {
                    console.log('WebSocket closed');
                    this.stopHeartbeat();
                    this.handleReconnect();
                };

                this.socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };

                this.socket.onmessage = (event) => {
                    try {
                        const message: NetworkMessage = JSON.parse(event.data);
                        this.handleMessage(message);
                    } catch (error) {
                        console.error('Error parsing message:', error);
                    }
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    public send(type: string, data: any): void {
        const message: NetworkMessage = {
            type,
            data,
            timestamp: Date.now(),
            sender: 'client' // Could be replaced with actual client ID
        };

        if (this.socket?.readyState !== WebSocket.OPEN) {
            this.messageQueue.push(message);
            return;
        }

        this.socket.send(JSON.stringify(message));
    }

    public on(type: string, handler: (data: any) => void): () => void {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, new Set());
        }

        const handlers = this.handlers.get(type)!;
        handlers.add(handler);

        return () => {
            handlers.delete(handler);
        };
    }

    private handleMessage(message: NetworkMessage): void {
        const handlers = this.handlers.get(message.type);
        if (!handlers) return;

        for (const handler of handlers) {
            try {
                handler(message.data);
            } catch (error) {
                console.error('Error in message handler:', error);
            }
        }
    }

    private async handleReconnect(): Promise<void> {
        if (this.reconnectAttempts >= this.config.reconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.config.reconnectDelay * this.reconnectAttempts;

        console.log(`Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts})`);
        await new Promise(resolve => setTimeout(resolve, delay));

        this.connect();
    }

    private startHeartbeat(): void {
        this.heartbeatInterval = window.setInterval(() => {
            this.send('heartbeat', { timestamp: Date.now() });
        }, this.config.heartbeatInterval);
    }

    private stopHeartbeat(): void {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
    }

    private flushMessageQueue(): void {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            if (message) {
                this.send(message.type, message.data);
            }
        }
    }

    public disconnect(): void {
        this.stopHeartbeat();
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}