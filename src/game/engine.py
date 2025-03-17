import time

class GameEngine:
    """游戏引擎，负责处理游戏逻辑"""
    
    def __init__(self, chart):
        """初始化游戏引擎
        
        Args:
            chart: 谱面对象
        """
        self.chart = chart
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_count = 0
        self.great_count = 0
        self.good_count = 0
        self.miss_count = 0
        self.start_time = 0
        self.is_playing = False
    
    def start_game(self):
        """开始游戏"""
        self.start_time = time.time()
        self.is_playing = True
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_count = 0
        self.great_count = 0
        self.good_count = 0
        self.miss_count = 0
    
    def pause_game(self):
        """暂停游戏"""
        self.is_playing = False
    
    def resume_game(self):
        """恢复游戏"""
        self.is_playing = True
    
    def get_elapsed_time(self):
        """获取游戏已进行的时间
        
        Returns:
            float: 游戏已进行的时间(秒)
        """
        if not self.is_playing:
            return 0
        return time.time() - self.start_time
    
    def get_active_notes(self, current_time, lookahead=2.0):
        """获取当前需要显示的音符
        
        Args:
            current_time: 当前游戏时间(秒)
            lookahead: 提前显示的时间(秒)
            
        Returns:
            list: 当前需要显示的音符列表
        """
        return self.chart.get_notes_in_time_range(
            current_time, current_time + lookahead
        )
    
    def judge_note(self, note, hit_time):
        """判断音符击打精准度
        
        Args:
            note: 音符对象
            hit_time: 击打时间(秒)
            
        Returns:
            str: 判定结果('perfect', 'great', 'good', 'miss')
        """
        time_diff = abs(hit_time - note.time)
        
        # 判定标准
        if time_diff < 0.05:
            result = 'perfect'
            self.perfect_count += 1
            self.score += 100
            self.combo += 1
        elif time_diff < 0.1:
            result = 'great'
            self.great_count += 1
            self.score += 80
            self.combo += 1
        elif time_diff < 0.15:
            result = 'good'
            self.good_count += 1
            self.score += 50
            self.combo += 1
        else:
            result = 'miss'
            self.miss_count += 1
            self.combo = 0
        
        # 更新最大连击数
        if self.combo > self.max_combo:
            self.max_combo = self.combo
            
        return result
    
    def calculate_final_score(self):
        """计算最终得分和评级
        
        Returns:
            dict: 包含得分和评级的字典
        """
        total_notes = self.perfect_count + self.great_count + self.good_count + self.miss_count
        if total_notes == 0:
            return {'score': 0, 'rank': 'F', 'accuracy': 0.0}
        
        # 计算准确率
        accuracy = (self.perfect_count * 100 + self.great_count * 80 + self.good_count * 50) / (total_notes * 100)
        
        # 评级
        rank = 'F'
        if accuracy >= 0.95:
            rank = 'S'
        elif accuracy >= 0.9:
            rank = 'A'
        elif accuracy >= 0.8:
            rank = 'B'
        elif accuracy >= 0.7:
            rank = 'C'
        elif accuracy >= 0.6:
            rank = 'D'
        
        return {
            'score': self.score,
            'rank': rank,
            'accuracy': accuracy * 100,  # 转为百分比
            'max_combo': self.max_combo,
            'perfect': self.perfect_count,
            'great': self.great_count,
            'good': self.good_count,
            'miss': self.miss_count
        }