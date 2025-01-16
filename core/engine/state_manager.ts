export class StateManager {
    private state: GameState;
    private subscribers: Map<string, Set<(state: Partial<GameState>) => void>>;

    constructor() {
        this.state = {
            agents: new Map(),
            world: {
                entities: new Map(),
                environment: {
                    time: Date.now(),
                    weather: 'clear',
                    settings: {}
                },
                timestamp: Date.now()
            },
            timestamp: Date.now(),
            version: '1.0.0'
        };
        this.subscribers = new Map();
    }

    public updateAgent(id: string, state: Partial<AgentState>): void {
        const currentState = this.state.agents.get(id) || {
            id,
            position: { x: 0, y: 0, z: 0 },
            status: 'idle',
            metadata: {}
        };

        const newState = { ...currentState, ...state };
        this.state.agents.set(id, newState);
        this.notify('agent', { [id]: newState });
    }

    public updateWorld(update: Partial<WorldState>): void {
        this.state.world = { ...this.state.world, ...update };
        this.notify('world', this.state.world);
    }

    public subscribe(type: string, callback: (state: Partial<GameState>) => void): () => void {
        if (!this.subscribers.has(type)) {
            this.subscribers.set(type, new Set());
        }

        const subscribers = this.subscribers.get(type)!;
        subscribers.add(callback);

        // Return unsubscribe function
        return () => {
            subscribers.delete(callback);
        };
    }

    private notify(type: string, update: Partial<GameState>): void {
        const subscribers = this.subscribers.get(type);
        if (!subscribers) return;

        for (const callback of subscribers) {
            try {
                callback(update);
            } catch (error) {
                console.error('Error in subscriber:', error);
            }
        }
    }

    public getState(): GameState {
        return this.state;
    }

    public serialize(): string {
        return JSON.stringify(this.state);
    }

    public deserialize(data: string): void {
        const parsed = JSON.parse(data);
        this.state = {
            ...parsed,
            agents: new Map(Object.entries(parsed.agents)),
            world: {
                ...parsed.world,
                entities: new Map(Object.entries(parsed.world.entities))
            }
        };
    }
}