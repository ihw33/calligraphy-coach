#!/usr/bin/env python3
"""
실제 서예 이미지 분석 시스템
- 교본과 작성본 비교
- 붓 움직임 궤적 추적
- HEIC 형식 지원
"""

import cv2
import numpy as np
from PIL import Image
import pillow_heif
from scipy import ndimage
from scipy.signal import find_peaks
from skimage.morphology import skeletonize, thin, medial_axis
from skimage.measure import label, regionprops
from skimage.filters import gaussian
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# HEIC 지원 등록
pillow_heif.register_heif_opener()

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class RealCalligraphyAnalyzer:
    def __init__(self):
        self.stroke_order = {
            '中': [
                {'name': '좌측 세로획', 'direction': 'vertical', 'order': 1},
                {'name': '우측 세로획', 'direction': 'vertical', 'order': 2},
                {'name': '상단 가로획', 'direction': 'horizontal', 'order': 3},
                {'name': '중앙 세로획', 'direction': 'vertical', 'order': 4},
                {'name': '하단 가로획', 'direction': 'horizontal', 'order': 5}
            ]
        }
    
    def load_and_preprocess(self, image_path):
        """이미지 로드 및 전처리"""
        # HEIC 형식 처리
        if image_path.lower().endswith('.heic'):
            img = Image.open(image_path)
            img_array = np.array(img)
        else:
            img_array = cv2.imread(image_path)
            if img_array is None:
                raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
        
        # 그레이스케일 변환
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        return gray
    
    def extract_brush_trajectory(self, img):
        """붓 움직임 궤적 추출"""
        # 이진화
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 스켈레톤 추출
        skeleton = skeletonize(binary > 0)
        
        # 거리 변환으로 두께 정보 획득
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # 스켈레톤 포인트들을 순서대로 연결
        skel_points = np.argwhere(skeleton)
        
        if len(skel_points) < 2:
            return None
        
        # 획순에 따른 궤적 재구성
        trajectories = []
        
        # 연결된 컴포넌트별로 분리
        labeled_skeleton = label(skeleton)
        num_strokes = np.max(labeled_skeleton)
        
        for stroke_id in range(1, num_strokes + 1):
            stroke_points = np.argwhere(labeled_skeleton == stroke_id)
            
            if len(stroke_points) > 1:
                # 시작점 찾기 (위쪽이나 왼쪽)
                start_idx = np.argmin(stroke_points[:, 0] + stroke_points[:, 1])
                start_point = stroke_points[start_idx]
                
                # 최근접 이웃으로 순서 정렬
                ordered_points = [start_point]
                remaining = list(stroke_points)
                remaining.remove(tuple(start_point))
                
                while remaining:
                    last_point = ordered_points[-1]
                    distances = [np.linalg.norm(np.array(p) - last_point) 
                                for p in remaining]
                    
                    if distances:
                        nearest_idx = np.argmin(distances)
                        if distances[nearest_idx] < 10:  # 연결 임계값
                            nearest = remaining[nearest_idx]
                            ordered_points.append(nearest)
                            remaining.remove(nearest)
                        else:
                            break
                
                # 각 점에서의 두께와 방향 정보 추가
                trajectory = []
                for i, point in enumerate(ordered_points):
                    y, x = point
                    thickness = dist_transform[y, x] * 2
                    
                    # 방향 벡터 계산
                    if i > 0 and i < len(ordered_points) - 1:
                        prev_point = ordered_points[i-1]
                        next_point = ordered_points[i+1]
                        direction = np.array(next_point) - np.array(prev_point)
                        angle = np.degrees(np.arctan2(direction[1], direction[0]))
                    else:
                        angle = 0
                    
                    trajectory.append({
                        'position': (x, y),
                        'thickness': thickness,
                        'angle': angle,
                        'order': i
                    })
                
                trajectories.append(trajectory)
        
        return trajectories
    
    def compare_strokes(self, reference_img, user_img):
        """교본과 작성본 획 비교"""
        # 궤적 추출
        ref_trajectories = self.extract_brush_trajectory(reference_img)
        user_trajectories = self.extract_brush_trajectory(user_img)
        
        if not ref_trajectories or not user_trajectories:
            return None
        
        comparisons = []
        
        # 각 획별 비교
        for i, (ref_traj, user_traj) in enumerate(zip(ref_trajectories, user_trajectories)):
            # 길이 정규화
            min_len = min(len(ref_traj), len(user_traj))
            
            # 두께 비교
            ref_thickness = [p['thickness'] for p in ref_traj[:min_len]]
            user_thickness = [p['thickness'] for p in user_traj[:min_len]]
            
            thickness_diff = np.mean(np.abs(np.array(ref_thickness) - np.array(user_thickness)))
            
            # 각도 비교
            ref_angles = [p['angle'] for p in ref_traj[:min_len]]
            user_angles = [p['angle'] for p in user_traj[:min_len]]
            
            angle_diff = np.mean(np.abs(np.array(ref_angles) - np.array(user_angles)))
            
            # 위치 비교 (정규화 후)
            ref_positions = np.array([p['position'] for p in ref_traj[:min_len]])
            user_positions = np.array([p['position'] for p in user_traj[:min_len]])
            
            # 중심 정렬
            ref_center = ref_positions.mean(axis=0)
            user_center = user_positions.mean(axis=0)
            
            ref_normalized = ref_positions - ref_center
            user_normalized = user_positions - user_center
            
            position_diff = np.mean(np.linalg.norm(ref_normalized - user_normalized, axis=1))
            
            comparisons.append({
                'stroke_num': i + 1,
                'thickness_diff': thickness_diff,
                'angle_diff': angle_diff,
                'position_diff': position_diff,
                'accuracy': max(0, 100 - thickness_diff * 5 - angle_diff * 0.5 - position_diff * 0.2)
            })
        
        return comparisons
    
    def visualize_brush_movement(self, img, trajectories, title="붓 움직임 분석"):
        """붓 움직임 시각화 (HEIC 이미지처럼)"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # 배경 이미지
        ax.imshow(img, cmap='gray', alpha=0.3)
        
        # 색상 팔레트
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for traj_idx, trajectory in enumerate(trajectories):
            if not trajectory:
                continue
            
            color = colors[traj_idx % len(colors)]
            
            # 궤적 그리기
            points = np.array([p['position'] for p in trajectory])
            
            if len(points) > 1:
                # 부드러운 곡선으로 연결
                for i in range(len(points) - 1):
                    start = points[i]
                    end = points[i + 1]
                    
                    # 두께에 따른 선 굵기 조절
                    thickness = trajectory[i]['thickness']
                    
                    # 화살표로 방향 표시
                    arrow = FancyArrowPatch(
                        start, end,
                        connectionstyle="arc3,rad=0.1",
                        arrowstyle='->,head_width=0.3,head_length=0.5',
                        color=color,
                        linewidth=max(1, thickness/5),
                        alpha=0.7
                    )
                    ax.add_patch(arrow)
                
                # 시작점과 끝점 표시
                ax.scatter(points[0][0], points[0][1], 
                          color=color, s=100, marker='o', 
                          edgecolors='white', linewidth=2,
                          label=f'획 {traj_idx+1} 시작')
                
                ax.scatter(points[-1][0], points[-1][1], 
                          color=color, s=100, marker='s',
                          edgecolors='white', linewidth=2)
                
                # 획 번호 표시
                mid_point = points[len(points)//2]
                ax.text(mid_point[0], mid_point[1], str(traj_idx+1),
                       fontsize=16, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='circle,pad=0.3', 
                                facecolor=color, alpha=0.8))
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.axis('off')
        ax.legend(loc='upper right')
        
        return fig
    
    def analyze_complete(self, reference_path, user_path, output_dir):
        """완전한 분석 수행"""
        # 이미지 로드
        ref_img = self.load_and_preprocess(reference_path)
        user_img = self.load_and_preprocess(user_path)
        
        # 궤적 추출
        ref_trajectories = self.extract_brush_trajectory(ref_img)
        user_trajectories = self.extract_brush_trajectory(user_img)
        
        # 비교 분석
        comparisons = self.compare_strokes(ref_img, user_img)
        
        # 전체 시각화
        fig = plt.figure(figsize=(24, 16))
        
        # 1. 교본 원본
        ax1 = plt.subplot(2, 4, 1)
        ax1.imshow(ref_img, cmap='gray')
        ax1.set_title('교본 (참조)', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. 작성본 원본  
        ax2 = plt.subplot(2, 4, 2)
        ax2.imshow(user_img, cmap='gray')
        ax2.set_title('작성본', fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        # 3. 교본 궤적
        ax3 = plt.subplot(2, 4, 3)
        ax3.imshow(ref_img, cmap='gray', alpha=0.3)
        if ref_trajectories:
            self._draw_trajectories_on_ax(ax3, ref_trajectories, '교본 붓 궤적')
        
        # 4. 작성본 궤적
        ax4 = plt.subplot(2, 4, 4)
        ax4.imshow(user_img, cmap='gray', alpha=0.3)
        if user_trajectories:
            self._draw_trajectories_on_ax(ax4, user_trajectories, '작성본 붓 궤적')
        
        # 5. 오버레이 비교
        ax5 = plt.subplot(2, 4, 5)
        overlay = np.zeros((*ref_img.shape, 3))
        overlay[:,:,0] = ref_img / 255  # 빨강: 교본
        overlay[:,:,1] = user_img / 255  # 초록: 작성본
        ax5.imshow(overlay)
        ax5.set_title('오버레이 비교\n(빨강:교본, 초록:작성본)', fontsize=12)
        ax5.axis('off')
        
        # 6. 획별 정확도
        ax6 = plt.subplot(2, 4, 6)
        if comparisons:
            stroke_nums = [c['stroke_num'] for c in comparisons]
            accuracies = [c['accuracy'] for c in comparisons]
            
            bars = ax6.bar(stroke_nums, accuracies, 
                          color=['green' if a >= 80 else 'orange' if a >= 60 else 'red' 
                                for a in accuracies])
            
            ax6.set_xlabel('획 번호')
            ax6.set_ylabel('정확도 (%)')
            ax6.set_title('획별 정확도 분석')
            ax6.set_ylim(0, 100)
            ax6.axhline(y=80, color='g', linestyle='--', alpha=0.5)
            ax6.axhline(y=60, color='orange', linestyle='--', alpha=0.5)
            
            for bar, acc in zip(bars, accuracies):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height + 2,
                        f'{acc:.1f}%', ha='center', va='bottom')
        
        # 7. 두께 변화 비교
        ax7 = plt.subplot(2, 4, 7)
        if ref_trajectories and user_trajectories:
            # 첫 번째 획의 두께 프로파일
            if len(ref_trajectories) > 0 and len(user_trajectories) > 0:
                ref_thickness = [p['thickness'] for p in ref_trajectories[0]]
                user_thickness = [p['thickness'] for p in user_trajectories[0]]
                
                x_ref = np.linspace(0, 100, len(ref_thickness))
                x_user = np.linspace(0, 100, len(user_thickness))
                
                ax7.plot(x_ref, ref_thickness, 'b-', label='교본', linewidth=2)
                ax7.plot(x_user, user_thickness, 'r-', label='작성본', linewidth=2)
                ax7.set_xlabel('획 진행도 (%)')
                ax7.set_ylabel('두께 (픽셀)')
                ax7.set_title('첫 번째 획 두께 변화')
                ax7.legend()
                ax7.grid(True, alpha=0.3)
        
        # 8. 종합 점수
        ax8 = plt.subplot(2, 4, 8)
        if comparisons:
            avg_accuracy = np.mean([c['accuracy'] for c in comparisons])
            
            # 등급 판정
            if avg_accuracy >= 90:
                grade = 'A'
                color = 'green'
            elif avg_accuracy >= 80:
                grade = 'B'
                color = 'lightgreen'
            elif avg_accuracy >= 70:
                grade = 'C'
                color = 'yellow'
            elif avg_accuracy >= 60:
                grade = 'D'
                color = 'orange'
            else:
                grade = 'F'
                color = 'red'
            
            # 원형 점수 표시
            circle = Circle((0.5, 0.5), 0.3, facecolor=color, 
                          edgecolor='black', linewidth=3,
                          transform=ax8.transAxes)
            ax8.add_patch(circle)
            
            ax8.text(0.5, 0.5, f'{avg_accuracy:.1f}점\n{grade}등급',
                    fontsize=20, fontweight='bold',
                    ha='center', va='center',
                    transform=ax8.transAxes)
            
            # 세부 점수
            details = f"\n획별 평균:\n"
            details += f"두께 차이: {np.mean([c['thickness_diff'] for c in comparisons]):.1f}\n"
            details += f"각도 차이: {np.mean([c['angle_diff'] for c in comparisons]):.1f}°\n"
            details += f"위치 차이: {np.mean([c['position_diff'] for c in comparisons]):.1f}px"
            
            ax8.text(0.5, 0.1, details, fontsize=10,
                    ha='center', va='center',
                    transform=ax8.transAxes)
        
        ax8.set_xlim(0, 1)
        ax8.set_ylim(0, 1)
        ax8.axis('off')
        
        plt.suptitle('서예 "中" 종합 분석 리포트', fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        # 저장
        output_path = f"{output_dir}/complete_analysis.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # 개별 붓 움직임 시각화도 저장
        fig_ref = self.visualize_brush_movement(ref_img, ref_trajectories, "교본 붓 움직임")
        fig_ref.savefig(f"{output_dir}/reference_brush_movement.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        fig_user = self.visualize_brush_movement(user_img, user_trajectories, "작성본 붓 움직임")
        fig_user.savefig(f"{output_dir}/user_brush_movement.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        return {
            'average_accuracy': avg_accuracy if comparisons else 0,
            'comparisons': comparisons,
            'output_files': [
                f"{output_dir}/complete_analysis.png",
                f"{output_dir}/reference_brush_movement.png",
                f"{output_dir}/user_brush_movement.png"
            ]
        }
    
    def _draw_trajectories_on_ax(self, ax, trajectories, title):
        """축에 궤적 그리기"""
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for traj_idx, trajectory in enumerate(trajectories):
            if not trajectory:
                continue
            
            color = colors[traj_idx % len(colors)]
            points = np.array([p['position'] for p in trajectory])
            
            if len(points) > 1:
                ax.plot(points[:, 0], points[:, 1], 
                       color=color, linewidth=2, alpha=0.7)
                
                # 시작점
                ax.scatter(points[0][0], points[0][1],
                          color=color, s=50, marker='o',
                          edgecolors='white', linewidth=2)
                
                # 방향 화살표
                for i in range(0, len(points)-1, max(1, len(points)//10)):
                    if i+1 < len(points):
                        dx = points[i+1][0] - points[i][0]
                        dy = points[i+1][1] - points[i][1]
                        ax.arrow(points[i][0], points[i][1], dx*0.3, dy*0.3,
                                head_width=3, head_length=2,
                                fc=color, ec=color, alpha=0.5)
        
        ax.set_title(title, fontsize=12)
        ax.axis('off')


# 테스트 실행
if __name__ == "__main__":
    analyzer = RealCalligraphyAnalyzer()
    
    # 더미 테스트 (실제 이미지 경로로 교체 필요)
    print("실제 서예 이미지 분석 시스템 준비 완료")
    print("\n사용법:")
    print("analyzer = RealCalligraphyAnalyzer()")
    print("results = analyzer.analyze_complete('교본.jpg', '작성본.jpg', './output')")
    print("\n지원 형식: JPG, PNG, HEIC")
    print("\n분석 내용:")
    print("1. 붓 움직임 궤적 추적")
    print("2. 획순별 정확도 분석")
    print("3. 두께 변화 비교")
    print("4. 각도 일관성 평가")
    print("5. 종합 점수 및 등급")