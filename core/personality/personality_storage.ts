import { EventEmitter } from 'events';

export interface PersonalityTrait {
    name: string;
    value: number;  // 0-1 scale
    category: 'emotional' | 'behavioral' | 'cognitive' | 'social';
    description: string;
}

export interface Personality {
    id: string;
    baseTraits: Map<string, PersonalityTrait>;
    adaptiveTraits: Map<string, PersonalityTrait>;
    mood: {
        happiness: number;
        energy: number;
        stress: number;
        dominance: number;
    };
    relationships: Map<string, number>;  // agent ID to relationship strength (-1 to 1)
}

export class PersonalityStorage extends EventEmitter {
    private personalities: Map<string, Personality> = new Map();
    private templates: Map<string, Partial<Personality>> = new Map();

    constructor() {
        super();
        this.initializeTemplates();
    }

    private initializeTemplates(): void {
        // Friendly personality template
        this.templates.set('friendly', {
            baseTraits: new Map([
                ['openness', { name: 'openness', value: 0.7, category: 'cognitive', description: 'Willingness to try new experiences' }],
                ['empathy', {
                    name: 'empathy', value: 0.8, category: 'emotional', description: 'Ability to understand others' feelings' }],
        ['sociability', { name: 'sociability', value: 0.9, category: 'social', description: 'Tendency to seek social interaction' }]
      ]),
            mood: {
                happiness: 0.7,
                energy: 0.6,
                stress: 0.3,
                dominance: 0.4
            }
        });

        // Analytical personality template
        this.templates.set('analytical', {
            baseTraits: new Map([
                ['logic', { name: 'logic', value: 0.9, category: 'cognitive', description: 'Preference for logical thinking' }],
                ['precision', { name: 'precision', value: 0.8, category: 'behavioral', description: 'Attention to detail' }],
                ['curiosity', { name: 'curiosity', value: 0.7, category: 'cognitive', description: 'Drive to learn and understand' }]
            ]),
            mood: {
                happiness: 0.5,
                energy: 0.6,
                stress: 0.4,
                dominance: 0.5
            }
        });
    }

    public createPersonality(agentId: string, template?: string): Personality {
        let personality: Personality = {
            id: agentId,
            baseTraits: new Map(),
            adaptiveTraits: new Map(),
            mood: {
                happiness: 0.5,
                energy: 0.5,
                stress: 0.5,
                dominance: 0.5
            },
            relationships: new Map()
        };

        if (template && this.templates.has(template)) {
            const templateData = this.templates.get(template)!;
            personality = {
                ...personality,
                ...templateData,
                baseTraits: new Map([...templateData.baseTraits || [], ...personality.baseTraits]),
                adaptiveTraits: new Map()
            };
        }

        this.personalities.set(agentId, personality);
        this.emit('personalityCreated', { agentId, personality });
        return personality;
    }

    public getPersonality(agentId: string): Personality | undefined {
        return this.personalities.get(agentId);
    }

    public updateTrait(agentId: string, traitName: string, value: number, isAdaptive: boolean = false): void {
        const personality = this.personalities.get(agentId);
        if (!personality) return;

        const traitMap = isAdaptive ? personality.adaptiveTraits : personality.baseTraits;
        const trait = traitMap.get(traitName);

        if (trait) {
            trait.value = Math.max(0, Math.min(1, value));
            this.emit('traitUpdated', { agentId, traitName, value, isAdaptive });
        }
    }

    public updateMood(agentId: string, moodUpdates: Partial<Personality['mood']>): void {
        const personality = this.personalities.get(agentId);
        if (!personality) return;

        Object.entries(moodUpdates).forEach(([key, value]) => {
            if (key in personality.mood) {
                personality.mood[key as keyof Personality['mood']] = Math.max(0, Math.min(1, value));
            }
        });

        this.emit('moodUpdated', { agentId, mood: personality.mood });
    }

    public addTemplate(name: string, template: Partial<Personality>): void {
        this.templates.set(name, template);
    }

    public getTemplates(): string[] {
        return Array.from(this.templates.keys());
    }
}