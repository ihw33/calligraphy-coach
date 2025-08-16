#!/usr/bin/env python3
"""
한자 "中" 통합 분석 시스템
- 모든 분석 기능 통합
- 실제 이미지 처리 가능
"""

import cv2
import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks, savgol_filter
from skimage.morphology import skeletonize, thin
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class IntegratedZhongAnalyzer:
    def __init__(self):
        self.character = "中"
        self.stroke_info = {
            1: {'name': '좌측 세로획', 'type': 'vertical', 'position': 'left'},
            2: {'name': '중앙 관통 세로획', 'type': 'vertical', 'position': 'center'},
            3: {'name': '상단 가로획', 'type': 'horizontal', 'position': 'top'},
            4: {'name': '하단 가로획', 'type': 'horizontal', 'position': 'bottom'}
        }
    
    def create_reference_zhong(self):
        """표준 中자 생성"""
        img = np.ones((400, 400), dtype=np.uint8) * 255
        
        # 외곽 사각형
        cv2.rectangle(img, (100, 50), (300, 350), 0, 3)
        
        # 중앙 세로획 (관통)
        cv2.line(img, (200, 30), (200, 370), 0, 8)
        
        # 상단 가로획
        cv2.line(img, (100, 120), (300, 120), 0, 5)
        
        # 하단 가로획
        cv2.line(img, (100, 280), (300, 280), 0, 5)
        
        return img
    
    def create_user_zhong(self, variation_level=0.2):
        """사용자 中자 시뮬레이션 (실제 이미지로 교체 가능)"""
        img = np.ones((400, 400), dtype=np.uint8) * 255
        
        # 변형 추가
        offset_x = int(20 * variation_level)
        offset_y = int(15 * variation_level)
        
        # 외곽 사각형 (약간 틀어짐)
        cv2.rectangle(img, (100+offset_x, 50+offset_y), 
                     (300-offset_x, 350-offset_y), 0, 3)
        
        # 중앙 세로획 (약간 기울어짐)
        cv2.line(img, (200+offset_x//2, 30), 
                (200-offset_x//2, 370), 0, 7)
        
        # 상단 가로획
        cv2.line(img, (100+offset_x, 120+offset_y), 
                (300-offset_x, 120-offset_y), 0, 4)
        
        # 하단 가로획
        cv2.line(img, (100+offset_x, 280-offset_y), 
                (300-offset_x, 280+offset_y), 0, 6)
        
        # 붓 효과 추가 (가우시안 블러)
        img = cv2.GaussianBlur(img, (5, 5), 1)
        _, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        
        return img
    
    def extract_strokes(self, img):
        """획 분리 및 추출"""
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 형태학적 연산으로 획 분리
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 연결된 컴포넌트 찾기
        num_labels, labels = cv2.connectedComponents(opened)
        
        strokes = []
        for i in range(1, num_labels):
            stroke_mask = (labels == i).astype(np.uint8) * 255
            strokes.append(stroke_mask)
        
        return strokes
    
    def analyze_brush_trajectory(self, img):
        """붓 움직임 궤적 분석"""
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 스켈레톤 추출
        skeleton = skeletonize(binary > 0)
        
        # 거리 변환
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # 궤적 포인트 수집
        skel_points = np.argwhere(skeleton)
        
        trajectories = []
        for point in skel_points[::5]:  # 5픽셀마다 샘플링
            y, x = point
            thickness = dist_transform[y, x] * 2
            
            # 국부 방향 계산
            window = 10
            y_min = max(0, y - window)
            y_max = min(skeleton.shape[0], y + window)
            x_min = max(0, x - window)
            x_max = min(skeleton.shape[1], x + window)
            
            local_skel = skeleton[y_min:y_max, x_min:x_max]
            local_points = np.argwhere(local_skel)
            
            if len(local_points) > 2:
                # PCA로 주 방향 찾기
                mean = local_points.mean(axis=0)
                centered = local_points - mean
                
                if centered.shape[0] > 1:
                    cov = np.cov(centered.T)
                    if cov.shape == (2, 2):
                        eigenvalues, eigenvectors = np.linalg.eig(cov)
                        main_direction = eigenvectors[:, np.argmax(eigenvalues)]
                        angle = np.degrees(np.arctan2(main_direction[1], main_direction[0]))
                    else:
                        angle = 0
                else:
                    angle = 0
            else:
                angle = 0
            
            trajectories.append({
                'position': (x, y),
                'thickness': thickness,
                'angle': angle
            })
        
        return trajectories
    
    def calculate_zhong_score(self, reference, user):
        """中자 특화 채점 시스템"""
        scores = {
            '구조_완성도': 0,
            '획_균형': 0,
            '중심선_정확도': 0,
            '좌우_대칭': 0,
            '상하_비율': 0
        }
        
        # 1. 구조 완성도 (획이 모두 있는지)
        ref_strokes = self.extract_strokes(reference)
        user_strokes = self.extract_strokes(user)
        
        stroke_ratio = min(len(user_strokes), len(ref_strokes)) / max(len(user_strokes), len(ref_strokes))
        scores['구조_완성도'] = stroke_ratio * 100
        
        # 2. 획 균형 (각 획의 길이 비율)
        _, ref_binary = cv2.threshold(reference, 127, 255, cv2.THRESH_BINARY_INV)
        _, user_binary = cv2.threshold(user, 127, 255, cv2.THRESH_BINARY_INV)
        
        ref_skeleton = skeletonize(ref_binary > 0)
        user_skeleton = skeletonize(user_binary > 0)
        
        ref_length = np.sum(ref_skeleton)
        user_length = np.sum(user_skeleton)
        
        length_ratio = min(ref_length, user_length) / max(ref_length, user_length)
        scores['획_균형'] = length_ratio * 100
        
        # 3. 중심선 정확도 (중앙 세로획이 정중앙인지)
        h, w = user_binary.shape
        center_line = user_binary[:, w//2-10:w//2+10]
        center_density = np.sum(center_line) / center_line.size
        scores['중심선_정확도'] = min(center_density * 200, 100)
        
        # 4. 좌우 대칭
        left_half = user_binary[:, :w//2]
        right_half = user_binary[:, w//2:]
        right_flipped = np.fliplr(right_half)
        
        # 크기 맞추기
        min_width = min(left_half.shape[1], right_flipped.shape[1])
        if min_width > 0:
            symmetry = 1 - np.abs(left_half[:, :min_width] - right_flipped[:, :min_width]).mean() / 255
            scores['좌우_대칭'] = symmetry * 100
        
        # 5. 상하 비율 (상단과 하단 공간의 균형)
        top_half = user_binary[:h//2, :]
        bottom_half = user_binary[h//2:, :]
        
        top_density = np.sum(top_half) / top_half.size
        bottom_density = np.sum(bottom_half) / bottom_half.size
        
        balance = 1 - abs(top_density - bottom_density) / max(top_density, bottom_density)
        scores['상하_비율'] = balance * 100
        
        return scores
    
    def visualize_complete_analysis(self, reference, user, output_path):
        """종합 분석 시각화"""
        # 분석 수행
        trajectories_ref = self.analyze_brush_trajectory(reference)
        trajectories_user = self.analyze_brush_trajectory(user)
        scores = self.calculate_zhong_score(reference, user)
        
        # 시각화
        fig = plt.figure(figsize=(20, 12))
        
        # 1. 교본
        ax1 = plt.subplot(3, 4, 1)
        ax1.imshow(reference, cmap='gray')
        ax1.set_title('교본 "中"', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. 작성본
        ax2 = plt.subplot(3, 4, 2)
        ax2.imshow(user, cmap='gray')
        ax2.set_title('작성본 "中"', fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        # 3. 스켈레톤 비교
        ax3 = plt.subplot(3, 4, 3)
        _, ref_binary = cv2.threshold(reference, 127, 255, cv2.THRESH_BINARY_INV)
        _, user_binary = cv2.threshold(user, 127, 255, cv2.THRESH_BINARY_INV)
        ref_skel = skeletonize(ref_binary > 0)
        user_skel = skeletonize(user_binary > 0)
        
        overlay_skel = np.zeros((*ref_skel.shape, 3))
        overlay_skel[:,:,0] = ref_skel  # 빨강: 교본
        overlay_skel[:,:,1] = user_skel  # 초록: 작성본
        ax3.imshow(overlay_skel)
        ax3.set_title('스켈레톤 비교\n(빨강:교본, 초록:작성본)')
        ax3.axis('off')
        
        # 4. 오버레이
        ax4 = plt.subplot(3, 4, 4)
        overlay = cv2.addWeighted(reference, 0.5, user, 0.5, 0)
        ax4.imshow(overlay, cmap='gray')
        ax4.set_title('중첩 비교')
        ax4.axis('off')
        
        # 5. 붓 궤적 (교본)
        ax5 = plt.subplot(3, 4, 5)
        ax5.imshow(reference, cmap='gray', alpha=0.3)
        for traj in trajectories_ref[::3]:
            x, y = traj['position']
            angle = traj['angle']
            dx = np.cos(np.radians(angle)) * 10
            dy = np.sin(np.radians(angle)) * 10
            ax5.arrow(x, y, dx, dy, head_width=3, head_length=2,
                     fc='blue', ec='blue', alpha=0.7)
        ax5.set_title('교본 붓 궤적')
        ax5.axis('off')
        
        # 6. 붓 궤적 (작성본)
        ax6 = plt.subplot(3, 4, 6)
        ax6.imshow(user, cmap='gray', alpha=0.3)
        for traj in trajectories_user[::3]:
            x, y = traj['position']
            angle = traj['angle']
            dx = np.cos(np.radians(angle)) * 10
            dy = np.sin(np.radians(angle)) * 10
            ax6.arrow(x, y, dx, dy, head_width=3, head_length=2,
                     fc='red', ec='red', alpha=0.7)
        ax6.set_title('작성본 붓 궤적')
        ax6.axis('off')
        
        # 7. 두께 히트맵
        ax7 = plt.subplot(3, 4, 7)
        dist_transform = cv2.distanceTransform(user_binary, cv2.DIST_L2, 5)
        im7 = ax7.imshow(dist_transform, cmap='hot')
        ax7.set_title('붓 압력 분포')
        plt.colorbar(im7, ax=ax7, fraction=0.046)
        ax7.axis('off')
        
        # 8. 획 분석
        ax8 = plt.subplot(3, 4, 8)
        user_strokes = self.extract_strokes(user)
        
        # 획별 색상 표시
        colored_strokes = np.zeros((*user.shape, 3))
        colors = [[1,0,0], [0,1,0], [0,0,1], [1,1,0]]  # 빨강, 초록, 파랑, 노랑
        
        for i, stroke in enumerate(user_strokes[:4]):
            for c in range(3):
                colored_strokes[:,:,c] += stroke/255 * colors[i%4][c]
        
        ax8.imshow(colored_strokes)
        ax8.set_title('획 분리 분석')
        ax8.axis('off')
        
        # 9. 대칭성 분석
        ax9 = plt.subplot(3, 4, 9)
        h, w = user.shape
        
        # 중심선 그리기
        ax9.imshow(user, cmap='gray', alpha=0.5)
        ax9.axvline(x=w//2, color='red', linestyle='--', linewidth=2)
        ax9.axhline(y=h//2, color='blue', linestyle='--', linewidth=2)
        
        # 사분면 표시
        rect1 = Rectangle((0, 0), w//2, h//2, fill=False, edgecolor='green', linewidth=2)
        rect2 = Rectangle((w//2, 0), w//2, h//2, fill=False, edgecolor='green', linewidth=2)
        rect3 = Rectangle((0, h//2), w//2, h//2, fill=False, edgecolor='green', linewidth=2)
        rect4 = Rectangle((w//2, h//2), w//2, h//2, fill=False, edgecolor='green', linewidth=2)
        
        ax9.add_patch(rect1)
        ax9.add_patch(rect2)
        ax9.add_patch(rect3)
        ax9.add_patch(rect4)
        
        ax9.set_title('대칭성 및 균형 분석')
        ax9.axis('off')
        
        # 10. 점수 막대그래프
        ax10 = plt.subplot(3, 4, 10)
        categories = list(scores.keys())
        values = list(scores.values())
        
        # 한글 레이블 축약
        categories_short = ['구조', '균형', '중심', '대칭', '비율']
        
        bars = ax10.bar(categories_short, values, 
                       color=['green' if v >= 80 else 'orange' if v >= 60 else 'red' 
                             for v in values])
        
        ax10.set_ylim(0, 100)
        ax10.set_ylabel('점수')
        ax10.set_title('항목별 점수')
        ax10.axhline(y=80, color='g', linestyle='--', alpha=0.3)
        ax10.axhline(y=60, color='orange', linestyle='--', alpha=0.3)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax10.text(bar.get_x() + bar.get_width()/2., height + 2,
                     f'{val:.0f}', ha='center', va='bottom')
        
        # 11. 획순 표시
        ax11 = plt.subplot(3, 4, 11)
        ax11.imshow(user, cmap='gray', alpha=0.3)
        
        # 획순 번호 표시 (中자의 표준 획순)
        stroke_positions = [
            (100, 200, '①'),  # 좌측 세로
            (200, 200, '②'),  # 중앙 세로
            (200, 120, '③'),  # 상단 가로
            (200, 280, '④')   # 하단 가로
        ]
        
        for x, y, num in stroke_positions:
            ax11.text(x, y, num, fontsize=20, fontweight='bold',
                     color='red', ha='center', va='center',
                     bbox=dict(boxstyle='circle,pad=0.3', 
                              facecolor='yellow', alpha=0.7))
        
        ax11.set_title('획순 (1→2→3→4)')
        ax11.axis('off')
        
        # 12. 종합 점수
        ax12 = plt.subplot(3, 4, 12)
        total_score = np.mean(list(scores.values()))
        
        # 등급 판정
        if total_score >= 90:
            grade = 'A'
            grade_color = 'green'
            comment = '훌륭합니다!'
        elif total_score >= 80:
            grade = 'B'
            grade_color = 'lightgreen'
            comment = '우수합니다'
        elif total_score >= 70:
            grade = 'C'
            grade_color = 'yellow'
            comment = '양호합니다'
        elif total_score >= 60:
            grade = 'D'
            grade_color = 'orange'
            comment = '연습이 필요합니다'
        else:
            grade = 'F'
            grade_color = 'red'
            comment = '기초부터 다시'
        
        # 원형 점수판
        circle = Circle((0.5, 0.6), 0.3, facecolor=grade_color,
                       edgecolor='black', linewidth=3,
                       transform=ax12.transAxes)
        ax12.add_patch(circle)
        
        ax12.text(0.5, 0.6, f'{total_score:.1f}점\n{grade}등급',
                 fontsize=24, fontweight='bold',
                 ha='center', va='center',
                 transform=ax12.transAxes)
        
        ax12.text(0.5, 0.2, comment,
                 fontsize=16, fontweight='bold',
                 ha='center', va='center',
                 transform=ax12.transAxes)
        
        ax12.set_xlim(0, 1)
        ax12.set_ylim(0, 1)
        ax12.axis('off')
        
        plt.suptitle('한자 "中" 종합 서예 분석', fontsize=20, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return total_score, scores
    
    def run_analysis(self):
        """전체 분석 실행"""
        # 이미지 생성 (실제 이미지로 교체 가능)
        reference = self.create_reference_zhong()
        user = self.create_user_zhong(variation_level=0.3)
        
        # 분석 실행
        output_path = '/Users/m4_macbook/char-comparison-system/zhong_complete_analysis.png'
        total_score, detailed_scores = self.visualize_complete_analysis(
            reference, user, output_path
        )
        
        # 결과 출력
        print("\n" + "="*60)
        print("              한자 '中' 서예 분석 결과")
        print("="*60)
        print(f"\n【종합 점수】 {total_score:.1f}점")
        print("\n【세부 평가】")
        for category, score in detailed_scores.items():
            bar_length = int(score / 5)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"  {category:12s}: {bar} {score:5.1f}점")
        
        print("\n【획순 안내】")
        print("  ① 외곽 좌측 세로획")
        print("  ② 중앙 관통 세로획")
        print("  ③ 상단 가로획")
        print("  ④ 하단 가로획")
        
        print("\n【개선 포인트】")
        weak_points = [k for k, v in detailed_scores.items() if v < 70]
        if weak_points:
            for point in weak_points:
                if point == '구조_완성도':
                    print("  • 모든 획을 빠짐없이 작성하세요")
                elif point == '획_균형':
                    print("  • 각 획의 길이와 굵기를 균일하게")
                elif point == '중심선_정확도':
                    print("  • 중앙 세로획을 정중앙에 배치")
                elif point == '좌우_대칭':
                    print("  • 좌우 균형을 맞춰 작성")
                elif point == '상하_비율':
                    print("  • 상하 공간 배분을 균등하게")
        else:
            print("  ✓ 전체적으로 우수한 작성입니다!")
        
        print(f"\n【분석 결과 저장】")
        print(f"  → {output_path}")
        print("="*60)
        
        return total_score, detailed_scores


# 실행
if __name__ == "__main__":
    analyzer = IntegratedZhongAnalyzer()
    analyzer.run_analysis()