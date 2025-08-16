#!/usr/bin/env python3
"""
빨간 테두리를 기준으로 정렬하여 비교
사용자가 추가한 테두리와 가이드의 테두리를 맞춰서 오버레이
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def process_aligned_comparison():
    """테두리 정렬 비교 실행"""
    
    # 이미지 경로
    reference_with_border = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"  # 교본 + 빨간 테두리
    guide_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png"  # 결구 가이드
    user_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"  # 사용자 글자
    
    # 이미지 로드
    ref_img = cv2.imread(reference_with_border)
    guide_img = cv2.imread(guide_path)
    user_img = cv2.imread(user_path)
    
    if ref_img is None or guide_img is None or user_img is None:
        print("이미지를 로드할 수 없습니다.")
        return
    
    print("✅ 이미지 로드 완료")
    
    # 출력 디렉토리
    output_dir = "aligned_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 크기 통일 (가이드 크기로)
    h, w = guide_img.shape[:2]
    ref_resized = cv2.resize(ref_img, (w, h))
    user_resized = cv2.resize(user_img, (w, h))
    
    # 빨간 테두리 검출
    ref_border = detect_red_border(ref_resized)
    guide_border = detect_red_border(guide_img)
    
    # 테두리 정렬
    aligned_ref = align_borders(ref_resized, ref_border, guide_border, guide_img.shape[:2])
    aligned_user = align_borders(user_resized, detect_red_border(user_resized), guide_border, guide_img.shape[:2])
    
    # 글자 추출
    ref_char = extract_character(aligned_ref)
    guide_char = extract_character(guide_img)
    user_char = extract_character(aligned_user)
    
    # 오버레이 생성
    overlay1 = create_overlay(guide_img, aligned_ref, "교본")
    overlay2 = create_overlay(guide_img, aligned_user, "사용자")
    overlay3 = create_triple_overlay(guide_img, ref_char, user_char)
    
    # 점수 계산
    scores = calculate_scores(user_char, guide_char, ref_char)
    
    # 시각화
    visualize_results(
        ref_resized, user_resized, guide_img,
        aligned_ref, aligned_user,
        overlay1, overlay2, overlay3,
        scores, output_dir
    )
    
    return scores


def detect_red_border(img):
    """빨간색 테두리 검출"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 빨간색 범위
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    return red_mask


