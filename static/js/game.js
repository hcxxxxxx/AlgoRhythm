/**
 * 音游游戏引擎
 */
class RhythmGame {
    /**
     * 初始化游戏
     * @param {Object} config 游戏配置
     */
    constructor(config) {
        this.config = Object.assign({
            containerId: 'game-container',  // 游戏容器ID
            lanes: 4,  // 轨道数量
            baseNoteSpeed: 600,  // 基础音符下落速度(像素/秒)
            audioPath: null,  // 音频文件路径
            chartData: null,  // 谱面数据
            judgeLine: 100,   // 判定线位置(距底部像素)
            offset: 0         // 音频偏移(毫秒)
        }, config);
        
        // 计算实际音符下落速度（根据BPM调整）
        this.noteSpeed = this._calculateNoteSpeed();
        
        // 游戏状态
        this.isPlaying = false;
        this.isPaused = false;
        this.startTime = 0;
        this.currentTime = 0;
        this.score = 0;
        this.combo = 0;
        this.maxCombo = 0;
        this.judgeResults = {
            perfect: 0,
            great: 0,
            good: 0,
            miss: 0
        };
        
        // 谱面和音符数据
        this.chart = null;
        this.audioElement = null;
        this.activeNotes = [];
        this.processedNotes = new Set();
        
        // 初始化DOM元素
        this.container = document.getElementById(this.config.containerId);
        this.scoreDisplay = document.getElementById('score-display');
        this.comboDisplay = document.getElementById('combo-display');
        
        // 初始化游戏区域
        this._setupGameArea();
        
        // 初始化音频
        if (this.config.audioPath) {
            this._setupAudio(this.config.audioPath);
        }
        
        // 初始化谱面
        if (this.config.chartData) {
            this._loadChart(this.config.chartData);
        }
        
        // 键盘事件监听
        this._setupKeyboardEvents();
        
        // 初始化游戏循环
        this.lastFrameTime = 0;
        this.animationFrameId = null;
    }
    
    /**
     * 计算音符下落速度
     * @private
     * @returns {number} 音符下落速度(像素/秒)
     */
    _calculateNoteSpeed() {
        if (!this.chart || !this.chart.tempo) {
            return this.config.baseNoteSpeed;
        }
        
        // 根据BPM调整音符下落速度
        // 基准：120BPM对应基础速度
        const bpmFactor = this.chart.tempo / 120;
        return this.config.baseNoteSpeed * bpmFactor;
    }
    
    /**
     * 设置游戏区域
     * @private
     */
    _setupGameArea() {
        this.container.innerHTML = '';
        this.container.style.position = 'relative';
        
        // 创建轨道容器
        const lanesContainer = document.createElement('div');
        lanesContainer.className = 'game-lanes';
        this.container.appendChild(lanesContainer);
        
        // 创建轨道
        for (let i = 0; i < this.config.lanes; i++) {
            const lane = document.createElement('div');
            lane.className = 'game-lane';
            lanesContainer.appendChild(lane);
            
            // 创建打击区域
            const hitArea = document.createElement('div');
            hitArea.className = 'hit-area';
            hitArea.setAttribute('data-lane', i);
            
            const hitAreaInner = document.createElement('div');
            hitAreaInner.className = 'hit-area-inner';
            hitArea.appendChild(hitAreaInner);
            
            lane.appendChild(hitArea);
        }
        
        // 创建判定线
        const judgeLine = document.createElement('div');
        judgeLine.className = 'judge-line';
        judgeLine.style.bottom = `${this.config.judgeLine}px`;
        this.container.appendChild(judgeLine);
        
        // 创建判定效果显示
        const judgeEffect = document.createElement('div');
        judgeEffect.className = 'judge-effect';
        judgeEffect.id = 'judge-effect';
        this.container.appendChild(judgeEffect);
        
        // 创建结果界面
        const resultScreen = document.createElement('div');
        resultScreen.className = 'result-screen';
        resultScreen.id = 'result-screen';
        resultScreen.innerHTML = `
            <div class="result-title">游戏结束</div>
            <div class="result-score" id="result-score">0</div>
            <div class="result-rank" id="result-rank">F</div>
            <div class="result-stats">
                <div class="label">准确率:</div>
                <div class="value" id="result-accuracy">0%</div>
                <div class="label">最大连击:</div>
                <div class="value" id="result-max-combo">0</div>
                <div class="label">Perfect:</div>
                <div class="value" id="result-perfect">0</div>
                <div class="label">Great:</div>
                <div class="value" id="result-great">0</div>
                <div class="label">Good:</div>
                <div class="value" id="result-good">0</div>
                <div class="label">Miss:</div>
                <div class="value" id="result-miss">0</div>
            </div>
            <div class="result-actions">
                <button class="btn" id="btn-retry">重新开始</button>
                <button class="btn btn-secondary" id="btn-back">返回</button>
            </div>
        `;
        this.container.appendChild(resultScreen);
        
        // 设置结果界面按钮事件
        document.getElementById('btn-retry').addEventListener('click', () => {
            this.restart();
        });
        
        document.getElementById('btn-back').addEventListener('click', () => {
            window.location.href = '/upload';
        });
    }
    
