#!/usr/bin/env python3
"""
ClawHub Skill 统一入口 - 流式视频处理
支持:
1. 压缩: ffmpeg 流式处理，无需下载
2. 封面: 部分下载，只取需要的帧
3. 音频: 流式提取，转 MP3/WAV
"""

import sys
import json
import argparse
import logging
from pathlib import Path

from utils import validate_video_url, sanitize_output_path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入模块
from frame_extractor import extract_thumbnail_from_url
from video_compressor import compress_video_streaming, compress_with_adaptive_crf
from audio_extractor import extract_audio_streaming, extract_audio_batch, get_audio_info


def handle_compress(params: dict) -> dict:
    video_url = params.get('video_url')
    if not video_url:
        return {'status': 'error', 'message': 'Missing video_url'}
    try:
        validate_video_url(video_url)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    
    output_path = params.get('output_path')
    if output_path:
        try:
            output_path = sanitize_output_path(output_path)
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}
    target_ratio = params.get('target_ratio', 0.1)
    adaptive = params.get('adaptive', True)
    crf = params.get('crf', 24)
    preset = params.get('preset', 'veryfast')
    
    logger.info(f"压缩请求: {video_url[:80]}...")
    
    if adaptive:
        result = compress_with_adaptive_crf(
            video_url=video_url,
            output_path=output_path,
            target_ratio=target_ratio,
            max_attempts=params.get('max_attempts', 3)
        )
    else:
        result = compress_video_streaming(
            video_url=video_url,
            output_path=output_path,
            target_ratio=target_ratio,
            crf=crf,
            preset=preset
        )
    
    return result


def handle_thumbnail(params: dict) -> dict:
    video_url = params.get('video_url')
    if not video_url:
        return {'status': 'error', 'message': 'Missing video_url'}
    try:
        validate_video_url(video_url)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    
    time_seconds = params.get('time_seconds')
    frame_number = params.get('frame_number')
    
    if time_seconds is None and frame_number is None:
        time_seconds = 0
    
    save_path = params.get('save_path')
    if save_path:
        try:
            save_path = sanitize_output_path(save_path)
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}
    resize_width = params.get('resize_width')
    quality = params.get('quality', 85)
    
    logger.info(f"封面提取: {video_url[:80]}... time={time_seconds}, frame={frame_number}")
    
    result = extract_thumbnail_from_url(
        video_url=video_url,
        time_seconds=time_seconds,
        frame_number=frame_number,
        save_path=save_path,
        resize_width=resize_width,
        quality=quality
    )
    
    return result


def handle_audio(params: dict) -> dict:
    video_url = params.get('video_url')
    if not video_url:
        return {'status': 'error', 'message': 'Missing video_url'}
    try:
        validate_video_url(video_url)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    
    output_path = params.get('output_path')
    if output_path:
        try:
            output_path = sanitize_output_path(output_path)
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}
    audio_format = params.get('format', 'mp3')  # mp3, wav, aac, m4a
    audio_bitrate = params.get('bitrate', '128k')
    sample_rate = params.get('sample_rate', 44100)
    channels = params.get('channels', 2)
    start_time = params.get('start_time')
    duration = params.get('duration')
    
    # 格式验证
    if audio_format not in ['mp3', 'wav', 'aac', 'm4a']:
        return {'status': 'error', 'message': f'Unsupported format: {audio_format}. Supported: mp3, wav, aac, m4a'}
    
    logger.info(f"音频提取: {video_url[:80]}... format={audio_format}, bitrate={audio_bitrate}")
    
    result = extract_audio_streaming(
        video_url=video_url,
        output_path=output_path,
        audio_format=audio_format,
        audio_bitrate=audio_bitrate,
        sample_rate=sample_rate,
        channels=channels,
        start_time=start_time,
        duration=duration
    )
    
    return result


def handle_audio_batch(params: dict) -> dict:
    """批量音频提取"""
    videos = params.get('videos', [])
    if not videos:
        return {'status': 'error', 'message': 'Missing videos list'}
    
    output_dir = params.get('output_dir', './audio_output')
    try:
        output_dir = sanitize_output_path(output_dir)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    audio_format = params.get('format', 'mp3')
    audio_bitrate = params.get('bitrate', '128k')
    sample_rate = params.get('sample_rate', 44100)
    
    logger.info(f"批量音频提取: {len(videos)} 个视频, 格式={audio_format}")
    
    result = extract_audio_batch(
        videos=videos,
        output_dir=output_dir,
        audio_format=audio_format,
        audio_bitrate=audio_bitrate,
        sample_rate=sample_rate
    )
    
    return result


