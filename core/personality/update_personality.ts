import { Personality, PersonalityTrait } from './PersonalityStorage';

interface EmotionalEvent {
    type: string;
    intensity: number;
    valence: number;  // -1 to 1, negative to positive
    source: string;
    context?: Record<string, any>;
}

interface PersonalityUpdate {
    traitUpdates: Map<string, number>;
    moodUpdates: Partial<Personality['mood']>;
    relationshipUpdates: Map<string, number>;
}

export class PersonalityUpdater {
    private readonly decayRate: number = 0.1;
    private readonly adaptationRate: number = 0.05;
    private readonly emotionalMemory: Map<string, EmotionalEvent[]> = new Map();

    public processEvent(personality: Personality, event: EmotionalEvent): PersonalityUpdate {
        // Store event in emotional memory
        if (!this.emotionalMemory.has(personality.id)) {
            this.emotionalMemory.set(personality.id, []);
        }
        this.emotionalMemory.get(personality.id)?.push(event);

        // Calculate updates based on event
        const traitUpdates = this.calculateTraitUpdates(personality, event);
        const moodUpdates = this.calculateMoodUpdates(personality, event);
        const relationshipUpdates = this.calculateRelationshipUpdates(personality, event);

        return {
            traitUpdates,
            moodUpdates,
            relationshipUpdates
        };
    }

    private calculateTraitUpdates(personality: Personality, event: EmotionalEvent): Map<string, number> {
        const updates = new Map<string, number>();

        // Example trait update rules
        switch (event.type) {
            case 'socialInteraction':
                updates.set('sociability', event.valence * this.adaptationRate);
                break;
            case 'challenge':
                updates.set('resilience', event.intensity * this.adaptationRate);
                break;
            case 'learning':
                updates.set('curiosity', event.valence * this.adaptationRate);
                break;
        }

        return updates;
    }

    private calculateMoodUpdates(personality: Personality, event: EmotionalEvent): Partial<Personality['mood']> {
        const moodUpdates: Partial<Personality['mood']> = {};

        // Base mood impact
        moodUpdates.happiness = event.valence * event.intensity;
        moodUpdates.energy = event.intensity * (event.valence > 0 ? 1 : -0.5);
        moodUpdates.stress = event.intensity * (event.valence < 0 ? 1 : -0.5);

        // Context-specific adjustments
        if (event.type === 'conflict') {
            moodUpdates.stress = Math.min(1, (moodUpdates.stress || 0) + 0.2);
            moodUpdates.dominance = event.valence > 0 ? 0.1 : -0.1;
        }

        return moodUpdates;
    }

    private calculateRelationshipUpdates(personality: Personality, event: EmotionalEvent): Map<string, number> {
        const updates = new Map<string, number>();

        if (event.source && event.source !== personality.id) {
            const currentRelationship = personality.relationships.get(event.source) || 0;
            const update = event.valence * event.intensity * this.adaptationRate;
            updates.set(event.source, Math.max(-1, Math.min(1, currentRelationship + update)));
        }

        return updates;
    }

    public decayPersonality(personality: Personality): PersonalityUpdate {
        const traitUpdates = new Map<string, number>();
        const moodUpdates: Partial<Personality['mood']> = {};

        // Decay adaptive traits towards base traits
        personality.adaptiveTraits.forEach((trait, name) => {
            const baseTrait = personality.baseTraits.get(name);
            if (baseTrait) {
                const diff = baseTrait.value - trait.value;
                traitUpdates.set(name, diff * this.decayRate);
            }
        });

        // Decay moods towards neutral
        Object.entries(personality.mood).forEach(([key, value]) => {
            const diff = 0.5 - value;
            moodUpdates[key as keyof Personality['mood']] = diff * this.decayRate;
        });

        return {
            traitUpdates,
            moodUpdates,
            relationshipUpdates: new Map()
        };
    }

    public getEmotionalMemory(personalityId: string, limit?: number): EmotionalEvent[] {
        const memory = this.emotionalMemory.get(personalityId) || [];
        return limit ? memory.slice(-limit) : memory;
    }

    public clearEmotionalMemory(personalityId: string): void {
        this.emotionalMemory.delete(personalityId);
    }
}