#!/usr/bin/env python3
"""
스크린샷 이미지 오버레이 비교 시스템
사용자 글자와 결구 가이드라인을 정확히 오버레이하여 점수 산출
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class ScreenshotOverlay:
    """스크린샷 기반 글자 비교 클래스"""
    
    def process_screenshots(self, user_path, reference_path, guide_path, output_dir="screenshot_output"):
        """
        세 개의 스크린샷 처리 및 비교
        
        Args:
            user_path: 사용자가 쓴 글자
            reference_path: 교본 글자
            guide_path: 결구 가이드라인
            output_dir: 출력 디렉토리
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 이미지 로드
        user_img = cv2.imread(user_path)
        ref_img = cv2.imread(reference_path)
        guide_img = cv2.imread(guide_path)
        
        # 크기 통일 (가이드 이미지 크기로)
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
        
        # 가이드라인 추출 (빨간색 선)
        guide_hsv = cv2.cvtColor(guide_img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        red_mask1 = cv2.inRange(guide_hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(guide_hsv, lower_red2, upper_red2)
        red_lines = red_mask1 + red_mask2
        
        # 검은 윤곽선 추출
        _, guide_binary = cv2.threshold(guide_gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # 오버레이 생성
        overlay1 = self.create_overlay_on_guide(guide_img, user_binary, "사용자 글자")
        overlay2 = self.create_overlay_on_guide(guide_img, ref_binary, "교본 글자")
        overlay3 = self.create_triple_overlay(guide_img, user_binary, ref_binary)
        
        # 점수 계산
        scores = self.calculate_detailed_scores(user_binary, ref_binary, guide_binary, red_lines)
        
        # 결과 시각화
        self.visualize_comprehensive_results(
            user_resized, ref_resized, guide_img,
            overlay1, overlay2, overlay3,
            scores, output_dir
        )
        
        return scores
    
    def create_overlay_on_guide(self, guide_img, char_binary, label):
        """가이드 위에 글자 오버레이"""
        overlay = guide_img.copy()
        
        # 글자를 반투명 파란색으로 오버레이
        if label == "사용자 글자":
            color = (255, 100, 0)  # 파란색
            alpha = 0.5
        else:
            color = (0, 255, 0)  # 초록색
            alpha = 0.3
        
        colored_char = np.zeros_like(overlay)
        colored_char[:, :] = color
        
        # 마스크 적용
        mask = char_binary > 0
        overlay[mask] = cv2.addWeighted(overlay[mask], 1-alpha, colored_char[mask], alpha, 0)
        
        return overlay
    
    def create_triple_overlay(self, guide_img, user_binary, ref_binary):
        """세 개 모두 오버레이"""
        overlay = guide_img.copy()
        
        # 사용자 글자 - 파란색
        user_mask = user_binary > 0
        overlay[user_mask, 0] = np.minimum(255, overlay[user_mask, 0] + 100)  # Blue
        
        # 교본 글자 - 초록색
        ref_mask = ref_binary > 0
        overlay[ref_mask, 1] = np.minimum(255, overlay[ref_mask, 1] + 100)  # Green
        
        return overlay
    
    def calculate_detailed_scores(self, user_binary, ref_binary, guide_binary, red_lines):
        """상세 점수 계산"""
        scores = {}
        
        # 1. 교본과의 일치도
        intersection = np.logical_and(user_binary > 0, ref_binary > 0)
        union = np.logical_or(user_binary > 0, ref_binary > 0)
        if np.sum(union) > 0:
            scores['reference_match'] = (np.sum(intersection) / np.sum(union)) * 100
        else:
            scores['reference_match'] = 0
        
        # 2. 가이드라인 준수도
        # 빨간 선 영역 확장 (선 주변 영역도 포함)
        kernel = np.ones((5, 5), np.uint8)
        red_area = cv2.dilate(red_lines, kernel, iterations=2)
        
        # 글자가 빨간 선 영역 내에 있는 비율
        user_in_red = np.logical_and(user_binary > 0, red_area > 0)
        if np.sum(user_binary > 0) > 0:
            scores['guideline_adherence'] = (np.sum(user_in_red) / np.sum(user_binary > 0)) * 100
        else:
            scores['guideline_adherence'] = 0
        
        # 3. 중심 정렬
        M_user = cv2.moments(user_binary)
        M_ref = cv2.moments(ref_binary)
        
        if M_user["m00"] > 0 and M_ref["m00"] > 0:
            cx_user = int(M_user["m10"] / M_user["m00"])
            cy_user = int(M_user["m01"] / M_user["m00"])
            cx_ref = int(M_ref["m10"] / M_ref["m00"])
            cy_ref = int(M_ref["m01"] / M_ref["m00"])
            
            h, w = user_binary.shape
            max_dist = np.sqrt(w**2 + h**2)
            actual_dist = np.sqrt((cx_user - cx_ref)**2 + (cy_user - cy_ref)**2)
            scores['center_alignment'] = max(0, 100 * (1 - actual_dist / max_dist))
        else:
            scores['center_alignment'] = 0
        
        # 4. 크기 비율
        user_pixels = np.sum(user_binary > 0)
        ref_pixels = np.sum(ref_binary > 0)
        
        if ref_pixels > 0:
            size_ratio = min(user_pixels, ref_pixels) / max(user_pixels, ref_pixels)
            scores['size_match'] = size_ratio * 100
        else:
            scores['size_match'] = 0
        
        # 5. 획 구조 일치도 (단순 엣지 기반)
        # 엣지 검출로 획 구조 비교
        user_edges = cv2.Canny(user_binary, 50, 150)
        ref_edges = cv2.Canny(ref_binary, 50, 150)
        
        edge_match = np.logical_and(user_edges > 0, ref_edges > 0)
        if np.sum(ref_edges > 0) > 0:
            scores['stroke_structure'] = (np.sum(edge_match) / np.sum(ref_edges > 0)) * 100
        else:
            scores['stroke_structure'] = 0
        
        # 최종 점수
        scores['final_score'] = np.mean([
            scores['reference_match'],
            scores['guideline_adherence'],
            scores['center_alignment'],
            scores['size_match'],
            scores['stroke_structure']
        ])
        
        return scores
    
    def visualize_comprehensive_results(self, user_img, ref_img, guide_img, 
                                       overlay1, overlay2, overlay3, scores, output_dir):
        """종합 결과 시각화"""
        
        fig = plt.figure(figsize=(20, 12))
        
        # 원본 이미지들
        ax1 = plt.subplot(3, 4, 1)
        ax1.imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
        ax1.set_title('사용자 글자', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        ax2 = plt.subplot(3, 4, 2)
        ax2.imshow(cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB))
        ax2.set_title('교본 글자', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        ax3 = plt.subplot(3, 4, 3)
        ax3.imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
        ax3.set_title('결구 가이드', fontsize=12, fontweight='bold')
        ax3.axis('off')
        
        # 오버레이 결과들
        ax4 = plt.subplot(3, 4, 5)
        ax4.imshow(cv2.cvtColor(overlay1, cv2.COLOR_BGR2RGB))
        ax4.set_title('사용자 + 가이드', fontsize=12)
        ax4.axis('off')
        
        ax5 = plt.subplot(3, 4, 6)
        ax5.imshow(cv2.cvtColor(overlay2, cv2.COLOR_BGR2RGB))
        ax5.set_title('교본 + 가이드', fontsize=12)
        ax5.axis('off')
        
        ax6 = plt.subplot(3, 4, 7)
        ax6.imshow(cv2.cvtColor(overlay3, cv2.COLOR_BGR2RGB))
        ax6.set_title('전체 오버레이', fontsize=12)
        ax6.axis('off')
        
        # 점수 막대 그래프
        ax7 = plt.subplot(3, 4, 9)
        score_names = ['교본\n일치도', '가이드\n준수도', '중심\n정렬', '크기\n일치', '획\n구조']
        score_values = [
            scores['reference_match'],
            scores['guideline_adherence'],
            scores['center_alignment'],
            scores['size_match'],
            scores['stroke_structure']
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        bars = ax7.bar(score_names, score_values, color=colors)
        ax7.set_ylim(0, 100)
        ax7.set_ylabel('점수', fontsize=11)
        ax7.set_title('항목별 점수', fontsize=12, fontweight='bold')
        
        for bar, value in zip(bars, score_values):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 점수 요약
        ax8 = plt.subplot(3, 4, 10)
        score_text = f"""
📊 결구 분석 결과

교본 일치도: {scores['reference_match']:.1f}점
가이드라인 준수도: {scores['guideline_adherence']:.1f}점
중심 정렬도: {scores['center_alignment']:.1f}점
크기 일치도: {scores['size_match']:.1f}점
획 구조 일치도: {scores['stroke_structure']:.1f}점

━━━━━━━━━━━━━━━━━━
최종 점수: {scores['final_score']:.1f}점
        """
        ax8.text(0.1, 0.5, score_text, fontsize=11,
                verticalalignment='center', fontfamily='monospace')
        ax8.axis('off')
        
        # 평가 및 조언
        ax9 = plt.subplot(3, 4, 11)
        final_score = scores['final_score']
        
        if final_score >= 90:
            grade = "S"
            message = "🏆 완벽합니다!"
            advice = "뛰어난 실력입니다.\n계속 유지하세요!"
            color = 'gold'
        elif final_score >= 80:
            grade = "A"
            message = "⭐ 우수합니다!"
            advice = "매우 잘하고 있습니다.\n세부 조정만 필요해요."
            color = 'silver'
        elif final_score >= 70:
            grade = "B"
            message = "👍 잘했습니다!"
            advice = "좋은 진전을 보이고 있어요.\n조금 더 연습하세요."
            color = '#CD7F32'
        elif final_score >= 60:
            grade = "C"
            message = "💪 노력하세요!"
            advice = "기본기는 갖춰졌어요.\n가이드라인을 더 의식하세요."
            color = 'lightblue'
        else:
            grade = "D"
            message = "📝 연습이 필요해요"
            advice = "가이드라인을 따라\n천천히 연습하세요."
            color = 'lightgray'
        
        # 등급 표시
        ax9.add_patch(plt.Circle((0.5, 0.7), 0.25, color=color, alpha=0.3))
        ax9.text(0.5, 0.7, grade, fontsize=48, fontweight='bold',
                ha='center', va='center')
        ax9.text(0.5, 0.3, message, fontsize=14, fontweight='bold',
                ha='center', va='center')
        ax9.text(0.5, 0.1, advice, fontsize=10,
                ha='center', va='center', style='italic')
        ax9.set_xlim(0, 1)
        ax9.set_ylim(0, 1)
        ax9.axis('off')
        
        # 개선 포인트
        ax10 = plt.subplot(3, 4, 12)
        
        # 가장 낮은 점수 항목 찾기
        score_dict = {
            '교본 일치도': scores['reference_match'],
            '가이드라인 준수도': scores['guideline_adherence'],
            '중심 정렬': scores['center_alignment'],
            '크기 일치': scores['size_match'],
            '획 구조': scores['stroke_structure']
        }
        
        weakest = min(score_dict, key=score_dict.get)
        strongest = max(score_dict, key=score_dict.get)
        
        improvement_text = f"""
💡 개선 포인트

✅ 강점: {strongest}
   ({score_dict[strongest]:.1f}점)

⚠️ 개선 필요: {weakest}
   ({score_dict[weakest]:.1f}점)

📌 연습 팁:
• 가이드라인을 자주 확인
• 획 순서 지키기
• 천천히 정확하게 쓰기
        """
        
        ax10.text(0.1, 0.5, improvement_text, fontsize=10,
                 verticalalignment='center')
        ax10.axis('off')
        
        plt.suptitle('中 글자 결구 종합 분석', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        # 저장
        result_path = os.path.join(output_dir, 'comprehensive_analysis.png')
        plt.savefig(result_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # 개별 오버레이도 저장
        cv2.imwrite(os.path.join(output_dir, 'overlay_user.png'), overlay1)
        cv2.imwrite(os.path.join(output_dir, 'overlay_reference.png'), overlay2)
        cv2.imwrite(os.path.join(output_dir, 'overlay_all.png'), overlay3)
        
        print(f"✅ 결과 저장 완료:")
        print(f"   - 종합 분석: {result_path}")
        print(f"   - 사용자 오버레이: {os.path.join(output_dir, 'overlay_user.png')}")
        print(f"   - 교본 오버레이: {os.path.join(output_dir, 'overlay_reference.png')}")
        print(f"   - 전체 오버레이: {os.path.join(output_dir, 'overlay_all.png')}")


def main():
    """메인 실행"""
    
    # 스크린샷 경로
    user_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.43.21.png"
    reference_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.19.png"
    guide_path = "/Users/m4_macbook/Desktop/스크린샷 2025-08-14 오후 12.42.53.png"
    
    # 파일 존재 확인
    for path, name in [(user_path, "사용자 글자"), 
                       (reference_path, "교본"), 
                       (guide_path, "가이드라인")]:
        if not os.path.exists(path):
            print(f"❌ {name} 파일을 찾을 수 없습니다: {path}")
            return
    
    print("="*60)
    print("📝 中 글자 결구 분석 시작")
    print("="*60)
    
    analyzer = ScreenshotOverlay()
    scores = analyzer.process_screenshots(user_path, reference_path, guide_path)
    
    print("\n" + "="*60)
    print("📊 최종 점수 요약")
    print("="*60)
    print(f"교본 일치도: {scores['reference_match']:.1f}점")
    print(f"가이드라인 준수도: {scores['guideline_adherence']:.1f}점")
    print(f"중심 정렬도: {scores['center_alignment']:.1f}점")
    print(f"크기 일치도: {scores['size_match']:.1f}점")
    print(f"획 구조 일치도: {scores['stroke_structure']:.1f}점")
    print("-"*60)
    print(f"🎯 최종 점수: {scores['final_score']:.1f}점")
    print("="*60)


if __name__ == "__main__":
    main()