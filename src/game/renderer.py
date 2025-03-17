class GameRenderer:
    """游戏渲染器，负责在界面上绘制游戏元素"""
    
    def __init__(self, lanes=4, note_speed=600):
        """初始化渲染器
        
        Args:
            lanes: 轨道数量
            note_speed: 音符下落速度(像素/秒)
        """
        self.lanes = lanes
        self.note_speed = note_speed
        
    def calculate_note_position(self, note, current_time, canvas_height):
        """计算音符在画布上的位置
        
        Args:
            note: 音符对象
            current_time: 当前游戏时间(秒)
            canvas_height: 画布高度(像素)
            
        Returns:
            dict: 包含音符位置和大小的字典
        """
        # 计算音符距离判定线的距离
        time_to_hit = note.time - current_time
        distance = time_to_hit * self.note_speed
        
        # 音符从上到下落下，判定线在底部
        y_position = canvas_height - distance
        
        # 计算轨道位置 (水平方向)
        lane_width = 100  # 轨道宽度(像素)
        x_position = note.lane * lane_width + lane_width / 2
        
        return {
            'x': x_position,
            'y': y_position,
            'type': note.type,
            'duration': note.duration,
            'length': note.duration * self.note_speed if note.type in ['hold', 'slide'] else 0
        }
    
    def get_note_style(self, note):
        """获取音符的样式
        
        Args:
            note: 音符对象
            
        Returns:
            dict: 包含音符样式的字典
        """
        # 根据音符类型和强度确定样式
        styles = {
            'tap': {
                'radius': 20,
                'color': f'rgba(0, 255, 255, {0.7 + note.intensity * 0.3})',
                'border': '2px solid white'
            },
            'hold': {
                'radius': 20,
                'color': f'rgba(255, 255, 0, {0.7 + note.intensity * 0.3})',
                'border': '2px solid white'
            },
            'slide': {
                'radius': 20,
                'color': f'rgba(255, 0, 255, {0.7 + note.intensity * 0.3})',
                'border': '2px solid white'
            }
        }
        
        return styles.get(note.type, styles['tap'])
    
    def generate_note_element(self, note_position, note_style):
        """生成音符HTML元素
        
        Args:
            note_position: 音符位置信息
            note_style: 音符样式信息
            
        Returns:
            str: 表示音符的HTML代码
        """
        element = f"""
        <div class="note {note_position['type']}" 
             style="left: {note_position['x']}px; 
                    top: {note_position['y']}px; 
                    width: {note_style['radius'] * 2}px; 
                    height: {note_style['radius'] * 2}px;
                    background-color: {note_style['color']};
                    border: {note_style['border']};">
        """
        
        # 添加尾部(对于长按和滑动音符)
        if note_position['type'] in ['hold', 'slide'] and note_position['length'] > 0:
            element += f"""
            <div class="note-tail" 
                 style="height: {note_position['length']}px;
                        background-color: {note_style['color'].replace(')', ', 0.5)')};">
            </div>
            """
        
        element += "</div>"
        return element