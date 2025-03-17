import os
import json
from pathlib import Path

class ChartStorage:
    """谱面数据存储管理器"""
    
    def __init__(self, base_dir='static/charts'):
        """初始化存储管理器
        
        Args:
            base_dir: 存储谱面数据的基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_chart(self, session_id, chart_data):
        """保存谱面数据到文件
        
        Args:
            session_id: 会话ID
            chart_data: 谱面数据字典
        """
        chart_path = self.base_dir / f"{session_id}.json"
        with open(chart_path, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f)
    
    def load_chart(self, session_id):
        """从文件加载谱面数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            dict: 谱面数据字典，如果文件不存在则返回None
        """
        chart_path = self.base_dir / f"{session_id}.json"
        if not chart_path.exists():
            return None
            
        with open(chart_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_chart(self, session_id):
        """删除谱面数据文件
        
        Args:
            session_id: 会话ID
        """
        chart_path = self.base_dir / f"{session_id}.json"
        if chart_path.exists():
            chart_path.unlink() 