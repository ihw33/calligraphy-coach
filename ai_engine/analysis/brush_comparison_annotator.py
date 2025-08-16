#!/usr/bin/env python3
"""
붓 압력/속도 비교 및 글자 위 주석 시스템
- 교본과 사용자 글자의 압력/속도 비교
- 차이점을 글자 위에 직접 표시
- 개선 포인트 시각화
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from scipy import ndimage
from scipy.interpolate import interp1d
from skimage.morphology import skeletonize
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
    return False


class BrushComparisonAnnotator:
    def __init__(self):
        self.setup_korean_font = setup_korean_font
        
    def extract_skeleton(self, binary_img):
        """스켈레톤 추출"""
        skeleton = skeletonize(binary_img > 0)
        return skeleton.astype(np.uint8) * 255
    
    def analyze_pressure_along_skeleton(self, binary_img, skeleton):
        """스켈레톤을 따라 압력(굵기) 분석"""
        dist_transform = cv2.distanceTransform(binary_img, cv2.DIST_L2, 5)
        
        skeleton_points = np.where(skeleton > 0)
        pressure_map = []
        
        for y, x in zip(skeleton_points[0], skeleton_points[1]):
            thickness = dist_transform[y, x] * 2
            pressure_map.append({
                'position': (x, y),
                'pressure': thickness
            })
        
        return pressure_map
    
    def analyze_speed_from_skeleton(self, skeleton, window_size=5):
        """스켈레톤에서 속도 추정 (점 간 거리)"""
        skeleton_points = np.where(skeleton > 0)
        
        if len(skeleton_points[0]) < window_size:
            return []
        
        speeds = []
        points = list(zip(skeleton_points[1], skeleton_points[0]))  # (x, y) 순서
        
        for i in range(len(points) - window_size):
            p1 = np.array(points[i])
            p2 = np.array(points[i + window_size])
            
            distance = np.linalg.norm(p2 - p1)
            speeds.append({
                'position': points[i],
                'speed': distance
            })
        
        return speeds
    
    def compare_pressure_profiles(self, user_pressure, ref_pressure):
        """압력 프로파일 비교"""
        comparisons = []
        
        # 가장 가까운 점 매칭
        for user_point in user_pressure:
            user_pos = np.array(user_point['position'])
            user_p = user_point['pressure']
            
            # 가장 가까운 교본 점 찾기
            min_dist = float('inf')
            closest_ref = None
            
            for ref_point in ref_pressure:
                ref_pos = np.array(ref_point['position'])
                dist = np.linalg.norm(user_pos - ref_pos)
                
                if dist < min_dist:
                    min_dist = dist
                    closest_ref = ref_point
            
            if closest_ref and min_dist < 50:  # 50픽셀 이내만 비교
                diff = user_p - closest_ref['pressure']
                diff_percent = (diff / closest_ref['pressure'] * 100) if closest_ref['pressure'] > 0 else 0
                
                comparisons.append({
                    'position': user_point['position'],
                    'user_pressure': user_p,
                    'ref_pressure': closest_ref['pressure'],
                    'difference': diff,
                    'diff_percent': diff_percent,
                    'status': self.classify_pressure_diff(diff_percent)
                })
        
        return comparisons
    
    def compare_speed_profiles(self, user_speed, ref_speed):
        """속도 프로파일 비교"""
        comparisons = []
        
        for user_point in user_speed:
            user_pos = np.array(user_point['position'])
            user_s = user_point['speed']
            
            # 가장 가까운 교본 점 찾기
            min_dist = float('inf')
            closest_ref = None
            
            for ref_point in ref_speed:
                ref_pos = np.array(ref_point['position'])
                dist = np.linalg.norm(user_pos - ref_pos)
                
                if dist < min_dist:
                    min_dist = dist
                    closest_ref = ref_point
            
            if closest_ref and min_dist < 50:
                diff = user_s - closest_ref['speed']
                diff_percent = (diff / closest_ref['speed'] * 100) if closest_ref['speed'] > 0 else 0
                
                comparisons.append({
                    'position': user_point['position'],
                    'user_speed': user_s,
                    'ref_speed': closest_ref['speed'],
                    'difference': diff,
                    'diff_percent': diff_percent,
                    'status': self.classify_speed_diff(diff_percent)
                })
        
        return comparisons
    
    def classify_pressure_diff(self, diff_percent):
        """압력 차이 분류"""
        if abs(diff_percent) < 10:
            return 'good'  # 적절
        elif diff_percent > 30:
            return 'too_heavy'  # 너무 세게
        elif diff_percent < -30:
            return 'too_light'  # 너무 약하게
        elif diff_percent > 10:
            return 'slightly_heavy'  # 약간 세게
        else:
            return 'slightly_light'  # 약간 약하게
    
    def classify_speed_diff(self, diff_percent):
        """속도 차이 분류"""
        if abs(diff_percent) < 15:
            return 'good'  # 적절
        elif diff_percent > 40:
            return 'too_fast'  # 너무 빠름
        elif diff_percent < -40:
            return 'too_slow'  # 너무 느림
        elif diff_percent > 15:
            return 'slightly_fast'  # 약간 빠름
        else:
            return 'slightly_slow'  # 약간 느림
    
    def identify_problem_areas(self, pressure_comp, speed_comp):
        """문제 영역 식별"""
        problem_areas = []
        
        # 압력 문제 영역
        for comp in pressure_comp:
            if comp['status'] != 'good':
                problem_areas.append({
                    'type': 'pressure',
                    'position': comp['position'],
                    'status': comp['status'],
                    'severity': abs(comp['diff_percent'])
                })
        
        # 속도 문제 영역
        for comp in speed_comp:
            if comp['status'] != 'good':
                problem_areas.append({
                    'type': 'speed',
                    'position': comp['position'],
                    'status': comp['status'],
                    'severity': abs(comp['diff_percent'])
                })
        
        # 심각도 순으로 정렬
        problem_areas.sort(key=lambda x: x['severity'], reverse=True)
        
        return problem_areas
    
    def create_annotated_image(self, user_img, pressure_comp, speed_comp, problem_areas):
        """글자 위에 주석 추가"""
        # RGB 이미지로 변환
        if len(user_img.shape) == 2:
            annotated = cv2.cvtColor(user_img, cv2.COLOR_GRAY2RGB)
        else:
            annotated = user_img.copy()
        
        h, w = annotated.shape[:2]
        
        # 오버레이 레이어 생성
        overlay = annotated.copy()
        
        # 압력 표시 (색상 코드)
        for comp in pressure_comp:
            x, y = comp['position']
            if 0 <= x < w and 0 <= y < h:
                if comp['status'] == 'too_heavy':
                    cv2.circle(overlay, (x, y), 3, (0, 0, 255), -1)  # 빨강
                elif comp['status'] == 'too_light':
                    cv2.circle(overlay, (x, y), 3, (255, 165, 0), -1)  # 주황
                elif comp['status'] == 'good':
                    cv2.circle(overlay, (x, y), 2, (0, 255, 0), -1)  # 초록
        
        # 속도 표시 (화살표)
        for i, comp in enumerate(speed_comp):
            if i % 10 == 0:  # 10개마다 하나씩 표시
                x, y = comp['position']
                if comp['status'] == 'too_fast':
                    # 긴 화살표
                    cv2.arrowedLine(overlay, (x-10, y), (x+10, y), (255, 0, 255), 2)
                elif comp['status'] == 'too_slow':
                    # 짧은 화살표
                    cv2.arrowedLine(overlay, (x-3, y), (x+3, y), (128, 0, 128), 2)
        
        # 반투명 합성
        annotated = cv2.addWeighted(annotated, 0.7, overlay, 0.3, 0)
        
        # 주요 문제 영역 표시
        for i, problem in enumerate(problem_areas[:5]):  # 상위 5개 문제
            x, y = problem['position']
            
            # 문제 영역 원으로 표시
            cv2.circle(annotated, (x, y), 15, (255, 255, 0), 2)
            
            # 번호 표시
            cv2.putText(annotated, str(i+1), (x-5, y+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        return annotated
    
    def create_legend(self):
        """범례 생성"""
        legend_height = 200
        legend_width = 300
        legend = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 255
        
        # 압력 범례
        cv2.putText(legend, "Pressure:", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.circle(legend, (30, 50), 5, (0, 0, 255), -1)
        cv2.putText(legend, "Too Heavy", (50, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.circle(legend, (30, 70), 5, (255, 165, 0), -1)
        cv2.putText(legend, "Too Light", (50, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.circle(legend, (30, 90), 5, (0, 255, 0), -1)
        cv2.putText(legend, "Good", (50, 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # 속도 범례
        cv2.putText(legend, "Speed:", (10, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.arrowedLine(legend, (20, 150), (50, 150), (255, 0, 255), 2)
        cv2.putText(legend, "Too Fast", (60, 155), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.arrowedLine(legend, (25, 170), (35, 170), (128, 0, 128), 2)
        cv2.putText(legend, "Too Slow", (60, 175), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return legend


def create_comprehensive_analysis(user_img, ref_img, user_binary, ref_binary, 
                                 pressure_comp, speed_comp, problem_areas, output_dir):
    """종합 분석 시각화"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # 1. 원본 비교
    ax1 = plt.subplot(2, 4, 1)
    ax1.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('사용자 글자', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    ax2 = plt.subplot(2, 4, 2)
    ax2.imshow(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('교본 글자', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # 2. 압력 비교 그래프
    ax3 = plt.subplot(2, 4, 3)
    user_pressures = [c['user_pressure'] for c in pressure_comp[:100]]
    ref_pressures = [c['ref_pressure'] for c in pressure_comp[:100]]
    
    x = range(len(user_pressures))
    ax3.plot(x, user_pressures, 'b-', label='사용자', linewidth=2)
    ax3.plot(x, ref_pressures, 'r--', label='교본', linewidth=2)
    ax3.fill_between(x, user_pressures, ref_pressures, 
                     where=np.array(user_pressures) > np.array(ref_pressures),
                     color='red', alpha=0.3, label='과도한 압력')
    ax3.fill_between(x, user_pressures, ref_pressures,
                     where=np.array(user_pressures) < np.array(ref_pressures),
                     color='blue', alpha=0.3, label='부족한 압력')
    ax3.set_title('압력 비교', fontsize=12, fontweight='bold')
    ax3.set_xlabel('경로 위치')
    ax3.set_ylabel('압력 (굵기)')
    ax3.legend(loc='upper right', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 3. 속도 비교 그래프
    ax4 = plt.subplot(2, 4, 4)
    user_speeds = [c['user_speed'] for c in speed_comp[:100]]
    ref_speeds = [c['ref_speed'] for c in speed_comp[:100]]
    
    x = range(len(user_speeds))
    ax4.plot(x, user_speeds, 'g-', label='사용자', linewidth=2)
    ax4.plot(x, ref_speeds, 'm--', label='교본', linewidth=2)
    ax4.fill_between(x, user_speeds, ref_speeds,
                     where=np.array(user_speeds) > np.array(ref_speeds),
                     color='yellow', alpha=0.3, label='너무 빠름')
    ax4.fill_between(x, user_speeds, ref_speeds,
                     where=np.array(user_speeds) < np.array(ref_speeds),
                     color='purple', alpha=0.3, label='너무 느림')
    ax4.set_title('속도 비교', fontsize=12, fontweight='bold')
    ax4.set_xlabel('경로 위치')
    ax4.set_ylabel('속도')
    ax4.legend(loc='upper right', fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # 4. 문제 영역 통계
    ax5 = plt.subplot(2, 4, 5)
    
    # 문제 유형별 카운트
    pressure_problems = sum(1 for p in problem_areas if p['type'] == 'pressure')
    speed_problems = sum(1 for p in problem_areas if p['type'] == 'speed')
    
    labels = ['압력 문제', '속도 문제']
    sizes = [pressure_problems, speed_problems]
    colors = ['#ff9999', '#66b3ff']
    
    if sum(sizes) > 0:
        wedges, texts, autotexts = ax5.pie(sizes, labels=labels, colors=colors,
                                           autopct='%1.1f%%', startangle=90)
        ax5.set_title('문제 유형 분포', fontsize=12, fontweight='bold')
    else:
        ax5.text(0.5, 0.5, '문제 없음', ha='center', va='center', fontsize=14)
        ax5.set_title('문제 유형 분포', fontsize=12, fontweight='bold')
    
    # 5. 압력 히트맵
    ax6 = plt.subplot(2, 4, 6)
    pressure_heatmap = create_pressure_heatmap(user_binary, pressure_comp)
    im = ax6.imshow(pressure_heatmap, cmap='RdYlGn_r')
    ax6.set_title('압력 차이 히트맵', fontsize=12, fontweight='bold')
    ax6.axis('off')
    plt.colorbar(im, ax=ax6, fraction=0.046)
    
    # 6. 속도 히트맵
    ax7 = plt.subplot(2, 4, 7)
    speed_heatmap = create_speed_heatmap(user_binary, speed_comp)
    im2 = ax7.imshow(speed_heatmap, cmap='coolwarm')
    ax7.set_title('속도 차이 히트맵', fontsize=12, fontweight='bold')
    ax7.axis('off')
    plt.colorbar(im2, ax=ax7, fraction=0.046)
    
    # 7. 개선 제안
    ax8 = plt.subplot(2, 4, 8)
    improvement_text = generate_improvement_suggestions(pressure_comp, speed_comp, problem_areas)
    ax8.text(0.05, 0.95, improvement_text, fontsize=10,
            verticalalignment='top', transform=ax8.transAxes,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax8.axis('off')
    ax8.set_title('개선 제안', fontsize=12, fontweight='bold')
    
    plt.suptitle('붓 압력 및 속도 상세 비교 분석', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'comprehensive_analysis.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ 종합 분석 저장: {result_path}")


def create_pressure_heatmap(binary_img, pressure_comp):
    """압력 차이 히트맵 생성"""
    h, w = binary_img.shape
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    for comp in pressure_comp:
        x, y = comp['position']
        if 0 <= x < w and 0 <= y < h:
            # 차이를 주변에 확산
            diff = comp['diff_percent']
            radius = 5
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        dist = np.sqrt(dx**2 + dy**2)
                        if dist <= radius:
                            weight = 1 - (dist / radius)
                            heatmap[ny, nx] += diff * weight
    
    return heatmap


def create_speed_heatmap(binary_img, speed_comp):
    """속도 차이 히트맵 생성"""
    h, w = binary_img.shape
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    for comp in speed_comp:
        x, y = comp['position']
        if 0 <= x < w and 0 <= y < h:
            diff = comp['diff_percent']
            radius = 5
            for dy in range(-radius, radius+1):
                for dx in range(-radius, radius+1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        dist = np.sqrt(dx**2 + dy**2)
                        if dist <= radius:
                            weight = 1 - (dist / radius)
                            heatmap[ny, nx] += diff * weight
    
    return heatmap


def generate_improvement_suggestions(pressure_comp, speed_comp, problem_areas):
    """개선 제안 생성"""
    suggestions = []
    
    # 압력 분석
    pressure_problems = {
        'too_heavy': 0,
        'too_light': 0,
        'slightly_heavy': 0,
        'slightly_light': 0
    }
    
    for comp in pressure_comp:
        if comp['status'] != 'good':
            pressure_problems[comp['status']] = pressure_problems.get(comp['status'], 0) + 1
    
    # 속도 분석
    speed_problems = {
        'too_fast': 0,
        'too_slow': 0,
        'slightly_fast': 0,
        'slightly_slow': 0
    }
    
    for comp in speed_comp:
        if comp['status'] != 'good':
            speed_problems[comp['status']] = speed_problems.get(comp['status'], 0) + 1
    
    # 제안 생성
    text = "📝 개선 제안\n" + "="*30 + "\n\n"
    
    # 압력 제안
    if pressure_problems['too_heavy'] > 10:
        text += "⚠️ 전반적으로 너무 세게 누름\n"
        text += "   → 붓을 가볍게 잡고 부드럽게\n\n"
    elif pressure_problems['too_light'] > 10:
        text += "⚠️ 전반적으로 너무 약하게 누름\n"
        text += "   → 붓을 더 확실하게 누르기\n\n"
    
    # 속도 제안
    if speed_problems['too_fast'] > 10:
        text += "⚠️ 너무 빠른 속도로 작성\n"
        text += "   → 천천히 정확하게 작성\n\n"
    elif speed_problems['too_slow'] > 10:
        text += "⚠️ 너무 느린 속도로 작성\n"
        text += "   → 자연스러운 속도 유지\n\n"
    
    # 주요 문제 영역
    if len(problem_areas) > 0:
        text += "📍 주요 개선 필요 영역:\n"
        for i, problem in enumerate(problem_areas[:3]):
            if problem['type'] == 'pressure':
                text += f"   {i+1}. 압력 조절 필요\n"
            else:
                text += f"   {i+1}. 속도 조절 필요\n"
    
    # 점수
    total_points = len(pressure_comp) + len(speed_comp)
    good_points = sum(1 for c in pressure_comp if c['status'] == 'good')
    good_points += sum(1 for c in speed_comp if c['status'] == 'good')
    
    if total_points > 0:
        score = (good_points / total_points) * 100
        text += f"\n종합 점수: {score:.1f}%"
    
    return text


def process_comparison():
    """비교 분석 실행"""
    
    annotator = BrushComparisonAnnotator()
    annotator.setup_korean_font()
    
    # 이미지 경로
    user_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"
    ref_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"
    
    # 이미지 로드
    user_img = cv2.imread(user_img_path)
    ref_img = cv2.imread(ref_img_path)
    
    user_gray = cv2.cvtColor(user_img, cv2.COLOR_BGR2GRAY)
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    
    print("✅ 이미지 로드 완료")
    
    # 이진화
    _, user_binary = cv2.threshold(user_gray, 127, 255, cv2.THRESH_BINARY_INV)
    _, ref_binary = cv2.threshold(ref_gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 스켈레톤 추출
    print("🔍 스켈레톤 추출 중...")
    user_skeleton = annotator.extract_skeleton(user_binary)
    ref_skeleton = annotator.extract_skeleton(ref_binary)
    
    # 압력 분석
    print("📊 압력 프로파일 분석 중...")
    user_pressure = annotator.analyze_pressure_along_skeleton(user_binary, user_skeleton)
    ref_pressure = annotator.analyze_pressure_along_skeleton(ref_binary, ref_skeleton)
    
    # 속도 분석
    print("⚡ 속도 프로파일 분석 중...")
    user_speed = annotator.analyze_speed_from_skeleton(user_skeleton)
    ref_speed = annotator.analyze_speed_from_skeleton(ref_skeleton)
    
    # 비교
    print("🔄 프로파일 비교 중...")
    pressure_comp = annotator.compare_pressure_profiles(user_pressure, ref_pressure)
    speed_comp = annotator.compare_speed_profiles(user_speed, ref_speed)
    
    # 문제 영역 식별
    problem_areas = annotator.identify_problem_areas(pressure_comp, speed_comp)
    
    # 출력 디렉토리
    output_dir = "comparison_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 글자 위 주석
    print("✏️ 글자 위 주석 생성 중...")
    annotated_img = annotator.create_annotated_image(user_img, pressure_comp, speed_comp, problem_areas)
    
    # 범례 생성
    legend = annotator.create_legend()
    
    # 주석된 이미지와 범례 결합
    h1, w1 = annotated_img.shape[:2]
    h2, w2 = legend.shape[:2]
    
    combined = np.ones((max(h1, h2), w1 + w2 + 10, 3), dtype=np.uint8) * 255
    combined[:h1, :w1] = annotated_img
    combined[:h2, w1+10:] = legend
    
    # 저장
    cv2.imwrite(os.path.join(output_dir, 'annotated_character.png'), combined)
    print(f"✅ 주석 이미지 저장: annotated_character.png")
    
    # 종합 분석
    print("📈 종합 분석 생성 중...")
    create_comprehensive_analysis(user_img, ref_img, user_binary, ref_binary,
                                 pressure_comp, speed_comp, problem_areas, output_dir)
    
    return pressure_comp, speed_comp, problem_areas


def main():
    print("="*60)
    print("🖌️ 붓 압력/속도 비교 및 주석 시스템")
    print("  - 교본과 사용자 글자 비교")
    print("  - 차이점을 글자 위에 직접 표시")
    print("="*60)
    
    try:
        pressure_comp, speed_comp, problem_areas = process_comparison()
        
        print("\n" + "="*60)
        print("📊 분석 완료")
        print("="*60)
        
        # 통계
        pressure_good = sum(1 for c in pressure_comp if c['status'] == 'good')
        speed_good = sum(1 for c in speed_comp if c['status'] == 'good')
        
        print(f"\n압력 분석:")
        print(f"  • 전체 점: {len(pressure_comp)}개")
        print(f"  • 적절한 압력: {pressure_good}개 ({pressure_good/len(pressure_comp)*100:.1f}%)")
        
        print(f"\n속도 분석:")
        print(f"  • 전체 점: {len(speed_comp)}개")
        print(f"  • 적절한 속도: {speed_good}개 ({speed_good/len(speed_comp)*100:.1f}%)")
        
        print(f"\n문제 영역:")
        print(f"  • 총 {len(problem_areas)}개 발견")
        
        if len(problem_areas) > 0:
            print("\n  주요 문제 (상위 3개):")
            for i, problem in enumerate(problem_areas[:3]):
                print(f"    {i+1}. {problem['type']} - 심각도: {problem['severity']:.1f}%")
        
        print("\n✅ 결과가 comparison_output/ 폴더에 저장되었습니다.")
        print("  - annotated_character.png (주석된 글자)")
        print("  - comprehensive_analysis.png (종합 분석)")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()