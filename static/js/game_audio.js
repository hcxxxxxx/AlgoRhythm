class GameAudio {
    constructor(audioPath) {
        this.audio = new Audio(audioPath);
        this.isPlaying = false;
        this.startTime = 0;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 音频加载完成事件
        this.audio.addEventListener('loadeddata', () => {
            console.log('Audio loaded successfully');
        });

        // 音频播放错误事件
        this.audio.addEventListener('error', (e) => {
            console.error('Audio error:', e);
        });

        // 音频结束事件
        this.audio.addEventListener('ended', () => {
            this.isPlaying = false;
            this.onGameEnd && this.onGameEnd();
        });
    }

    play() {
        if (!this.isPlaying) {
            this.startTime = Date.now();
            this.audio.currentTime = 0;
            this.audio.play().catch(e => console.error('Play error:', e));
            this.isPlaying = true;
        }
    }

    pause() {
        if (this.isPlaying) {
            this.audio.pause();
            this.isPlaying = false;
        }
    }

    stop() {
        this.pause();
        this.audio.currentTime = 0;
    }

    getCurrentTime() {
        return this.isPlaying ? (Date.now() - this.startTime) / 1000 : 0;
    }

    setVolume(volume) {
        this.audio.volume = Math.max(0, Math.min(1, volume));
    }

    setOnGameEnd(callback) {
        this.onGameEnd = callback;
    }
} 