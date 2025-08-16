#!/usr/bin/env python3
"""
수동으로 지정한 좌표로 한글 글자 영역만 크롭하여 비교
"""

import cv2
import numpy as np
from char_comparison import CharacterComparator
import os


def crop_and_compare(image_path, ref_coords, user_coords, output_name):
    """
    이미지에서 지정된 좌표로 크롭하여 비교
    
    Args:
        image_path: 원본 이미지 경로
        ref_coords: 교본 영역 좌표 (x1, y1, x2, y2)
        user_coords: 작성본 영역 좌표 (x1, y1, x2, y2)
        output_name: 출력 파일 이름 (확장자 제외)
    """
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 로드할 수 없습니다: {image_path}")
        return
    
    # 교본 영역 크롭
    ref_x1, ref_y1, ref_x2, ref_y2 = ref_coords
    ref_img = img[ref_y1:ref_y2, ref_x1:ref_x2]
    
    # 작성본 영역 크롭
    user_x1, user_y1, user_x2, user_y2 = user_coords
    user_img = img[user_y1:user_y2, user_x1:user_x2]
    
    # 출력 디렉토리 생성
    output_dir = "manual_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 크롭된 이미지 저장
    ref_path = os.path.join(output_dir, f"{output_name}_ref.png")
    user_path = os.path.join(output_dir, f"{output_name}_user.png")
    
    cv2.imwrite(ref_path, ref_img)
    cv2.imwrite(user_path, user_img)
    
    print(f"\n{'='*60}")
    print(f"처리 중: {output_name}")
    print(f"{'='*60}")
    print(f"✅ 이미지 크롭 완료:")
    print(f"   - 교본: {ref_path}")
    print(f"   - 작성본: {user_path}")
    
    # 비교 실행
    comparator = CharacterComparator()
    comparison_dir = os.path.join(output_dir, f"{output_name}_comparison")
    scores = comparator.compare_char(ref_path, user_path, comparison_dir)
    
    # 점수 출력
    comparator.print_scores()
    
    return scores


def main():
    """메인 실행 함수"""
    
    # 각 이미지별 좌표 (수동으로 측정한 값)
    # 이미지를 보고 대략적인 좌표를 지정합니다
    
    image_configs = [
        {
            "path": "/Users/m4_macbook/Downloads/IMG_2272.png",
            "name": "中",
            # 왼쪽 박스 (교본): 대략 50,80 ~ 380,410
            "ref_coords": (50, 80, 380, 410),
            # 오른쪽 박스 (작성본): 대략 420,80 ~ 750,410
            "user_coords": (420, 80, 750, 410)
        },
        {
            "path": "/Users/m4_macbook/Downloads/IMG_2273.png",
            "name": "水",
            "ref_coords": (50, 60, 380, 390),
            "user_coords": (420, 60, 750, 390)
        },
        {
            "path": "/Users/m4_macbook/Downloads/IMG_2274.png",
            "name": "火",
            "ref_coords": (50, 60, 380, 390),
            "user_coords": (420, 60, 750, 390)
        },
        {
            "path": "/Users/m4_macbook/Downloads/IMG_2275.png",
            "name": "本",
            "ref_coords": (50, 60, 380, 390),
            "user_coords": (420, 60, 750, 390)
        }
    ]
    
    all_scores = []
    
    for config in image_configs:
        if os.path.exists(config["path"]):
            scores = crop_and_compare(
                config["path"],
                config["ref_coords"],
                config["user_coords"],
                config["name"]
            )
            if scores:
                scores['character'] = config["name"]
                all_scores.append(scores)
        else:
            print(f"파일을 찾을 수 없습니다: {config['path']}")
    
    # 전체 결과 요약
    if all_scores:
        print(f"\n{'='*60}")
        print("📊 전체 결과 요약")
        print(f"{'='*60}")
        
        for score_data in all_scores:
            print(f"\n{score_data['character']} 글자:")
            print(f"  - 여백 비율: {score_data['margin_score']:.1f}")
            print(f"  - 획 기울기: {score_data['angle_score']:.1f}")
            print(f"  - 중심선: {score_data['center_score']:.1f}")
            print(f"  - 형태 유사도: {score_data['similarity_score']:.1f}")
            print(f"  - 최종 점수: {score_data['final_score']:.1f}")
        
        # 평균 점수
        avg_score = sum(s['final_score'] for s in all_scores) / len(all_scores)
        print(f"\n📈 전체 평균 점수: {avg_score:.2f}")


if __name__ == "__main__":
    main()