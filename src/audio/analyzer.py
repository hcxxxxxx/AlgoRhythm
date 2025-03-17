import librosa
import numpy as np
from src.audio.features import AudioFeatures
from config import SAMPLE_RATE, HOP_LENGTH, N_FFT

class AudioAnalyzer:
    """音频分析器，负责从音频文件中提取特征"""
    
    def __init__(self, audio_path):
        """初始化分析器
        
        Args:
            audio_path: 音频文件路径
        """
        self.audio_path = audio_path
        self.y = None
        self.sr = None
        self.duration = 0
        self._load_audio()
    
    def _load_audio(self):
        """加载音频文件"""
        try:
            self.y, self.sr = librosa.load(self.audio_path, sr=SAMPLE_RATE)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            print(f"音频加载成功，时长: {self.duration:.2f}秒")
        except Exception as e:
            print(f"音频加载失败: {str(e)}")
            raise
    
    def extract_features(self):
        """提取音频特征
        
        Returns:
            AudioFeatures: 包含所有音频特征的对象
        """
        features = AudioFeatures()
        
        # 1. 提取节拍信息
        tempo, beats = self._extract_beats()
        features.tempo = tempo
        features.beats = beats
        features.beat_times = librosa.frames_to_time(beats, sr=self.sr)
        
        # 2. 提取能量特征
        features.onset_strength = self._extract_onset_strength()
        features.onset_frames = self._extract_onsets(features.onset_strength)
        features.onset_times = librosa.frames_to_time(features.onset_frames, sr=self.sr)
        
        # 3. 提取频谱和音高特征
        features.harmonic, features.percussive = self._separate_harmonic_percussive()
        features.pitches, features.magnitudes = self._extract_pitch()
        
        # 4. 计算每个音符的类型和难度
        features.note_intensities = self._calculate_note_intensities(features.onset_frames)
        
        return features
    
    def _extract_beats(self):
        """提取节拍信息
        
        Returns:
            tuple: (tempo, beats) - 速度(BPM)和节拍帧位置
        """
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr, hop_length=HOP_LENGTH)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=self.sr)
        return tempo, beats
    
    def _extract_onset_strength(self):
        """提取音符起始强度序列
        
        Returns:
            np.ndarray: 音符起始强度序列
        """
        onset_strength = librosa.onset.onset_strength(
            y=self.y, sr=self.sr, hop_length=HOP_LENGTH
        )
        return onset_strength
    
    def _extract_onsets(self, onset_strength):
        """提取音符起始帧位置
        
        Args:
            onset_strength: 音符起始强度序列
            
        Returns:
            np.ndarray: 音符起始帧位置
        """
        onsets = librosa.onset.onset_detect(
            onset_envelope=onset_strength, sr=self.sr, hop_length=HOP_LENGTH
        )
        return onsets
    
    def _separate_harmonic_percussive(self):
        """分离和声和打击乐部分
        
        Returns:
            tuple: (harmonic, percussive) - 和声部分和打击乐部分的波形
        """
        harmonic, percussive = librosa.effects.hpss(self.y)
        return harmonic, percussive
    
    def _extract_pitch(self):
        """提取音高信息
        
        Returns:
            tuple: (pitches, magnitudes) - 音高和对应的强度
        """
        pitches, magnitudes = librosa.piptrack(
            y=self.y, sr=self.sr, hop_length=HOP_LENGTH, n_fft=N_FFT
        )
        return pitches, magnitudes
    
    def _calculate_note_intensities(self, onset_frames):
        """计算每个音符的强度
        
        Args:
            onset_frames: 音符起始帧位置
            
        Returns:
            np.ndarray: 每个音符的强度值(0-1之间)
        """
        if len(onset_frames) == 0:
            return np.array([])
            
        # 获取每个起始帧对应的能量值
        onset_strength = self._extract_onset_strength()
        intensities = onset_strength[onset_frames]
        
        # 归一化到0-1之间
        if len(intensities) > 0:
            min_val = np.min(intensities)
            max_val = np.max(intensities)
            if max_val > min_val:
                intensities = (intensities - min_val) / (max_val - min_val)
            
        return intensities