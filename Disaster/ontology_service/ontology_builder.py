from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
import os
import json
from datetime import datetime

class OntologyBuilder:
    """온톨로지 생성 및 관리 클래스"""
    
    def __init__(self, base_uri="http://example.org/ontology/"):
        self.base_uri = base_uri
        self.ontologies = {}
        self.ontology_folder = 'ontologies'
        os.makedirs(self.ontology_folder, exist_ok=True)
        
        # 네임스페이스 정의
        self.EX = Namespace(base_uri)
        self.TS = Namespace(f"{base_uri}timeseries/")
        self.IMG = Namespace(f"{base_uri}image/")
    
    def create_ontology(self, name, data_sources=None):
        """새로운 온톨로지 생성"""
        g = Graph()
        
        # 네임스페이스 바인딩
        g.bind("ex", self.EX)
        g.bind("ts", self.TS)
        g.bind("img", self.IMG)
        g.bind("owl", OWL)
        
        # 온톨로지 메타데이터
        ontology_uri = URIRef(f"{self.base_uri}{name}")
        g.add((ontology_uri, RDF.type, OWL.Ontology))
        g.add((ontology_uri, RDFS.label, Literal(name)))
        g.add((ontology_uri, RDFS.comment, Literal(f"Ontology for {name}")))
        g.add((ontology_uri, OWL.versionInfo, Literal("1.0")))
        
        # 기본 클래스 정의
        self._define_base_classes(g)
        
        # 온톨로지 저장
        self.ontologies[name] = g
        self._save_ontology(name, g)
        
        return os.path.join(self.ontology_folder, f"{name}.owl")
    
    def _define_base_classes(self, g):
        """기본 클래스 및 프로퍼티 정의"""
        # 시계열 데이터 클래스
        TimeSeries = self.TS.TimeSeries
        g.add((TimeSeries, RDF.type, OWL.Class))
        g.add((TimeSeries, RDFS.label, Literal("Time Series Data")))
        g.add((TimeSeries, RDFS.comment, Literal("시계열 데이터를 나타내는 클래스")))
        
        DataPoint = self.TS.DataPoint
        g.add((DataPoint, RDF.type, OWL.Class))
        g.add((DataPoint, RDFS.label, Literal("Data Point")))
        g.add((DataPoint, RDFS.comment, Literal("시계열의 개별 데이터 포인트")))
        
        # 이미지 데이터 클래스
        Image = self.IMG.Image
        g.add((Image, RDF.type, OWL.Class))
        g.add((Image, RDFS.label, Literal("Image")))
        g.add((Image, RDFS.comment, Literal("이미지 데이터를 나타내는 클래스")))
        
        ImageMetadata = self.IMG.ImageMetadata
        g.add((ImageMetadata, RDF.type, OWL.Class))
        g.add((ImageMetadata, RDFS.label, Literal("Image Metadata")))
        
        # 프로퍼티 정의
        # 시계열 프로퍼티
        hasTimestamp = self.TS.hasTimestamp
        g.add((hasTimestamp, RDF.type, OWL.DatatypeProperty))
        g.add((hasTimestamp, RDFS.domain, DataPoint))
        g.add((hasTimestamp, RDFS.range, XSD.dateTime))
        g.add((hasTimestamp, RDFS.label, Literal("has timestamp")))
        
        hasValue = self.TS.hasValue
        g.add((hasValue, RDF.type, OWL.DatatypeProperty))
        g.add((hasValue, RDFS.domain, DataPoint))
        g.add((hasValue, RDFS.range, XSD.float))
        g.add((hasValue, RDFS.label, Literal("has value")))
        
        hasDataPoint = self.TS.hasDataPoint
        g.add((hasDataPoint, RDF.type, OWL.ObjectProperty))
        g.add((hasDataPoint, RDFS.domain, TimeSeries))
        g.add((hasDataPoint, RDFS.range, DataPoint))
        
        # 이미지 프로퍼티
        hasWidth = self.IMG.hasWidth
        g.add((hasWidth, RDF.type, OWL.DatatypeProperty))
        g.add((hasWidth, RDFS.domain, Image))
        g.add((hasWidth, RDFS.range, XSD.integer))
        
        hasHeight = self.IMG.hasHeight
        g.add((hasHeight, RDF.type, OWL.DatatypeProperty))
        g.add((hasHeight, RDFS.domain, Image))
        g.add((hasHeight, RDFS.range, XSD.integer))
        
        hasFormat = self.IMG.hasFormat
        g.add((hasFormat, RDF.type, OWL.DatatypeProperty))
        g.add((hasFormat, RDFS.domain, Image))
        g.add((hasFormat, RDFS.range, XSD.string))
        
        hasFilePath = self.EX.hasFilePath
        g.add((hasFilePath, RDF.type, OWL.DatatypeProperty))
        g.add((hasFilePath, RDFS.range, XSD.string))
    
    def add_timeseries_data(self, ontology_name, filepath, concept_name):
        """시계열 데이터를 온톨로지에 추가"""
        if ontology_name not in self.ontologies:
            self._load_ontology(ontology_name)
        
        g = self.ontologies[ontology_name]
        
        # 시계열 인스턴스 생성
        ts_uri = self.TS[f"{concept_name}_{datetime.now().timestamp()}"]
        g.add((ts_uri, RDF.type, self.TS.TimeSeries))
        g.add((ts_uri, RDFS.label, Literal(concept_name)))
        g.add((ts_uri, self.EX.hasFilePath, Literal(filepath)))
        
        # 데이터 파일 읽기 및 포인트 추가
        import pandas as pd
        try:
            df = pd.read_csv(filepath)
            # 첫 100개 포인트만 추가 (예시)
            for idx, row in df.head(100).iterrows():
                point_uri = self.TS[f"point_{concept_name}_{idx}"]
                g.add((point_uri, RDF.type, self.TS.DataPoint))
                g.add((ts_uri, self.TS.hasDataPoint, point_uri))
                
                # 타임스탬프가 있으면 추가
                if 'timestamp' in df.columns or 'time' in df.columns:
                    ts_col = 'timestamp' if 'timestamp' in df.columns else 'time'
                    g.add((point_uri, self.TS.hasTimestamp, 
                          Literal(str(row[ts_col]), datatype=XSD.dateTime)))
                
                # 값 컬럼 추가
                value_cols = [col for col in df.columns if col not in ['timestamp', 'time', 'index']]
                if value_cols:
                    g.add((point_uri, self.TS.hasValue, 
                          Literal(float(row[value_cols[0]]), datatype=XSD.float)))
        except Exception as e:
            print(f"데이터 파일 읽기 오류: {e}")
        
        self._save_ontology(ontology_name, g)
    
    def add_image_data(self, ontology_name, filepath, concept_name):
        """이미지 데이터를 온톨로지에 추가"""
        if ontology_name not in self.ontologies:
            self._load_ontology(ontology_name)
        
        g = self.ontologies[ontology_name]
        
        # 이미지 인스턴스 생성
        img_uri = self.IMG[f"{concept_name}_{datetime.now().timestamp()}"]
        g.add((img_uri, RDF.type, self.IMG.Image))
        g.add((img_uri, RDFS.label, Literal(concept_name)))
        g.add((img_uri, self.EX.hasFilePath, Literal(filepath)))
        
        # 이미지 메타데이터 추가
        from PIL import Image
        try:
            img = Image.open(filepath)
            g.add((img_uri, self.IMG.hasWidth, Literal(img.width, datatype=XSD.integer)))
            g.add((img_uri, self.IMG.hasHeight, Literal(img.height, datatype=XSD.integer)))
            g.add((img_uri, self.IMG.hasFormat, Literal(img.format)))
        except Exception as e:
            print(f"이미지 메타데이터 추출 오류: {e}")
        
        self._save_ontology(ontology_name, g)
    
    def query(self, ontology_name, sparql_query):
        """SPARQL 쿼리 실행"""
        if ontology_name not in self.ontologies:
            self._load_ontology(ontology_name)
        
        g = self.ontologies[ontology_name]
        results = g.query(sparql_query)
        
        # 결과를 JSON 형식으로 변환
        result_list = []
        for row in results:
            result_list.append({str(var): str(val) for var, val in zip(results.vars, row)})
        
        return result_list
    
    def export(self, ontology_name):
        """온톨로지를 파일로 내보내기"""
        if ontology_name not in self.ontologies:
            self._load_ontology(ontology_name)
        
        filepath = os.path.join(self.ontology_folder, f"{ontology_name}.owl")
        return filepath
    
    def list_ontologies(self):
        """저장된 온톨로지 목록 반환"""
        files = [f.replace('.owl', '') for f in os.listdir(self.ontology_folder) if f.endswith('.owl')]
        return files
    
    def get_ontology_uri(self, ontology_name):
        """온톨로지 URI 반환"""
        return f"{self.base_uri}{ontology_name}"
    
    def get_visualization_data(self, ontology_name):
        """온톨로지 시각화를 위한 그래프 데이터 반환"""
        if ontology_name not in self.ontologies:
            self._load_ontology(ontology_name)
        
        g = self.ontologies[ontology_name]
        
        nodes = []
        edges = []
        node_set = set()
        
        for s, p, o in g:
            # 주체(subject) 노드 추가
            if s not in node_set:
                nodes.append({
                    'id': str(s),
                    'label': self._get_label(g, s),
                    'type': self._get_type(g, s)
                })
                node_set.add(s)
            
            # 객체(object) 노드 추가 (URI인 경우만)
            if isinstance(o, URIRef) and o not in node_set:
                nodes.append({
                    'id': str(o),
                    'label': self._get_label(g, o),
                    'type': self._get_type(g, o)
                })
                node_set.add(o)
            
            # 엣지 추가
            edges.append({
                'source': str(s),
                'target': str(o) if isinstance(o, URIRef) else str(o)[:50],
                'label': str(p).split('/')[-1].split('#')[-1]
            })
        
        return {'nodes': nodes[:100], 'edges': edges[:200]}  # 시각화를 위해 제한
    
    def _get_label(self, g, uri):
        """리소스의 레이블 가져오기"""
        for _, _, label in g.triples((uri, RDFS.label, None)):
            return str(label)
        # 레이블이 없으면 URI의 마지막 부분 반환
        return str(uri).split('/')[-1].split('#')[-1]
    
    def _get_type(self, g, uri):
        """리소스의 타입 가져오기"""
        for _, _, type_uri in g.triples((uri, RDF.type, None)):
            return str(type_uri).split('/')[-1].split('#')[-1]
        return 'Unknown'
    
    def _save_ontology(self, name, g):
        """온톨로지를 파일로 저장"""
        filepath = os.path.join(self.ontology_folder, f"{name}.owl")
        g.serialize(destination=filepath, format='xml')
    
    def _load_ontology(self, name):
        """파일에서 온톨로지 로드"""
        filepath = os.path.join(self.ontology_folder, f"{name}.owl")
        if os.path.exists(filepath):
            g = Graph()
            g.parse(filepath, format='xml')
            self.ontologies[name] = g
        else:
            raise FileNotFoundError(f"온톨로지 '{name}'을 찾을 수 없습니다")
