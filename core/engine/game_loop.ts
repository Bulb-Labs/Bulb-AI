export class GameLoop {
    private systems: Set<SystemFunction>;
    private isRunning: boolean;
    private lastFrameTime: number;
    private frameCount: number;
    private startTime: number;
    private targetFPS: number;
    private frameTime: number;
    private rafId: number;

    constructor(targetFPS: number = 60) {
        this.systems = new Set();
        this.isRunning = false;
        this.lastFrameTime = 0;
        this.frameCount = 0;
        this.startTime = 0;
        this.targetFPS = targetFPS;
        this.frameTime = 1000 / targetFPS;
        this.rafId = 0;
    }

    public addSystem(system: SystemFunction): void {
        this.systems.add(system);
    }

    public removeSystem(system: SystemFunction): void {
        this.systems.delete(system);
    }

    public async start(): Promise<void> {
        if (this.isRunning) return;

        this.isRunning = true;
        this.startTime = performance.now();
        this.lastFrameTime = this.startTime;
        this.frameCount = 0;

        const gameLoop = async (timestamp: number) => {
            if (!this.isRunning) return;

            const deltaTime = timestamp - this.lastFrameTime;

            if (deltaTime >= this.frameTime) {
                // Execute all systems
                for (const system of this.systems) {
                    try {
                        await system(deltaTime);
                    } catch (error) {
                        console.error('Error in system:', error);
                    }
                }

                this.frameCount++;
                this.lastFrameTime = timestamp;
            }

            this.rafId = requestAnimationFrame(gameLoop);
        };

        this.rafId = requestAnimationFrame(gameLoop);
    }

    public stop(): void {
        this.isRunning = false;
        cancelAnimationFrame(this.rafId);
    }

    public getMetrics(): GameMetrics {
        const currentTime = performance.now();
        const elapsed = (currentTime - this.startTime) / 1000; // Convert to seconds

        return {
            fps: this.frameCount / elapsed,
            frameTime: this.lastFrameTime,
            totalFrames: this.frameCount,
            uptime: elapsed
        };
    }
}