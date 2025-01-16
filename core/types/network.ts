export interface NetworkMessage {
    type: string;
    data: any;
    timestamp: number;
    sender: string;
}

export interface NetworkConfig {
    url: string;
    reconnectAttempts: number;
    reconnectDelay: number;
    heartbeatInterval: number;
}