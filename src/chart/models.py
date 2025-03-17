class Note:
    """音符类，表示谱面中的一个音符"""
    
    def __init__(self, time, lane, type='tap', duration=0.0, intensity=0.5):
        """初始化音符
        
        Args:
            time: 音符出现时间(秒)
            lane: 音符所在轨道(0到lanes-1)
            type: 音符类型('tap', 'hold', 'slide')
            duration: 音符持续时间(秒)，对于长按和滑动音符有效
            intensity: 音符强度(0-1)，影响音符显示效果
        """
        self.time = time
        self.lane = lane
        self.type = type
        self.duration = duration
        self.intensity = intensity
    
    def to_dict(self):
        """转换为字典形式，用于JSON序列化"""
        return {
            'time': float(self.time),
            'lane': int(self.lane),
            'type': self.type,
            'duration': float(self.duration),
            'intensity': float(self.intensity)
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建音符对象
        
        Args:
            data: 字典数据
            
        Returns:
            Note: 音符对象
        """
        return cls(
            time=data['time'],
            lane=data['lane'],
            type=data['type'],
            duration=data.get('duration', 0.0),
            intensity=data.get('intensity', 0.5)
        )


class Chart:
    """谱面类，包含一个完整的音游关卡"""
    
    def __init__(self, tempo=120.0, duration=0.0, difficulty='normal'):
        """初始化谱面
        
        Args:
            tempo: 歌曲速度(BPM)
            duration: 歌曲时长(秒)
            difficulty: 难度级别('easy', 'normal', 'hard')
        """
        self.tempo = tempo
        self.duration = duration
        self.difficulty = difficulty
        self.notes = []
    
    def add_note(self, note):
        """添加音符到谱面
        
        Args:
            note: 要添加的音符对象
        """
        self.notes.append(note)
    
    def get_notes_in_time_range(self, start_time, end_time):
        """获取指定时间范围内的音符
        
        Args:
            start_time: 开始时间(秒)
            end_time: 结束时间(秒)
            
        Returns:
            list: 该时间范围内的音符列表
        """
        return [note for note in self.notes if start_time <= note.time < end_time]
    
    def sort_notes(self):
        """按时间对音符进行排序"""
        self.notes.sort(key=lambda note: note.time)
    
    def to_dict(self):
        """转换为字典形式，用于JSON序列化"""
        return {
            'tempo': self.tempo,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'notes': [note.to_dict() for note in self.notes]
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建谱面对象
        
        Args:
            data: 字典数据
            
        Returns:
            Chart: 谱面对象
        """
        chart = cls(
            tempo=data['tempo'],
            duration=data['duration'],
            difficulty=data['difficulty']
        )
        
        for note_data in data['notes']:
            note = Note.from_dict(note_data)
            chart.add_note(note)
            
        return chart