#!/usr/bin/env python3
"""
사용자 글자 크기를 가이드에 맞게 조정하여 비교
글자 크기를 적절히 확대하여 더 정확한 비교
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
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            return True
    
    plt.rcParams['axes.unicode_minus'] = False
    return False


def process_scaled_comparison():
    """사용자 글자를 크기 조정하여 비교"""
    
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
    output_dir = "scaled_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 글자 추출
    user_char = extract_character(user_img)
    guide_char = extract_character(guide_img)
    
    # 글자 영역 찾기 (바운딩 박스)
    user_bbox = find_character_bbox(user_char)
    guide_bbox = find_character_bbox(guide_char)
    
    # 크기 조정 비율 계산
    scale_x = guide_bbox[2] / user_bbox[2] if user_bbox[2] > 0 else 1
    scale_y = guide_bbox[3] / user_bbox[3] if user_bbox[3] > 0 else 1
    scale = min(scale_x, scale_y) * 0.9  # 90% 크기로 조정 (약간 여유)
    
    print(f"📏 크기 조정 비율: {scale:.2f}배")
    
    # 사용자 이미지 크기 조정
    scaled_user = scale_image(user_img, scale)
    scaled_user_char = extract_character(scaled_user)
    
    # 중심 정렬
    user_center = find_center(scaled_user_char)
    guide_center = find_center(guide_char)
    aligned_user = align_by_center(scaled_user, user_center, guide_center, guide_img.shape[:2])
    aligned_user_char = extract_character(aligned_user)
    
    # 오버레이 생성
    overlays = create_overlays(guide_img, aligned_user, aligned_user_char, guide_char)
    
    # 점수 계산
    scores = calculate_scores(aligned_user_char, guide_char)
    
    # 시각화
    visualize_results(
        user_img, scaled_user, guide_img, aligned_user,
        overlays, scores, output_dir, scale
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
    
    binary = cv2.bitwise_and(binary, cv2.bitwise_not(red_mask))
    
    return binary


def find_character_bbox(char_binary):
    """글자의 바운딩 박스 찾기"""
    contours, _ = cv2.findContours(char_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        h, w = char_binary.shape
        return (0, 0, w, h)
    
    # 모든 컨투어를 포함하는 바운딩 박스
    x_min, y_min = char_binary.shape[1], char_binary.shape[0]
    x_max, y_max = 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < 100:  # 너무 작은 것은 무시
            continue
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
    
    width = x_max - x_min
    height = y_max - y_min
    
    return (x_min, y_min, width, height)


def scale_image(img, scale_factor):
    """이미지 크기 조정"""
    h, w = img.shape[:2]
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    
    scaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # 원본 크기 캔버스에 중앙 배치
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
    y_offset = (h - new_h) // 2
    x_offset = (w - new_w) // 2
    
    if y_offset >= 0 and x_offset >= 0:
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = scaled
    else:
        # 크기가 더 큰 경우 중앙 부분만 사용
        cy, cx = new_h // 2, new_w // 2
        half_h, half_w = h // 2, w // 2
        canvas = scaled[cy-half_h:cy+half_h, cx-half_w:cx+half_w]
    
    return canvas


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
    translate_x = target_center[0] - img_center[0]
    translate_y = target_center[1] - img_center[1]
    
    M = np.array([[1, 0, translate_x],
                  [0, 1, translate_y]], dtype=np.float32)
    
    aligned = cv2.warpAffine(img, M, (target_shape[1], target_shape[0]),
                            borderValue=(255, 255, 255))
    
    return aligned


def create_overlays(guide_img, aligned_user, user_char, guide_char):
    """오버레이 생성"""
    overlays = {}
    
    # 1. 기본 오버레이
    basic = guide_img.copy()
    mask = user_char > 0
    color_overlay = np.zeros_like(basic)
    color_overlay[:] = [255, 100, 100]
    basic[mask] = cv2.addWeighted(basic[mask], 0.5, color_overlay[mask], 0.5, 0)
    overlays['basic'] = basic
    
    # 2. 투명 오버레이
    transparent = cv2.addWeighted(guide_img, 0.5, aligned_user, 0.5, 0)
    overlays['transparent'] = transparent
    
    # 3. 차이 분석
    diff = np.ones_like(guide_img) * 255
    
    common = cv2.bitwise_and(guide_char, user_char)
    diff[common > 0] = [200, 100, 200]  # 보라색
    
    guide_only = cv2.bitwise_and(guide_char, cv2.bitwise_not(user_char))
    diff[guide_only > 0] = [100, 100, 255]  # 빨간색
    
    user_only = cv2.bitwise_and(user_char, cv2.bitwise_not(guide_char))
    diff[user_only > 0] = [255, 100, 100]  # 파란색
    
    overlays['difference'] = diff
    
    return overlays


def calculate_scores(user_char, guide_char):
    """점수 계산"""
    scores = {}
    
    # 1. 겹침도 (IoU)
    intersection = np.logical_and(user_char > 0, guide_char > 0)
    union = np.logical_or(user_char > 0, guide_char > 0)
    if np.sum(union) > 0:
        scores['overlap'] = (np.sum(intersection) / np.sum(union)) * 100
    else:
        scores['overlap'] = 0
    
    # 2. 채움도 (가이드 영역을 얼마나 채웠는지)
    if np.sum(guide_char > 0) > 0:
        scores['fill_rate'] = (np.sum(intersection) / np.sum(guide_char > 0)) * 100
    else:
        scores['fill_rate'] = 0
    
    # 3. 정확도 (불필요한 부분이 얼마나 적은지)
    user_only = np.logical_and(user_char > 0, guide_char == 0)
    if np.sum(user_char > 0) > 0:
        scores['accuracy'] = (1 - np.sum(user_only) / np.sum(user_char > 0)) * 100
    else:
        scores['accuracy'] = 0
    
    # 4. 획 매칭
    user_edges = cv2.Canny(user_char.astype(np.uint8), 50, 150)
    guide_edges = cv2.Canny(guide_char.astype(np.uint8), 50, 150)
    
    edge_match = np.logical_and(user_edges > 0, guide_edges > 0)
    if np.sum(guide_edges > 0) > 0:
        scores['stroke_match'] = (np.sum(edge_match) / np.sum(guide_edges > 0)) * 100
    else:
        scores['stroke_match'] = 0
    
    # 최종 점수 (가중 평균)
    scores['final'] = (
        scores['overlap'] * 0.3 +
        scores['fill_rate'] * 0.3 +
        scores['accuracy'] * 0.2 +
        scores['stroke_match'] * 0.2
    )
    
    return scores


def visualize_results(original_user, scaled_user, guide_img, aligned_user,
                      overlays, scores, output_dir, scale_factor):
    """결과 시각화"""
    
    fig = plt.figure(figsize=(18, 10))
    
    # 원본과 크기 조정된 이미지
    ax1 = plt.subplot(2, 5, 1)
    ax1.imshow(cv2.cvtColor(original_user, cv2.COLOR_BGR2RGB))
    ax1.set_title('원본 사용자 글자', fontsize=11, fontweight='bold')
    ax1.axis('off')
    
    ax2 = plt.subplot(2, 5, 2)
    ax2.imshow(cv2.cvtColor(scaled_user, cv2.COLOR_BGR2RGB))
    ax2.set_title(f'크기 조정 ({scale_factor:.1f}배)', fontsize=11, fontweight='bold')
    ax2.axis('off')
    
    ax3 = plt.subplot(2, 5, 3)
    ax3.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
    ax3.set_title('결구 가이드', fontsize=11, fontweight='bold')
    ax3.axis('off')
    
    ax4 = plt.subplot(2, 5, 4)
    ax4.imshow(cv2.cvtColor(aligned_user, cv2.COLOR_BGR2RGB))
    ax4.set_title('정렬된 글자', fontsize=11, fontweight='bold')
    ax4.axis('off')
    
    # 오버레이
    ax5 = plt.subplot(2, 5, 6)
    ax5.imshow(cv2.cvtColor(overlays['basic'], cv2.COLOR_BGR2RGB))
    ax5.set_title('기본 오버레이', fontsize=11)
    ax5.axis('off')
    
    ax6 = plt.subplot(2, 5, 7)
    ax6.imshow(cv2.cvtColor(overlays['transparent'], cv2.COLOR_BGR2RGB))
    ax6.set_title('투명 오버레이', fontsize=11)
    ax6.axis('off')
    
    ax7 = plt.subplot(2, 5, 8)
    ax7.imshow(cv2.cvtColor(overlays['difference'], cv2.COLOR_BGR2RGB))
    ax7.set_title('차이 분석', fontsize=11)
    ax7.axis('off')
    
    # 점수 그래프
    ax8 = plt.subplot(2, 5, 5)
    
    score_names = ['겹침도', '채움도', '정확도', '획매칭']
    score_values = [
        scores['overlap'],
        scores['fill_rate'],
        scores['accuracy'],
        scores['stroke_match']
    ]
    
    colors = ['#3498DB', '#2ECC71', '#F39C12', '#E74C3C']
    bars = ax8.bar(score_names, score_values, color=colors)
    ax8.set_ylim(0, 100)
    ax8.set_ylabel('점수 (%)', fontsize=11)
    ax8.set_title('항목별 점수', fontsize=12, fontweight='bold')
    ax8.grid(axis='y', alpha=0.3)
    
    for bar, value in zip(bars, score_values):
        ax8.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{value:.1f}', ha='center', va='bottom', fontsize=10)
    
    # 점수 요약
    ax9 = plt.subplot(2, 5, 9)
    
    score_text = f"""
