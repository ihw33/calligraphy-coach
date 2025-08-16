#!/usr/bin/env python3
"""
스켈레톤 기반 글자 분석 시스템
- 글자의 스켈레톤(골격) 추출
- 획의 기울기 분석
- 획의 굵기 측정
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import ndimage
from skimage.morphology import skeletonize
from skimage import measure
import math
import os
import platform

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
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    return False


class SkeletonAnalyzer:
    def __init__(self):
        self.setup_korean_font = setup_korean_font
        
    def extract_skeleton(self, binary_img):
        """스켈레톤 추출"""
        # scikit-image의 skeletonize 사용
        skeleton = skeletonize(binary_img > 0)
        return skeleton.astype(np.uint8) * 255
    
    def extract_skeleton_cv2(self, binary_img):
        """OpenCV를 사용한 스켈레톤 추출 (Zhang-Suen thinning)"""
        # OpenCV의 thinning 알고리즘
        skeleton = cv2.ximgproc.thinning(binary_img, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
        return skeleton
    
    def analyze_stroke_angles(self, skeleton):
        """스켈레톤에서 획의 기울기 분석"""
        # 연결된 컴포넌트 찾기
        num_labels, labels = cv2.connectedComponents(skeleton)
        
        stroke_angles = []
        
        for label in range(1, num_labels):
            # 각 획의 픽셀 추출
            stroke_pixels = np.where(labels == label)
            
            if len(stroke_pixels[0]) < 10:  # 너무 작은 컴포넌트 무시
                continue
            
            # 주성분 분석(PCA)로 주방향 찾기
            points = np.column_stack((stroke_pixels[1], stroke_pixels[0]))
            
            # 중심점 계산
            mean = np.mean(points, axis=0)
            
            # 공분산 행렬
            cov_matrix = np.cov(points.T)
            
            # 고유값과 고유벡터
            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
            
            # 주방향 (가장 큰 고유값의 고유벡터)
            main_direction = eigenvectors[:, np.argmax(eigenvalues)]
            
            # 각도 계산 (도 단위)
            angle = np.arctan2(main_direction[1], main_direction[0]) * 180 / np.pi
            
            stroke_angles.append({
                'label': label,
                'angle': angle,
                'center': mean,
                'length': np.sqrt(np.max(eigenvalues)) * 2,  # 획의 대략적 길이
                'num_pixels': len(stroke_pixels[0])
            })
        
        return stroke_angles
    
    def measure_stroke_thickness(self, binary_img, skeleton):
        """스켈레톤을 기준으로 획의 굵기 측정"""
        # 거리 변환으로 각 스켈레톤 점에서 가장 가까운 배경까지의 거리 계산
        dist_transform = cv2.distanceTransform(binary_img, cv2.DIST_L2, 5)
        
        # 스켈레톤 위치에서의 거리값 = 굵기의 절반
        skeleton_points = np.where(skeleton > 0)
        thickness_values = dist_transform[skeleton_points] * 2  # 굵기 = 반지름 * 2
        
        if len(thickness_values) > 0:
            avg_thickness = np.mean(thickness_values)
            max_thickness = np.max(thickness_values)
            min_thickness = np.min(thickness_values)
            std_thickness = np.std(thickness_values)
            
            # 획별 굵기 분석
            num_labels, labels = cv2.connectedComponents(skeleton)
            stroke_thickness = []
            
            for label in range(1, num_labels):
                stroke_points = np.where(labels == label)
                if len(stroke_points[0]) > 0:
                    stroke_thick = dist_transform[stroke_points] * 2
                    stroke_thickness.append({
                        'label': label,
                        'avg_thickness': np.mean(stroke_thick),
                        'max_thickness': np.max(stroke_thick),
                        'min_thickness': np.min(stroke_thick),
                        'uniformity': 1 - (np.std(stroke_thick) / np.mean(stroke_thick)) if np.mean(stroke_thick) > 0 else 0
                    })
            
            return {
                'overall': {
                    'avg': avg_thickness,
                    'max': max_thickness,
                    'min': min_thickness,
                    'std': std_thickness,
                    'uniformity': 1 - (std_thickness / avg_thickness) if avg_thickness > 0 else 0
                },
                'strokes': stroke_thickness
            }
        
        return None
    
    def detect_key_points(self, skeleton):
        """스켈레톤에서 주요 점 검출 (끝점, 교차점)"""
        # 3x3 커널로 이웃 픽셀 수 계산
        kernel = np.ones((3, 3), np.uint8)
        neighbors = cv2.filter2D(skeleton.astype(np.float32), -1, kernel)
        
        # 스켈레톤 위치에서만 계산
        skeleton_mask = skeleton > 0
        neighbors[~skeleton_mask] = 0
        
        # 끝점: 이웃이 2개인 점 (자기 자신 + 1개)
        endpoints = (neighbors == 2) & skeleton_mask
        
        # 교차점: 이웃이 4개 이상인 점
        junctions = (neighbors >= 4) & skeleton_mask
        
        # 좌표 추출
        endpoint_coords = np.column_stack(np.where(endpoints))
        junction_coords = np.column_stack(np.where(junctions))
        
        return {
            'endpoints': endpoint_coords,
            'junctions': junction_coords
        }
    
    def compare_skeletons(self, skeleton1, skeleton2):
        """두 스켈레톤 비교"""
        # 크기 정규화
        h = max(skeleton1.shape[0], skeleton2.shape[0])
        w = max(skeleton1.shape[1], skeleton2.shape[1])
        
        skel1_resized = cv2.resize(skeleton1, (w, h))
        skel2_resized = cv2.resize(skeleton2, (w, h))
        
        # Hausdorff 거리 계산 (형태 유사도)
        points1 = np.column_stack(np.where(skel1_resized > 0))
        points2 = np.column_stack(np.where(skel2_resized > 0))
        
        if len(points1) > 0 and len(points2) > 0:
            # 각 점에서 가장 가까운 점까지의 거리
            distances1 = []
            for p1 in points1:
                min_dist = np.min(np.sqrt(np.sum((points2 - p1)**2, axis=1)))
                distances1.append(min_dist)
            
            distances2 = []
            for p2 in points2:
                min_dist = np.min(np.sqrt(np.sum((points1 - p2)**2, axis=1)))
                distances2.append(min_dist)
            
            hausdorff_dist = max(np.max(distances1), np.max(distances2))
            avg_dist = (np.mean(distances1) + np.mean(distances2)) / 2
            
            # 정규화된 유사도 점수 (0-100)
            max_possible_dist = np.sqrt(h**2 + w**2)
            similarity = max(0, 100 * (1 - hausdorff_dist / max_possible_dist))
            
            return {
                'hausdorff_distance': hausdorff_dist,
                'average_distance': avg_dist,
                'similarity_score': similarity
            }
        
        return None


def process_skeleton_analysis():
    """스켈레톤 분석 실행"""
    
    analyzer = SkeletonAnalyzer()
    analyzer.setup_korean_font()
    
    # 이미지 경로
    user_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"
    ref_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"
    guide_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png"
    
    # 이미지 로드
    user_img = cv2.imread(user_img_path)
    ref_img = cv2.imread(ref_img_path)
    guide_img = cv2.imread(guide_img_path)
    
    print("✅ 이미지 로드 완료")
    
    # 출력 디렉토리
    output_dir = "skeleton_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 글자 추출
    user_char = extract_character(user_img)
    ref_char = extract_character(ref_img)
    guide_char = extract_character(guide_img)
    
    # 스켈레톤 추출
    print("🔍 스켈레톤 추출 중...")
    user_skeleton = analyzer.extract_skeleton(user_char)
    ref_skeleton = analyzer.extract_skeleton(ref_char)
    guide_skeleton = analyzer.extract_skeleton(guide_char)
    
    # 획 기울기 분석
    print("📐 획 기울기 분석 중...")
    user_angles = analyzer.analyze_stroke_angles(user_skeleton)
    ref_angles = analyzer.analyze_stroke_angles(ref_skeleton)
    
    # 획 굵기 측정
    print("📏 획 굵기 측정 중...")
    user_thickness = analyzer.measure_stroke_thickness(user_char, user_skeleton)
    ref_thickness = analyzer.measure_stroke_thickness(ref_char, ref_skeleton)
    
    # 주요 점 검출
    print("🎯 주요 점 검출 중...")
    user_keypoints = analyzer.detect_key_points(user_skeleton)
    ref_keypoints = analyzer.detect_key_points(ref_skeleton)
    
    # 스켈레톤 비교
    print("🔄 스켈레톤 비교 중...")
    skeleton_comparison = analyzer.compare_skeletons(user_skeleton, ref_skeleton)
    
    # 시각화
    print("📊 결과 시각화 중...")
    visualize_skeleton_analysis(
        user_img, ref_img, guide_img,
        user_char, ref_char, guide_char,
        user_skeleton, ref_skeleton, guide_skeleton,
        user_angles, ref_angles,
        user_thickness, ref_thickness,
        user_keypoints, ref_keypoints,
        skeleton_comparison,
        output_dir
    )
    
    return {
        'angles': {'user': user_angles, 'ref': ref_angles},
        'thickness': {'user': user_thickness, 'ref': ref_thickness},
        'keypoints': {'user': user_keypoints, 'ref': ref_keypoints},
        'comparison': skeleton_comparison
    }


def extract_character(img):
    """글자 추출"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 빨간색 제거
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    binary = cv2.bitwise_and(binary, cv2.bitwise_not(red_mask))
    
    return binary


