from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import uuid
import json
import numpy as np
from src.utils.file_handler import save_uploaded_file, get_upload_path
from src.utils.chart_storage import ChartStorage
from src.audio.analyzer import AudioAnalyzer
from src.chart.generator import ChartGenerator
from src.game.audio_manager import AudioManager
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, SECRET_KEY

class NumpyJSONEncoder(json.JSONEncoder):
    """处理NumPy类型的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 限制上传文件大小为32MB
app.secret_key = SECRET_KEY
app.json_encoder = NumpyJSONEncoder

# 初始化存储管理器
chart_storage = ChartStorage()

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # 检查是否有文件
        if 'audio_file' not in request.files:
            return redirect(request.url)
        
        file = request.files['audio_file']
        
        # 如果用户没有选择文件
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # 生成唯一标识符作为会话ID
            session_id = str(uuid.uuid4())
            
            # 保存文件
            filename = save_uploaded_file(file, session_id)
            
            # 开始分析音频
            audio_path = get_upload_path(session_id, filename)
            analyzer = AudioAnalyzer(audio_path)
            features = analyzer.extract_features()
            
            # 生成谱面
            chart_generator = ChartGenerator(features)
            chart = chart_generator.generate_chart()
            
            # 将谱面数据保存到文件
            chart_storage.save_chart(session_id, chart.to_dict())
            
            # 只在session中存储必要的信息
            session['session_id'] = session_id
            session['filename'] = filename
            # session['chart'] = chart.to_dict()
            
            return redirect(url_for('play'))
    
    return render_template('upload.html')

@app.route('/play')
def play():
    if 'session_id' not in session:
        return redirect(url_for('upload'))
    
    session_id = session['session_id']
    filename = session['filename']
    
    # 检查谱面数据是否存在
    chart_data = chart_storage.load_chart(session_id)
    if chart_data is None:
        return redirect(url_for('upload'))
    
    # 获取音频文件路径
    audio_path = get_upload_path(session_id, filename)
    
    # 创建音频管理器
    audio_manager = AudioManager(audio_path.replace('static/', ''))
    
    return render_template('play.html', 
                          audio_path=audio_path.replace('static/', ''),
                          session_id=session_id,
                          audio_data=audio_manager.to_dict())

@app.route('/api/chart/<session_id>')
def get_chart(session_id):
    # 从文件加载谱面数据
    chart_data = chart_storage.load_chart(session_id)
    if chart_data is not None and session.get('session_id') == session_id:
        return jsonify(chart_data)
    return jsonify({'error': 'Chart not found'}), 404

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始游戏，返回初始化数据"""
    if 'session_id' not in session:
        return jsonify({'error': 'No session found'}), 404
        
    session_id = session['session_id']
    filename = session['filename']
    
    # 加载谱面数据
    chart_data = chart_storage.load_chart(session_id)
    if chart_data is None:
        return jsonify({'error': 'Chart not found'}), 404
        
    # 获取音频路径
    audio_path = get_upload_path(session_id, filename)
    audio_manager = AudioManager(audio_path.replace('static/', ''))
    
    # 返回游戏初始化数据
    return jsonify({
        'chart': chart_data,
        'audio': audio_manager.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)