    /**
     * 设置音频
     * @param {string} audioPath 音频文件路径
     * @private
     */
    _setupAudio(audioPath) {
        this.audioElement = new Audio(audioPath);
        this.audioElement.volume = 0.8;
        
        // 添加音频加载事件
        this.audioElement.addEventListener('loadeddata', () => {
            console.log('音频加载完成，时长:', this.audioElement.duration);
        });
        
        // 添加音频错误处理
        this.audioElement.addEventListener('error', (e) => {
            console.error('音频加载失败:', e);
            alert('音频加载失败，请重试');
        });
        
        // 音频结束事件
        this.audioElement.addEventListener('ended', () => {
            this.stop();
            this._showResult();
        });
        
        // 预加载音频
        this.audioElement.load();
    }
    
    /**
     * 加载谱面数据
     * @param {Object} chartData 谱面数据
     * @private
     */
    _loadChart(chartData) {
        this.chart = chartData;
        console.log('谱面加载成功:', this.chart);
    }
    
    /**
     * 设置键盘事件
     * @private
     */
    _setupKeyboardEvents() {
        // 键盘按键映射
        const keyMap = {
            'd': 0,
            'f': 1,
            'j': 2,
            'k': 3
        };
        
        document.addEventListener('keydown', (event) => {
            if (!this.isPlaying || this.isPaused) return;
            
            const key = event.key.toLowerCase();
            if (keyMap.hasOwnProperty(key)) {
                const lane = keyMap[key];
                this._handleNoteHit(lane);
                
                // 显示按键效果
                const hitArea = document.querySelector(`.hit-area[data-lane="${lane}"] .hit-area-inner`);
                if (hitArea) {
                    hitArea.classList.add('active');
                    
                    // 创建波动效果
                    this._createRippleEffect(lane);
                }
            }
        });
        
        document.addEventListener('keyup', (event) => {
            const key = event.key.toLowerCase();
            if (keyMap.hasOwnProperty(key)) {
                const lane = keyMap[key];
                const hitArea = document.querySelector(`.hit-area[data-lane="${lane}"] .hit-area-inner`);
                if (hitArea) {
                    hitArea.classList.remove('active');
                }
            }
            
            // 空格键暂停/继续
            if (event.key === ' ' && this.isPlaying) {
                this.togglePause();
            }
        });
    }
    
    /**
     * 创建判定线波动效果
     * @param {number} lane 轨道索引
     * @private
     */
    _createRippleEffect(lane) {
        // 创建波动元素
        const ripple = document.createElement('div');
        ripple.className = 'judge-line-ripple';
        
        // 获取游戏轨道容器
        const lanesContainer = document.querySelector('.game-lanes');
        if (!lanesContainer) return;
        
        // 获取轨道元素
        const laneElement = lanesContainer.children[lane];
        if (!laneElement) return;
        
        // 计算波动位置（相对于判定线）
        const laneRect = laneElement.getBoundingClientRect();
        const judgeLineRect = document.querySelector('.judge-line').getBoundingClientRect();
        
        // 计算波动的水平位置（轨道中心）
        const rippleX = laneRect.left - judgeLineRect.left + (laneRect.width / 2);
        
        // 设置波动位置
        ripple.style.left = `${rippleX}px`;
        ripple.style.top = '50%';
        
        // 将波动添加到判定线
        const judgeLine = document.querySelector('.judge-line');
        if (judgeLine) {
            judgeLine.appendChild(ripple);
            
            // 动画结束后移除元素
            ripple.addEventListener('animationend', () => {
                ripple.remove();
            });
        }
    }
    
