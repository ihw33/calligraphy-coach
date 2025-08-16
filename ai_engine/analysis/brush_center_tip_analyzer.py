#!/usr/bin/env python3
"""
붓 중봉(中鋒) 분석 시스템
- 붓이 바로 세워졌는지 추적
- 편봉(偏鋒) vs 중봉(中鋒) 구분
- 붓끝 궤적과 선 중심선 비교
"""

import cv2
import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks, savgol_filter
from skimage.morphology import skeletonize, medial_axis
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Arrow
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class BrushCenterTipAnalyzer:
    def __init__(self):
        self.center_line = None
        self.brush_trajectory = None
        self.deviation_map = None
        
    def analyze_stroke_symmetry(self, stroke_img):
        """획의 좌우 대칭성 분석 - 중봉의 핵심 지표"""
        _, binary = cv2.threshold(stroke_img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 스켈레톤 (중심선) 추출
        skeleton = skeletonize(binary > 0)
        
        # 거리 변환으로 각 점의 두께 측정
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # 스켈레톤 상의 각 점에서 좌우 대칭성 검사
        skel_points = np.argwhere(skeleton)
        symmetry_scores = []
        
        for point in skel_points:
            y, x = point
            
            # 해당 점에서의 획 두께
            thickness = dist_transform[y, x]
            if thickness < 2:
                continue
                
            # 국부적 그래디언트로 방향 계산
            window_size = 5
            y_min = max(0, y - window_size)
            y_max = min(binary.shape[0], y + window_size)
            x_min = max(0, x - window_size)
            x_max = min(binary.shape[1], x + window_size)
            
            local_region = binary[y_min:y_max, x_min:x_max]
            
            if local_region.size == 0:
                continue
            
            # 좌우 대칭성 계산
            cy, cx = local_region.shape[0]//2, local_region.shape[1]//2
            
            # 수직선 기준 좌우 비교
            left_half = local_region[:, :cx]
            right_half = local_region[:, cx:]
            
            if left_half.size > 0 and right_half.size > 0:
                # 좌우 반전 후 비교
                right_flipped = np.fliplr(right_half)
                
                # 크기 맞추기
                min_width = min(left_half.shape[1], right_flipped.shape[1])
                if min_width > 0:
                    left_compare = left_half[:, -min_width:]
                    right_compare = right_flipped[:, -min_width:]
                    
                    # 대칭성 점수 (0~1, 1이 완벽한 대칭)
                    if left_compare.size > 0 and right_compare.size > 0:
                        symmetry = 1 - (np.abs(left_compare - right_compare).sum() / 
                                       (left_compare.size * 255))
                        symmetry_scores.append({
                            'position': (x, y),
                            'symmetry': symmetry,
                            'thickness': thickness
                        })
        
        return symmetry_scores
    
    def detect_brush_angle(self, stroke_img):
        """붓의 각도 추정 - 선의 가장자리 분석"""
        _, binary = cv2.threshold(stroke_img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 엣지 검출
        edges = cv2.Canny(binary.astype(np.uint8), 50, 150)
        
        # 스켈레톤 추출
        skeleton = skeletonize(binary > 0)
        skel_points = np.argwhere(skeleton)
        
        brush_angles = []
        
        for i in range(0, len(skel_points), 5):  # 5픽셀마다 샘플링
            y, x = skel_points[i]
            
            # 해당 점 주변의 엣지 분석
            window_size = 15
            y_min = max(0, y - window_size)
            y_max = min(edges.shape[0], y + window_size)
            x_min = max(0, x - window_size)
            x_max = min(edges.shape[1], x + window_size)
            
            local_edges = edges[y_min:y_max, x_min:x_max]
            edge_points = np.argwhere(local_edges > 0)
            
            if len(edge_points) < 4:
                continue
            
            # PCA로 주 방향 찾기
            mean = edge_points.mean(axis=0)
            centered = edge_points - mean
            cov = np.cov(centered.T)
            
            if cov.shape == (2, 2):
                eigenvalues, eigenvectors = np.linalg.eig(cov)
                
                # 주 방향 (가장 큰 고유값의 고유벡터)
                main_direction = eigenvectors[:, np.argmax(eigenvalues)]
                angle = np.degrees(np.arctan2(main_direction[1], main_direction[0]))
                
                # 엣지의 분산도 (붓이 기울어졌을 때 증가)
                spread = np.sqrt(eigenvalues[0] / (eigenvalues[1] + 1e-6))
                
                brush_angles.append({
                    'position': (x, y),
                    'angle': angle,
                    'spread': spread,
                    'confidence': min(eigenvalues) / (max(eigenvalues) + 1e-6)
                })
        
        return brush_angles
    
    def analyze_ink_distribution(self, stroke_img):
        """먹의 분포 분석 - 중봉일 때 균일함"""
        _, binary = cv2.threshold(stroke_img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 거리 변환으로 농도 맵 생성
        dist_map = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # 스켈레톤 추출
        skeleton = skeletonize(binary > 0)
        
        # 스켈레톤을 따라 농도 프로파일 생성
        skel_points = np.argwhere(skeleton)
        
        ink_profiles = []
        
        for point in skel_points[::3]:  # 3픽셀마다 샘플링
            y, x = point
            
            # 수직 방향 농도 프로파일
            perpendicular_samples = []
            for offset in range(-10, 11):
                if 0 <= x + offset < dist_map.shape[1]:
                    perpendicular_samples.append(dist_map[y, x + offset])
            
            if perpendicular_samples:
                # 프로파일의 대칭성과 균일성 계산
                profile = np.array(perpendicular_samples)
                center_idx = len(profile) // 2
                
                # 중심 대비 가장자리 농도 비율
                if center_idx > 0:
                    center_value = profile[center_idx]
                    edge_values = (profile[0] + profile[-1]) / 2
                    
                    # 중봉: 중심이 진함, 편봉: 한쪽이 진함
                    concentration_ratio = center_value / (edge_values + 1e-6)
                    
                    # 좌우 비대칭도
                    left_half = profile[:center_idx]
                    right_half = profile[center_idx+1:]
                    
                    if len(left_half) > 0 and len(right_half) > 0:
                        asymmetry = abs(left_half.mean() - right_half.mean())
                        
                        ink_profiles.append({
                            'position': (x, y),
                            'concentration_ratio': concentration_ratio,
                            'asymmetry': asymmetry,
                            'profile': profile
                        })
        
        return ink_profiles
    
    def calculate_center_tip_score(self, symmetry_scores, brush_angles, ink_profiles):
        """종합 중봉 점수 계산"""
        if not symmetry_scores or not brush_angles or not ink_profiles:
            return {
                'total': 0,
                'symmetry': 0,
                'angle_consistency': 0,
                'ink_distribution': 0
            }
        
        # 1. 대칭성 점수 (40%)
        avg_symmetry = np.mean([s['symmetry'] for s in symmetry_scores])
        symmetry_score = avg_symmetry * 100
        
        # 2. 붓 각도 일관성 점수 (30%)
        angle_variations = [a['spread'] for a in brush_angles]
        avg_variation = np.mean(angle_variations)
        # 변화가 적을수록 점수 높음
        angle_score = max(0, 100 - avg_variation * 10)
        
        # 3. 먹 분포 균일성 점수 (30%)
        concentration_ratios = [i['concentration_ratio'] for i in ink_profiles]
        asymmetries = [i['asymmetry'] for i in ink_profiles]
        
        # 중심 농도가 높고 비대칭이 적을수록 좋음
        avg_concentration = np.mean(concentration_ratios)
        avg_asymmetry = np.mean(asymmetries)
        
        ink_score = (min(avg_concentration, 2) / 2 * 50 +  # 농도 비율
                    max(0, 50 - avg_asymmetry * 10))        # 대칭성
        
        # 가중 평균
        total_score = (symmetry_score * 0.4 + 
                      angle_score * 0.3 + 
                      ink_score * 0.3)
        
        return {
            'total': total_score,
            'symmetry': symmetry_score,
            'angle_consistency': angle_score,
            'ink_distribution': ink_score
        }
    
    def visualize_center_tip_analysis(self, stroke_img, output_path):
        """중봉 분석 시각화"""
        # 분석 수행
        symmetry_scores = self.analyze_stroke_symmetry(stroke_img)
        brush_angles = self.detect_brush_angle(stroke_img)
        ink_profiles = self.analyze_ink_distribution(stroke_img)
        
        # 점수 계산
        scores = self.calculate_center_tip_score(symmetry_scores, brush_angles, ink_profiles)
        
        # 시각화
        fig = plt.figure(figsize=(20, 12))
        
        # 1. 원본 이미지와 중심선
        ax1 = plt.subplot(2, 4, 1)
        ax1.imshow(stroke_img, cmap='gray')
        
        # 스켈레톤 오버레이
        _, binary = cv2.threshold(stroke_img, 127, 255, cv2.THRESH_BINARY_INV)
        skeleton = skeletonize(binary > 0)
        skeleton_overlay = np.zeros_like(stroke_img)
        skeleton_overlay[skeleton] = 255
        ax1.imshow(skeleton_overlay, cmap='Reds', alpha=0.5)
        
        ax1.set_title('획과 중심선')
        ax1.axis('off')
        
        # 2. 대칭성 히트맵
        ax2 = plt.subplot(2, 4, 2)
        if symmetry_scores:
            # 히트맵 생성
            heatmap = np.zeros_like(stroke_img, dtype=np.float32)
            for score in symmetry_scores:
                x, y = score['position']
                radius = int(score['thickness'])
                cv2.circle(heatmap, (x, y), radius, score['symmetry'], -1)
            
            im2 = ax2.imshow(heatmap, cmap='RdYlGn', vmin=0, vmax=1)
            ax2.set_title(f'좌우 대칭성 (평균: {scores["symmetry"]:.1f}점)')
            plt.colorbar(im2, ax=ax2, label='대칭도')
        ax2.axis('off')
        
        # 3. 붓 각도 분석
        ax3 = plt.subplot(2, 4, 3)
        ax3.imshow(stroke_img, cmap='gray', alpha=0.3)
        
        if brush_angles:
            for angle_data in brush_angles[::3]:  # 표시 간격 조정
                x, y = angle_data['position']
                angle = angle_data['angle']
                spread = angle_data['spread']
                
                # 각도를 화살표로 표시
                dx = np.cos(np.radians(angle)) * 10
                dy = np.sin(np.radians(angle)) * 10
                
                # 색상: 일관성이 높을수록 녹색
                color = 'green' if spread < 2 else 'orange' if spread < 3 else 'red'
                ax3.arrow(x, y, dx, dy, head_width=2, head_length=1, 
                         fc=color, ec=color, alpha=0.7)
        
        ax3.set_title(f'붓 각도 일관성 ({scores["angle_consistency"]:.1f}점)')
        ax3.axis('off')
        
        # 4. 먹 농도 분포
        ax4 = plt.subplot(2, 4, 4)
        
        # 거리 변환 히트맵
        dist_map = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        im4 = ax4.imshow(dist_map, cmap='hot')
        ax4.set_title(f'먹 농도 분포 ({scores["ink_distribution"]:.1f}점)')
        plt.colorbar(im4, ax=ax4, label='농도')
        ax4.axis('off')
        
        # 5. 중봉 vs 편봉 판정
        ax5 = plt.subplot(2, 4, 5)
        
        # 판정 결과
        if scores['total'] >= 80:
            status = "중봉 (中鋒)"
            color = 'green'
            description = "붓이 바로 세워짐\n이상적인 운필"
        elif scores['total'] >= 60:
            status = "준중봉"
            color = 'orange'
            description = "대체로 바른 자세\n약간의 개선 필요"
        else:
            status = "편봉 (偏鋒)"
            color = 'red'
            description = "붓이 기울어짐\n교정 필요"
        
        # 시각적 표현
        ax5.add_patch(Circle((0.5, 0.5), 0.3, color=color, alpha=0.3, 
                            transform=ax5.transAxes))
        ax5.text(0.5, 0.5, status, fontsize=24, fontweight='bold',
                ha='center', va='center', transform=ax5.transAxes)
        ax5.text(0.5, 0.2, description, fontsize=12,
                ha='center', va='center', transform=ax5.transAxes)
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.axis('off')
        
        # 6. 프로파일 예시
        ax6 = plt.subplot(2, 4, 6)
        
        if ink_profiles and len(ink_profiles) > 5:
            # 대표적인 프로파일 몇 개 선택
            sample_profiles = ink_profiles[::len(ink_profiles)//5][:5]
            
            for i, prof in enumerate(sample_profiles):
                profile = prof['profile']
                x_axis = np.linspace(-10, 10, len(profile))
                ax6.plot(x_axis, profile, alpha=0.7, label=f'지점 {i+1}')
            
            ax6.axvline(x=0, color='red', linestyle='--', alpha=0.5)
            ax6.set_xlabel('중심선으로부터 거리 (픽셀)')
            ax6.set_ylabel('먹 농도')
            ax6.set_title('단면 농도 프로파일')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
        
        # 7. 점수 막대 그래프
        ax7 = plt.subplot(2, 4, 7)
        
        categories = ['종합', '대칭성', '각도\n일관성', '먹 분포']
        values = [scores['total'], scores['symmetry'], 
                 scores['angle_consistency'], scores['ink_distribution']]
        colors_bar = ['blue', 'green', 'orange', 'red']
        
        bars = ax7.bar(categories, values, color=colors_bar, alpha=0.7)
        ax7.set_ylim(0, 100)
        ax7.axhline(y=80, color='g', linestyle='--', alpha=0.5, label='중봉 기준')
        ax7.axhline(y=60, color='orange', linestyle='--', alpha=0.5, label='준중봉 기준')
        ax7.set_ylabel('점수')
        ax7.set_title('중봉 평가 점수')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{val:.0f}', ha='center', va='bottom')
        ax7.legend()
        
        # 8. 운필 조언
        ax8 = plt.subplot(2, 4, 8)
        ax8.axis('off')
        
        # 조언 텍스트
        advice_text = "【운필 조언】\n\n"
        
        if scores['symmetry'] < 70:
            advice_text += "◆ 대칭성 개선\n"
            advice_text += "  • 붓을 수직으로 세우기\n"
            advice_text += "  • 손목 고정, 팔 전체 사용\n\n"
        
        if scores['angle_consistency'] < 70:
            advice_text += "◆ 각도 일관성\n"
            advice_text += "  • 붓대를 일정하게 유지\n"
            advice_text += "  • 급격한 방향 전환 피하기\n\n"
        
        if scores['ink_distribution'] < 70:
            advice_text += "◆ 먹 분포 균일화\n"
            advice_text += "  • 붓 압력 일정하게\n"
            advice_text += "  • 붓끝이 중심 통과하도록\n\n"
        
        if scores['total'] >= 80:
            advice_text += "✓ 우수한 중봉 상태!\n"
            advice_text += "  현재 자세 유지하며\n"
            advice_text += "  속도 조절 연습 추천"
        
        ax8.text(0.1, 0.9, advice_text, fontsize=11,
                verticalalignment='top', transform=ax8.transAxes)
        
        plt.suptitle(f'붓 중봉(中鋒) 분석 - 종합점수: {scores["total"]:.1f}점', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return scores
    
    def analyze_stroke_sequence(self, strokes_list):
        """여러 획의 중봉 일관성 분석"""
        consistency_scores = []
        
        for i, stroke in enumerate(strokes_list):
            symmetry = self.analyze_stroke_symmetry(stroke)
            angles = self.detect_brush_angle(stroke)
            ink = self.analyze_ink_distribution(stroke)
            
            score = self.calculate_center_tip_score(symmetry, angles, ink)
            consistency_scores.append({
                'stroke_num': i + 1,
                'score': score['total'],
                'details': score
            })
        
        # 일관성 계산 (표준편차가 작을수록 좋음)
        scores_array = np.array([s['score'] for s in consistency_scores])
        consistency = 100 - np.std(scores_array)
        
        return {
            'stroke_scores': consistency_scores,
            'overall_consistency': consistency,
            'average_score': np.mean(scores_array)
        }


# 테스트 실행
if __name__ == "__main__":
    analyzer = BrushCenterTipAnalyzer()
    
    # 테스트용 획 이미지 생성
    # 중봉 시뮬레이션 (대칭적인 획)
    center_stroke = np.ones((200, 200), dtype=np.uint8) * 255
    cv2.ellipse(center_stroke, (100, 50), (80, 15), 0, 0, 180, 0, -1)
    cv2.ellipse(center_stroke, (100, 150), (80, 15), 180, 0, 180, 0, -1)
    cv2.rectangle(center_stroke, (20, 50), (180, 150), 0, -1)
    
    # 편봉 시뮬레이션 (비대칭적인 획)
    side_stroke = np.ones((200, 200), dtype=np.uint8) * 255
    points = np.array([[30, 50], [170, 60], [160, 150], [20, 140]], np.int32)
    cv2.fillPoly(side_stroke, [points], 0)
    
    # 분석 실행
    output_path = '/Users/m4_macbook/char-comparison-system/visualizations/center_tip_analysis.png'
    scores = analyzer.visualize_center_tip_analysis(center_stroke, output_path)
    
    print("\n=== 붓 중봉(中鋒) 분석 결과 ===")
    print(f"종합 점수: {scores['total']:.1f}점")
    print(f"  - 좌우 대칭성: {scores['symmetry']:.1f}점")
    print(f"  - 각도 일관성: {scores['angle_consistency']:.1f}점")
    print(f"  - 먹 분포 균일성: {scores['ink_distribution']:.1f}점")
    
    if scores['total'] >= 80:
        print("\n판정: 중봉(中鋒) - 우수한 운필!")
    elif scores['total'] >= 60:
        print("\n판정: 준중봉 - 약간의 개선 필요")
    else:
        print("\n판정: 편봉(偏鋒) - 붓 자세 교정 필요")
    
    print(f"\n분석 결과 저장: {output_path}")