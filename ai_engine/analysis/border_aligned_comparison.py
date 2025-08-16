#!/usr/bin/env python3
"""
테두리가 추가된 사용자 글자와 결구 가이드 비교
빨간 테두리를 기준으로 정렬하여 정확한 오버레이 생성
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class BorderAlignedComparison:
    """테두리 기준 정렬 비교 클래스"""
    
    def process_with_border_alignment(self, user_with_border_path, guide_path, reference_path=None):
        """
        테두리가 있는 사용자 글자와 가이드를 정렬하여 비교
        
        Args:
            user_with_border_path: 빨간 테두리가 있는 사용자 글자
            guide_path: 결구 가이드라인
            reference_path: 교본 글자 (선택)
        """
        # 이미지 로드
        user_img = cv2.imread(user_with_border_path)
        guide_img = cv2.imread(guide_path)
        
        if user_img is None or guide_img is None:
            print("이미지를 로드할 수 없습니다.")
            return None
        
        # 빨간 테두리 검출
        user_border = self.detect_red_border(user_img)
        guide_border = self.detect_red_border(guide_img)
        
        # 테두리 기준으로 정렬
        aligned_user, transform_matrix = self.align_by_borders(user_img, user_border, guide_border, guide_img.shape[:2])
        
        # 글자 추출
        user_char = self.extract_character(aligned_user)
        guide_char = self.extract_character(guide_img)
        
        # 오버레이 생성 (여러 버전)
        overlays = self.create_multiple_overlays(guide_img, aligned_user, user_char)
        
        # 점수 계산
        scores = self.calculate_alignment_scores(user_char, guide_char, user_border, guide_border)
        
        # 시각화
        output_dir = "border_aligned_output"
        os.makedirs(output_dir, exist_ok=True)
        self.visualize_results(user_img, guide_img, aligned_user, overlays, scores, output_dir)
        
        return scores
    
    def detect_red_border(self, img):
        """빨간색 테두리 검출"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 빨간색 범위 (두 범위 모두 체크)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        
        return red_mask
    
    def align_by_borders(self, user_img, user_border, guide_border, target_shape):
        """테두리를 기준으로 이미지 정렬"""
        
        # 테두리의 외곽선 찾기
        user_contours, _ = cv2.findContours(user_border, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        guide_contours, _ = cv2.findContours(guide_border, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not user_contours or not guide_contours:
            # 테두리를 찾을 수 없으면 단순 리사이즈
            return cv2.resize(user_img, (target_shape[1], target_shape[0])), np.eye(3)
        
        # 가장 큰 컨투어 선택 (테두리)
        user_rect_contour = max(user_contours, key=cv2.contourArea)
        guide_rect_contour = max(guide_contours, key=cv2.contourArea)
        
        # 바운딩 박스 추출
        user_x, user_y, user_w, user_h = cv2.boundingRect(user_rect_contour)
        guide_x, guide_y, guide_w, guide_h = cv2.boundingRect(guide_rect_contour)
        
        # 스케일 계산
        scale_x = guide_w / user_w if user_w > 0 else 1
        scale_y = guide_h / user_h if user_h > 0 else 1
        
        # 평행이동 계산
        translate_x = guide_x - user_x * scale_x
        translate_y = guide_y - user_y * scale_y
        
        # 변환 행렬 생성
        transform_matrix = np.array([
            [scale_x, 0, translate_x],
            [0, scale_y, translate_y],
            [0, 0, 1]
        ])
        
        # 이미지 변환 적용
        aligned_img = cv2.warpAffine(
            user_img, 
            transform_matrix[:2], 
            (target_shape[1], target_shape[0]),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )
        
        return aligned_img, transform_matrix
    
    def extract_character(self, img):
        """이미지에서 글자 부분만 추출"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 빨간 테두리 제거 (빨간색 부분을 배경으로)
        red_mask = self.detect_red_border(img)
        binary = cv2.bitwise_and(binary, cv2.bitwise_not(red_mask))
        
        return binary
    
    def create_multiple_overlays(self, guide_img, aligned_user, user_char):
        """여러 종류의 오버레이 생성"""
        overlays = {}
        
        # 1. 기본 오버레이 (가이드 + 정렬된 사용자 글자)
        basic_overlay = guide_img.copy()
        mask = user_char > 0
        basic_overlay[mask] = cv2.addWeighted(
            basic_overlay[mask], 0.5,
            np.array([255, 100, 0]), 0.5, 0  # 파란색
        )
        overlays['basic'] = basic_overlay
        
        # 2. 투명 오버레이 (전체 이미지 블렌딩)
        transparent_overlay = cv2.addWeighted(guide_img, 0.6, aligned_user, 0.4, 0)
        overlays['transparent'] = transparent_overlay
        
        # 3. 차이 강조 오버레이
        diff_overlay = guide_img.copy()
        guide_char = self.extract_character(guide_img)
        
        # 공통 부분: 보라색
        common = cv2.bitwise_and(guide_char, user_char)
        # 가이드만: 빨간색
        guide_only = cv2.bitwise_and(guide_char, cv2.bitwise_not(user_char))
        # 사용자만: 파란색
        user_only = cv2.bitwise_and(user_char, cv2.bitwise_not(guide_char))
        
        diff_overlay[common > 0] = [128, 0, 128]  # 보라색
        diff_overlay[guide_only > 0] = [0, 0, 255]  # 빨간색
        diff_overlay[user_only > 0] = [255, 0, 0]  # 파란색
        
        overlays['difference'] = diff_overlay
        
        # 4. 테두리 정렬 확인용
        border_check = guide_img.copy()
        user_border = self.detect_red_border(aligned_user)
        border_check[user_border > 0] = [0, 255, 0]  # 초록색으로 표시
        overlays['border_check'] = border_check
        
        return overlays
    
    def calculate_alignment_scores(self, user_char, guide_char, user_border, guide_border):
        """정렬 기반 점수 계산"""
        scores = {}
        
        # 1. 테두리 정렬도
        border_overlap = np.logical_and(user_border > 0, guide_border > 0)
        border_union = np.logical_or(user_border > 0, guide_border > 0)
        if np.sum(border_union) > 0:
            scores['border_alignment'] = (np.sum(border_overlap) / np.sum(border_union)) * 100
        else:
            scores['border_alignment'] = 0
        
        # 2. 글자 겹침도 (IoU)
        char_intersection = np.logical_and(user_char > 0, guide_char > 0)
        char_union = np.logical_or(user_char > 0, guide_char > 0)
        if np.sum(char_union) > 0:
            scores['character_overlap'] = (np.sum(char_intersection) / np.sum(char_union)) * 100
        else:
            scores['character_overlap'] = 0
        
        # 3. 글자 위치 정확도
        # 각 글자의 무게중심 비교
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
            scores['position_accuracy'] = max(0, 100 * (1 - actual_dist / max_dist))
        else:
            scores['position_accuracy'] = 0
        
        # 4. 획 일치도
        # 엣지 비교
        user_edges = cv2.Canny(user_char.astype(np.uint8), 50, 150)
        guide_edges = cv2.Canny(guide_char.astype(np.uint8), 50, 150)
        
        edge_match = np.logical_and(user_edges > 0, guide_edges > 0)
        if np.sum(guide_edges > 0) > 0:
            scores['stroke_match'] = (np.sum(edge_match) / np.sum(guide_edges > 0)) * 100
        else:
            scores['stroke_match'] = 0
        
        # 5. 크기 일치도
        user_area = np.sum(user_char > 0)
        guide_area = np.sum(guide_char > 0)
        if guide_area > 0:
            size_ratio = min(user_area, guide_area) / max(user_area, guide_area)
            scores['size_match'] = size_ratio * 100
        else:
            scores['size_match'] = 0
        
        # 최종 점수 (가중 평균)
        weights = {
            'border_alignment': 0.15,
            'character_overlap': 0.30,
            'position_accuracy': 0.20,
            'stroke_match': 0.20,
            'size_match': 0.15
        }
        
        scores['final_score'] = sum(scores[key] * weights[key] for key in weights.keys())
        
        return scores
    
    def visualize_results(self, original_user, guide_img, aligned_user, overlays, scores, output_dir):
        """결과 시각화"""
        
        fig = plt.figure(figsize=(20, 12))
        
        # 원본 이미지들
        ax1 = plt.subplot(3, 5, 1)
        ax1.imshow(cv2.cvtColor(original_user, cv2.COLOR_BGR2RGB))
        ax1.set_title('원본 사용자 글자\n(빨간 테두리)', fontsize=10)
        ax1.axis('off')
        
        ax2 = plt.subplot(3, 5, 2)
        ax2.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
        ax2.set_title('결구 가이드', fontsize=10)
        ax2.axis('off')
        
        ax3 = plt.subplot(3, 5, 3)
        ax3.imshow(cv2.cvtColor(aligned_user, cv2.COLOR_BGR2RGB))
        ax3.set_title('정렬된 사용자 글자', fontsize=10)
        ax3.axis('off')
        
        # 오버레이들
        ax4 = plt.subplot(3, 5, 6)
        ax4.imshow(cv2.cvtColor(overlays['basic'], cv2.COLOR_BGR2RGB))
        ax4.set_title('기본 오버레이', fontsize=10)
        ax4.axis('off')
        
        ax5 = plt.subplot(3, 5, 7)
        ax5.imshow(cv2.cvtColor(overlays['transparent'], cv2.COLOR_BGR2RGB))
        ax5.set_title('투명 오버레이', fontsize=10)
        ax5.axis('off')
        
        ax6 = plt.subplot(3, 5, 8)
        ax6.imshow(cv2.cvtColor(overlays['difference'], cv2.COLOR_BGR2RGB))
        ax6.set_title('차이 분석\n(빨강:가이드만, 파랑:사용자만)', fontsize=10)
        ax6.axis('off')
        
        ax7 = plt.subplot(3, 5, 9)
        ax7.imshow(cv2.cvtColor(overlays['border_check'], cv2.COLOR_BGR2RGB))
        ax7.set_title('테두리 정렬 확인\n(초록:정렬된 테두리)', fontsize=10)
        ax7.axis('off')
        
        # 점수 막대 그래프
        ax8 = plt.subplot(3, 5, 11)
        score_names = ['테두리\n정렬', '글자\n겹침', '위치\n정확도', '획\n일치', '크기\n일치']
        score_values = [
            scores['border_alignment'],
            scores['character_overlap'],
            scores['position_accuracy'],
            scores['stroke_match'],
            scores['size_match']
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        bars = ax8.bar(score_names, score_values, color=colors)
        ax8.set_ylim(0, 100)
        ax8.set_ylabel('점수', fontsize=10)
        ax8.set_title('항목별 점수', fontsize=11, fontweight='bold')
        ax8.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars, score_values):
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 점수 요약
        ax9 = plt.subplot(3, 5, 12)
        score_text = f"""
📊 테두리 정렬 기준 분석

테두리 정렬도: {scores['border_alignment']:.1f}점
글자 겹침도: {scores['character_overlap']:.1f}점
위치 정확도: {scores['position_accuracy']:.1f}점
획 일치도: {scores['stroke_match']:.1f}점
크기 일치도: {scores['size_match']:.1f}점

━━━━━━━━━━━━━━━
최종 점수: {scores['final_score']:.1f}점
        """
        ax9.text(0.1, 0.5, score_text, fontsize=10,
                verticalalignment='center', fontfamily='monospace')
        ax9.axis('off')
        
        # 개선 분석
        ax10 = plt.subplot(3, 5, 13)
        
        # 점수 기반 평가
        final = scores['final_score']
        if final >= 80:
            grade = "A"
            evaluation = "훌륭합니다!"
            color = 'green'
        elif final >= 70:
            grade = "B"
            evaluation = "잘했습니다!"
            color = 'blue'
        elif final >= 60:
            grade = "C"
            evaluation = "양호합니다"
            color = 'orange'
        else:
            grade = "D"
            evaluation = "연습 필요"
            color = 'red'
        
        ax10.text(0.5, 0.7, grade, fontsize=36, fontweight='bold',
                 ha='center', va='center', color=color)
        ax10.text(0.5, 0.3, evaluation, fontsize=14,
                 ha='center', va='center')
        ax10.text(0.5, 0.1, f"종합 점수: {final:.1f}점", fontsize=11,
                 ha='center', va='center')
        ax10.set_xlim(0, 1)
        ax10.set_ylim(0, 1)
        ax10.axis('off')
        
        # 상세 분석
        ax11 = plt.subplot(3, 5, 14)
        
        # 가장 높은/낮은 점수 찾기
        score_dict = {
            '테두리 정렬': scores['border_alignment'],
            '글자 겹침': scores['character_overlap'],
            '위치 정확도': scores['position_accuracy'],
            '획 일치': scores['stroke_match'],
            '크기 일치': scores['size_match']
        }
        
        best = max(score_dict, key=score_dict.get)
        worst = min(score_dict, key=score_dict.get)
        
        analysis_text = f"""
💡 상세 분석

✅ 가장 우수: {best}
   ({score_dict[best]:.1f}점)

⚠️ 개선 필요: {worst}
   ({score_dict[worst]:.1f}점)

📝 조언:
테두리를 정확히 맞춘 후
획의 시작과 끝을
가이드와 일치시키세요.
        """
        
        ax11.text(0.1, 0.5, analysis_text, fontsize=9,
                 verticalalignment='center')
        ax11.axis('off')
        
        plt.suptitle('中 글자 테두리 정렬 비교 분석', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # 저장
        result_path = os.path.join(output_dir, 'border_aligned_analysis.png')
        plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # 개별 오버레이 저장
        for name, overlay in overlays.items():
            overlay_path = os.path.join(output_dir, f'overlay_{name}.png')
            cv2.imwrite(overlay_path, overlay)
        
        print(f"\n✅ 분석 완료!")
        print(f"결과 저장 위치: {output_dir}/")
        print(f"  - 종합 분석: border_aligned_analysis.png")
        print(f"  - 오버레이 이미지: overlay_*.png")


def main():
    """메인 실행"""
    
    # 이미지 경로 (사용자가 제공한 새로운 이미지)
    user_with_border = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"  # 빨간 테두리가 있는 사용자 글자
    guide_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png"  # 결구 가이드
    
    print("="*60)
    print("📝 테두리 정렬 기반 글자 비교 분석")
    print("="*60)
    
    analyzer = BorderAlignedComparison()
    scores = analyzer.process_with_border_alignment(user_with_border, guide_path)
    
    if scores:
        print("\n" + "="*60)
        print("📊 분석 결과")
        print("="*60)
        print(f"테두리 정렬도: {scores['border_alignment']:.1f}점")
        print(f"글자 겹침도: {scores['character_overlap']:.1f}점")
        print(f"위치 정확도: {scores['position_accuracy']:.1f}점")
        print(f"획 일치도: {scores['stroke_match']:.1f}점")
        print(f"크기 일치도: {scores['size_match']:.1f}점")
        print("-"*60)
        print(f"🎯 최종 점수: {scores['final_score']:.1f}점")
        print("="*60)
        
        # 평가
        if scores['final_score'] >= 80:
            print("🎉 매우 우수한 수준입니다!")
        elif scores['final_score'] >= 70:
            print("👏 잘 쓰셨습니다!")
        elif scores['final_score'] >= 60:
            print("💡 양호한 수준입니다.")
        else:
            print("📚 더 연습이 필요합니다.")


if __name__ == "__main__":
    main()