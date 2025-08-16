#!/usr/bin/env python3
"""
사용자 글자의 중심을 기준으로 가이드와 비교
한글 폰트 문제 해결
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        font_paths = [
            '/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/Library/Fonts/NanumGothic.ttf',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        ]
    elif system == 'Windows':
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/NanumGothic.ttf'
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            return True
    
    # 폰트를 찾을 수 없으면 기본 설정
    plt.rcParams['axes.unicode_minus'] = False
    return False


def process_center_aligned_comparison():
    """사용자 글자 중심 기준 정렬 비교"""
    
    # 한글 폰트 설정
    setup_korean_font()
    
    # 이미지 경로
    user_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"  # 사용자 글자
    guide_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png"  # 결구 가이드
    
    # 이미지 로드
    user_img = cv2.imread(user_path)
    guide_img = cv2.imread(guide_path)
    
    if user_img is None or guide_img is None:
        print("이미지를 로드할 수 없습니다.")
        return
    
    print("✅ 이미지 로드 완료")
    
    # 출력 디렉토리
    output_dir = "center_aligned_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 글자 추출
    user_char = extract_character(user_img)
    guide_char = extract_character(guide_img)
    
    # 사용자 글자의 중심 찾기
    user_center = find_center(user_char)
    guide_center = find_center(guide_char)
    
    # 중심 기준 정렬
    aligned_user = align_by_center(user_img, user_center, guide_center, guide_img.shape[:2])
    aligned_user_char = extract_character(aligned_user)
    
    # 오버레이 생성 (여러 버전)
    overlays = create_multiple_overlays(guide_img, aligned_user, aligned_user_char, guide_char)
    
    # 점수 계산
    scores = calculate_scores(aligned_user_char, guide_char)
    
    # 시각화
    visualize_results(
        user_img, guide_img, aligned_user,
        overlays, scores, output_dir,
        user_center, guide_center
    )
    
    return scores


def extract_character(img):
    """글자 부분만 추출"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 빨간색 선 제거
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    # 빨간색 부분 제거
    binary = cv2.bitwise_and(binary, cv2.bitwise_not(red_mask))
    
    return binary


