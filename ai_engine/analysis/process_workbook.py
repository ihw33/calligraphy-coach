#!/usr/bin/env python3
"""
한글 서예 교본 이미지 처리 및 비교
교본과 작성본이 나란히 있는 이미지를 분리하여 비교
"""

import cv2
import numpy as np
from char_comparison import CharacterComparator
import os
import sys


def split_workbook_image(image_path):
    """
    교본 이미지를 왼쪽(교본)과 오른쪽(작성본)으로 분리
    
    Args:
        image_path: 전체 이미지 경로
    
    Returns:
        tuple: (교본 이미지, 작성본 이미지)
    """
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
    
    h, w = img.shape[:2]
    
    # 이미지를 반으로 나누기 (왼쪽: 교본, 오른쪽: 작성본)
    mid_x = w // 2
    
    # 왼쪽 절반 (교본)
    left_img = img[:, :mid_x]
    
    # 오른쪽 절반 (작성본)
    right_img = img[:, mid_x:]
    
    # 각 이미지에서 글자 영역만 크롭
    left_cropped = crop_character_area(left_img)
    right_cropped = crop_character_area(right_img)
    
    return left_cropped, right_cropped


def crop_character_area(img):
    """
    이미지에서 글자 영역만 자동으로 크롭
    
    Args:
        img: 입력 이미지
    
    Returns:
        크롭된 이미지
    """
    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 바이너리 이미지 생성 (글자 부분 찾기)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 컨투어 찾기
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return img
    
    # 모든 컨투어를 포함하는 바운딩 박스 찾기
    x_min, y_min = img.shape[1], img.shape[0]
    x_max, y_max = 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # 너무 작은 컨투어는 무시 (노이즈 제거)
        if w * h < 100:
            continue
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
    
    # 여백 추가 (글자가 잘리지 않도록)
    margin = 20
    x_min = max(0, x_min - margin)
    y_min = max(0, y_min - margin)
    x_max = min(img.shape[1], x_max + margin)
    y_max = min(img.shape[0], y_max + margin)
    
    # 크롭
    cropped = img[y_min:y_max, x_min:x_max]
    
    # 정사각형으로 만들기 (비교를 위해)
    h, w = cropped.shape[:2]
    if h != w:
        max_dim = max(h, w)
        # 새로운 정사각형 캔버스 생성
        square_img = np.ones((max_dim, max_dim, 3), dtype=np.uint8) * 255
        # 중앙에 배치
        y_offset = (max_dim - h) // 2
        x_offset = (max_dim - w) // 2
        square_img[y_offset:y_offset+h, x_offset:x_offset+w] = cropped
        return square_img
    
    return cropped


def process_workbook_images(image_paths, output_dir="workbook_output"):
    """
    여러 교본 이미지를 처리하고 비교
    
    Args:
        image_paths: 이미지 경로 리스트
        output_dir: 출력 디렉토리
    """
    os.makedirs(output_dir, exist_ok=True)
    
    comparator = CharacterComparator()
    all_scores = []
    
    for idx, image_path in enumerate(image_paths):
        print(f"\n{'='*60}")
        print(f"처리 중: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        try:
            # 이미지 분리
            ref_img, user_img = split_workbook_image(image_path)
            
            # 분리된 이미지 저장
            ref_path = os.path.join(output_dir, f"ref_{idx+1}.png")
            user_path = os.path.join(output_dir, f"user_{idx+1}.png")
            
            cv2.imwrite(ref_path, ref_img)
            cv2.imwrite(user_path, user_img)
            
            print(f"✅ 이미지 분리 완료:")
            print(f"   - 교본: {ref_path}")
            print(f"   - 작성본: {user_path}")
            
            # 비교 실행
            char_output_dir = os.path.join(output_dir, f"comparison_{idx+1}")
            scores = comparator.compare_char(ref_path, user_path, char_output_dir)
            
            # 점수 출력
            comparator.print_scores()
            
            # 점수 저장
            scores['image'] = os.path.basename(image_path)
            all_scores.append(scores)
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            continue
    
    # 전체 결과 요약
    if all_scores:
        print(f"\n{'='*60}")
        print("📊 전체 결과 요약")
        print(f"{'='*60}")
        
        for score_data in all_scores:
            print(f"\n{score_data['image']}:")
            print(f"  - 최종 점수: {score_data['final_score']:.2f}")
        
        # 평균 점수
        avg_score = sum(s['final_score'] for s in all_scores) / len(all_scores)
        print(f"\n📈 전체 평균 점수: {avg_score:.2f}")
        
        # 결과 저장
        import json
        result_file = os.path.join(output_dir, "all_scores.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(all_scores, f, ensure_ascii=False, indent=2)
        print(f"\n💾 결과 저장: {result_file}")


def main():
    """메인 실행 함수"""
    # Downloads 폴더의 이미지들
    image_files = [
        "/Users/m4_macbook/Downloads/IMG_2272.png",
        "/Users/m4_macbook/Downloads/IMG_2273.png",
        "/Users/m4_macbook/Downloads/IMG_2274.png",
        "/Users/m4_macbook/Downloads/IMG_2275.png"
    ]
    
    # 존재하는 파일만 필터링
    existing_files = [f for f in image_files if os.path.exists(f)]
    
    if not existing_files:
        print("처리할 이미지 파일이 없습니다.")
        return
    
    print(f"🎯 {len(existing_files)}개의 이미지를 처리합니다.")
    
    # 처리 실행
    process_workbook_images(existing_files)


if __name__ == "__main__":
    main()