def align_borders(img, img_border, target_border, target_shape):
    """테두리를 기준으로 정렬"""
    
    # 테두리 컨투어 찾기
    img_contours, _ = cv2.findContours(img_border, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    target_contours, _ = cv2.findContours(target_border, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not img_contours or not target_contours:
        return img
    
    # 가장 큰 컨투어 (테두리)
    img_rect = max(img_contours, key=cv2.contourArea)
    target_rect = max(target_contours, key=cv2.contourArea)
    
    # 바운딩 박스
    ix, iy, iw, ih = cv2.boundingRect(img_rect)
    tx, ty, tw, th = cv2.boundingRect(target_rect)
    
    # 변환 계산
    scale_x = tw / iw if iw > 0 else 1
    scale_y = th / ih if ih > 0 else 1
    translate_x = tx - ix * scale_x
    translate_y = ty - iy * scale_y
    
    # 변환 행렬
    M = np.array([[scale_x, 0, translate_x],
                  [0, scale_y, translate_y]], dtype=np.float32)
    
    # 적용
    aligned = cv2.warpAffine(img, M, (target_shape[1], target_shape[0]),
                            borderValue=(255, 255, 255))
    
    return aligned


def extract_character(img):
    """글자 추출 (빨간 테두리 제외)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 빨간색 제거
    red_mask = detect_red_border(img)
    binary = cv2.bitwise_and(binary, cv2.bitwise_not(red_mask))
    
    return binary


def create_overlay(base_img, overlay_img, label):
    """오버레이 생성"""
    result = base_img.copy()
    
    # 글자 추출
    char_mask = extract_character(overlay_img)
    
    # 색상 설정
    if label == "교본":
        color = [0, 255, 0]  # 초록
        alpha = 0.3
    else:
        color = [255, 0, 0]  # 파랑
        alpha = 0.4
    
    # 오버레이
    mask = char_mask > 0
    color_overlay = np.zeros_like(result)
    color_overlay[:] = color
    result[mask] = cv2.addWeighted(result[mask], 1-alpha, color_overlay[mask], alpha, 0)
    
    return result


def create_triple_overlay(base_img, ref_char, user_char):
    """3중 오버레이 (가이드 + 교본 + 사용자)"""
    result = base_img.copy()
    
    # 교본: 초록
    ref_mask = ref_char > 0
    result[ref_mask, 1] = np.minimum(255, result[ref_mask, 1] + 100)
    
    # 사용자: 파랑
    user_mask = user_char > 0
    result[user_mask, 0] = np.minimum(255, result[user_mask, 0] + 100)
    
    # 겹치는 부분: 보라
    overlap = np.logical_and(ref_mask, user_mask)
    result[overlap] = [128, 0, 128]
    
    return result


def calculate_scores(user_char, guide_char, ref_char):
    """점수 계산"""
    scores = {}
    
    # 1. 가이드와의 일치도
    guide_overlap = np.logical_and(user_char > 0, guide_char > 0)
    guide_union = np.logical_or(user_char > 0, guide_char > 0)
    if np.sum(guide_union) > 0:
        scores['guide_match'] = (np.sum(guide_overlap) / np.sum(guide_union)) * 100
    else:
        scores['guide_match'] = 0
    
    # 2. 교본과의 일치도
    ref_overlap = np.logical_and(user_char > 0, ref_char > 0)
    ref_union = np.logical_or(user_char > 0, ref_char > 0)
    if np.sum(ref_union) > 0:
        scores['reference_match'] = (np.sum(ref_overlap) / np.sum(ref_union)) * 100
    else:
        scores['reference_match'] = 0
    
    # 3. 중심 정렬
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
        scores['center_alignment'] = max(0, 100 * (1 - actual_dist / max_dist))
    else:
        scores['center_alignment'] = 0
    
    # 4. 크기 일치도
    user_area = np.sum(user_char > 0)
    guide_area = np.sum(guide_char > 0)
    if guide_area > 0:
        scores['size_match'] = min(user_area, guide_area) / max(user_area, guide_area) * 100
    else:
        scores['size_match'] = 0
    
    # 5. 획 구조
    user_edges = cv2.Canny(user_char.astype(np.uint8), 50, 150)
    guide_edges = cv2.Canny(guide_char.astype(np.uint8), 50, 150)
    
    edge_match = np.logical_and(user_edges > 0, guide_edges > 0)
    if np.sum(guide_edges > 0) > 0:
        scores['stroke_structure'] = (np.sum(edge_match) / np.sum(guide_edges > 0)) * 100
    else:
        scores['stroke_structure'] = 0
    
    # 최종 점수
    scores['final_score'] = np.mean([
        scores['guide_match'],
        scores['reference_match'],
        scores['center_alignment'],
        scores['size_match'],
        scores['stroke_structure']
    ])
    
    return scores


def visualize_results(ref_img, user_img, guide_img,
                      aligned_ref, aligned_user,
                      overlay1, overlay2, overlay3,
                      scores, output_dir):
    """결과 시각화"""
    
    fig = plt.figure(figsize=(18, 10))
    
    # 원본 이미지
    ax1 = plt.subplot(2, 4, 1)
    ax1.imshow(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('교본 (빨간 테두리)', fontsize=11)
    ax1.axis('off')
    
    ax2 = plt.subplot(2, 4, 2)
    ax2.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('사용자 글자', fontsize=11)
    ax2.axis('off')
    
    ax3 = plt.subplot(2, 4, 3)
    ax3.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
    ax3.set_title('결구 가이드', fontsize=11)
    ax3.axis('off')
    
    # 오버레이
    ax4 = plt.subplot(2, 4, 5)
    ax4.imshow(cv2.cvtColor(overlay1, cv2.COLOR_BGR2RGB))
    ax4.set_title('교본 + 가이드 (초록)', fontsize=11)
    ax4.axis('off')
    
    ax5 = plt.subplot(2, 4, 6)
    ax5.imshow(cv2.cvtColor(overlay2, cv2.COLOR_BGR2RGB))
    ax5.set_title('사용자 + 가이드 (파랑)', fontsize=11)
    ax5.axis('off')
    
    ax6 = plt.subplot(2, 4, 7)
    ax6.imshow(cv2.cvtColor(overlay3, cv2.COLOR_BGR2RGB))
    ax6.set_title('전체 오버레이\n(초록:교본, 파랑:사용자, 보라:겹침)', fontsize=11)
    ax6.axis('off')
    
    # 점수
    ax7 = plt.subplot(2, 4, 4)
    
    score_text = f"""
📊 테두리 정렬 분석 결과

가이드 일치도: {scores['guide_match']:.1f}%
교본 일치도: {scores['reference_match']:.1f}%
중심 정렬: {scores['center_alignment']:.1f}%
크기 일치: {scores['size_match']:.1f}%
획 구조: {scores['stroke_structure']:.1f}%

━━━━━━━━━━━━━━━
최종 점수: {scores['final_score']:.1f}점
    """
    
    ax7.text(0.1, 0.5, score_text, fontsize=11,
            verticalalignment='center', fontfamily='monospace')
    ax7.axis('off')
    
    # 평가
    ax8 = plt.subplot(2, 4, 8)
    
    final = scores['final_score']
    if final >= 80:
        grade = "A"
        msg = "🎉 훌륭합니다!"
        color = 'green'
    elif final >= 70:
        grade = "B"
        msg = "👍 잘했습니다!"
        color = 'blue'
    elif final >= 60:
        grade = "C"
        msg = "💡 양호합니다"
        color = 'orange'
    else:
        grade = "D"
        msg = "📚 연습 필요"
        color = 'red'
    
    ax8.text(0.5, 0.6, grade, fontsize=48, fontweight='bold',
            ha='center', va='center', color=color)
    ax8.text(0.5, 0.3, msg, fontsize=14,
            ha='center', va='center')
    ax8.text(0.5, 0.1, f"{final:.1f}점", fontsize=12,
            ha='center', va='center')
    ax8.set_xlim(0, 1)
    ax8.set_ylim(0, 1)
    ax8.axis('off')
    
    plt.suptitle('테두리 정렬 기준 글자 비교 분석', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'aligned_analysis.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # 오버레이 저장
    cv2.imwrite(os.path.join(output_dir, 'overlay_reference.png'), overlay1)
    cv2.imwrite(os.path.join(output_dir, 'overlay_user.png'), overlay2)
    cv2.imwrite(os.path.join(output_dir, 'overlay_all.png'), overlay3)
    
    print(f"\n✅ 결과 저장 완료: {output_dir}/")


def main():
    print("="*60)
    print("📝 테두리 정렬 비교 분석")
    print("="*60)
    
    scores = process_aligned_comparison()
    
    if scores:
        print("\n" + "="*60)
        print("📊 최종 결과")
        print("="*60)
        print(f"가이드 일치도: {scores['guide_match']:.1f}%")
        print(f"교본 일치도: {scores['reference_match']:.1f}%")
        print(f"중심 정렬: {scores['center_alignment']:.1f}%")
        print(f"크기 일치: {scores['size_match']:.1f}%")
        print(f"획 구조: {scores['stroke_structure']:.1f}%")
        print("-"*60)
        print(f"🎯 최종 점수: {scores['final_score']:.1f}점")
        print("="*60)


if __name__ == "__main__":
    main()