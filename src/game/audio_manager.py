class AudioManager:
    """游戏音频管理器，负责处理音频播放和同步"""
    
    def __init__(self, audio_path):
        """初始化音频管理器
        
        Args:
            audio_path: 音频文件路径
        """
        self.audio_path = audio_path
        self.is_playing = False
        self.current_time = 0
        
    def to_dict(self):
        """转换为字典形式，用于前端初始化
        
        Returns:
            dict: 音频信息字典
        """
        return {
            'audio_path': self.audio_path,
            'is_playing': self.is_playing,
            'current_time': self.current_time
        } 