def handle_audio_info(params: dict) -> dict:
    video_url = params.get('video_url')
    if not video_url:
        return {'status': 'error', 'message': 'Missing video_url'}
    try:
        validate_video_url(video_url)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    
    logger.info(f"获取音频信息: {video_url[:80]}...")
    
    result = get_audio_info(video_url)
    return result


def handle_batch(params: dict) -> dict:
    """批量处理（压缩/封面）"""
    videos = params.get('videos', [])
    action = params.get('action', 'thumbnail')
    
    if not videos:
        return {'status': 'error', 'message': 'Missing videos list'}
    
    results = []
    for i, video in enumerate(videos):
        logger.info(f"批量处理 [{i+1}/{len(videos)}]")
        if action == 'compress':
            res = handle_compress(video)
        elif action == 'audio':
            res = handle_audio(video)
        else:
            res = handle_thumbnail(video)
        results.append(res)
    
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    return {
        'status': 'success',
        'total': len(results),
        'success': success_count,
        'failed': len(results) - success_count,
        'results': results
    }


def handle_info(params: dict) -> dict:
    video_url = params.get('video_url')
    if not video_url:
        return {'status': 'error', 'message': 'Missing video_url'}
    try:
        validate_video_url(video_url)
    except ValueError as e:
        return {'status': 'error', 'message': str(e)}
    
    from frame_extractor import RemoteVideoFrameExtractor
    
    try:
        extractor = RemoteVideoFrameExtractor(video_url, timeout=30)
        info = extractor.get_video_info()
        info['file_size_mb'] = round(extractor.file_size / (1024 * 1024), 2)
        return {'status': 'success', 'info': info}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


# Action 映射
ACTIONS = {
    'compress': handle_compress,
    'thumbnail': handle_thumbnail,
    'audio': handle_audio,
    'audio_batch': handle_audio_batch,
    'audio_info': handle_audio_info,
    'batch': handle_batch,
    'info': handle_info
}


def run_cli():
    """命令行模式"""
    parser = argparse.ArgumentParser(description='Video Streaming Skill')
    parser.add_argument('--input', '-i', required=True, help='Input JSON string or file path')
    parser.add_argument('--action', '-a', choices=ACTIONS.keys(), help='Action to perform')
    args = parser.parse_args()
    
    try:
        if Path(args.input).exists():
            with open(args.input, 'r') as f:
                params = json.load(f)
        else:
            params = json.loads(args.input)
    except json.JSONDecodeError:
        params = {'action': args.action} if args.action else {}
        for pair in args.input.split():
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
    
    action = params.get('action')
    if not action and args.action:
        action = args.action
    
    if not action or action not in ACTIONS:
        print(json.dumps({'status': 'error', 'message': f'Invalid action: {action}'}))
        sys.exit(1)
    
    result = ACTIONS[action](params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def run_http_server(host='127.0.0.1', port=8080):
    """HTTP 服务模式"""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok', 'skill': 'video-streaming-toolkit'})
        
        @app.route('/skill/compress', methods=['POST'])
        def compress():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_compress(data))
        
        @app.route('/skill/thumbnail', methods=['POST'])
        def thumbnail():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_thumbnail(data))
        
        @app.route('/skill/audio', methods=['POST'])
        def audio():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_audio(data))
        
        @app.route('/skill/audio_batch', methods=['POST'])
        def audio_batch():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_audio_batch(data))
        
        @app.route('/skill/audio_info', methods=['POST'])
        def audio_info():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_audio_info(data))
        
        @app.route('/skill/batch', methods=['POST'])
        def batch():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_batch(data))
        
        @app.route('/skill/info', methods=['POST'])
        def info():
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No JSON body'}), 400
            return jsonify(handle_info(data))
        
        logger.info(f"Starting HTTP server on {host}:{port}")
        app.run(host=host, port=port, threaded=True)
        
    except ImportError:
        logger.error("Flask not installed. Run: pip install flask flask-cors")
        sys.exit(1)


if __name__ == '__main__':
    if '--serve' in sys.argv or '-s' in sys.argv:
        argv = sys.argv[1:]
        host = '127.0.0.1'
        port = 8080
        i = 0
        while i < len(argv):
            if argv[i] == '--host' and i + 1 < len(argv):
                host = argv[i + 1]
                i += 2
            elif argv[i] == '--port' and i + 1 < len(argv):
                port = int(argv[i + 1])
                i += 2
            else:
                i += 1
        run_http_server(host=host, port=port)
    else:
        run_cli()