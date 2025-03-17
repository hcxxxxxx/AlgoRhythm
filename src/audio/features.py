import numpy as np

class AudioFeatures:
    """存储音频特征的数据结构"""
    
    def __init__(self):
        # 基本信息
        self.duration = 0.0     # 音频时长(秒)
        
        # 节拍特征
        self.tempo = 0.0        # 速度(BPM)
        self.beats = np.array([])  # 节拍帧位置
        self.beat_times = np.array([])  # 节拍时间点(秒)
        
        # 音符起始特征
        self.onset_strength = np.array([])  # 音符起始强度序列
        self.onset_frames = np.array([])    # 音符起始帧位置
        self.onset_times = np.array([])     # 音符起始时间点(秒)
        self.note_intensities = np.array([])  # 每个音符的强度
        
        # 频谱特征
        self.harmonic = np.array([])        # 和声部分波形
        self.percussive = np.array([])      # 打击乐部分波形
        self.pitches = np.array([])         # 音高信息
        self.magnitudes = np.array([])      # 音高强度

    def get_beat_count(self):
        """获取节拍数量"""
        return len(self.beats)
    
    def get_note_count(self):
        """获取音符数量"""
        return len(self.onset_frames)
    
    def get_notes_in_beat_range(self, start_beat_idx, end_beat_idx):
        """获取指定节拍范围内的音符索引
        
        Args:
            start_beat_idx: 起始节拍索引
            end_beat_idx: 结束节拍索引
            
        Returns:
            list: 该范围内的音符索引列表
        """
        if len(self.beats) == 0 or len(self.onset_times) == 0:
            return []
            
        if start_beat_idx >= len(self.beat_times) or end_beat_idx >= len(self.beat_times):
            return []
            
        start_time = self.beat_times[start_beat_idx]
        end_time = self.beat_times[end_beat_idx]
        
        note_indices = []
        for i, note_time in enumerate(self.onset_times):
            if start_time <= note_time < end_time:
                note_indices.append(i)
                
        return note_indices
    
    def get_intensity_at_time(self, time):
        """获取指定时间点的音频强度
        
        Args:
            time: 时间点(秒)
            
        Returns:
            float: 该时间点的音频强度(0-1之间)
        """
        if len(self.onset_times) == 0 or len(self.note_intensities) == 0:
            return 0.0
            
        # 找到最接近的音符
        closest_idx = np.argmin(np.abs(self.onset_times - time))
        
        # 如果时间差大于0.1秒，认为没有音符
        if abs(self.onset_times[closest_idx] - time) > 0.1:
            return 0.0
            
        return self.note_intensities[closest_idx]