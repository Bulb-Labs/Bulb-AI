import { EventEmitter } from 'events';

interface ConnectionStrength {
    value: number;  // -1 to 1
    trust: number;  // 0 to 1
    familiarity: number;  // 0 to 1
    lastInteraction: number;
}

interface AgentInteraction {
    type: string;
    sourceId: string;
    targetId: string;
    timestamp: number;
    content: any;
    impact: {
        trust: number;
        familiarity: number;
        connectionStrength: number;
    };
}

interface ConnectionRule {
    condition: (interaction: AgentInteraction) => boolean;
    impact: (interaction: AgentInteraction, current: ConnectionStrength) => Partial<ConnectionStrength>;
}

export class ConnectionManager extends EventEmitter {
    private connections: Map<string, Map<string, ConnectionStrength>> = new Map();
    private interactionHistory: Map<string, AgentInteraction[]> = new Map();
    private rules: ConnectionRule[] = [];

    constructor() {
        super();
        this.initializeDefaultRules();
    }

    private initializeDefaultRules(): void {
        // Rule for positive interactions
        this.addRule({
            condition: (interaction) => interaction.impact.connectionStrength > 0,
            impact: (interaction, current) => ({
                trust: Math.min(1, current.trust + interaction.impact.trust),
                familiarity: Math.min(1, current.familiarity + interaction.impact.familiarity),
                value: Math.min(1, current.value + interaction.impact.connectionStrength)
            })
        });

        // Rule for negative interactions
        this.addRule({
            condition: (interaction) => interaction.impact.connectionStrength < 0,
            impact: (interaction, current) => ({
                trust: Math.max(0, current.trust + interaction.impact.trust),
                value: Math.max(-1, current.value + interaction.impact.connectionStrength)
            })
        });
    }

    public addRule(rule: ConnectionRule): void {
        this.rules.push(rule);
    }

    public connect(sourceId: string, targetId: string, initialStrength: Partial<ConnectionStrength> = {}): void {
        if (!this.connections.has(sourceId)) {
            this.connections.set(sourceId, new Map());
        }

        const connection: ConnectionStrength = {
            value: initialStrength.value ?? 0,
            trust: initialStrength.trust ?? 0.1,
            familiarity: initialStrength.familiarity ?? 0,
            lastInteraction: Date.now()
        };

        this.connections.get(sourceId)!.set(targetId, connection);
        this.emit('connected', { sourceId, targetId, connection });
    }

    public disconnect(sourceId: string, targetId: string): void {
        this.connections.get(sourceId)?.delete(targetId);
        this.emit('disconnected', { sourceId, targetId });
    }

    public getConnection(sourceId: string, targetId: string): ConnectionStrength | undefined {
        return this.connections.get(sourceId)?.get(targetId);
    }

    public recordInteraction(interaction: AgentInteraction): void {
        // Store in history
        const key = `${interaction.sourceId}-${interaction.targetId}`;
        if (!this.interactionHistory.has(key)) {
            this.interactionHistory.set(key, []);
        }
        this.interactionHistory.get(key)!.push(interaction);

        // Update connection strength
        const connection = this.getConnection(interaction.sourceId, interaction.targetId);
        if (connection) {
            // Apply rules
            this.rules
                .filter(rule => rule.condition(interaction))
                .forEach(rule => {
                    const updates = rule.impact(interaction, connection);
                    Object.assign(connection, updates);
                });

            connection.lastInteraction = interaction.timestamp;
            this.emit('connectionUpdated', {
                sourceId: interaction.sourceId,
                targetId: interaction.targetId,
                connection,
                interaction
            });
        }
    }