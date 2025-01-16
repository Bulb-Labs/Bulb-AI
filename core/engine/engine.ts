export interface SystemFunction {
    (deltaTime: number): void | Promise<void>;
}

export interface GameMetrics {
    fps: number;
    frameTime: number;
    totalFrames: number;
    uptime: number;
}

export interface GameState {
    agents: Map<string, AgentState>;
    world: WorldState;
    timestamp: number;
    version: string;
}

export interface AgentState {
    id: string;
    position: Vector3;
    status: string;
    metadata: Record<string, any>;
}

export interface WorldState {
    entities: Map<string, Entity>;
    environment: Environment;
    timestamp: number;
}

export interface Vector3 {
    x: number;
    y: number;
    z: number;
}

export interface Entity {
    id: string;
    type: string;
    position: Vector3;
    metadata: Record<string, any>;
}

export interface Environment {
    time: number;
    weather: string;
    settings: Record<string, any>;
}