    /**
     * 处理音符点击
     * @param {number} lane 轨道索引
     * @private
     */
    _handleNoteHit(lane) {
        // 找到最接近判定线的音符
        let closestNote = null;
        let minTimeDiff = Infinity;
        
        for (const note of this.activeNotes) {
            if (note.lane === lane && !this.processedNotes.has(note.id)) {
                // 计算音符与判定时间的差值
                const timeDiff = Math.abs(note.time - (this.currentTime + this.config.offset / 1000));
                
                // 如果这个音符比之前找到的更近判定线
                if (timeDiff < minTimeDiff) {
                    minTimeDiff = timeDiff;
                    closestNote = note;
                }
            }
        }
        
        // 如果找到了音符，且在判定范围内
        if (closestNote && minTimeDiff <= 0.2) {
            this._judgeNote(closestNote, minTimeDiff);
        }
    }
    
    /**
     * 判定音符
     * @param {Object} note 音符对象
     * @param {number} timeDiff 时间差值
     * @private
     */
    _judgeNote(note, timeDiff) {
        // 标记音符为已处理
        this.processedNotes.add(note.id);
        
        // 根据时间差判定等级
        let judgeResult;
        if (timeDiff <= 0.05) {
            judgeResult = 'perfect';
            this.score += 100;
            this.combo++;
        } else if (timeDiff <= 0.1) {
            judgeResult = 'great';
            this.score += 80;
            this.combo++;
        } else if (timeDiff <= 0.15) {
            judgeResult = 'good';
            this.score += 50;
            this.combo++;
        } else {
            judgeResult = 'miss';
            this.combo = 0;
        }
        
        // 更新判定统计
        this.judgeResults[judgeResult]++;
        
        // 更新最大连击
        if (this.combo > this.maxCombo) {
            this.maxCombo = this.combo;
        }
        
        // 显示判定效果
        this._showJudgeEffect(judgeResult);
        
        // 更新显示
        this._updateDisplay();
        
        // 移除音符元素
        const noteElement = document.getElementById(`note-${note.id}`);
        if (noteElement) {
            noteElement.remove();
        }
    }
    
    /**
     * 显示判定效果
     * @param {string} result 判定结果
     * @private
     */
    _showJudgeEffect(result) {
        const judgeEffect = document.getElementById('judge-effect');
        judgeEffect.textContent = result.toUpperCase();
        judgeEffect.className = 'judge-effect';
        
        // 添加判定效果样式
        setTimeout(() => {
            judgeEffect.classList.add(result);
            judgeEffect.classList.add('show');
        }, 10);
        
        // 移除判定效果
        setTimeout(() => {
            judgeEffect.classList.remove('show');
        }, 500);
    }
    
    /**
     * 更新分数和连击显示
     * @private
     */
    _updateDisplay() {
        if (this.scoreDisplay) {
            this.scoreDisplay.textContent = this.score;
        }
        
        if (this.comboDisplay) {
            this.comboDisplay.textContent = this.combo > 1 ? `${this.combo} COMBO` : '';
        }
    }
    
    /**
     * 显示结果界面
     * @private
     */
    _showResult() {
        const totalNotes = Object.values(this.judgeResults).reduce((acc, val) => acc + val, 0);
        if (totalNotes === 0) return;
        
        // 计算准确率
        const accuracy = (this.judgeResults.perfect * 100 + this.judgeResults.great * 80 + this.judgeResults.good * 50) / (totalNotes * 100);
        
        // 确定评级
        let rank = 'F';
        if (accuracy >= 0.95) {
            rank = 'S';
        } else if (accuracy >= 0.9) {
            rank = 'A';
        } else if (accuracy >= 0.8) {
            rank = 'B';
        } else if (accuracy >= 0.7) {
            rank = 'C';
        } else if (accuracy >= 0.6) {
            rank = 'D';
        }
        
        // 更新结果界面
        document.getElementById('result-score').textContent = this.score;
        document.getElementById('result-rank').textContent = rank;
        document.getElementById('result-rank').className = `result-rank ${rank}`;
        document.getElementById('result-accuracy').textContent = `${(accuracy * 100).toFixed(2)}%`;
        document.getElementById('result-max-combo').textContent = this.maxCombo;
        document.getElementById('result-perfect').textContent = this.judgeResults.perfect;
        document.getElementById('result-great').textContent = this.judgeResults.great;
        document.getElementById('result-good').textContent = this.judgeResults.good;
        document.getElementById('result-miss').textContent = this.judgeResults.miss;
        
        // 显示结果界面
        const resultScreen = document.getElementById('result-screen');
        resultScreen.classList.add('show');
    }
    
