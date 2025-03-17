import numpy as np
import random
from src.chart.models import Chart, Note
from config import DIFFICULTY_LEVELS, LANES

class ChartGenerator:
    """谱面生成器，负责将音频特征转换为音游谱面"""
    
    def __init__(self, audio_features, difficulty='normal'):
        """初始化谱面生成器
        
        Args:
            audio_features: 音频特征对象
            difficulty: 难度级别 ('easy', 'normal', 'hard')
        """
        self.features = audio_features
        self.difficulty = difficulty
        self.difficulty_config = DIFFICULTY_LEVELS[difficulty]
        self.lanes = LANES
        self.notes = []
    
    def generate_chart(self):
        """生成音游谱面
        
        Returns:
            Chart: 生成的谱面对象
        """
        # 创建谱面对象
        chart = Chart(tempo=self.features.tempo, 
                     duration=self.features.duration,
                     difficulty=self.difficulty)
        
        # 分配音符到轨道
        self._assign_notes_to_lanes()
        
        # 添加音符到谱面
        for note in self.notes:
            chart.add_note(note)
            
        return chart
    
    def _assign_notes_to_lanes(self):
        """将音符分配到不同轨道"""
        if len(self.features.onset_times) == 0:
            return
        
        # 清空原有的音符列表
        self.notes = []
        
        # 处理每个检测到的音符起始点
        for i, time in enumerate(self.features.onset_times):
            # 获取音符强度，用于决定音符类型和轨道
            intensity = self.features.note_intensities[i] if i < len(self.features.note_intensities) else 0.5
            
            # 决定在这个时间点放置多少个音符 (基于难度)
            num_notes = self._decide_note_count(intensity)
            
            # 选择要使用的轨道
            lanes = self._select_lanes(num_notes, time)
            
            # 为每个选中的轨道创建音符
            for lane in lanes:
                note_type = self._decide_note_type(intensity)
                duration = self._decide_note_duration(note_type, time)
                
                note = Note(
                    time=time,
                    lane=lane,
                    type=note_type,
                    duration=duration,
                    intensity=intensity
                )
                self.notes.append(note)
    
    def _decide_note_count(self, intensity):
        """决定在一个时间点放置多少个音符
        
        Args:
            intensity: 音符强度 (0-1)
            
        Returns:
            int: 音符数量
        """
        max_notes = self.difficulty_config['max_notes_per_beat']
        
        # 音符强度越高，放置的音符越多
        prob_distribution = []
        for i in range(1, max_notes + 1):
            # 难度越高，多音符的概率越大
            if i == 1:
                prob_distribution.append(1.0 - intensity * 0.7)
            else:
                prob_distribution.append(intensity * 0.7 / (max_notes - 1))
                
        # 按概率分布随机选择音符数量
        return np.random.choice(range(1, max_notes + 1), p=prob_distribution)
    
    def _select_lanes(self, num_notes, time):
        """选择要使用的轨道
        
        Args:
            num_notes: 音符数量
            time: 音符时间
            
        Returns:
            list: 选中的轨道索引列表
        """
        available_lanes = list(range(self.lanes))
        
        # 避免选择到最近使用过的轨道
        recent_used_lanes = []
        time_threshold = 0.3  # 300毫秒内认为是最近使用的轨道
        
        for note in self.notes:
            if abs(note.time - time) < time_threshold:
                recent_used_lanes.append(note.lane)
        
        # 优先选择未使用的轨道
        preferred_lanes = [lane for lane in available_lanes if lane not in recent_used_lanes]
        
        if len(preferred_lanes) >= num_notes:
            return random.sample(preferred_lanes, num_notes)
        else:
            # 如果可用轨道不够，从所有轨道中随机选择
            return random.sample(available_lanes, num_notes)
    
    def _decide_note_type(self, intensity):
        """决定音符类型
        
        Args:
            intensity: 音符强度 (0-1)
            
        Returns:
            str: 音符类型 ('tap', 'hold', 'slide')
        """
        # 根据难度配置决定不同类型音符的概率
        hold_prob = self.difficulty_config['hold_note_prob']
        slide_prob = self.difficulty_config['slide_note_prob']
        tap_prob = 1.0 - hold_prob - slide_prob
        
        # 音符强度会影响类型选择
        if intensity > 0.8:
            # 强音符更可能是滑动或长按
            hold_prob *= 1.5
            slide_prob *= 1.5
        elif intensity < 0.3:
            # 弱音符更可能是单击
            tap_prob *= 1.5
            
        # 重新归一化概率
        total = tap_prob + hold_prob + slide_prob
        tap_prob /= total
        hold_prob /= total
        slide_prob /= total
        
        # 按概率随机选择类型
        rand = random.random()
        if rand < tap_prob:
            return 'tap'
        elif rand < tap_prob + hold_prob:
            return 'hold'
        else:
            return 'slide'
    
    def _decide_note_duration(self, note_type, start_time):
        """决定音符持续时间
        
        Args:
            note_type: 音符类型
            start_time: 音符开始时间
            
        Returns:
            float: 音符持续时间 (秒)
        """
        if note_type == 'tap':
            return 0.0  # 单击音符没有持续时间
            
        # 寻找下一个节拍或音符
        next_beat_time = None
        for beat_time in self.features.beat_times:
            if beat_time > start_time + 0.1:  # 至少持续0.1秒
                next_beat_time = beat_time
                break
                
        if next_beat_time is None:
            # 如果没有找到下一个节拍，使用默认持续时间
            return random.uniform(0.2, 0.5)
        
        # 根据音符类型调整持续时间
        if note_type == 'hold':
            # 长按音符持续到下一个节拍
            return next_beat_time - start_time
        elif note_type == 'slide':
            # 滑动音符持续时间略短
            return (next_beat_time - start_time) * 0.8
        
        return 0.0