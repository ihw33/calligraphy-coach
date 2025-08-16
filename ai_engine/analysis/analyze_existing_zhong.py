#!/usr/bin/env python3
"""
기존 中자 이미지들을 활용한 종합 분석
"""

import cv2
import numpy as np
from integrated_zhong_analyzer import IntegratedZhongAnalyzer
from advanced_stroke_analyzer import AdvancedStrokeAnalyzer
from brush_center_tip_analyzer import BrushCenterTipAnalyzer
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def create_master_analysis():
    """모든 분석 기능을 통합한 마스터 분석"""
    
    # 분석기 초기화
    zhong_analyzer = IntegratedZhongAnalyzer()
    stroke_analyzer = AdvancedStrokeAnalyzer()
    brush_analyzer = BrushCenterTipAnalyzer()
    
    # 기존 이미지 생성 (교본과 작성본)
    reference = zhong_analyzer.create_reference_zhong()
    user = zhong_analyzer.create_user_zhong(variation_level=0.25)
    
    print("\n" + "="*70)
    print("                    한자 '中' 마스터 분석 시작")
    print("="*70)
    
    # 1. 기본 구조 분석
    print("\n[1/5] 기본 구조 분석 중...")
    scores = zhong_analyzer.calculate_zhong_score(reference, user)
    
    # 2. 획 정렬 및 상세 분석
    print("[2/5] 획 정렬 및 상세 분석 중...")
    aligned_user, center, start = stroke_analyzer.align_images(reference, user)
    thickness_ref = stroke_analyzer.analyze_thickness_variation(reference)
    thickness_user = stroke_analyzer.analyze_thickness_variation(aligned_user)
    turning_points = stroke_analyzer.detect_turning_points(aligned_user)
    spacing = stroke_analyzer.analyze_stroke_spacing(aligned_user)
    
    # 3. 중봉 분석
    print("[3/5] 붓 중봉 상태 분석 중...")
    symmetry_scores = brush_analyzer.analyze_stroke_symmetry(aligned_user)
    brush_angles = brush_analyzer.detect_brush_angle(aligned_user)
    ink_profiles = brush_analyzer.analyze_ink_distribution(aligned_user)
    center_tip_scores = brush_analyzer.calculate_center_tip_score(
        symmetry_scores, brush_angles, ink_profiles
    )
    
    # 4. 붓 궤적 추적
    print("[4/5] 붓 움직임 궤적 추적 중...")
    trajectories = zhong_analyzer.analyze_brush_trajectory(aligned_user)
    
    # 5. 종합 시각화
    print("[5/5] 종합 리포트 생성 중...")
    
    fig = plt.figure(figsize=(24, 20))
    
    # === 첫 번째 행: 기본 비교 ===
    
    # 1-1. 교본
    ax1 = plt.subplot(5, 5, 1)
    ax1.imshow(reference, cmap='gray')
    ax1.set_title('교본 "中"', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # 1-2. 작성본
    ax2 = plt.subplot(5, 5, 2)
    ax2.imshow(user, cmap='gray')
    ax2.set_title('작성본', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # 1-3. 정렬된 작성본
    ax3 = plt.subplot(5, 5, 3)
    ax3.imshow(aligned_user, cmap='gray')
    ax3.plot(center[0], center[1], 'r+', markersize=10, label='중심')
    ax3.plot(start[0], start[1], 'g^', markersize=8, label='시작')
    ax3.set_title('정렬 후', fontsize=12)
    ax3.legend(fontsize=8)
    ax3.axis('off')
    
    # 1-4. 오버레이
    ax4 = plt.subplot(5, 5, 4)
    overlay = cv2.addWeighted(reference, 0.5, aligned_user, 0.5, 0)
    ax4.imshow(overlay, cmap='gray')
    ax4.set_title('중첩 비교', fontsize=12)
    ax4.axis('off')
    
    # 1-5. 차이 맵
    ax5 = plt.subplot(5, 5, 5)
    diff = cv2.absdiff(reference, aligned_user)
    ax5.imshow(diff, cmap='hot')
    ax5.set_title('차이점 히트맵', fontsize=12)
    ax5.axis('off')
    
    # === 두 번째 행: 스켈레톤 및 궤적 ===
    
    # 2-1. 스켈레톤
    ax6 = plt.subplot(5, 5, 6)
    from skimage.morphology import skeletonize
    _, binary = cv2.threshold(aligned_user, 127, 255, cv2.THRESH_BINARY_INV)
    skeleton = skeletonize(binary > 0)
    ax6.imshow(skeleton, cmap='gray')
    ax6.set_title('스켈레톤', fontsize=12)
    ax6.axis('off')
    
    # 2-2. 붓 궤적
    ax7 = plt.subplot(5, 5, 7)
    ax7.imshow(aligned_user, cmap='gray', alpha=0.3)
    for i, traj in enumerate(trajectories[::5]):
        x, y = traj['position']
        angle = traj['angle']
        dx = np.cos(np.radians(angle)) * 8
        dy = np.sin(np.radians(angle)) * 8
        color = plt.cm.rainbow(i / len(trajectories))
        ax7.arrow(x, y, dx, dy, head_width=2, head_length=1,
                 fc=color, ec=color, alpha=0.7)
    ax7.set_title('붓 진행 방향', fontsize=12)
    ax7.axis('off')
    
    # 2-3. 두께 맵
    ax8 = plt.subplot(5, 5, 8)
    dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    im8 = ax8.imshow(dist_transform, cmap='viridis')
    ax8.set_title('선 두께 분포', fontsize=12)
    plt.colorbar(im8, ax=ax8, fraction=0.046)
    ax8.axis('off')
    
    # 2-4. 압력 추정
    ax9 = plt.subplot(5, 5, 9)
    pressure_map = dist_transform * (binary > 0)
    im9 = ax9.imshow(pressure_map, cmap='hot')
    ax9.set_title('추정 붓 압력', fontsize=12)
    plt.colorbar(im9, ax=ax9, fraction=0.046)
    ax9.axis('off')
    
    # 2-5. 꺾임점
    ax10 = plt.subplot(5, 5, 10)
    ax10.imshow(aligned_user, cmap='gray', alpha=0.5)
    if turning_points:
        for tp in turning_points[:10]:
            y, x = tp['position']
            ax10.plot(x, y, 'ro', markersize=6)
            ax10.text(x+5, y+5, f"{tp['angle']:.0f}°", 
                     fontsize=8, color='red')
    ax10.set_title('꺾임 부분', fontsize=12)
    ax10.axis('off')
    
    # === 세 번째 행: 중봉 분석 ===
    
    # 3-1. 좌우 대칭성
    ax11 = plt.subplot(5, 5, 11)
    if symmetry_scores:
        heatmap = np.zeros_like(aligned_user, dtype=np.float32)
        for score in symmetry_scores:
            x, y = score['position']
            radius = max(1, int(score['thickness']))
            cv2.circle(heatmap, (x, y), radius, score['symmetry'], -1)
        im11 = ax11.imshow(heatmap, cmap='RdYlGn', vmin=0, vmax=1)
        ax11.set_title(f'좌우 대칭성', fontsize=12)
        plt.colorbar(im11, ax=ax11, fraction=0.046)
    ax11.axis('off')
    
    # 3-2. 붓 각도
    ax12 = plt.subplot(5, 5, 12)
    ax12.imshow(aligned_user, cmap='gray', alpha=0.3)
    if brush_angles:
        for angle_data in brush_angles[::5]:
            x, y = angle_data['position']
            spread = angle_data['spread']
            color = 'green' if spread < 2 else 'orange' if spread < 3 else 'red'
            ax12.scatter(x, y, c=color, s=20, alpha=0.7)
    ax12.set_title('붓 각도 일관성', fontsize=12)
    ax12.axis('off')
    
    # 3-3. 먹 분포
    ax13 = plt.subplot(5, 5, 13)
    ink_map = dist_transform.copy()
    ink_map = ink_map / (ink_map.max() + 1e-6)
    im13 = ax13.imshow(ink_map, cmap='Greys')
    ax13.set_title('먹 농도 분포', fontsize=12)
    plt.colorbar(im13, ax=ax13, fraction=0.046)
    ax13.axis('off')
    
    # 3-4. 중봉 판정
    ax14 = plt.subplot(5, 5, 14)
    if center_tip_scores['total'] >= 80:
        status = "중봉"
        color = 'green'
    elif center_tip_scores['total'] >= 60:
        status = "준중봉"
        color = 'orange'
    else:
        status = "편봉"
        color = 'red'
    
    circle = Circle((0.5, 0.5), 0.3, facecolor=color, alpha=0.3,
                   transform=ax14.transAxes)
    ax14.add_patch(circle)
    ax14.text(0.5, 0.5, f'{status}\n{center_tip_scores["total"]:.0f}점',
             fontsize=14, fontweight='bold', ha='center', va='center',
             transform=ax14.transAxes)
    ax14.set_xlim(0, 1)
    ax14.set_ylim(0, 1)
    ax14.axis('off')
    
    # 3-5. 단면 프로파일
    ax15 = plt.subplot(5, 5, 15)
    if ink_profiles and len(ink_profiles) > 0:
        sample = ink_profiles[len(ink_profiles)//2]
        profile = sample['profile']
        x_axis = np.linspace(-10, 10, len(profile))
        ax15.plot(x_axis, profile, 'b-', linewidth=2)
        ax15.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        ax15.set_xlabel('거리 (px)', fontsize=10)
        ax15.set_ylabel('농도', fontsize=10)
        ax15.set_title('단면 농도', fontsize=12)
        ax15.grid(True, alpha=0.3)
    
    # === 네 번째 행: 획 분석 ===
    
    # 4-1. 획 분리
    ax16 = plt.subplot(5, 5, 16)
    strokes = zhong_analyzer.extract_strokes(aligned_user)
    colored = np.zeros((*aligned_user.shape, 3))
    colors_stroke = [[1,0,0], [0,1,0], [0,0,1], [1,1,0]]
    for i, stroke in enumerate(strokes[:4]):
        for c in range(3):
            colored[:,:,c] += stroke/255 * colors_stroke[i%4][c]
    ax16.imshow(colored)
    ax16.set_title('획 분리', fontsize=12)
    ax16.axis('off')
    
    # 4-2. 획순
    ax17 = plt.subplot(5, 5, 17)
    ax17.imshow(aligned_user, cmap='gray', alpha=0.3)
    positions = [(100, 200, '①'), (200, 200, '②'), 
                 (200, 120, '③'), (200, 280, '④')]
    for x, y, num in positions:
        ax17.text(x, y, num, fontsize=16, fontweight='bold',
                 color='red', ha='center', va='center',
                 bbox=dict(boxstyle='circle', facecolor='yellow', alpha=0.7))
    ax17.set_title('획순', fontsize=12)
    ax17.axis('off')
    
    # 4-3. 획 간격
    ax18 = plt.subplot(5, 5, 18)
    if spacing:
        spacing_matrix = np.zeros((4, 4))
        for s in spacing:
            if s['stroke1'] < 4 and s['stroke2'] < 4:
                spacing_matrix[s['stroke1'], s['stroke2']] = s['distance']
                spacing_matrix[s['stroke2'], s['stroke1']] = s['distance']
        im18 = ax18.imshow(spacing_matrix, cmap='coolwarm')
        ax18.set_title('획 간격', fontsize=12)
        plt.colorbar(im18, ax=ax18, fraction=0.046)
    ax18.axis('off')
    
    # 4-4. 균형 분석
    ax19 = plt.subplot(5, 5, 19)
    ax19.imshow(aligned_user, cmap='gray', alpha=0.5)
    h, w = aligned_user.shape
    ax19.axvline(x=w//2, color='red', linestyle='--', linewidth=2)
    ax19.axhline(y=h//2, color='blue', linestyle='--', linewidth=2)
    for i in range(4):
        x = (i % 2) * w//2
        y = (i // 2) * h//2
        rect = Rectangle((x, y), w//2, h//2, fill=False, 
                        edgecolor='green', linewidth=2)
        ax19.add_patch(rect)
    ax19.set_title('균형', fontsize=12)
    ax19.axis('off')
    
    # 4-5. 두께 변화
    ax20 = plt.subplot(5, 5, 20)
    if thickness_ref and thickness_user:
        x_ref = np.linspace(0, 100, len(thickness_ref['thickness_profile']))
        x_user = np.linspace(0, 100, len(thickness_user['thickness_profile']))
        ax20.plot(x_ref, thickness_ref['thickness_profile'], 'b-', 
                 label='교본', linewidth=2, alpha=0.7)
        ax20.plot(x_user, thickness_user['thickness_profile'], 'r-', 
                 label='작성본', linewidth=2, alpha=0.7)
        ax20.set_xlabel('진행도 (%)', fontsize=10)
        ax20.set_ylabel('두께', fontsize=10)
        ax20.set_title('두께 변화', fontsize=12)
        ax20.legend(fontsize=9)
        ax20.grid(True, alpha=0.3)
    
    # === 다섯 번째 행: 점수 및 평가 ===
    
    # 5-1. 구조 점수
    ax21 = plt.subplot(5, 5, 21)
    categories = ['구조', '균형', '중심', '대칭', '비율']
    values = list(scores.values())
    bars = ax21.bar(categories, values, 
                   color=['green' if v >= 80 else 'orange' if v >= 60 else 'red' 
                         for v in values])
    ax21.set_ylim(0, 100)
    ax21.set_title('구조 점수', fontsize=12)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax21.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{val:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 5-2. 중봉 점수
    ax22 = plt.subplot(5, 5, 22)
    categories_brush = ['대칭', '각도', '먹']
    values_brush = [center_tip_scores['symmetry'], 
                   center_tip_scores['angle_consistency'],
                   center_tip_scores['ink_distribution']]
    bars2 = ax22.bar(categories_brush, values_brush,
                    color=['green' if v >= 80 else 'orange' if v >= 60 else 'red' 
                          for v in values_brush])
    ax22.set_ylim(0, 100)
    ax22.set_title('중봉 점수', fontsize=12)
    for bar, val in zip(bars2, values_brush):
        height = bar.get_height()
        ax22.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{val:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 5-3. 종합 점수
    ax23 = plt.subplot(5, 5, 23)
    total_score = np.mean(list(scores.values()))
    
    # 등급
    if total_score >= 90:
        grade = 'A'
        grade_color = 'green'
    elif total_score >= 80:
        grade = 'B'
        grade_color = 'lightgreen'
    elif total_score >= 70:
        grade = 'C'
        grade_color = 'yellow'
    elif total_score >= 60:
        grade = 'D'
        grade_color = 'orange'
    else:
        grade = 'F'
        grade_color = 'red'
    
    circle_main = Circle((0.5, 0.5), 0.35, facecolor=grade_color,
                         edgecolor='black', linewidth=3,
                         transform=ax23.transAxes)
    ax23.add_patch(circle_main)
    ax23.text(0.5, 0.5, f'{total_score:.1f}점\n{grade}등급',
             fontsize=18, fontweight='bold', ha='center', va='center',
             transform=ax23.transAxes)
    ax23.set_xlim(0, 1)
    ax23.set_ylim(0, 1)
    ax23.axis('off')
    
    # 5-4. 개선 사항
    ax24 = plt.subplot(5, 5, 24)
    ax24.axis('off')
    advice = "【개선 조언】\n\n"
    
    weak_areas = []
    if scores['구조_완성도'] < 80:
        weak_areas.append("• 획 완성도 개선")
    if scores['좌우_대칭'] < 80:
        weak_areas.append("• 좌우 균형 조정")
    if center_tip_scores['total'] < 80:
        weak_areas.append("• 붓 수직 유지")
    
    if weak_areas:
        advice += "\n".join(weak_areas)
    else:
        advice += "✓ 우수한 작성!\n계속 연습하세요"
    
    ax24.text(0.1, 0.8, advice, fontsize=11,
             verticalalignment='top', transform=ax24.transAxes)
    
    # 5-5. 통계
    ax25 = plt.subplot(5, 5, 25)
    ax25.axis('off')
    
    stats_text = "【통계 요약】\n\n"
    stats_text += f"종합: {total_score:.1f}점\n"
    stats_text += f"중봉: {center_tip_scores['total']:.1f}점\n"
    if thickness_user:
        stats_text += f"평균 두께: {thickness_user['mean_thickness']:.1f}px\n"
    stats_text += f"획 개수: {len(strokes)}개\n"
    
    ax25.text(0.1, 0.8, stats_text, fontsize=11,
             verticalalignment='top', transform=ax25.transAxes)
    
    plt.suptitle('한자 "中" 완전 분석 리포트', fontsize=20, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    output_path = '/Users/m4_macbook/char-comparison-system/zhong_master_analysis.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\n" + "="*70)
    print("                    분석 완료")
    print("="*70)
    print(f"\n【종합 점수】 {total_score:.1f}점 ({grade}등급)")
    print(f"【중봉 상태】 {status} ({center_tip_scores['total']:.1f}점)")
    print("\n【세부 점수】")
    for key, value in scores.items():
        print(f"  • {key}: {value:.1f}점")
    print(f"\n【결과 저장】")
    print(f"  → {output_path}")
    print("="*70)
    
    return output_path

if __name__ == "__main__":
    output = create_master_analysis()