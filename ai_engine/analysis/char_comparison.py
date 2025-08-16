#!/usr/bin/env python3
"""
결구 점수 시연 시스템
교본과 사용자 글자를 비교하여 점수를 산출하는 프로그램
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GUI 없이 실행
import matplotlib.pyplot as plt
from pathlib import Path
import os


class CharacterComparator:
    """한글 글자 비교 및 점수 산출 클래스"""
    
    def __init__(self):
        self.scores = {}
        self.overlay_image = None
        
    def compare_char(self, ref_path, user_path, output_dir="output"):
        """
        교본과 사용자 글자를 비교하여 점수 산출
        
        Args:
            ref_path: 교본 이미지 경로
            user_path: 사용자 글자 이미지 경로
            output_dir: 결과 이미지 저장 디렉토리
        
        Returns:
            dict: 각 항목별 점수와 최종 점수
        """
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 이미지 로드
        ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
        user_img = cv2.imread(user_path, cv2.IMREAD_GRAYSCALE)
        
        if ref_img is None or user_img is None:
            raise ValueError("이미지를 로드할 수 없습니다.")
        
        # 2. 크기 맞추기
        user_img_resized = cv2.resize(user_img, (ref_img.shape[1], ref_img.shape[0]))
        
        # 3. 바이너리 마스크 생성 (적응형 임계값 사용)
        ref_mask = self._create_binary_mask(ref_img)
        user_mask = self._create_binary_mask(user_img_resized)
        
        # 4. 여백 비율 점수 계산
        margin_score = self._calculate_margin_score(ref_mask, user_mask)
        
        # 5. 획 기울기 점수 계산
        angle_score = self._calculate_angle_score(ref_mask, user_mask)
        
        # 6. 중심선 점수 계산
        center_score = self._calculate_center_score(ref_mask, user_mask)
        
        # 7. 형태 유사도 점수 계산
        similarity_score = self._calculate_similarity_score(ref_mask, user_mask)
        
        # 8. 최종 결구 점수 계산
        final_score = (margin_score + angle_score + center_score + similarity_score) / 4
        
        # 9. 오버레이 이미지 생성
        self.overlay_image = self._create_overlay(ref_mask, user_mask)
        
        # 10. 결과 저장
        self.scores = {
            "margin_score": margin_score,
            "angle_score": angle_score,
            "center_score": center_score,
            "similarity_score": similarity_score,
            "final_score": final_score
        }
        
        # 결과 이미지 저장
        overlay_path = os.path.join(output_dir, "overlay_result.png")
        cv2.imwrite(overlay_path, self.overlay_image)
        
        # 시각화
        self._visualize_results(ref_img, user_img_resized, ref_mask, user_mask, output_dir)
        
        return self.scores
    
    def _create_binary_mask(self, img):
        """바이너리 마스크 생성 (글자=255, 배경=0)"""
        # 적응형 임계값 처리
        mask = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 노이즈 제거
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def _calculate_margin_score(self, ref_mask, user_mask):
        """여백 비율 점수 계산"""
        ref_pixels = np.sum(ref_mask > 0)
        user_pixels = np.sum(user_mask > 0)
        
        if ref_pixels == 0:
            return 0
        
        # 픽셀 수 차이를 백분율로 계산
        diff_ratio = abs(ref_pixels - user_pixels) / ref_pixels
        score = max(0, 100 * (1 - diff_ratio))
        
        return round(score, 2)
    
    def _calculate_angle_score(self, ref_mask, user_mask):
        """획 기울기 점수 계산"""
        def get_dominant_angle(mask):
            # 엣지 검출
            edges = cv2.Canny(mask, 50, 150)
            
            # Hough 변환으로 직선 검출
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            if lines is None:
                return 0
            
            # 각도 추출 및 평균 계산
            angles = []
            for line in lines[:min(10, len(lines))]:  # 상위 10개 직선만 사용
                rho, theta = line[0]
                angle = np.degrees(theta)
                angles.append(angle)
            
            return np.mean(angles) if angles else 0
        
        ref_angle = get_dominant_angle(ref_mask)
        user_angle = get_dominant_angle(user_mask)
        
        # 각도 차이를 점수로 변환
        angle_diff = abs(ref_angle - user_angle)
        score = max(0, 100 - angle_diff * 2)  # 45도 차이 = 10점 감점
        
        return round(score, 2)
    
    def _calculate_center_score(self, ref_mask, user_mask):
        """중심선 점수 계산"""
        def get_center(mask):
            moments = cv2.moments(mask)
            if moments["m00"] == 0:
                return mask.shape[1] // 2, mask.shape[0] // 2
            
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            return cx, cy
        
        ref_cx, ref_cy = get_center(ref_mask)
        user_cx, user_cy = get_center(user_mask)
        
        # 중심점 거리 계산
        h, w = ref_mask.shape
        max_distance = np.sqrt(w**2 + h**2)
        actual_distance = np.sqrt((ref_cx - user_cx)**2 + (ref_cy - user_cy)**2)
        
        # 거리를 점수로 변환
        score = max(0, 100 * (1 - actual_distance / max_distance))
        
        return round(score, 2)
    
    def _calculate_similarity_score(self, ref_mask, user_mask):
        """형태 유사도 점수 계산 (템플릿 매칭)"""
        # 템플릿 매칭으로 유사도 계산
        result = cv2.matchTemplate(ref_mask, user_mask, cv2.TM_CCOEFF_NORMED)
        
        # 최대 유사도 값을 점수로 변환
        max_val = np.max(result)
        score = max(0, min(100, max_val * 100))
        
        return round(score, 2)
    
    def _create_overlay(self, ref_mask, user_mask):
        """오버레이 비교 이미지 생성"""
        # 3채널 이미지로 변환
        h, w = ref_mask.shape
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        
        # 교본: 빨간색, 사용자: 파란색, 겹침: 보라색
        overlay[:, :, 2] = ref_mask  # Red channel
        overlay[:, :, 0] = user_mask  # Blue channel
        
        return overlay
    
    def _visualize_results(self, ref_img, user_img, ref_mask, user_mask, output_dir):
        """결과 시각화 및 저장"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 원본 이미지
        axes[0, 0].imshow(ref_img, cmap='gray')
        axes[0, 0].set_title('교본')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(user_img, cmap='gray')
        axes[0, 1].set_title('작성본')
        axes[0, 1].axis('off')
        
        # 마스크
        axes[1, 0].imshow(ref_mask, cmap='gray')
        axes[1, 0].set_title('교본 마스크')
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(user_mask, cmap='gray')
        axes[1, 1].set_title('작성본 마스크')
        axes[1, 1].axis('off')
        
        # 오버레이
        axes[0, 2].imshow(self.overlay_image)
        axes[0, 2].set_title('오버레이 비교')
        axes[0, 2].axis('off')
        
        # 점수 표시
        score_text = f"""
        여백 비율 점수: {self.scores['margin_score']:.2f}
        획 기울기 점수: {self.scores['angle_score']:.2f}
        중심선 점수: {self.scores['center_score']:.2f}
        형태 유사도 점수: {self.scores['similarity_score']:.2f}
        
        최종 결구 점수: {self.scores['final_score']:.2f}
        """
        axes[1, 2].text(0.1, 0.5, score_text, fontsize=12, 
                       verticalalignment='center', fontfamily='monospace')
        axes[1, 2].axis('off')
        
        plt.suptitle('결구 점수 분석 결과', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 결과 저장
        result_path = os.path.join(output_dir, 'comparison_result.png')
        plt.savefig(result_path, dpi=100, bbox_inches='tight')
        plt.close()  # show() 대신 close() 사용
        
        print(f"\n결과 이미지 저장 완료:")
        print(f"  - 오버레이: {os.path.join(output_dir, 'overlay_result.png')}")
        print(f"  - 전체 결과: {result_path}")
    
    def print_scores(self):
        """점수 출력"""
        if not self.scores:
            print("아직 비교를 수행하지 않았습니다.")
            return
        
        print("\n" + "="*50)
        print("         결구 점수 분석 결과")
        print("="*50)
        print(f"여백 비율 점수:   {self.scores['margin_score']:6.2f}")
        print(f"획 기울기 점수:   {self.scores['angle_score']:6.2f}")
        print(f"중심선 점수:      {self.scores['center_score']:6.2f}")
        print(f"형태 유사도 점수: {self.scores['similarity_score']:6.2f}")
        print("-"*50)
        print(f"최종 결구 점수:   {self.scores['final_score']:6.2f}")
        print("="*50)


def main():
    """테스트 실행"""
    comparator = CharacterComparator()
    
    # 테스트용 이미지 경로 (실제 경로로 변경 필요)
    ref_path = "sample_images/reference.png"
    user_path = "sample_images/user_written.png"
    
    try:
        scores = comparator.compare_char(ref_path, user_path)
        comparator.print_scores()
    except Exception as e:
        print(f"오류 발생: {e}")
        print("\n샘플 이미지를 생성하여 테스트하겠습니다...")
        
        # 샘플 이미지 생성 및 테스트
        create_sample_images()
        scores = comparator.compare_char(
            "sample_images/reference.png",
            "sample_images/user_written.png"
        )
        comparator.print_scores()


def create_sample_images():
    """테스트용 샘플 이미지 생성"""
    import os
    os.makedirs("sample_images", exist_ok=True)
    
    # 빈 캔버스 생성
    canvas_ref = np.ones((200, 200), dtype=np.uint8) * 255
    canvas_user = np.ones((200, 200), dtype=np.uint8) * 255
    
    # 간단한 한글 모양 시뮬레이션 (ㅁ 모양)
    # 교본
    cv2.rectangle(canvas_ref, (50, 50), (150, 150), 0, 3)
    cv2.line(canvas_ref, (50, 100), (150, 100), 0, 2)
    cv2.line(canvas_ref, (100, 50), (100, 150), 0, 2)
    
    # 사용자 (약간 기울어지고 위치 이동)
    pts = np.array([[55, 45], [155, 55], [145, 155], [45, 145]], np.int32)
    cv2.polylines(canvas_user, [pts], True, 0, 3)
    cv2.line(canvas_user, (50, 95), (150, 105), 0, 2)
    cv2.line(canvas_user, (95, 50), (105, 150), 0, 2)
    
    cv2.imwrite("sample_images/reference.png", canvas_ref)
    cv2.imwrite("sample_images/user_written.png", canvas_user)
    print("샘플 이미지 생성 완료!")


if __name__ == "__main__":
    main()