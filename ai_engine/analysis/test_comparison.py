#!/usr/bin/env python3
"""
결구 점수 시연 테스트 스크립트
실제 이미지 파일로 테스트
"""

from char_comparison import CharacterComparator
import sys
import os


def test_with_images(ref_path, user_path):
    """실제 이미지로 테스트"""
    print(f"\n교본 이미지: {ref_path}")
    print(f"작성본 이미지: {user_path}")
    print("-" * 50)
    
    comparator = CharacterComparator()
    
    try:
        # 비교 실행
        scores = comparator.compare_char(ref_path, user_path, output_dir="output")
        
        # 결과 출력
        comparator.print_scores()
        
        print(f"\n비교 이미지가 'output/overlay_result.png'에 저장되었습니다.")
        
        return scores
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def main():
    """메인 실행 함수"""
    # 명령행 인자 확인
    if len(sys.argv) == 3:
        ref_path = sys.argv[1]
        user_path = sys.argv[2]
    else:
        # 기본 테스트 이미지 경로
        print("사용법: python test_comparison.py <교본_이미지> <작성본_이미지>")
        print("\n기본 샘플 이미지로 테스트합니다...")
        
        # 샘플 이미지 생성
        from char_comparison import create_sample_images
        create_sample_images()
        
        ref_path = "sample_images/reference.png"
        user_path = "sample_images/user_written.png"
    
    # 파일 존재 확인
    if not os.path.exists(ref_path):
        print(f"교본 이미지를 찾을 수 없습니다: {ref_path}")
        return
    
    if not os.path.exists(user_path):
        print(f"작성본 이미지를 찾을 수 없습니다: {user_path}")
        return
    
    # 테스트 실행
    scores = test_with_images(ref_path, user_path)
    
    if scores:
        print("\n" + "="*50)
        print("테스트 완료!")
        print("="*50)


if __name__ == "__main__":
    main()