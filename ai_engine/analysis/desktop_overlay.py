#!/usr/bin/env python3
"""
Desktop 스크린샷 이미지를 사용한 결구 비교 시스템
사용자 글자를 결구 가이드라인과 오버레이하여 점수 산출
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def process_desktop_images():
    """Desktop의 스크린샷 이미지들을 처리"""
    
    # 이미지 경로
    user_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"  # 사용자가 쓴 글자
    ref_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"   # 교본 글자
    guide_img_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png" # 결구 가이드
    
    # 이미지 로드
    user_img = cv2.imread(user_img_path)
    ref_img = cv2.imread(ref_img_path)
    guide_img = cv2.imread(guide_img_path)
    
    if user_img is None or ref_img is None or guide_img is None:
        print("이미지를 로드할 수 없습니다.")
        return
    
    print("✅ 이미지 로드 완료")
    print(f"   - 사용자 글자: {user_img.shape}")
    print(f"   - 교본 글자: {ref_img.shape}")
    print(f"   - 결구 가이드: {guide_img.shape}")
    
    # 출력 디렉토리
    output_dir = "desktop_analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # 크기 통일 (가이드 크기에 맞춤)
    h, w = guide_img.shape[:2]
    user_resized = cv2.resize(user_img, (w, h))
    ref_resized = cv2.resize(ref_img, (w, h))
    
    # 그레이스케일 변환
    user_gray = cv2.cvtColor(user_resized, cv2.COLOR_BGR2GRAY)
    ref_gray = cv2.cvtColor(ref_resized, cv2.COLOR_BGR2GRAY)
    guide_gray = cv2.cvtColor(guide_img, cv2.COLOR_BGR2GRAY)
    
    # 이진화 (글자 추출)
    _, user_binary = cv2.threshold(user_gray, 127, 255, cv2.THRESH_BINARY_INV)
    _, ref_binary = cv2.threshold(ref_gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 오버레이 생성
    overlay = create_overlay(guide_img, user_resized, user_binary)
    
    # 가이드라인 추출 (빨간색과 검은색 선)
    guideline_mask = extract_guidelines(guide_img)
    
    # 점수 계산
    scores = calculate_scores(user_binary, ref_binary, guideline_mask, guide_gray)
    
    # 결과 시각화
    visualize_results(user_resized, ref_resized, guide_img, overlay, scores, output_dir)
    
    return scores


def extract_guidelines(guide_img):
    """가이드 이미지에서 가이드라인 추출"""
    
    # HSV 변환
    hsv = cv2.cvtColor(guide_img, cv2.COLOR_BGR2HSV)
    
    # 빨간색 선 추출
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask_red1 + mask_red2
    
    # 검은색 선 추출 (윤곽선)
    gray = cv2.cvtColor(guide_img, cv2.COLOR_BGR2GRAY)
    _, black_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # 가이드라인 결합
    guideline_mask = cv2.bitwise_or(red_mask, black_mask)
    
    return guideline_mask


def create_overlay(guide_img, user_img, user_mask):
    """가이드와 사용자 글자 오버레이 생성"""
    
    # 오버레이 베이스는 가이드 이미지
    overlay = guide_img.copy()
    
    # 사용자 글자를 파란색으로 오버레이
    blue_overlay = np.zeros_like(overlay)
    blue_overlay[:, :, 0] = user_mask  # Blue channel
    
    # 알파 블렌딩 (투명도 40%)
    alpha = 0.4
    overlay = cv2.addWeighted(overlay, 1-alpha, blue_overlay, alpha, 0)
    
    return overlay


def calculate_scores(user_binary, ref_binary, guideline_mask, guide_gray):
    """점수 계산"""
    
    scores = {}
    
    # 1. 가이드라인 내부 비율
    # 가이드라인으로 둘러싸인 영역 찾기
    kernel = np.ones((5,5), np.uint8)
    guideline_filled = cv2.morphologyEx(guideline_mask, cv2.MORPH_CLOSE, kernel)
    
    # 가이드 영역 내 글자 비율
    inside_guide = cv2.bitwise_and(user_binary, guideline_filled)
    total_pixels = np.sum(user_binary > 0)
    if total_pixels > 0:
        inside_pixels = np.sum(inside_guide > 0)
        guide_score = (inside_pixels / total_pixels) * 100
    else:
        guide_score = 0
    
    scores['guide_adherence'] = min(100, guide_score)
    
    # 2. 교본과의 중심 비교
    M_ref = cv2.moments(ref_binary)
    M_user = cv2.moments(user_binary)
    
    if M_ref["m00"] > 0 and M_user["m00"] > 0:
        cx_ref = int(M_ref["m10"] / M_ref["m00"])
        cy_ref = int(M_ref["m01"] / M_ref["m00"])
        cx_user = int(M_user["m10"] / M_user["m00"])
        cy_user = int(M_user["m01"] / M_user["m00"])
        
        h, w = ref_binary.shape
        max_dist = np.sqrt(w**2 + h**2)
        actual_dist = np.sqrt((cx_ref - cx_user)**2 + (cy_ref - cy_user)**2)
        center_score = max(0, 100 * (1 - actual_dist / max_dist))
    else:
        center_score = 0
    
    scores['center_alignment'] = center_score
    
    # 3. 크기 비율 (교본 대비)
    ref_pixels = np.sum(ref_binary > 0)
    user_pixels = np.sum(user_binary > 0)
    
    if ref_pixels > 0:
        size_ratio = min(ref_pixels, user_pixels) / max(ref_pixels, user_pixels)
        size_score = size_ratio * 100
    else:
        size_score = 0
    
    scores['size_match'] = size_score
    
    # 4. 획의 균형도
    # 상하좌우 4분면으로 나누어 균형 측정
    h, w = user_binary.shape
    mid_h, mid_w = h // 2, w // 2
    
    quadrants = [
        user_binary[:mid_h, :mid_w],    # 좌상
        user_binary[:mid_h, mid_w:],    # 우상
        user_binary[mid_h:, :mid_w],    # 좌하
        user_binary[mid_h:, mid_w:]     # 우하
    ]
    
    quad_pixels = [np.sum(q > 0) for q in quadrants]
    if sum(quad_pixels) > 0:
        # 균형도: 각 사분면의 픽셀 분포가 얼마나 균등한지
        mean_pixels = np.mean(quad_pixels)
        std_pixels = np.std(quad_pixels)
        balance_score = max(0, 100 * (1 - std_pixels / mean_pixels)) if mean_pixels > 0 else 0
    else:
        balance_score = 0
    
    scores['balance'] = balance_score
    
    # 5. 형태 유사도 (IoU)
    intersection = np.sum(np.logical_and(ref_binary > 0, user_binary > 0))
    union = np.sum(np.logical_or(ref_binary > 0, user_binary > 0))
    
    if union > 0:
        iou_score = (intersection / union) * 100
    else:
        iou_score = 0
    
    scores['shape_similarity'] = iou_score
    
    # 최종 점수 (가중 평균)
    weights = {
        'guide_adherence': 0.25,
        'center_alignment': 0.20,
        'size_match': 0.20,
        'balance': 0.15,
        'shape_similarity': 0.20
    }
    
    final_score = sum(scores[key] * weights[key] for key in weights.keys())
    scores['final_score'] = final_score
    
    return scores


def visualize_results(user_img, ref_img, guide_img, overlay, scores, output_dir):
    """결과 시각화 및 저장"""
    
    fig = plt.figure(figsize=(16, 10))
    
    # 이미지 표시
    ax1 = plt.subplot(2, 4, 1)
    ax1.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
    ax1.set_title('작성한 글자', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    ax2 = plt.subplot(2, 4, 2)
    ax2.imshow(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB))
    ax2.set_title('교본 글자', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    ax3 = plt.subplot(2, 4, 3)
    ax3.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
    ax3.set_title('결구 가이드', fontsize=12, fontweight='bold')
    ax3.axis('off')
    
    ax4 = plt.subplot(2, 4, 4)
    ax4.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    ax4.set_title('오버레이 결과', fontsize=12, fontweight='bold')
    ax4.axis('off')
    
    # 점수 막대 그래프
    ax5 = plt.subplot(2, 2, 3)
    
    score_names = ['가이드\n준수', '중심\n정렬', '크기\n일치', '균형도', '형태\n유사도']
    score_values = [
        scores['guide_adherence'],
        scores['center_alignment'],
        scores['size_match'],
        scores['balance'],
        scores['shape_similarity']
    ]
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    bars = ax5.bar(score_names, score_values, color=colors)
    ax5.set_ylim(0, 100)
    ax5.set_ylabel('점수', fontsize=11)
    ax5.set_title('항목별 점수 분석', fontsize=12, fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    
    # 막대 위에 점수 표시
    for bar, value in zip(bars, score_values):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}', ha='center', va='bottom', fontsize=10)
    
    # 점수 요약 및 평가
    ax6 = plt.subplot(2, 2, 4)
    
    score_text = f"""
    📊 中 글자 분석 결과
    
    가이드라인 준수도: {scores['guide_adherence']:6.1f}점
    중심 정렬도:      {scores['center_alignment']:6.1f}점
    크기 일치도:      {scores['size_match']:6.1f}점
    균형도:          {scores['balance']:6.1f}점
    형태 유사도:      {scores['shape_similarity']:6.1f}점
    
    ━━━━━━━━━━━━━━━━━━━━
    최종 점수:       {scores['final_score']:6.1f}점
    """
    
    ax6.text(0.1, 0.5, score_text, fontsize=11,
            verticalalignment='center', fontfamily='monospace')
    ax6.axis('off')
    
    # 평가 메시지
    final_score = scores['final_score']
    if final_score >= 90:
        message = "🏆 완벽합니다! 교본과 거의 일치합니다."
        color = 'darkgreen'
    elif final_score >= 80:
        message = "🎯 훌륭합니다! 매우 잘 쓰셨습니다."
        color = 'green'
    elif final_score >= 70:
        message = "😊 잘했습니다! 좋은 수준입니다."
        color = 'blue'
    elif final_score >= 60:
        message = "👍 양호합니다! 조금 더 연습하세요."
        color = 'orange'
    elif final_score >= 50:
        message = "💪 노력이 필요합니다!"
        color = 'darkorange'
    else:
        message = "📝 더 많은 연습이 필요합니다!"
        color = 'red'
    
    ax6.text(0.5, 0.1, message, fontsize=14, 
            ha='center', va='center', fontweight='bold', color=color)
    
    plt.suptitle('한자 "中" 결구 분석 시스템', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 저장
    result_path = os.path.join(output_dir, 'desktop_analysis_result.png')
    plt.savefig(result_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # 오버레이 이미지도 별도 저장
    overlay_path = os.path.join(output_dir, 'desktop_overlay.png')
    cv2.imwrite(overlay_path, overlay)
    
    print(f"\n✅ 결과 저장 완료:")
    print(f"   - 분석 결과: {result_path}")
    print(f"   - 오버레이: {overlay_path}")


def main():
    """메인 실행"""
    
    print("="*60)
    print("Desktop 스크린샷 이미지 분석 시작")
    print("="*60)
    
    scores = process_desktop_images()
    
    if scores:
        print("\n" + "="*60)
        print("📊 분석 결과")
        print("="*60)
        
        print(f"가이드라인 준수도: {scores['guide_adherence']:.1f}점")
        print(f"중심 정렬도: {scores['center_alignment']:.1f}점")
        print(f"크기 일치도: {scores['size_match']:.1f}점")
        print(f"균형도: {scores['balance']:.1f}점")
        print(f"형태 유사도: {scores['shape_similarity']:.1f}점")
        print("-"*60)
        print(f"✨ 최종 점수: {scores['final_score']:.1f}점")
        print("="*60)
        
        # 평가 메시지
        final = scores['final_score']
        if final >= 80:
            print("🎉 매우 잘 쓰셨습니다!")
        elif final >= 70:
            print("👏 잘 쓰셨습니다!")
        elif final >= 60:
            print("💡 양호한 수준입니다.")
        else:
            print("📚 더 연습하면 좋아질 거예요!")


if __name__ == "__main__":
    main()