📊 크기 조정 후 분석 결과

크기 조정: {scale_factor:.1f}배 확대

겹침도: {scores['overlap']:.1f}%
채움도: {scores['fill_rate']:.1f}%
정확도: {scores['accuracy']:.1f}%
획 매칭: {scores['stroke_match']:.1f}%

━━━━━━━━━━━━
종합 점수: {scores['final']:.1f}점
    """
    
    ax9.text(0.1, 0.5, score_text, fontsize=11,
            verticalalignment='center', fontfamily='monospace')
    ax9.axis('off')
    
    # 등급
    ax10 = plt.subplot(2, 5, 10)
    
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
    else:
        grade = "D"
        msg = "연습 필요"
        color = '#E74C3C'
    
    circle = plt.Circle((0.5, 0.6), 0.3, color=color, alpha=0.2)
    ax10.add_patch(circle)
    ax10.text(0.5, 0.6, grade, fontsize=48, fontweight='bold',
            ha='center', va='center', color=color)
    ax10.text(0.5, 0.25, msg, fontsize=14,
            ha='center', va='center')
    ax10.text(0.5, 0.1, f"{final:.1f}점", fontsize=12,
            ha='center', va='center', fontweight='bold')
    ax10.set_xlim(0, 1)
    ax10.set_ylim(0, 1)
    ax10.axis('off')
    
    plt.suptitle('크기 조정 글자 비교 분석', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'scaled_analysis.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # 오버레이 개별 저장
    for name, overlay in overlays.items():
        cv2.imwrite(os.path.join(output_dir, f'overlay_{name}.png'), overlay)
    
    print(f"\n✅ 결과 저장 완료: {output_dir}/")


def main():
    print("="*60)
    print("📝 크기 조정 글자 비교 분석")
    print("  (사용자 글자를 가이드 크기에 맞춤)")
    print("="*60)
    
    scores = process_scaled_comparison()
    
    if scores:
        print("\n" + "="*60)
        print("📊 분석 결과")
        print("="*60)
        print(f"겹침도: {scores['overlap']:.1f}%")
        print(f"채움도: {scores['fill_rate']:.1f}%")
        print(f"정확도: {scores['accuracy']:.1f}%")
        print(f"획 매칭: {scores['stroke_match']:.1f}%")
        print("-"*60)
        print(f"🎯 종합 점수: {scores['final']:.1f}점")
        print("="*60)


if __name__ == "__main__":
    main()