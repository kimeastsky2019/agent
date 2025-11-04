from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
import json
from ontology_builder import OntologyBuilder
from data_processor import TimeSeriesProcessor, ImageProcessor

app = Flask(__name__)
CORS(app)

# 설정
UPLOAD_FOLDER = 'uploads'
ONTOLOGY_FOLDER = 'ontologies'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ONTOLOGY_FOLDER, exist_ok=True)

ontology_builder = OntologyBuilder()
ts_processor = TimeSeriesProcessor()
img_processor = ImageProcessor()

@app.route('/')
def index():
    """Serve frontend HTML"""
    try:
        return send_file('frontend.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/upload/timeseries', methods=['POST'])
def upload_timeseries():
    """시계열 데이터 업로드 및 분석"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일명이 없습니다'}), 400
        
        # 파일 저장
        filepath = os.path.join(UPLOAD_FOLDER, f"ts_{datetime.now().timestamp()}_{file.filename}")
        file.save(filepath)
        
        # 데이터 분석
        metadata = ts_processor.analyze(filepath)
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """이미지 데이터 업로드 및 분석"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일명이 없습니다'}), 400
        
        # 파일 저장
        filepath = os.path.join(UPLOAD_FOLDER, f"img_{datetime.now().timestamp()}_{file.filename}")
        file.save(filepath)
        
        # 이미지 분석
        metadata = img_processor.analyze(filepath)
        
        return jsonify({
            'success': True,
            'filepath': filepath,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/create', methods=['POST'])
def create_ontology():
    """온톨로지 생성"""
    try:
        data = request.json
        ontology_name = data.get('name', f'ontology_{datetime.now().timestamp()}')
        data_sources = data.get('data_sources', [])
        
        # 온톨로지 생성
        ontology_path = ontology_builder.create_ontology(
            name=ontology_name,
            data_sources=data_sources
        )
        
        return jsonify({
            'success': True,
            'ontology_path': ontology_path,
            'ontology_uri': ontology_builder.get_ontology_uri(ontology_name)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/add_timeseries', methods=['POST'])
def add_timeseries_to_ontology():
    """시계열 데이터를 온톨로지에 추가"""
    try:
        data = request.json
        ontology_name = data.get('ontology_name')
        filepath = data.get('filepath')
        concept_name = data.get('concept_name')
        
        ontology_builder.add_timeseries_data(
            ontology_name=ontology_name,
            filepath=filepath,
            concept_name=concept_name
        )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/add_image', methods=['POST'])
def add_image_to_ontology():
    """이미지 데이터를 온톨로지에 추가"""
    try:
        data = request.json
        ontology_name = data.get('ontology_name')
        filepath = data.get('filepath')
        concept_name = data.get('concept_name')
        
        ontology_builder.add_image_data(
            ontology_name=ontology_name,
            filepath=filepath,
            concept_name=concept_name
        )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/query', methods=['POST'])
def query_ontology():
    """온톨로지 쿼리 (SPARQL)"""
    try:
        data = request.json
        ontology_name = data.get('ontology_name')
        query = data.get('query')
        
        results = ontology_builder.query(ontology_name, query)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/export/<ontology_name>', methods=['GET'])
def export_ontology(ontology_name):
    """온톨로지 내보내기"""
    try:
        export_path = ontology_builder.export(ontology_name)
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/list', methods=['GET'])
def list_ontologies():
    """저장된 온톨로지 목록"""
    try:
        ontologies = ontology_builder.list_ontologies()
        return jsonify({
            'success': True,
            'ontologies': ontologies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ontology/visualize/<ontology_name>', methods=['GET'])
def visualize_ontology(ontology_name):
    """온톨로지 시각화 데이터"""
    try:
        graph_data = ontology_builder.get_visualization_data(ontology_name)
        return jsonify({
            'success': True,
            'graph': graph_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
