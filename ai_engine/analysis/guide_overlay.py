#!/usr/bin/env python3
"""
결구 가이드라인과 사용자 글자 오버레이 비교 시스템
교본의 결구 가이드(왼쪽 아래)와 사용자가 쓴 글자(오른쪽)를 오버레이하여 점수 산출
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class GuideOverlayComparator:
    """결구 가이드라인 기반 글자 비교 클래스"""
    
    def __init__(self):
        self.scores = {}
        
    def process_workbook(self, image_path, char_name):
        """
        교본 이미지 처리 및 비교
        
        Args:
            image_path: 전체 이미지 경로
            char_name: 글자 이름 (中, 水, 火, 本)
        """
        # 이미지 로드
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
        
        h, w = img.shape[:2]
        
        # 이미지 영역 분할 (대략적인 좌표)
        # 왼쪽 위: 교본 글자 (참고용)
        # 왼쪽 아래: 결구 가이드
        # 오른쪽: 사용자가 쓴 글자
        
        mid_x = w // 2
        mid_y = h // 2
        
        # 왼쪽 아래 결구 가이드 추출 (빨간 선이 있는 부분)
        guide_img = img[mid_y:h-50, 50:mid_x-20]
        
        # 오른쪽 사용자 글자 추출
        user_img = img[80:mid_y+100, mid_x+50:w-50]
        
        # 출력 디렉토리
        output_dir = f"guide_output/{char_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 추출된 이미지 저장
        guide_path = os.path.join(output_dir, "guide.png")
        user_path = os.path.join(output_dir, "user.png")
        
        cv2.imwrite(guide_path, guide_img)
        cv2.imwrite(user_path, user_img)
        
        # 크기 맞추기 (가이드 크기에 맞춤)
        user_resized = cv2.resize(user_img, (guide_img.shape[1], guide_img.shape[0]))
        
        # 그레이스케일 변환
        guide_gray = cv2.cvtColor(guide_img, cv2.COLOR_BGR2GRAY)
        user_gray = cv2.cvtColor(user_resized, cv2.COLOR_BGR2GRAY)
        
        # 이진화 처리
        _, guide_binary = cv2.threshold(guide_gray, 127, 255, cv2.THRESH_BINARY_INV)
        _, user_binary = cv2.threshold(user_gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # 가이드라인 추출 (빨간색 선)
        guide_hsv = cv2.cvtColor(guide_img, cv2.COLOR_BGR2HSV)
        
        # 빨간색 범위 정의
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # 빨간색 마스크 생성
        mask1 = cv2.inRange(guide_hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(guide_hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # 오버레이 이미지 생성
        overlay = self.create_overlay(guide_img, user_resized, user_binary)
        
        # 점수 계산
        scores = self.calculate_scores(guide_binary, user_binary, red_mask)
        
        # 결과 시각화
        self.visualize_results(
            guide_img, user_resized, overlay, 
            scores, output_dir, char_name
        )
        
        return scores
    
    def create_overlay(self, guide_img, user_img, user_mask):
        """
        가이드와 사용자 글자 오버레이 생성
        
        Args:
            guide_img: 가이드 이미지 (컬러)
            user_img: 사용자 글자 이미지 (리사이즈됨)
            user_mask: 사용자 글자 마스크
        """
        # 오버레이 베이스는 가이드 이미지
        overlay = guide_img.copy()
        
        # 사용자 글자를 반투명 파란색으로 오버레이
        blue_overlay = np.zeros_like(overlay)
        blue_overlay[:, :, 0] = user_mask  # Blue channel
        
        # 알파 블렌딩
        alpha = 0.4
        overlay = cv2.addWeighted(overlay, 1-alpha, blue_overlay, alpha, 0)
        
        return overlay
    
    def calculate_scores(self, guide_binary, user_binary, red_mask):
        """
        가이드라인 기준 점수 계산
        
        Args:
            guide_binary: 가이드 이진 이미지
            user_binary: 사용자 글자 이진 이미지
            red_mask: 빨간 가이드라인 마스크
        """
        scores = {}
        
        # 1. 가이드라인 준수도 (빨간 선 내부에 글자가 있는지)
        # 빨간 선으로 둘러싸인 영역 찾기
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 가장 큰 컨투어를 가이드 영역으로 간주
            largest_contour = max(contours, key=cv2.contourArea)
            guide_area = np.zeros_like(red_mask)
            cv2.drawContours(guide_area, [largest_contour], -1, 255, -1)
            
            # 가이드 영역 내 글자 비율
            inside_guide = cv2.bitwise_and(user_binary, guide_area)
            guide_score = (np.sum(inside_guide > 0) / max(1, np.sum(user_binary > 0))) * 100
        else:
            guide_score = 50  # 가이드라인이 없으면 기본 점수
        
        scores['guide_adherence'] = min(100, guide_score)
        
        # 2. 중심 정렬도
        # 무게중심 계산
        M_guide = cv2.moments(guide_binary)
        M_user = cv2.moments(user_binary)
        
        if M_guide["m00"] > 0 and M_user["m00"] > 0:
            cx_guide = int(M_guide["m10"] / M_guide["m00"])
            cy_guide = int(M_guide["m01"] / M_guide["m00"])
            cx_user = int(M_user["m10"] / M_user["m00"])
            cy_user = int(M_user["m01"] / M_user["m00"])
            
            # 중심 거리
            h, w = guide_binary.shape
            max_dist = np.sqrt(w**2 + h**2)
            actual_dist = np.sqrt((cx_guide - cx_user)**2 + (cy_guide - cy_user)**2)
            center_score = max(0, 100 * (1 - actual_dist / max_dist))
        else:
            center_score = 0
        
        scores['center_alignment'] = center_score
        
        # 3. 크기 비율
        guide_pixels = np.sum(guide_binary > 0)
        user_pixels = np.sum(user_binary > 0)
        
        if guide_pixels > 0:
            size_ratio = min(guide_pixels, user_pixels) / max(guide_pixels, user_pixels)
            size_score = size_ratio * 100
        else:
            size_score = 0
        
        scores['size_match'] = size_score
        
        # 4. 형태 유사도 (IoU)
        intersection = np.sum(np.logical_and(guide_binary > 0, user_binary > 0))
        union = np.sum(np.logical_or(guide_binary > 0, user_binary > 0))
        
        if union > 0:
            iou_score = (intersection / union) * 100
        else:
            iou_score = 0
        
        scores['shape_similarity'] = iou_score
        
        # 최종 점수
        scores['final_score'] = np.mean([
            scores['guide_adherence'],
            scores['center_alignment'],
            scores['size_match'],
            scores['shape_similarity']
        ])
        
        return scores
    
    def visualize_results(self, guide_img, user_img, overlay, scores, output_dir, char_name):
        """결과 시각화 및 저장"""
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 가이드 이미지
        axes[0, 0].imshow(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title(f'결구 가이드 ({char_name})')
        axes[0, 0].axis('off')
        
        # 사용자 글자
        axes[0, 1].imshow(cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB))
        axes[0, 1].set_title('작성한 글자')
        axes[0, 1].axis('off')
        
        # 오버레이
        axes[0, 2].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        axes[0, 2].set_title('오버레이 비교')
        axes[0, 2].axis('off')
        
        # 점수 막대 그래프
        score_names = ['가이드\n준수도', '중심\n정렬', '크기\n일치', '형태\n유사도']
        score_values = [
            scores['guide_adherence'],
            scores['center_alignment'],
            scores['size_match'],
            scores['shape_similarity']
        ]
        
        bars = axes[1, 0].bar(score_names, score_values, color=['red', 'blue', 'green', 'orange'])
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].set_ylabel('점수')
        axes[1, 0].set_title('항목별 점수')
        
        # 막대 위에 점수 표시
        for bar, value in zip(bars, score_values):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                          f'{value:.1f}', ha='center', va='bottom')
        
        # 점수 요약
        score_text = f"""
        {char_name} 글자 분석 결과
        
        가이드라인 준수도: {scores['guide_adherence']:.1f}점
        중심 정렬도: {scores['center_alignment']:.1f}점
        크기 일치도: {scores['size_match']:.1f}점
        형태 유사도: {scores['shape_similarity']:.1f}점
        
        ━━━━━━━━━━━━━━━━━━
        최종 점수: {scores['final_score']:.1f}점
        """
        
        axes[1, 1].text(0.1, 0.5, score_text, fontsize=12,
                       verticalalignment='center', fontfamily='monospace')
        axes[1, 1].axis('off')
        
        # 평가 메시지
        final_score = scores['final_score']
        if final_score >= 90:
            message = "🏆 훌륭합니다!"
        elif final_score >= 80:
            message = "😊 잘했습니다!"
        elif final_score >= 70:
            message = "👍 좋습니다!"
        elif final_score >= 60:
            message = "💪 조금 더 노력하세요!"
        else:
            message = "📝 더 연습이 필요합니다!"
        
        axes[1, 2].text(0.5, 0.5, message, fontsize=20, 
                       ha='center', va='center', fontweight='bold')
        axes[1, 2].axis('off')
        
        plt.suptitle(f'{char_name} 글자 결구 분석', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 저장
        result_path = os.path.join(output_dir, 'analysis_result.png')
        plt.savefig(result_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        # 오버레이 이미지도 별도 저장
        overlay_path = os.path.join(output_dir, 'overlay.png')
        cv2.imwrite(overlay_path, overlay)
        
        print(f"✅ 결과 저장 완료:")
        print(f"   - 분석 결과: {result_path}")
        print(f"   - 오버레이: {overlay_path}")


def main():
    """메인 실행 함수"""
    
    # 이미지와 글자 매핑
    image_configs = [
        {"path": "/Users/m4_macbook/Downloads/IMG_2272.png", "char": "中"},
        {"path": "/Users/m4_macbook/Downloads/IMG_2273.png", "char": "水"},
        {"path": "/Users/m4_macbook/Downloads/IMG_2274.png", "char": "火"},
        {"path": "/Users/m4_macbook/Downloads/IMG_2275.png", "char": "本"},
    ]
    
    comparator = GuideOverlayComparator()
    all_scores = []
    
    for config in image_configs:
        if not os.path.exists(config["path"]):
            print(f"파일을 찾을 수 없습니다: {config['path']}")
            continue
        
        print(f"\n{'='*60}")
        print(f"처리 중: {config['char']} 글자")
        print(f"{'='*60}")
        
        try:
            scores = comparator.process_workbook(config["path"], config["char"])
            scores['character'] = config["char"]
            all_scores.append(scores)
            
            # 점수 출력
            print(f"\n📊 {config['char']} 글자 점수:")
            print(f"   가이드라인 준수도: {scores['guide_adherence']:.1f}점")
            print(f"   중심 정렬도: {scores['center_alignment']:.1f}점")
            print(f"   크기 일치도: {scores['size_match']:.1f}점")
            print(f"   형태 유사도: {scores['shape_similarity']:.1f}점")
            print(f"   최종 점수: {scores['final_score']:.1f}점")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            continue
    
    # 전체 요약
    if all_scores:
        print(f"\n{'='*60}")
        print("📈 전체 결과 요약")
        print(f"{'='*60}")
        
        total_final = sum(s['final_score'] for s in all_scores)
        avg_score = total_final / len(all_scores)
        
        for score_data in all_scores:
            print(f"{score_data['character']}: {score_data['final_score']:.1f}점")
        
        print(f"\n전체 평균: {avg_score:.1f}점")
        
        if avg_score >= 80:
            print("🎉 전체적으로 매우 우수합니다!")
        elif avg_score >= 70:
            print("👏 전체적으로 잘 쓰셨습니다!")
        elif avg_score >= 60:
            print("💡 조금 더 연습하면 좋겠습니다!")
        else:
            print("📚 꾸준한 연습이 필요합니다!")


if __name__ == "__main__":
    main()