def find_center(char_binary):
    """글자의 무게중심 찾기"""
    M = cv2.moments(char_binary)
    if M["m00"] > 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    else:
        h, w = char_binary.shape
        return (w // 2, h // 2)


def align_by_center(img, img_center, target_center, target_shape):
    """중심점을 기준으로 정렬"""
    # 이동 거리 계산
    translate_x = target_center[0] - img_center[0]
    translate_y = target_center[1] - img_center[1]
    
    # 변환 행렬 (이동만)
    M = np.array([[1, 0, translate_x],
                  [0, 1, translate_y]], dtype=np.float32)
    
    # 적용
    aligned = cv2.warpAffine(img, M, (target_shape[1], target_shape[0]),
                            borderValue=(255, 255, 255))
    
    return aligned


def create_multiple_overlays(guide_img, aligned_user, user_char, guide_char):
    """여러 종류의 오버레이 생성"""
    overlays = {}
    
    # 1. 기본 오버레이 (가이드 + 사용자)
    basic = guide_img.copy()
    mask = user_char > 0
    basic[mask] = [255, 100, 100]  # 파란빨강 혼합
    overlays['basic'] = basic
    
    # 2. 투명 오버레이
    transparent = cv2.addWeighted(guide_img, 0.6, aligned_user, 0.4, 0)
    overlays['transparent'] = transparent
    
    # 3. 차이 분석 오버레이
    diff = np.ones_like(guide_img) * 255
    
    # 공통 부분: 보라색
    common = cv2.bitwise_and(guide_char, user_char)
    diff[common > 0] = [200, 100, 200]
    
    # 가이드만: 빨간색
    guide_only = cv2.bitwise_and(guide_char, cv2.bitwise_not(user_char))
    diff[guide_only > 0] = [100, 100, 255]
    
    # 사용자만: 파란색
    user_only = cv2.bitwise_and(user_char, cv2.bitwise_not(guide_char))
    diff[user_only > 0] = [255, 100, 100]
    
    overlays['difference'] = diff
    
    # 4. 컨투어 오버레이
    contour_overlay = guide_img.copy()
    user_contours, _ = cv2.findContours(user_char, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(contour_overlay, user_contours, -1, (255, 0, 0), 2)
    overlays['contour'] = contour_overlay
    
    return overlays


def calculate_scores(user_char, guide_char):
    """점수 계산 (사용자 vs 가이드만)"""
    scores = {}
    
    # 1. 겹침도 (IoU)
    intersection = np.logical_and(user_char > 0, guide_char > 0)
    union = np.logical_or(user_char > 0, guide_char > 0)
    if np.sum(union) > 0:
        scores['overlap'] = (np.sum(intersection) / np.sum(union)) * 100
    else:
        scores['overlap'] = 0
    
    # 2. 중심 정렬도 (이미 정렬했으므로 높아야 함)
    M_user = cv2.moments(user_char)
    M_guide = cv2.moments(guide_char)
    
    if M_user["m00"] > 0 and M_guide["m00"] > 0:
        cx_user = int(M_user["m10"] / M_user["m00"])
        cy_user = int(M_user["m01"] / M_user["m00"])
        cx_guide = int(M_guide["m10"] / M_guide["m00"])
        cy_guide = int(M_guide["m01"] / M_guide["m00"])
        
        h, w = user_char.shape
        max_dist = np.sqrt(w**2 + h**2)
        actual_dist = np.sqrt((cx_user - cx_guide)**2 + (cy_user - cy_guide)**2)
        scores['center'] = max(0, 100 * (1 - actual_dist / max_dist))
    else:
        scores['center'] = 0
    
    # 3. 크기 비율
    user_area = np.sum(user_char > 0)
    guide_area = np.sum(guide_char > 0)
    if guide_area > 0:
        scores['size'] = min(user_area, guide_area) / max(user_area, guide_area) * 100
    else:
        scores['size'] = 0
    
    # 4. 획 구조 일치도
    user_edges = cv2.Canny(user_char.astype(np.uint8), 50, 150)
    guide_edges = cv2.Canny(guide_char.astype(np.uint8), 50, 150)
    
    edge_match = np.logical_and(user_edges > 0, guide_edges > 0)
    if np.sum(guide_edges > 0) > 0:
        scores['stroke'] = (np.sum(edge_match) / np.sum(guide_edges > 0)) * 100
    else:
        scores['stroke'] = 0
    
    # 5. 균형도 (4분면 분석)
    h, w = user_char.shape
    mid_h, mid_w = h // 2, w // 2
    
    quadrants_user = [
        np.sum(user_char[:mid_h, :mid_w] > 0),
        np.sum(user_char[:mid_h, mid_w:] > 0),
        np.sum(user_char[mid_h:, :mid_w] > 0),
        np.sum(user_char[mid_h:, mid_w:] > 0)
    ]
    
    quadrants_guide = [
        np.sum(guide_char[:mid_h, :mid_w] > 0),
        np.sum(guide_char[:mid_h, mid_w:] > 0),
        np.sum(guide_char[mid_h:, :mid_w] > 0),
        np.sum(guide_char[mid_h:, mid_w:] > 0)
    ]
    
    balance_diffs = []
    for u, g in zip(quadrants_user, quadrants_guide):
        if g > 0:
            balance_diffs.append(abs(u - g) / g)
        else:
            balance_diffs.append(0 if u == 0 else 1)
    
    scores['balance'] = max(0, 100 * (1 - np.mean(balance_diffs)))
    
    # 최종 점수
    scores['final'] = np.mean([
        scores['overlap'],
        scores['center'],
        scores['size'],
        scores['stroke'],
        scores['balance']
    ])
    
    return scores


def visualize_results(user_img, guide_img, aligned_user,
                      overlays, scores, output_dir,
                      user_center, guide_center):
    """결과 시각화 (한글 폰트 적용)"""
    
    fig = plt.figure(figsize=(16, 10))
    
    # 원본 이미지
    ax1 = plt.subplot(2, 4, 1)
    ax1.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('사용자 글자', fontsize=12, fontweight='bold')
    ax1.plot(user_center[0], user_center[1], 'r+', markersize=15, markeredgewidth=2)
    ax1.axis('off')
    
    ax2 = plt.subplot(2, 4, 2)
    ax2.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('결구 가이드', fontsize=12, fontweight='bold')
    ax2.plot(guide_center[0], guide_center[1], 'b+', markersize=15, markeredgewidth=2)
    ax2.axis('off')
    
    ax3 = plt.subplot(2, 4, 3)
    ax3.imshow(cv2.cvtColor(aligned_user, cv2.COLOR_BGR2RGB))
    ax3.set_title('중심 정렬된 사용자 글자', fontsize=12, fontweight='bold')
    ax3.axis('off')
    
    # 오버레이
    ax4 = plt.subplot(2, 4, 5)
    ax4.imshow(cv2.cvtColor(overlays['basic'], cv2.COLOR_BGR2RGB))
    ax4.set_title('기본 오버레이', fontsize=11)
    ax4.axis('off')
    
    ax5 = plt.subplot(2, 4, 6)
    ax5.imshow(cv2.cvtColor(overlays['transparent'], cv2.COLOR_BGR2RGB))
    ax5.set_title('투명 오버레이', fontsize=11)
    ax5.axis('off')
    
    ax6 = plt.subplot(2, 4, 7)
    ax6.imshow(cv2.cvtColor(overlays['difference'], cv2.COLOR_BGR2RGB))
    ax6.set_title('차이 분석\n(빨강:가이드만, 파랑:사용자만, 보라:겹침)', fontsize=10)
    ax6.axis('off')
    
    # 점수 표시
    ax7 = plt.subplot(2, 4, 4)
    
    score_names = ['겹침도', '중심정렬', '크기비율', '획구조', '균형도']
    score_values = [
        scores['overlap'],
        scores['center'],
        scores['size'],
        scores['stroke'],
        scores['balance']
    ]
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    bars = ax7.bar(score_names, score_values, color=colors)
    ax7.set_ylim(0, 100)
    ax7.set_ylabel('점수 (%)', fontsize=11)
    ax7.set_title('항목별 점수', fontsize=12, fontweight='bold')
    ax7.grid(axis='y', alpha=0.3)
    
    for bar, value in zip(bars, score_values):
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}', ha='center', va='bottom', fontsize=10)
    
    # 최종 평가
    ax8 = plt.subplot(2, 4, 8)
    
    final = scores['final']
    if final >= 80:
        grade = "A"
        msg = "훌륭합니다!"
        color = '#2ECC71'
    elif final >= 70:
        grade = "B"
        msg = "잘했습니다!"
        color = '#3498DB'
    elif final >= 60:
        grade = "C"
        msg = "양호합니다"
        color = '#F39C12'
    elif final >= 50:
        grade = "D"
        msg = "노력 필요"
        color = '#E67E22'
    else:
        grade = "F"
        msg = "많은 연습 필요"
        color = '#E74C3C'
    
    # 원형 등급 표시
    circle = plt.Circle((0.5, 0.6), 0.3, color=color, alpha=0.2)
    ax8.add_patch(circle)
    ax8.text(0.5, 0.6, grade, fontsize=48, fontweight='bold',
            ha='center', va='center', color=color)
    ax8.text(0.5, 0.25, msg, fontsize=14,
            ha='center', va='center')
    ax8.text(0.5, 0.1, f"종합점수: {final:.1f}점", fontsize=12,
            ha='center', va='center', fontweight='bold')
    ax8.set_xlim(0, 1)
    ax8.set_ylim(0, 1)
    ax8.axis('off')
    
    plt.suptitle('중심 기준 글자 비교 분석', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'center_analysis.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 오버레이 개별 저장
    for name, overlay in overlays.items():
        cv2.imwrite(os.path.join(output_dir, f'overlay_{name}.png'), overlay)
    
    print(f"\n✅ 결과 저장 완료: {output_dir}/")
    print(f"  - 종합 분석: center_analysis.png")
    print(f"  - 오버레이 이미지: overlay_*.png")


def main():
    print("="*60)
    print("📝 중심 기준 글자 비교 분석")
    print("  (사용자 글자 중심을 가이드 중심에 맞춤)")
    print("="*60)
    
    scores = process_center_aligned_comparison()
    
    if scores:
        print("\n" + "="*60)
        print("📊 분석 결과")
        print("="*60)
        print(f"겹침도: {scores['overlap']:.1f}%")
        print(f"중심 정렬: {scores['center']:.1f}%")
        print(f"크기 비율: {scores['size']:.1f}%")
        print(f"획 구조: {scores['stroke']:.1f}%")
        print(f"균형도: {scores['balance']:.1f}%")
        print("-"*60)
        print(f"🎯 종합 점수: {scores['final']:.1f}점")
        print("="*60)
        
        if scores['final'] >= 70:
            print("👏 잘 쓰셨습니다!")
        elif scores['final'] >= 60:
            print("💡 조금 더 연습하면 좋겠습니다.")
        else:
            print("📚 가이드를 참고하여 더 연습해보세요.")


if __name__ == "__main__":
    main()