def visualize_skeleton_analysis(user_img, ref_img, guide_img,
                                user_char, ref_char, guide_char,
                                user_skeleton, ref_skeleton, guide_skeleton,
                                user_angles, ref_angles,
                                user_thickness, ref_thickness,
                                user_keypoints, ref_keypoints,
                                skeleton_comparison,
                                output_dir):
    """스켈레톤 분석 결과 시각화"""
    
    fig = plt.figure(figsize=(24, 16))
    
    # 1. 원본 이미지들
    ax1 = plt.subplot(4, 6, 1)
    ax1.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('작성한 글자', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    ax2 = plt.subplot(4, 6, 2)
    ax2.imshow(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('교본 글자', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # 2. 이진화 이미지
    ax3 = plt.subplot(4, 6, 7)
    ax3.imshow(user_char, cmap='gray')
    ax3.set_title('작성 글자 (이진화)', fontsize=12)
    ax3.axis('off')
    
    ax4 = plt.subplot(4, 6, 8)
    ax4.imshow(ref_char, cmap='gray')
    ax4.set_title('교본 글자 (이진화)', fontsize=12)
    ax4.axis('off')
    
    # 3. 스켈레톤
    ax5 = plt.subplot(4, 6, 13)
    ax5.imshow(user_skeleton, cmap='gray')
    ax5.set_title('작성 글자 스켈레톤', fontsize=12, fontweight='bold', color='blue')
    ax5.axis('off')
    
    ax6 = plt.subplot(4, 6, 14)
    ax6.imshow(ref_skeleton, cmap='gray')
    ax6.set_title('교본 글자 스켈레톤', fontsize=12, fontweight='bold', color='red')
    ax6.axis('off')
    
    # 4. 스켈레톤 오버레이
    ax7 = plt.subplot(4, 6, 19)
    overlay = create_skeleton_overlay(user_char, user_skeleton, user_keypoints)
    ax7.imshow(overlay)
    ax7.set_title('스켈레톤 + 주요점', fontsize=12)
    ax7.axis('off')
    
    # 5. 두 스켈레톤 비교
    ax8 = plt.subplot(4, 6, 20)
    comparison_overlay = create_skeleton_comparison(user_skeleton, ref_skeleton)
    ax8.imshow(comparison_overlay)
    ax8.set_title('스켈레톤 비교', fontsize=12, fontweight='bold')
    ax8.axis('off')
    
    # 6. 획 기울기 분석
    ax9 = plt.subplot(4, 6, 3)
    if user_angles:
        angles = [stroke['angle'] for stroke in user_angles[:4]]  # 주요 4획
        labels = [f"획{i+1}" for i in range(len(angles))]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        bars = ax9.bar(labels, angles, color=colors)
        ax9.set_ylabel('기울기 (도)', fontsize=11)
        ax9.set_title('작성 글자 획 기울기', fontsize=12, fontweight='bold')
        ax9.set_ylim(-90, 90)
        ax9.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax9.grid(axis='y', alpha=0.3)
        
        for bar, angle in zip(bars, angles):
            ax9.text(bar.get_x() + bar.get_width()/2., angle + np.sign(angle)*3,
                    f'{angle:.1f}°', ha='center', va='bottom' if angle >= 0 else 'top', fontsize=10)
    
    # 7. 획 굵기 분석
    ax10 = plt.subplot(4, 6, 4)
    if user_thickness and user_thickness['strokes']:
        thickness_data = user_thickness['strokes'][:4]  # 주요 4획
        avg_thickness = [stroke['avg_thickness'] for stroke in thickness_data]
        uniformity = [stroke['uniformity'] * 100 for stroke in thickness_data]
        
        x = np.arange(len(thickness_data))
        width = 0.35
        
        bars1 = ax10.bar(x - width/2, avg_thickness, width, label='평균 굵기', color='#3498DB')
        bars2 = ax10.bar(x + width/2, uniformity, width, label='균일도(%)', color='#E74C3C')
        
        ax10.set_xlabel('획 번호', fontsize=11)
        ax10.set_ylabel('값', fontsize=11)
        ax10.set_title('획 굵기 분석', fontsize=12, fontweight='bold')
        ax10.set_xticks(x)
        ax10.set_xticklabels([f"획{i+1}" for i in range(len(thickness_data))])
        ax10.legend(fontsize=9)
        ax10.grid(axis='y', alpha=0.3)
    
    # 8. 굵기 히트맵
    ax11 = plt.subplot(4, 6, 9)
    thickness_heatmap = create_thickness_heatmap(user_char, user_skeleton)
    im = ax11.imshow(thickness_heatmap, cmap='jet')
    ax11.set_title('굵기 분포 히트맵', fontsize=12)
    ax11.axis('off')
    plt.colorbar(im, ax=ax11, fraction=0.046, pad=0.04)
    
    # 9. 각도 시각화
    ax12 = plt.subplot(4, 6, 15)
    angle_viz = visualize_stroke_angles(user_skeleton, user_angles)
    ax12.imshow(angle_viz)
    ax12.set_title('획 방향 시각화', fontsize=12)
    ax12.axis('off')
    
    # 10. 상세 분석 텍스트
    ax13 = plt.subplot(4, 6, 5)
    analysis_text = f"""
📐 획 기울기 분석
━━━━━━━━━━━━━━━━
• 수직획 편차: {calculate_vertical_deviation(user_angles):.1f}°
• 수평획 편차: {calculate_horizontal_deviation(user_angles):.1f}°
• 대각선 일관성: {calculate_diagonal_consistency(user_angles):.1f}%

📏 획 굵기 분석
━━━━━━━━━━━━━━━━
• 평균 굵기: {user_thickness['overall']['avg']:.1f}px
• 굵기 변화: {user_thickness['overall']['std']:.1f}px
• 균일도: {user_thickness['overall']['uniformity']*100:.1f}%

🎯 주요점 분석
━━━━━━━━━━━━━━━━
• 끝점 개수: {len(user_keypoints['endpoints'])}개
• 교차점 개수: {len(user_keypoints['junctions'])}개
"""
    ax13.text(0.05, 0.95, analysis_text, fontsize=10,
             verticalalignment='top', transform=ax13.transAxes)
    ax13.axis('off')
    ax13.set_title('상세 분석', fontsize=12, fontweight='bold')
    
    # 11. 비교 점수
    ax14 = plt.subplot(4, 6, 6)
    if skeleton_comparison:
        score_text = f"""
🔄 스켈레톤 비교
━━━━━━━━━━━━━━━━
형태 유사도: {skeleton_comparison['similarity_score']:.1f}%
Hausdorff 거리: {skeleton_comparison['hausdorff_distance']:.1f}px
평균 거리: {skeleton_comparison['average_distance']:.1f}px

📊 종합 평가
━━━━━━━━━━━━━━━━
기울기 정확도: {calculate_angle_accuracy(user_angles, ref_angles):.1f}%
굵기 일치도: {calculate_thickness_match(user_thickness, ref_thickness):.1f}%
구조 유사도: {skeleton_comparison['similarity_score']:.1f}%

최종 점수: {calculate_final_score(user_angles, ref_angles, user_thickness, ref_thickness, skeleton_comparison):.1f}점
"""
        ax14.text(0.05, 0.95, score_text, fontsize=10,
                 verticalalignment='top', transform=ax14.transAxes)
    ax14.axis('off')
    ax14.set_title('비교 결과', fontsize=12, fontweight='bold')
    
    # 12. 개선 제안
    ax15 = plt.subplot(4, 6, (21, 24))
    improvement = generate_improvement_suggestions(user_angles, ref_angles, 
                                                  user_thickness, ref_thickness,
                                                  skeleton_comparison)
    ax15.text(0.05, 0.95, improvement, fontsize=11,
             verticalalignment='top', transform=ax15.transAxes)
    ax15.axis('off')
    ax15.set_title('개선 제안', fontsize=14, fontweight='bold')
    
    plt.suptitle('中 글자 스켈레톤 기반 상세 분석', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'skeleton_analysis.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 개별 이미지 저장
    cv2.imwrite(os.path.join(output_dir, 'user_skeleton.png'), user_skeleton)
    cv2.imwrite(os.path.join(output_dir, 'ref_skeleton.png'), ref_skeleton)
    cv2.imwrite(os.path.join(output_dir, 'skeleton_overlay.png'), 
                cv2.cvtColor(comparison_overlay, cv2.COLOR_RGB2BGR))
    
    print(f"✅ 결과 저장 완료: {output_dir}/")


def create_skeleton_overlay(binary_img, skeleton, keypoints):
    """스켈레톤과 주요점 오버레이"""
    # RGB 이미지 생성
    h, w = binary_img.shape
    overlay = np.zeros((h, w, 3), dtype=np.uint8)
    
    # 원본 글자 (회색)
    overlay[binary_img > 0] = [150, 150, 150]
    
    # 스켈레톤 (파란색)
    overlay[skeleton > 0] = [255, 100, 0]
    
    # 끝점 (빨간색)
    for point in keypoints['endpoints']:
        cv2.circle(overlay, (point[1], point[0]), 3, (0, 0, 255), -1)
    
    # 교차점 (녹색)
    for point in keypoints['junctions']:
        cv2.circle(overlay, (point[1], point[0]), 3, (0, 255, 0), -1)
    
    return overlay


def create_skeleton_comparison(skeleton1, skeleton2):
    """두 스켈레톤 비교 시각화"""
    h = max(skeleton1.shape[0], skeleton2.shape[0])
    w = max(skeleton1.shape[1], skeleton2.shape[1])
    
    # 크기 맞추기
    skel1 = cv2.resize(skeleton1, (w, h))
    skel2 = cv2.resize(skeleton2, (w, h))
    
    # RGB 이미지 생성
    comparison = np.zeros((h, w, 3), dtype=np.uint8)
    comparison[:, :] = [255, 255, 255]  # 흰 배경
    
    # 작성 글자 스켈레톤 (파란색)
    comparison[skel1 > 0] = [255, 100, 0]
    
    # 교본 글자 스켈레톤 (빨간색)
    comparison[skel2 > 0] = [0, 0, 255]
    
    # 겹치는 부분 (보라색)
    overlap = (skel1 > 0) & (skel2 > 0)
    comparison[overlap] = [255, 0, 255]
    
    return comparison


def create_thickness_heatmap(binary_img, skeleton):
    """굵기 히트맵 생성"""
    # 거리 변환
    dist_transform = cv2.distanceTransform(binary_img, cv2.DIST_L2, 5)
    
    # 스켈레톤 위치의 굵기값으로 히트맵 생성
    heatmap = np.zeros_like(dist_transform)
    
    # 스켈레톤 각 점에서 굵기 값 확산
    skeleton_points = np.where(skeleton > 0)
    for y, x in zip(skeleton_points[0], skeleton_points[1]):
        thickness = dist_transform[y, x] * 2
        # cv2.circle에서 color는 정수여야 함
        cv2.circle(heatmap, (x, y), int(thickness/2), int(thickness), -1)
    
    # 원본 글자 영역만 표시
    heatmap[binary_img == 0] = 0
    
    return heatmap


def visualize_stroke_angles(skeleton, angles):
    """획 방향 시각화"""
    h, w = skeleton.shape
    viz = np.zeros((h, w, 3), dtype=np.uint8)
    viz[:, :] = [255, 255, 255]  # 흰 배경
    
    # 스켈레톤 표시
    viz[skeleton > 0] = [200, 200, 200]
    
    # 각 획의 방향 화살표 그리기
    for stroke in angles:
        center = stroke['center'].astype(int)
        angle_rad = stroke['angle'] * np.pi / 180
        length = min(stroke['length'] / 2, 30)
        
        # 화살표 끝점
        end_x = int(center[0] + length * np.cos(angle_rad))
        end_y = int(center[1] + length * np.sin(angle_rad))
        
        # 색상 (각도에 따라)
        if -10 <= stroke['angle'] <= 10:  # 수평
            color = (255, 0, 0)  # 빨강
        elif 80 <= abs(stroke['angle']) <= 100:  # 수직
            color = (0, 255, 0)  # 녹색
        else:  # 대각선
            color = (0, 0, 255)  # 파랑
        
        cv2.arrowedLine(viz, tuple(center), (end_x, end_y), color, 2)
        cv2.circle(viz, tuple(center), 3, color, -1)
    
    return viz


def calculate_vertical_deviation(angles):
    """수직획 편차 계산"""
    vertical_angles = [abs(90 - abs(s['angle'])) for s in angles if 70 <= abs(s['angle']) <= 110]
    return np.mean(vertical_angles) if vertical_angles else 0


def calculate_horizontal_deviation(angles):
    """수평획 편차 계산"""
    horizontal_angles = [abs(s['angle']) for s in angles if abs(s['angle']) <= 20]
    return np.mean(horizontal_angles) if horizontal_angles else 0


def calculate_diagonal_consistency(angles):
    """대각선 일관성 계산"""
    diagonal_angles = [s['angle'] for s in angles if 20 < abs(s['angle']) < 70]
    if len(diagonal_angles) > 1:
        return max(0, 100 - np.std(diagonal_angles))
    return 100


def calculate_angle_accuracy(user_angles, ref_angles):
    """기울기 정확도 계산"""
    if not user_angles or not ref_angles:
        return 0
    
    scores = []
    for i in range(min(len(user_angles), len(ref_angles))):
        diff = abs(user_angles[i]['angle'] - ref_angles[i]['angle'])
        score = max(0, 100 - diff * 2)  # 1도 차이당 2점 감점
        scores.append(score)
    
    return np.mean(scores) if scores else 0


def calculate_thickness_match(user_thickness, ref_thickness):
    """굵기 일치도 계산"""
    if not user_thickness or not ref_thickness:
        return 0
    
    user_avg = user_thickness['overall']['avg']
    ref_avg = ref_thickness['overall']['avg']
    
    diff_ratio = abs(user_avg - ref_avg) / ref_avg if ref_avg > 0 else 1
    return max(0, 100 * (1 - diff_ratio))


def calculate_final_score(user_angles, ref_angles, user_thickness, ref_thickness, skeleton_comparison):
    """최종 점수 계산"""
    angle_score = calculate_angle_accuracy(user_angles, ref_angles)
    thickness_score = calculate_thickness_match(user_thickness, ref_thickness)
    skeleton_score = skeleton_comparison['similarity_score'] if skeleton_comparison else 0
    
    # 가중 평균
    weights = [0.3, 0.2, 0.5]  # 기울기, 굵기, 구조
    scores = [angle_score, thickness_score, skeleton_score]
    
    return sum(w * s for w, s in zip(weights, scores))


def generate_improvement_suggestions(user_angles, ref_angles, user_thickness, ref_thickness, skeleton_comparison):
    """개선 제안 생성"""
    suggestions = []
    
    # 기울기 분석
    angle_accuracy = calculate_angle_accuracy(user_angles, ref_angles)
    if angle_accuracy < 80:
        suggestions.append("📐 획의 기울기 교정 필요")
        vertical_dev = calculate_vertical_deviation(user_angles)
        if vertical_dev > 5:
            suggestions.append("   • 수직획을 더 곧게 작성")
        horizontal_dev = calculate_horizontal_deviation(user_angles)
        if horizontal_dev > 5:
            suggestions.append("   • 수평획을 더 평평하게 작성")
    
    # 굵기 분석
    if user_thickness and ref_thickness:
        thickness_match = calculate_thickness_match(user_thickness, ref_thickness)
        if thickness_match < 80:
            if user_thickness['overall']['avg'] < ref_thickness['overall']['avg']:
                suggestions.append("📏 획을 더 굵게 작성")
            else:
                suggestions.append("📏 획을 더 가늘게 작성")
        
        if user_thickness['overall']['uniformity'] < 0.7:
            suggestions.append("   • 획 굵기를 더 균일하게 유지")
    
    # 구조 분석
    if skeleton_comparison and skeleton_comparison['similarity_score'] < 80:
        suggestions.append("🔄 전체적인 글자 구조 개선 필요")
        suggestions.append("   • 획의 시작과 끝 위치 확인")
        suggestions.append("   • 획 간 비율 조정")
    
    if not suggestions:
        suggestions.append("✨ 훌륭합니다! 계속 연습하세요.")
    
    return "💡 개선 제안\n" + "━" * 30 + "\n" + "\n".join(suggestions)


def main():
    print("="*60)
    print("🔬 스켈레톤 기반 글자 분석 시스템")
    print("  - 획 기울기 분석")
    print("  - 획 굵기 측정")
    print("  - 구조 비교")
    print("="*60)
    
    try:
        results = process_skeleton_analysis()
        
        print("\n" + "="*60)
        print("📊 분석 완료")
        print("="*60)
        
        # 결과 출력
        if results['comparison']:
            print(f"\n🔄 스켈레톤 유사도: {results['comparison']['similarity_score']:.1f}%")
        
        if results['thickness']['user']:
            print(f"\n📏 평균 획 굵기: {results['thickness']['user']['overall']['avg']:.1f}px")
            print(f"   굵기 균일도: {results['thickness']['user']['overall']['uniformity']*100:.1f}%")
        
        if results['angles']['user']:
            print(f"\n📐 검출된 획 수: {len(results['angles']['user'])}개")
            for i, stroke in enumerate(results['angles']['user'][:4]):
                print(f"   획{i+1} 기울기: {stroke['angle']:.1f}°")
        
        print("\n✅ 모든 결과가 skeleton_output/ 폴더에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()