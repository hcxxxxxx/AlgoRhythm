import os

# 应用配置
SECRET_KEY = 'your-secret-key-here'

# 文件上传配置
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac'}

# 音频分析配置
SAMPLE_RATE = 22050
HOP_LENGTH = 512
N_FFT = 2048

# 谱面生成配置
NOTE_TYPES = ['tap', 'hold', 'slide']
DIFFICULTY_LEVELS = {
    'easy': {
        'max_notes_per_beat': 2,
        'hold_note_prob': 0.1,
        'slide_note_prob': 0.05
    },
    'normal': {
        'max_notes_per_beat': 3,
        'hold_note_prob': 0.2,
        'slide_note_prob': 0.1
    },
    'hard': {
        'max_notes_per_beat': 4,
        'hold_note_prob': 0.3,
        'slide_note_prob': 0.2
    }
}

# 游戏配置
LANES = 4  # 轨道数量
NOTE_SPEED = 600  # 音符下落速度 (像素/秒)