#!/usr/bin/env python3
"""
붓 움직임과 압력 분석 시스템
- 스켈레톤에서 붓의 이동 방향 추정
- 굵기 변화로 압력 추정
- 획순 및 방향 검출
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import ndimage
from scipy.interpolate import interp1d
from skimage.morphology import skeletonize
from skimage import measure, graph
import math
import os
import platform
from collections import deque

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/Library/Fonts/AppleGothic.ttf',
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            if font_path.endswith('.ttc'):
                plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
            else:
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            print(f"✅ 한글 폰트 설정 완료: {font_path}")
            return True
    return False


class BrushDynamicsAnalyzer:
    def __init__(self):
        self.setup_korean_font = setup_korean_font
        
    def extract_skeleton(self, binary_img):
        """스켈레톤 추출"""
        skeleton = skeletonize(binary_img > 0)
        return skeleton.astype(np.uint8) * 255
    
    def trace_skeleton_path(self, skeleton):
        """스켈레톤을 따라 경로 추적"""
        # 끝점 찾기 (시작점)
        endpoints = self.find_endpoints(skeleton)
        
        if len(endpoints) == 0:
            # 끝점이 없으면 임의의 점에서 시작
            points = np.where(skeleton > 0)
            if len(points[0]) > 0:
                endpoints = [(points[0][0], points[1][0])]
            else:
                return []
        
        paths = []
        visited = np.zeros_like(skeleton, dtype=bool)
        
        for endpoint in endpoints:
            if visited[endpoint[0], endpoint[1]]:
                continue
                
            path = self.trace_from_point(skeleton, endpoint, visited)
            if len(path) > 10:  # 너무 짧은 경로는 무시
                paths.append(path)
        
        return paths
    
    def find_endpoints(self, skeleton):
        """스켈레톤의 끝점 찾기"""
        kernel = np.array([[1, 1, 1],
                          [1, 10, 1],
                          [1, 1, 1]], dtype=np.uint8)
        
        filtered = cv2.filter2D(skeleton.astype(np.uint8), -1, kernel)
        
        # 끝점: 이웃이 1개인 점 (자기 자신 10 + 이웃 1 = 11)
        endpoints = np.where((filtered == 11) & (skeleton > 0))
        
        return list(zip(endpoints[0], endpoints[1]))
    
    def trace_from_point(self, skeleton, start_point, visited):
        """특정 점에서 시작하여 경로 추적"""
        path = []
        queue = deque([start_point])
        
        while queue:
            current = queue.popleft()
            y, x = current
            
            if visited[y, x]:
                continue
                
            visited[y, x] = True
            path.append((x, y))  # (x, y) 순서로 저장
            
            # 8방향 이웃 확인
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    
                    ny, nx = y + dy, x + dx
                    
                    if (0 <= ny < skeleton.shape[0] and 
                        0 <= nx < skeleton.shape[1] and
                        skeleton[ny, nx] > 0 and 
                        not visited[ny, nx]):
                        queue.append((ny, nx))
                        break  # 한 방향으로만 진행
        
        return path
    
    def analyze_stroke_direction(self, path, window_size=5):
        """경로를 따라 이동 방향 분석"""
        if len(path) < window_size:
            return []
        
        directions = []
        
        for i in range(len(path) - window_size):
            # 현재 위치와 다음 위치들의 평균으로 방향 계산
            start_point = np.array(path[i])
            end_point = np.array(path[i + window_size])
            
            direction_vector = end_point - start_point
            
            # 각도 계산 (도 단위)
            angle = np.arctan2(direction_vector[1], direction_vector[0]) * 180 / np.pi
            
            # 속도 (거리)
            speed = np.linalg.norm(direction_vector)
            
            directions.append({
                'position': path[i],
                'angle': angle,
                'speed': speed,
                'vector': direction_vector
            })
        
        return directions
    
    def estimate_pressure_from_thickness(self, binary_img, skeleton, path):
        """경로를 따라 굵기 변화로 압력 추정"""
        # 거리 변환으로 각 점의 굵기 계산
        dist_transform = cv2.distanceTransform(binary_img, cv2.DIST_L2, 5)
        
        pressure_profile = []
        
        for x, y in path:
            if 0 <= y < dist_transform.shape[0] and 0 <= x < dist_transform.shape[1]:
                # 굵기 = 거리 * 2
                thickness = dist_transform[y, x] * 2
                
                # 압력은 굵기에 비례한다고 가정
                # 정규화: 얇은 곳 = 낮은 압력, 두꺼운 곳 = 높은 압력
                pressure_profile.append({
                    'position': (x, y),
                    'thickness': thickness,
                    'pressure': thickness  # 실제로는 더 복잡한 변환 필요
                })
        
        return pressure_profile
    
    def detect_stroke_features(self, path, pressure_profile):
        """획의 특징 검출 (시작, 끝, 전환점 등)"""
        features = {
            'start': None,
            'end': None,
            'turning_points': [],
            'pressure_peaks': [],
            'pressure_valleys': []
        }
        
        if len(path) > 0:
            features['start'] = path[0]
            features['end'] = path[-1]
        
        # 전환점 찾기 (방향이 크게 바뀌는 점)
        if len(path) > 2:
            for i in range(1, len(path) - 1):
                prev = np.array(path[i-1])
                curr = np.array(path[i])
                next = np.array(path[i+1])
                
                v1 = curr - prev
                v2 = next - curr
                
                # 외적으로 방향 변화 감지
                cross = np.cross(v1, v2)
                
                if abs(cross) > 10:  # 임계값
                    features['turning_points'].append(path[i])
        
        # 압력 피크와 밸리 찾기
        if len(pressure_profile) > 2:
            pressures = [p['pressure'] for p in pressure_profile]
            
            for i in range(1, len(pressures) - 1):
                if pressures[i] > pressures[i-1] and pressures[i] > pressures[i+1]:
                    features['pressure_peaks'].append(pressure_profile[i]['position'])
                elif pressures[i] < pressures[i-1] and pressures[i] < pressures[i+1]:
                    features['pressure_valleys'].append(pressure_profile[i]['position'])
        
        return features
    
    def analyze_brush_dynamics(self, binary_img):
        """전체 붓 다이나믹스 분석"""
        # 스켈레톤 추출
        skeleton = self.extract_skeleton(binary_img)
        
        # 경로 추적
        paths = self.trace_skeleton_path(skeleton)
        
        strokes = []
        
        for i, path in enumerate(paths):
            # 방향 분석
            directions = self.analyze_stroke_direction(path)
            
            # 압력 추정
            pressure_profile = self.estimate_pressure_from_thickness(binary_img, skeleton, path)
            
            # 특징 검출
            features = self.detect_stroke_features(path, pressure_profile)
            
            strokes.append({
                'id': i + 1,
                'path': path,
                'directions': directions,
                'pressure_profile': pressure_profile,
                'features': features,
                'length': self.calculate_path_length(path)
            })
        
        return {
            'skeleton': skeleton,
            'strokes': strokes,
            'num_strokes': len(strokes)
        }
    
    def calculate_path_length(self, path):
        """경로 길이 계산"""
        if len(path) < 2:
            return 0
        
        length = 0
        for i in range(1, len(path)):
            p1 = np.array(path[i-1])
            p2 = np.array(path[i])
            length += np.linalg.norm(p2 - p1)
        
        return length
    
    def estimate_stroke_order(self, strokes, binary_img):
        """획순 추정 (한자 작성 규칙 기반)"""
        # 일반적인 한자 획순 규칙:
        # 1. 위에서 아래로
        # 2. 왼쪽에서 오른쪽으로
        # 3. 가로획 다음 세로획
        # 4. 삐침 다음 파임
        
        stroke_scores = []
        
        for stroke in strokes:
            if len(stroke['path']) == 0:
                continue
                
            start = stroke['path'][0]
            end = stroke['path'][-1]
            
            # 점수 계산 (낮을수록 먼저)
            score = 0
            
            # 1. 위쪽에서 시작하는 획 우선
            score += start[1] * 100
            
            # 2. 왼쪽에서 시작하는 획 우선
            score += start[0] * 10
            
            # 3. 가로획인지 세로획인지 판단
            dx = abs(end[0] - start[0])
            dy = abs(end[1] - start[1])
            
            if dx > dy:  # 가로획
                score -= 50
            
            stroke_scores.append((stroke['id'], score))
        
        # 점수 순으로 정렬
        stroke_scores.sort(key=lambda x: x[1])
        
        return [s[0] for s in stroke_scores]


def visualize_brush_dynamics(analysis_result, original_img, output_dir):
    """붓 다이나믹스 시각화"""
    
    fig = plt.figure(figsize=(24, 16))
    
    strokes = analysis_result['strokes']
    skeleton = analysis_result['skeleton']
    
    # 1. 원본 이미지
    ax1 = plt.subplot(3, 4, 1)
    ax1.imshow(original_img, cmap='gray')
    ax1.set_title('원본 글자', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # 2. 스켈레톤
    ax2 = plt.subplot(3, 4, 2)
    ax2.imshow(skeleton, cmap='gray')
    ax2.set_title('스켈레톤', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # 3. 붓 움직임 방향
    ax3 = plt.subplot(3, 4, 3)
    direction_map = create_direction_map(strokes, original_img.shape)
    ax3.imshow(direction_map)
    ax3.set_title('붓 이동 방향', fontsize=12, fontweight='bold')
    ax3.axis('off')
    
    # 4. 압력 히트맵
    ax4 = plt.subplot(3, 4, 4)
    pressure_map = create_pressure_heatmap(strokes, original_img.shape)
    im = ax4.imshow(pressure_map, cmap='hot')
    ax4.set_title('압력 분포', fontsize=12, fontweight='bold')
    ax4.axis('off')
    plt.colorbar(im, ax=ax4, fraction=0.046)
    
    # 5. 획순 시각화
    ax5 = plt.subplot(3, 4, 5)
    stroke_order_map = create_stroke_order_visualization(strokes, original_img.shape)
    ax5.imshow(stroke_order_map)
    ax5.set_title('추정 획순', fontsize=12, fontweight='bold')
    ax5.axis('off')
    
    # 6. 속도 분석
    ax6 = plt.subplot(3, 4, 6)
    speed_profile = create_speed_profile(strokes)
    if speed_profile:
        ax6.plot(speed_profile, 'b-', linewidth=2)
        ax6.set_title('붓 속도 프로파일', fontsize=12, fontweight='bold')
        ax6.set_xlabel('경로 상 위치')
        ax6.set_ylabel('속도')
        ax6.grid(True, alpha=0.3)
    
    # 7. 압력 프로파일
    ax7 = plt.subplot(3, 4, 7)
    pressure_graph = create_pressure_graph(strokes)
    if pressure_graph is not None and len(pressure_graph) > 0:
        ax7.plot(pressure_graph, 'r-', linewidth=2)
        ax7.fill_between(range(len(pressure_graph)), pressure_graph, alpha=0.3, color='red')
        ax7.set_title('압력 변화 그래프', fontsize=12, fontweight='bold')
        ax7.set_xlabel('경로 상 위치')
        ax7.set_ylabel('압력 (굵기)')
        ax7.grid(True, alpha=0.3)
    
    # 8. 특징점 표시
    ax8 = plt.subplot(3, 4, 8)
    feature_map = create_feature_map(strokes, original_img)
    ax8.imshow(feature_map)
    ax8.set_title('주요 특징점', fontsize=12, fontweight='bold')
    ax8.axis('off')
    
    # 9. 각 획별 상세 분석
    for i, stroke in enumerate(strokes[:4]):  # 최대 4개 획
        ax = plt.subplot(3, 4, 9 + i)
        stroke_detail = visualize_single_stroke(stroke, original_img.shape)
        ax.imshow(stroke_detail)
        ax.set_title(f'획 {stroke["id"]} 상세', fontsize=10)
        ax.axis('off')
    
    # 전체 제목
    plt.suptitle('붓 움직임 및 압력 다이나믹스 분석', fontsize=16, fontweight='bold')
    
    # 텍스트 분석 결과
    analysis_text = generate_analysis_text(strokes)
    fig.text(0.02, 0.02, analysis_text, fontsize=10, 
             verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'brush_dynamics.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ 붓 다이나믹스 분석 저장: {result_path}")


def create_direction_map(strokes, shape):
    """방향 맵 생성"""
    h, w = shape[:2]
    direction_map = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    # HSV 색상으로 방향 표현 (색상 = 각도)
    for stroke in strokes:
        for direction in stroke['directions']:
            x, y = direction['position']
            angle = direction['angle']
            
            # 각도를 0-180 범위로 정규화
            hue = int((angle + 180) * 180 / 360)
            
            # HSV 색상 설정
            color_hsv = np.array([[[hue, 255, 255]]], dtype=np.uint8)
            color_rgb = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2RGB)[0, 0]
            
            # 화살표 그리기
            if 'vector' in direction:
                v = direction['vector']
                v_len = np.linalg.norm(v)
                if v_len > 0:
                    v_norm = v / v_len * 10
                    end_x = int(x + v_norm[0])
                    end_y = int(y + v_norm[1])
                    # color_rgb를 리스트로 변환하고 int로 캐스팅
                    color_list = [int(c) for c in color_rgb.tolist()]
                    cv2.arrowedLine(direction_map, (x, y), (end_x, end_y), 
                                  color_list, 2, tipLength=0.3)
    
    return direction_map


def create_pressure_heatmap(strokes, shape):
    """압력 히트맵 생성"""
    h, w = shape[:2]
    pressure_map = np.zeros((h, w), dtype=np.float32)
    
    for stroke in strokes:
        for point in stroke['pressure_profile']:
            x, y = point['position']
            pressure = point['pressure']
            
            # 압력값을 주변에 확산
            radius = max(1, int(pressure / 2))
            cv2.circle(pressure_map, (x, y), radius, float(pressure), -1)
    
    # 정규화
    if pressure_map.max() > 0:
        pressure_map = pressure_map / pressure_map.max()
    
    return pressure_map


def create_stroke_order_visualization(strokes, shape):
    """획순 시각화"""
    h, w = shape[:2]
    order_map = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    # 색상 그라데이션으로 획순 표현
    colors = plt.cm.rainbow(np.linspace(0, 1, len(strokes)))
    
    for i, stroke in enumerate(strokes):
        color = (colors[i][:3] * 255).astype(np.uint8)
        
        # 획 경로 그리기
        for j in range(len(stroke['path']) - 1):
            p1 = stroke['path'][j]
            p2 = stroke['path'][j + 1]
            cv2.line(order_map, p1, p2, color.tolist(), 3)
        
        # 시작점 표시
        if len(stroke['path']) > 0:
            cv2.circle(order_map, stroke['path'][0], 5, (0, 255, 0), -1)
            cv2.putText(order_map, str(i+1), stroke['path'][0], 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # 끝점 표시
        if len(stroke['path']) > 0:
            cv2.circle(order_map, stroke['path'][-1], 5, (255, 0, 0), -1)
    
    return order_map


def create_speed_profile(strokes):
    """속도 프로파일 생성"""
    all_speeds = []
    
    for stroke in strokes:
        for direction in stroke['directions']:
            all_speeds.append(direction['speed'])
    
    return all_speeds


def create_pressure_graph(strokes):
    """압력 그래프 생성"""
    all_pressures = []
    
    for stroke in strokes:
        for point in stroke['pressure_profile']:
            all_pressures.append(point['pressure'])
    
    # 스무딩
    if len(all_pressures) > 10:
        window_size = 5
        smoothed = np.convolve(all_pressures, 
                               np.ones(window_size)/window_size, 
                               mode='valid')
        return smoothed
    
    return all_pressures


def create_feature_map(strokes, original_img):
    """특징점 맵 생성"""
    if len(original_img.shape) == 2:
        feature_map = cv2.cvtColor(original_img, cv2.COLOR_GRAY2RGB)
    else:
        feature_map = original_img.copy()
    
    for stroke in strokes:
        features = stroke['features']
        
        # 시작점 (녹색)
        if features['start']:
            cv2.circle(feature_map, features['start'], 8, (0, 255, 0), -1)
            cv2.putText(feature_map, 'S', features['start'], 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 끝점 (빨간색)
        if features['end']:
            cv2.circle(feature_map, features['end'], 8, (255, 0, 0), -1)
            cv2.putText(feature_map, 'E', features['end'], 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 전환점 (파란색)
        for tp in features['turning_points']:
            cv2.circle(feature_map, tp, 5, (0, 0, 255), -1)
        
        # 압력 피크 (노란색)
        for pp in features['pressure_peaks']:
            cv2.circle(feature_map, pp, 4, (255, 255, 0), -1)
    
    return feature_map


def visualize_single_stroke(stroke, shape):
    """단일 획 상세 시각화"""
    h, w = shape[:2]
    detail_map = np.ones((h, w, 3), dtype=np.uint8) * 255
    
    if len(stroke['path']) == 0:
        return detail_map
    
    # 경로 그리기 (그라데이션)
    for i in range(len(stroke['path']) - 1):
        # 진행도에 따른 색상 변화 (파랑 -> 빨강)
        progress = i / max(1, len(stroke['path']) - 1)
        color = (int(255 * progress), 0, int(255 * (1 - progress)))
        
        p1 = stroke['path'][i]
        p2 = stroke['path'][i + 1]
        
        # 압력에 따른 굵기
        thickness = 2
        if i < len(stroke['pressure_profile']):
            thickness = max(1, int(stroke['pressure_profile'][i]['pressure'] / 10))
        
        cv2.line(detail_map, p1, p2, color, thickness)
    
    # 시작점과 끝점 강조
    cv2.circle(detail_map, stroke['path'][0], 5, (0, 255, 0), -1)
    cv2.circle(detail_map, stroke['path'][-1], 5, (255, 0, 0), -1)
    
    return detail_map


def generate_analysis_text(strokes):
    """분석 텍스트 생성"""
    text = "📊 붓 다이나믹스 분석 결과\n"
    text += "=" * 40 + "\n"
    text += f"검출된 획 수: {len(strokes)}개\n\n"
    
    for i, stroke in enumerate(strokes[:3]):  # 주요 3개 획
        text += f"획 {stroke['id']}:\n"
        text += f"  • 길이: {stroke['length']:.1f}px\n"
        
        if stroke['pressure_profile']:
            pressures = [p['pressure'] for p in stroke['pressure_profile']]
            text += f"  • 평균 압력: {np.mean(pressures):.1f}\n"
            text += f"  • 압력 변화: {np.std(pressures):.1f}\n"
        
        if stroke['directions']:
            speeds = [d['speed'] for d in stroke['directions']]
            text += f"  • 평균 속도: {np.mean(speeds):.1f}\n"
        
        text += f"  • 전환점: {len(stroke['features']['turning_points'])}개\n"
        text += "\n"
    
    return text


def process_brush_dynamics():
    """붓 다이나믹스 분석 실행"""
    
    analyzer = BrushDynamicsAnalyzer()
    analyzer.setup_korean_font()
    
    # 이미지 경로
    user_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"
    ref_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"
    
    # 이미지 로드
    user_img = cv2.imread(user_img_path, cv2.IMREAD_GRAYSCALE)
    ref_img = cv2.imread(ref_img_path, cv2.IMREAD_GRAYSCALE)
    
    print("✅ 이미지 로드 완료")
    
    # 이진화
    _, user_binary = cv2.threshold(user_img, 127, 255, cv2.THRESH_BINARY_INV)
    _, ref_binary = cv2.threshold(ref_img, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 출력 디렉토리
    output_dir = "brush_dynamics_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🖌️ 사용자 글자 붓 다이나믹스 분석 중...")
    user_dynamics = analyzer.analyze_brush_dynamics(user_binary)
    
    print("🖌️ 교본 글자 붓 다이나믹스 분석 중...")
    ref_dynamics = analyzer.analyze_brush_dynamics(ref_binary)
    
    # 획순 추정
    if user_dynamics['strokes']:
        stroke_order = analyzer.estimate_stroke_order(user_dynamics['strokes'], user_binary)
        print(f"📝 추정 획순: {stroke_order}")
    
    # 시각화
    print("📊 시각화 생성 중...")
    visualize_brush_dynamics(user_dynamics, user_binary, output_dir)
    
    # 교본 분석도 시각화
    visualize_brush_dynamics(ref_dynamics, ref_binary, output_dir)
    os.rename(os.path.join(output_dir, 'brush_dynamics.png'),
              os.path.join(output_dir, 'ref_brush_dynamics.png'))
    
    # 사용자 것 다시 생성
    visualize_brush_dynamics(user_dynamics, user_binary, output_dir)
    
    return user_dynamics, ref_dynamics


def main():
    print("="*60)
    print("🖌️ 붓 움직임 및 압력 분석 시스템")
    print("  - 스켈레톤 기반 붓 경로 추적")
    print("  - 굵기 변화로 압력 추정")
    print("  - 획순 및 방향 검출")
    print("="*60)
    
    try:
        user_dynamics, ref_dynamics = process_brush_dynamics()
        
        print("\n" + "="*60)
        print("📊 분석 완료")
        print("="*60)
        
        print(f"\n사용자 글자:")
        print(f"  • 검출된 획 수: {user_dynamics['num_strokes']}개")
        
        for stroke in user_dynamics['strokes'][:3]:
            print(f"  • 획 {stroke['id']}: 길이 {stroke['length']:.1f}px")
        
        print(f"\n교본 글자:")
        print(f"  • 검출된 획 수: {ref_dynamics['num_strokes']}개")
        
        print("\n✅ 결과가 brush_dynamics_output/ 폴더에 저장되었습니다.")
        print("  - brush_dynamics.png (사용자 글자)")
        print("  - ref_brush_dynamics.png (교본 글자)")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()