    /**
     * 游戏循环
     * @param {number} timestamp 当前时间戳
     * @private
     */
    _gameLoop(timestamp) {
        if (!this.isPlaying || this.isPaused) return;
        
        // 使用音频当前时间作为游戏时间基准
        this.currentTime = this.audioElement.currentTime;
        
        // 更新并渲染音符
        this._updateNotes();
        
        // 检查Miss的音符
        this._checkMissedNotes();
        
        // 请求下一帧
        this.animationFrameId = requestAnimationFrame(this._gameLoop.bind(this));
    }
    
    /**
     * 更新音符位置
     * @private
     */
    _updateNotes() {
        // 更新活动音符列表
        this.activeNotes = this.chart.notes.filter(note => {
            const timeToHit = note.time - this.currentTime;
            // 根据BPM动态调整预显示时间
            const previewTime = Math.min(4, (this.container.clientHeight - this.config.judgeLine) / this.noteSpeed);
            
            // 计算音符完全消失的时间点
            let disappearTime = -0.5;  // 基础消失时间
            
            // 如果是长音符，考虑尾部长度
            if ((note.type === 'hold' || note.type === 'slide') && note.duration > 0) {
                // 计算尾部完全消失所需的额外时间
                const tailDisappearTime = note.duration + (this.config.judgeLine / this.noteSpeed);
                disappearTime -= tailDisappearTime;
            }
            
            return timeToHit >= disappearTime && timeToHit <= previewTime;
        });
        
        // 为每个音符添加唯一ID
        this.activeNotes.forEach(note => {
            if (!note.id) {
                note.id = `${note.time}-${note.lane}`;
            }
        });
        
        // 清除不在活动列表中的音符元素
        const noteElements = document.querySelectorAll('.note');
        noteElements.forEach(el => {
            const noteId = el.id.replace('note-', '');
            if (!this.activeNotes.some(note => note.id === noteId)) {
                el.remove();
            }
        });
        
        // 渲染活动音符
        this.activeNotes.forEach(note => {
            if (this.processedNotes.has(note.id)) return;
            
            // 计算音符位置，考虑音符强度影响视觉效果
            const timeToHit = note.time - this.currentTime;
            const distance = timeToHit * this.noteSpeed;
            const yPosition = this.container.clientHeight - this.config.judgeLine - distance;
            
            let noteElement = document.getElementById(`note-${note.id}`);
            
            if (!noteElement) {
                noteElement = document.createElement('div');
                noteElement.id = `note-${note.id}`;
                noteElement.className = `note ${note.type}`;
                
                // 根据音符强度调整大小和亮度
                const scale = 1 + note.intensity * 0.2;  // 强音符略大
                const brightness = 100 + note.intensity * 50;  // 强音符更亮
                noteElement.style.transform = `translate(-50%, -50%) scale(${scale})`;
                noteElement.style.filter = `brightness(${brightness}%)`;
                
                // 处理长音符
                if ((note.type === 'hold' || note.type === 'slide') && note.duration > 0) {
                    const tail = document.createElement('div');
                    tail.className = 'note-tail';
                    // 根据BPM调整尾部长度
                    const tailHeight = note.duration * this.noteSpeed;
                    tail.style.height = `${tailHeight}px`;
                    noteElement.appendChild(tail);
                }
                
                // 将音符添加到对应的轨道中
                const lane = document.querySelector(`.game-lane:nth-child(${note.lane + 1})`);
                if (lane) {
                    lane.appendChild(noteElement);
                }
            }
            
            // 更新音符位置（现在只需要更新垂直位置）
            noteElement.style.top = `${yPosition}px`;
            noteElement.style.left = '50%';  // 在轨道中水平居中
        });
    }
    
