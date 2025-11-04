import pandas as pd
import numpy as np
from PIL import Image
import os
from datetime import datetime

class TimeSeriesProcessor:
    """시계열 데이터 처리 클래스"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.xlsx']
    
    def analyze(self, filepath):
        """시계열 데이터 분석"""
        try:
            # 파일 확장자 확인
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.csv':
                df = pd.read_csv(filepath)
            elif ext == '.json':
                df = pd.read_json(filepath)
            elif ext == '.xlsx':
                df = pd.read_excel(filepath)
            else:
                return {'error': f'지원하지 않는 파일 형식: {ext}'}
            
            # 기본 통계
            metadata = {
                'filename': os.path.basename(filepath),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'missing_values': df.isnull().sum().to_dict(),
                'statistics': {}
            }
            
            # 수치형 컬럼 통계
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                metadata['statistics'][col] = {
                    'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                    'std': float(df[col].std()) if not df[col].isnull().all() else None,
                    'min': float(df[col].min()) if not df[col].isnull().all() else None,
                    'max': float(df[col].max()) if not df[col].isnull().all() else None,
                    'median': float(df[col].median()) if not df[col].isnull().all() else None
                }
            
            # 시간 컬럼 감지
            time_columns = []
            for col in df.columns:
                if 'time' in col.lower() or 'date' in col.lower():
                    time_columns.append(col)
                else:
                    try:
                        pd.to_datetime(df[col])
                        time_columns.append(col)
                    except:
                        pass
            
            metadata['time_columns'] = time_columns
            
            # 시계열 특성 분석
            if time_columns:
                time_col = time_columns[0]
                try:
                    df[time_col] = pd.to_datetime(df[time_col])
                    metadata['time_range'] = {
                        'start': str(df[time_col].min()),
                        'end': str(df[time_col].max()),
                        'duration': str(df[time_col].max() - df[time_col].min())
                    }
                    
                    # 샘플링 빈도 추정
                    if len(df) > 1:
                        time_diff = df[time_col].diff().median()
                        metadata['estimated_frequency'] = str(time_diff)
                except Exception as e:
                    metadata['time_analysis_error'] = str(e)
            
            return metadata
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_patterns(self, filepath):
        """시계열 패턴 감지"""
        try:
            df = pd.read_csv(filepath)
            patterns = {
                'trend': [],
                'seasonality': [],
                'anomalies': []
            }
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) > 10:
                    # 간단한 추세 분석
                    if data.is_monotonic_increasing:
                        patterns['trend'].append({'column': col, 'type': 'increasing'})
                    elif data.is_monotonic_decreasing:
                        patterns['trend'].append({'column': col, 'type': 'decreasing'})
                    
                    # 이상치 감지 (IQR 방법)
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = data[(data < Q1 - 1.5 * IQR) | (data > Q3 + 1.5 * IQR)]
                    
                    if len(outliers) > 0:
                        patterns['anomalies'].append({
                            'column': col,
                            'count': len(outliers),
                            'percentage': round(len(outliers) / len(data) * 100, 2)
                        })
            
            return patterns
        except Exception as e:
            return {'error': str(e)}


class ImageProcessor:
    """이미지 데이터 처리 클래스"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    
    def analyze(self, filepath):
        """이미지 분석"""
        try:
            img = Image.open(filepath)
            
            metadata = {
                'filename': os.path.basename(filepath),
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'size': os.path.getsize(filepath),
                'aspect_ratio': round(img.width / img.height, 2) if img.height > 0 else None
            }
            
            # 이미지 정보
            if hasattr(img, 'info'):
                metadata['info'] = {k: str(v) for k, v in img.info.items()}
            
            # 컬러 모드 분석
            if img.mode == 'RGB' or img.mode == 'RGBA':
                # 이미지를 작은 크기로 리샘플링하여 색상 분석
                img_small = img.resize((100, 100))
                pixels = np.array(img_small)
                
                metadata['color_analysis'] = {
                    'channels': pixels.shape[2] if len(pixels.shape) > 2 else 1,
                    'mean_brightness': float(np.mean(pixels)),
                    'std_brightness': float(np.std(pixels))
                }
                
                if len(pixels.shape) > 2 and pixels.shape[2] >= 3:
                    metadata['color_analysis']['mean_rgb'] = {
                        'red': float(np.mean(pixels[:, :, 0])),
                        'green': float(np.mean(pixels[:, :, 1])),
                        'blue': float(np.mean(pixels[:, :, 2]))
                    }
            
            # EXIF 데이터 (JPEG인 경우)
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_data = {}
                for tag_id, value in img._getexif().items():
                    try:
                        exif_data[str(tag_id)] = str(value)
                    except:
                        pass
                metadata['exif'] = exif_data
            
            return metadata
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_features(self, filepath):
        """이미지 특징 추출"""
        try:
            img = Image.open(filepath)
            img_array = np.array(img)
            
            features = {
                'shape': img_array.shape,
                'histogram': {}
            }
            
            # 히스토그램 계산
            if len(img_array.shape) == 2:  # 그레이스케일
                hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
                features['histogram']['gray'] = hist.tolist()[:50]  # 처음 50개만
            elif len(img_array.shape) == 3:  # 컬러
                for i, color in enumerate(['red', 'green', 'blue']):
                    if i < img_array.shape[2]:
                        hist, _ = np.histogram(img_array[:, :, i].flatten(), 
                                              bins=256, range=(0, 256))
                        features['histogram'][color] = hist.tolist()[:50]
            
            # 에지 감지 (간단한 그래디언트)
            if len(img_array.shape) == 2:
                grad_x = np.abs(np.gradient(img_array, axis=1))
                grad_y = np.abs(np.gradient(img_array, axis=0))
                features['edge_strength'] = float(np.mean(grad_x + grad_y))
            
            return features
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_objects(self, filepath):
        """객체 감지 (기본 구현)"""
        # 실제 환경에서는 YOLOv5, DETR 등의 모델 사용
        try:
            img = Image.open(filepath)
            
            # 여기서는 간단한 밝기 기반 영역 감지
            img_gray = img.convert('L')
            img_array = np.array(img_gray)
            
            # 임계값 기반 세그멘테이션
            threshold = np.mean(img_array)
            binary = img_array > threshold
            
            return {
                'detected_regions': int(np.sum(binary)),
                'threshold': float(threshold),
                'note': '실제 객체 감지를 위해서는 딥러닝 모델 필요'
            }
        except Exception as e:
            return {'error': str(e)}
