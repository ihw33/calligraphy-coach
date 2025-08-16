#!/usr/bin/env python3
"""
고급 서예 획 분석 시스템
- 선 굵기 변화 추적
- 획 간격 측정
- 꺾임 부분 붓 움직임 분석
- 시작점과 중심점 정렬
"""

import cv2
import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks
from skimage.morphology import skeletonize, medial_axis
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class AdvancedStrokeAnalyzer:
    def __init__(self):
        self.stroke_order = []
        self.thickness_profile = []
        self.turning_points = []
        self.stroke_spacing = []
        
    def detect_starting_point(self, img):
        """글자의 시작점 검출 (획순 1번)"""
        # 에지 검출
        edges = cv2.Canny(img, 50, 150)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 가장 큰 윤곽선 선택
            largest = max(contours, key=cv2.contourArea)
            
            # 중국 서예 규칙: 위에서 아래, 왼쪽에서 오른쪽
            # "中"자의 경우 왼쪽 세로획이 첫 획
            if len(largest) > 0:
                leftmost = tuple(largest[largest[:,:,0].argmin()][0])
                
                # 왼쪽 세로획의 상단 찾기
                left_x = leftmost[0]
                left_points = [pt[0] for pt in largest if pt[0][0] < left_x + 20]
                if left_points:
                    topmost = min(left_points, key=lambda p: p[1])
                    return tuple(topmost)
                return leftmost
            
        return (img.shape[1]//4, img.shape[0]//4)  # 기본값
    
    def find_center_point(self, img):
        """글자의 중심점 찾기"""
        # 이진화
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 모멘트 계산
        M = cv2.moments(binary)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
        
        return (img.shape[1]//2, img.shape[0]//2)
    
    def align_images(self, reference_img, user_img):
        """시작점과 중심점을 기준으로 이미지 정렬"""
        # 중심점 찾기
        ref_center = self.find_center_point(reference_img)
        user_center = self.find_center_point(user_img)
        
        # 시작점 찾기
        ref_start = self.detect_starting_point(reference_img)
        user_start = self.detect_starting_point(user_img)
        
        # 이동 벡터 계산
        dx = ref_center[0] - user_center[0]
        dy = ref_center[1] - user_center[1]
        
        # 회전 각도 계산 (시작점 기준)
        angle_ref = np.arctan2(ref_start[1] - ref_center[1], 
                               ref_start[0] - ref_center[0])
        angle_user = np.arctan2(user_start[1] - user_center[1], 
                                user_start[0] - user_center[0])
        rotation = np.degrees(angle_ref - angle_user)
        
        # 변환 행렬 생성
        M_translate = np.float32([[1, 0, dx], [0, 1, dy]])
        M_rotate = cv2.getRotationMatrix2D(user_center, rotation, 1)
        
        # 이미지 변환 적용
        aligned = cv2.warpAffine(user_img, M_translate, 
                                 (user_img.shape[1], user_img.shape[0]))
        aligned = cv2.warpAffine(aligned, M_rotate,
                                 (aligned.shape[1], aligned.shape[0]))
        
        return aligned, ref_center, ref_start
    
    def analyze_thickness_variation(self, img):
        """선 굵기 변화 분석"""
        # 이진화
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 거리 변환으로 굵기 맵 생성
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # 스켈레톤 추출
        skeleton = skeletonize(binary > 0)
        
        # 스켈레톤 따라 굵기 샘플링
        skel_points = np.argwhere(skeleton)
        thickness_values = []
        
        for point in skel_points:
            thickness = dist_transform[point[0], point[1]] * 2  # 반경을 직경으로
            thickness_values.append(thickness)
        
        # 굵기 변화 프로파일 생성
        if thickness_values:
            # 스무딩
            from scipy.ndimage import gaussian_filter1d
            smoothed = gaussian_filter1d(thickness_values, sigma=2)
            
            # 변화율 계산
            variation = np.gradient(smoothed)
            
            return {
                'mean_thickness': np.mean(thickness_values),
                'max_thickness': np.max(thickness_values),
                'min_thickness': np.min(thickness_values),
                'variation_std': np.std(variation),
                'thickness_profile': smoothed,
                'skeleton_points': skel_points
            }
        
        return None
    
    def detect_turning_points(self, img):
        """꺾임 부분 검출 및 붓 움직임 분석"""
        # 스켈레톤 추출
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        skeleton = skeletonize(binary > 0)
        
        # 스켈레톤 포인트 추출
        skel_points = np.argwhere(skeleton)
        
        if len(skel_points) < 3:
            return []
        
        # 각도 변화 계산
        turning_points = []
        window_size = 5
        
        for i in range(window_size, len(skel_points) - window_size):
            # 이전과 이후 벡터
            v1 = skel_points[i] - skel_points[i-window_size]
            v2 = skel_points[i+window_size] - skel_points[i]
            
            # 각도 계산
            angle = np.arccos(np.clip(np.dot(v1, v2) / 
                                      (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6),
                                      -1, 1))
            angle_deg = np.degrees(angle)
            
            # 급격한 방향 변화 감지 (30도 이상)
            if angle_deg > 30:
                # 붓 압력 추정 (꺾임 부분의 굵기)
                dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
                pressure = dist_transform[skel_points[i][0], skel_points[i][1]]
                
                turning_points.append({
                    'position': skel_points[i],
                    'angle': angle_deg,
                    'estimated_pressure': pressure,
                    'stroke_direction_before': np.degrees(np.arctan2(v1[1], v1[0])),
                    'stroke_direction_after': np.degrees(np.arctan2(v2[1], v2[0]))
                })
        
        return turning_points
    
    def analyze_stroke_spacing(self, img):
        """획 사이 간격 분석"""
        # 이진화
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 연결된 컴포넌트 레이블링
        labeled = label(binary)
        regions = regionprops(labeled)
        
        if len(regions) < 2:
            return None
        
        # 각 획의 중심점 계산
        centroids = [r.centroid for r in regions]
        
        # 획 간 거리 계산
        spacing_data = []
        for i in range(len(centroids)):
            for j in range(i+1, len(centroids)):
                dist = np.linalg.norm(np.array(centroids[i]) - np.array(centroids[j]))
                spacing_data.append({
                    'stroke1': i,
                    'stroke2': j,
                    'distance': dist,
                    'relative_position': self._get_relative_position(centroids[i], centroids[j])
                })
        
        return spacing_data
    
    def _get_relative_position(self, p1, p2):
        """두 점의 상대 위치 관계"""
        dx = p2[1] - p1[1]  # x 차이
        dy = p2[0] - p1[0]  # y 차이
        
        if abs(dx) > abs(dy):
            return "horizontal" if dx > 0 else "horizontal_reversed"
        else:
            return "vertical" if dy > 0 else "vertical_reversed"
    
    def analyze_stroke_order(self, img):
        """획순 분석 (中자 기준)"""
        # 中자의 표준 획순
        # 1. 왼쪽 세로획
        # 2. 가운데 세로획 (관통)
        # 3. 상단 가로획
        # 4. 하단 가로획
        
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        h, w = binary.shape
        
        # 영역별 획 검출
        strokes = {
            '1_left_vertical': binary[:, :w//3],
            '2_center_vertical': binary[:, w//3:2*w//3],
            '3_top_horizontal': binary[:h//2, :],
            '4_bottom_horizontal': binary[h//2:, :]
        }
        
        stroke_presence = {}
        for name, region in strokes.items():
            presence = np.sum(region > 0) / region.size
            stroke_presence[name] = presence
        
        return stroke_presence
    
    def visualize_analysis(self, reference_img, user_img, output_path):
        """종합 분석 시각화"""
        # 이미지 정렬
        aligned_user, center, start = self.align_images(reference_img, user_img)
        
        # 분석 수행
        ref_thickness = self.analyze_thickness_variation(reference_img)
        user_thickness = self.analyze_thickness_variation(aligned_user)
        
        ref_turning = self.detect_turning_points(reference_img)
        user_turning = self.detect_turning_points(aligned_user)
        
        ref_spacing = self.analyze_stroke_spacing(reference_img)
        user_spacing = self.analyze_stroke_spacing(aligned_user)
        
        ref_order = self.analyze_stroke_order(reference_img)
        user_order = self.analyze_stroke_order(aligned_user)
        
        # 시각화
        fig = plt.figure(figsize=(20, 12))
        
        # 1. 정렬된 오버레이
        ax1 = plt.subplot(2, 4, 1)
        overlay = cv2.addWeighted(reference_img, 0.5, aligned_user, 0.5, 0)
        ax1.imshow(overlay, cmap='gray')
        ax1.plot(center[0], center[1], 'r+', markersize=15, label='중심점')
        ax1.plot(start[0], start[1], 'g^', markersize=10, label='시작점')
        ax1.set_title('정렬된 비교 (중심점/시작점 기준)')
        ax1.legend()
        ax1.axis('off')
        
        # 2. 굵기 변화 프로파일
        ax2 = plt.subplot(2, 4, 2)
        if ref_thickness and user_thickness:
            x_ref = np.linspace(0, 100, len(ref_thickness['thickness_profile']))
            x_user = np.linspace(0, 100, len(user_thickness['thickness_profile']))
            ax2.plot(x_ref, ref_thickness['thickness_profile'], 'b-', label='교본', linewidth=2)
            ax2.plot(x_user, user_thickness['thickness_profile'], 'r-', label='작성본', linewidth=2)
            ax2.set_xlabel('획 진행도 (%)')
            ax2.set_ylabel('선 굵기 (픽셀)')
            ax2.set_title('선 굵기 변화 분석')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. 꺾임 부분 분석
        ax3 = plt.subplot(2, 4, 3)
        ax3.imshow(aligned_user, cmap='gray')
        for tp in user_turning[:5]:  # 상위 5개 꺾임점
            y, x = tp['position']
            ax3.plot(x, y, 'ro', markersize=8)
            ax3.annotate(f"{tp['angle']:.0f}°", 
                        (x, y), xytext=(5, 5), 
                        textcoords='offset points',
                        color='red', fontsize=8)
        ax3.set_title('꺾임 부분 검출 (각도 표시)')
        ax3.axis('off')
        
        # 4. 획 간격 히트맵
        ax4 = plt.subplot(2, 4, 4)
        if ref_spacing and user_spacing:
            # 간격 비교 매트릭스
            n_strokes = 4  # 中자는 4획
            spacing_matrix = np.zeros((n_strokes, n_strokes))
            for s in user_spacing:
                if s['stroke1'] < n_strokes and s['stroke2'] < n_strokes:
                    spacing_matrix[s['stroke1'], s['stroke2']] = s['distance']
                    spacing_matrix[s['stroke2'], s['stroke1']] = s['distance']
            
            im = ax4.imshow(spacing_matrix, cmap='coolwarm')
            ax4.set_title('획 간격 매트릭스')
            ax4.set_xlabel('획 번호')
            ax4.set_ylabel('획 번호')
            plt.colorbar(im, ax=ax4, label='거리(픽셀)')
        
        # 5. 붓 압력 추정 맵
        ax5 = plt.subplot(2, 4, 5)
        _, binary = cv2.threshold(aligned_user, 127, 255, cv2.THRESH_BINARY_INV)
        dist_map = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        im5 = ax5.imshow(dist_map, cmap='hot')
        ax5.set_title('추정 붓 압력 분포')
        plt.colorbar(im5, ax=ax5, label='압력')
        ax5.axis('off')
        
        # 6. 획순 정확도
        ax6 = plt.subplot(2, 4, 6)
        stroke_names = ['좌측\n세로', '중앙\n세로', '상단\n가로', '하단\n가로']
        ref_values = list(ref_order.values())
        user_values = list(user_order.values())
        
        x = np.arange(len(stroke_names))
        width = 0.35
        
        ax6.bar(x - width/2, ref_values, width, label='교본', color='blue', alpha=0.7)
        ax6.bar(x + width/2, user_values, width, label='작성본', color='red', alpha=0.7)
        ax6.set_xlabel('획 순서')
        ax6.set_ylabel('획 강도')
        ax6.set_title('획순별 분포')
        ax6.set_xticks(x)
        ax6.set_xticklabels(stroke_names)
        ax6.legend()
        
        # 7. 방향 벡터 필드
        ax7 = plt.subplot(2, 4, 7)
        if user_thickness:
            skel_points = user_thickness['skeleton_points']
            if len(skel_points) > 20:
                # 샘플링
                step = len(skel_points) // 20
                sampled = skel_points[::step]
                
                ax7.imshow(aligned_user, cmap='gray', alpha=0.3)
                
                for i in range(1, len(sampled)):
                    y1, x1 = sampled[i-1]
                    y2, x2 = sampled[i]
                    ax7.arrow(x1, y1, x2-x1, y2-y1,
                             head_width=3, head_length=2,
                             fc='red', ec='red', alpha=0.7)
                
                ax7.set_title('붓 진행 방향 벡터')
                ax7.axis('off')
        
        # 8. 종합 점수
        ax8 = plt.subplot(2, 4, 8)
        
        # 점수 계산
        scores = {
            '굵기 일치도': self._calculate_thickness_score(ref_thickness, user_thickness),
            '꺾임 정확도': self._calculate_turning_score(ref_turning, user_turning),
            '간격 균일성': self._calculate_spacing_score(ref_spacing, user_spacing),
            '획순 정확도': self._calculate_order_score(ref_order, user_order)
        }
        
        categories = list(scores.keys())
        values = list(scores.values())
        colors = ['green' if v >= 70 else 'orange' if v >= 50 else 'red' for v in values]
        
        bars = ax8.bar(categories, values, color=colors, alpha=0.7)
        ax8.set_ylim(0, 100)
        ax8.set_ylabel('점수')
        ax8.set_title('종합 분석 점수')
        ax8.axhline(y=70, color='g', linestyle='--', alpha=0.5, label='목표선')
        
        # 점수 표시
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{val:.0f}점', ha='center', va='bottom')
        
        plt.suptitle('한자 "中" 고급 서예 분석', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return scores
    
    def _calculate_thickness_score(self, ref, user):
        """굵기 일치도 점수"""
        if not ref or not user:
            return 0
        
        diff = abs(ref['mean_thickness'] - user['mean_thickness'])
        variation_diff = abs(ref['variation_std'] - user['variation_std'])
        
        score = max(0, 100 - diff * 5 - variation_diff * 10)
        return min(100, score)
    
    def _calculate_turning_score(self, ref, user):
        """꺾임 정확도 점수"""
        if not ref and not user:
            return 100
        if not ref or not user:
            return 50
        
        # 꺾임 개수 비교
        count_diff = abs(len(ref) - len(user))
        score = max(0, 100 - count_diff * 20)
        
        return min(100, score)
    
    def _calculate_spacing_score(self, ref, user):
        """간격 균일성 점수"""
        if not ref or not user:
            return 50
        
        # 평균 간격 계산
        ref_mean = np.mean([s['distance'] for s in ref])
        user_mean = np.mean([s['distance'] for s in user])
        
        diff = abs(ref_mean - user_mean) / ref_mean * 100
        score = max(0, 100 - diff)
        
        return min(100, score)
    
    def _calculate_order_score(self, ref, user):
        """획순 정확도 점수"""
        if not ref or not user:
            return 50
        
        # 각 획의 존재 비율 비교
        total_diff = 0
        for key in ref.keys():
            if key in user:
                total_diff += abs(ref[key] - user[key])
        
        score = max(0, 100 - total_diff * 100)
        return min(100, score)


# 테스트 실행
if __name__ == "__main__":
    analyzer = AdvancedStrokeAnalyzer()
    
    # 더미 이미지 생성 (실제 이미지로 교체 필요)
    reference = np.ones((200, 200), dtype=np.uint8) * 255
    cv2.rectangle(reference, (50, 20), (60, 180), 0, -1)  # 왼쪽 세로
    cv2.rectangle(reference, (95, 10), (105, 190), 0, -1)  # 중앙 세로
    cv2.rectangle(reference, (40, 50), (160, 60), 0, -1)  # 상단 가로
    cv2.rectangle(reference, (40, 140), (160, 150), 0, -1)  # 하단 가로
    
    user = np.ones((200, 200), dtype=np.uint8) * 255
    cv2.rectangle(user, (48, 25), (62, 175), 0, -1)  # 왼쪽 세로 (약간 틀림)
    cv2.rectangle(user, (93, 15), (107, 185), 0, -1)  # 중앙 세로
    cv2.rectangle(user, (38, 52), (162, 63), 0, -1)  # 상단 가로
    cv2.rectangle(user, (38, 138), (162, 152), 0, -1)  # 하단 가로
    
    # 분석 실행
    output_path = '/Users/m4_macbook/char-comparison-system/visualizations/advanced_analysis.png'
    scores = analyzer.visualize_analysis(reference, user, output_path)
    
    print("\n=== 고급 서예 분석 완료 ===")
    print(f"분석 결과 저장: {output_path}")
    print("\n종합 점수:")
    for category, score in scores.items():
        print(f"  {category}: {score:.1f}점")
    
    total_score = np.mean(list(scores.values()))
    print(f"\n최종 점수: {total_score:.1f}점")
    
    # 등급 판정
    if total_score >= 90:
        grade = "A (우수)"
    elif total_score >= 80:
        grade = "B (양호)"
    elif total_score >= 70:
        grade = "C (보통)"
    elif total_score >= 60:
        grade = "D (미흡)"
    else:
        grade = "F (부족)"
    
    print(f"등급: {grade}")