    /**
     * 检查是否有错过的音符
     * @private
     */
    _checkMissedNotes() {
        const missThreshold = 0.2; // 200毫秒
        
        this.chart.notes.forEach(note => {
            // 跳过已处理的音符
            if (this.processedNotes.has(note.id)) return;
            
            // 如果音符已经过了判定点太久
            const timePassed = this.currentTime - note.time;
            if (timePassed > missThreshold) {
                this.processedNotes.add(note.id);
                this.judgeResults.miss++;
                this.combo = 0;
                this._updateDisplay();
                
                // 移除音符元素
                const noteElement = document.getElementById(`note-${note.id}`);
                if (noteElement) {
                    noteElement.remove();
                }
            }
        });
    }
    
    /**
     * 开始游戏
     */
    start() {
        if (!this.chart || !this.audioElement) {
            console.error('缺少谱面或音频数据');
            return;
        }
        
        // 确保音频已加载
        if (this.audioElement.readyState < 3) {
            console.log('等待音频加载...');
            this.audioElement.addEventListener('canplay', () => {
                this._startGame();
            }, { once: true });
            return;
        }
        
        this._startGame();
    }
    
    _startGame() {
        // 重新计算音符下落速度
        this.noteSpeed = this._calculateNoteSpeed();
        
        // 重置游戏状态
        this.isPlaying = true;
        this.isPaused = false;
        this.startTime = Date.now();
        this.lastFrameTime = performance.now();
        this.score = 0;
        this.combo = 0;
        this.maxCombo = 0;
        this.judgeResults = {
            perfect: 0,
            great: 0,
            good: 0,
            miss: 0
        };
        this.processedNotes = new Set();
        
        // 隐藏结果界面
        const resultScreen = document.getElementById('result-screen');
        resultScreen.classList.remove('show');
        
        // 为每个音符添加唯一ID
        this.chart.notes.forEach(note => {
            note.id = `${note.time}-${note.lane}`;
        });
        
        // 开始音频播放
        this.audioElement.currentTime = 0;
        Promise.resolve(this.audioElement.play()).catch(error => {
            console.error('音频播放失败:', error);
            this.stop();
            alert('音频播放失败，请重试');
        });
        
        // 开始游戏循环
        this.animationFrameId = requestAnimationFrame(this._gameLoop.bind(this));
        
        console.log('游戏开始');
    }
    
    /**
     * 暂停/继续游戏
     */
    togglePause() {
        if (!this.isPlaying) return;
        
        if (this.isPaused) {
            // 继续游戏
            this.isPaused = false;
            this.startTime = Date.now() - (this.currentTime * 1000);
            this.lastFrameTime = performance.now();
            this.audioElement.play();
            this.animationFrameId = requestAnimationFrame(this._gameLoop.bind(this));
        } else {
            // 暂停游戏
            this.isPaused = true;
            this.audioElement.pause();
            if (this.animationFrameId) {
                cancelAnimationFrame(this.animationFrameId);
            }
        }
    }
    
    /**
     * 停止游戏
     */
    stop() {
        this.isPlaying = false;
        this.isPaused = false;
        
        // 停止音频
        if (this.audioElement) {
            this.audioElement.pause();
        }
        
        // 停止游戏循环
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
        
        console.log('游戏结束');
    }
    
    /**
     * 重新开始游戏
     */
    restart() {
        this.stop();
        this.container.querySelectorAll('.note').forEach(el => el.remove());
        this.start();
    }
}

// 当页面加载完成时初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    const sessionId = document.getElementById('session-id').value;
    const audioPath = document.getElementById('audio-path').value;
    
    // 加载谱面数据
    fetch(`/api/chart/${sessionId}`)
        .then(response => response.json())
        .then(chartData => {
            // 创建游戏实例
            const game = new RhythmGame({
                containerId: 'game-container',
                lanes: 4,
                baseNoteSpeed: 600,
                audioPath: audioPath,
                chartData: chartData,
                offset: 0
            });
            
            // 为控制按钮绑定事件
            document.getElementById('btn-start').addEventListener('click', () => {
                game.start();
                document.getElementById('btn-start').style.display = 'none';
                document.getElementById('btn-restart').style.display = 'inline-block';
            });
            
            document.getElementById('btn-restart').addEventListener('click', () => {
                game.restart();
            });
            
            document.getElementById('btn-pause').addEventListener('click', () => {
                game.togglePause();
                const btnPause = document.getElementById('btn-pause');
                btnPause.textContent = game.isPaused ? '继续' : '暂停';
            });
        })
        .catch(error => {
            console.error('加载谱面失败:', error);
            alert('加载谱面失败，请重试');
        });
});