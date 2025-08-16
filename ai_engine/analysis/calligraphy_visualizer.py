#!/usr/bin/env python3
"""
서예 분석 시각화 시스템
한자 작성 분석 결과를 시각적으로 표현
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager, rc
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트 설정"""
    try:
        font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttc'
        if not os.path.exists(font_path):
            font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
        return font_path
    except:
        print("한글 폰트 설정 실패")
        return None

class CalligraphyVisualizer:
    def __init__(self):
        self.font_path = setup_korean_font()
        self.colors = {
            'excellent': '#10B981',  # 녹색
            'good': '#F59E0B',       # 노란색
            'poor': '#EF4444',       # 빨간색
            'reference': '#1F2937',   # 검정
            'user': '#3B82F6'        # 파란색
        }
        
    def create_overlay_comparison(self, reference_img, user_img, output_path):
        """오버레이 비교 이미지 생성"""
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        
        # 1. 교본
        axes[0].imshow(reference_img, cmap='gray')
        axes[0].set_title('교본', fontsize=14, fontweight='bold')
        axes[0].axis('off')
        
        # 2. 작성한 글자
        axes[1].imshow(user_img, cmap='gray')
        axes[1].set_title('작성한 글자', fontsize=14, fontweight='bold')
        axes[1].axis('off')
        
        # 3. 오버레이 (반투명)
        overlay = np.zeros((*reference_img.shape, 3))
        overlay[:,:,0] = reference_img / 255.0  # R channel
        overlay[:,:,2] = user_img / 255.0       # B channel
        axes[2].imshow(overlay)
        axes[2].set_title('오버레이 비교', fontsize=14, fontweight='bold')
        axes[2].axis('off')
        
        # 4. 차이점 하이라이트
        diff = cv2.absdiff(reference_img, user_img)
        diff_colored = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
        axes[3].imshow(cv2.cvtColor(diff_colored, cv2.COLOR_BGR2RGB))
        axes[3].set_title('차이점 히트맵', fontsize=14, fontweight='bold')
        axes[3].axis('off')
        
        plt.suptitle('한자 "中" 비교 분석', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_heatmap_analysis(self, scores_dict, output_path):
        """구역별 점수 히트맵 생성"""
        # 3x3 그리드로 점수 매핑
        grid_scores = np.array([
            [60, 30, 60],  # 상단
            [99, 99, 99],  # 중앙  
            [40, 30, 40]   # 하단
        ])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 히트맵
        sns.heatmap(grid_scores, annot=True, fmt='d', cmap='RdYlGn', 
                   vmin=0, vmax=100, cbar_kws={'label': '정확도 (%)'},
                   xticklabels=['좌', '중', '우'],
                   yticklabels=['상', '중', '하'],
                   ax=ax1, square=True, linewidths=2, linecolor='white')
        ax1.set_title('구역별 정확도 히트맵', fontsize=14, fontweight='bold')
        
        # 막대 그래프
        categories = ['가이드\n준수', '중심\n정렬', '크기\n일치', '균형도', '형태\n유사도']
        values = [12, 99, 25, 78, 54]
        colors_list = ['#EF4444', '#10B981', '#EF4444', '#F59E0B', '#F59E0B']
        
        bars = ax2.bar(categories, values, color=colors_list, edgecolor='black', linewidth=2)
        ax2.set_ylim(0, 100)
        ax2.set_ylabel('점수 (%)', fontsize=12)
        ax2.set_title('항목별 점수 분석', fontsize=14, fontweight='bold')
        
        # 점수 표시
        for bar, val in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val}%', ha='center', fontweight='bold')
        
        # 기준선 추가
        ax2.axhline(y=70, color='gray', linestyle='--', alpha=0.5, label='목표 기준선')
        ax2.legend()
        
        plt.suptitle('한자 "中" 구역별 분석', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_stroke_vector_analysis(self, img_shape, output_path):
        """획 방향 벡터 분석 시각화"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 배경 그리드
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # 중심선 (세로)
        ax.arrow(50, 90, 0, -70, head_width=3, head_length=3, 
                fc='blue', ec='blue', linewidth=3, label='세로획 (87°)')
        ax.text(55, 50, '87°\n(목표: 90°)', fontsize=10, color='blue')
        
        # 상단 가로선
        ax.arrow(20, 70, 60, 0, head_width=3, head_length=3,
                fc='red', ec='red', linewidth=2, label='가로획 상 (3°)')
        ax.text(50, 75, '3° 기울어짐', fontsize=10, color='red')
        
        # 하단 가로선  
        ax.arrow(25, 30, 50, 0, head_width=3, head_length=3,
                fc='orange', ec='orange', linewidth=2, label='가로획 하 (2°)')
        ax.text(50, 25, '2° 기울어짐\n길이 부족', fontsize=10, color='orange')
        
        # 외곽 사각형
        rect = mpatches.Rectangle((15, 15), 70, 70, fill=False, 
                                 edgecolor='green', linewidth=2, 
                                 linestyle='--', label='외곽선')
        ax.add_patch(rect)
        
        # 이상적인 형태 (회색 점선)
        ax.plot([50, 50], [10, 90], 'k--', alpha=0.3, linewidth=1)
        ax.plot([10, 90], [70, 70], 'k--', alpha=0.3, linewidth=1)
        ax.plot([10, 90], [30, 30], 'k--', alpha=0.3, linewidth=1)
        
        ax.set_title('획 방향 및 각도 분석', fontsize=14, fontweight='bold')
        ax.set_xlabel('X 좌표', fontsize=12)
        ax.set_ylabel('Y 좌표', fontsize=12)
        ax.legend(loc='upper right')
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_comprehensive_report(self, output_path):
        """종합 리포트 이미지 생성"""
        fig = plt.figure(figsize=(16, 20))
        
        # 메인 타이틀
        fig.suptitle('한자 "中" 서예 분석 종합 리포트', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. 종합 점수 (크게 표시)
        ax1 = plt.subplot2grid((5, 3), (0, 0), colspan=3)
        ax1.axis('off')
        
        # 등급 원
        circle = plt.Circle((0.5, 0.5), 0.3, color='#FEE2E2', alpha=0.5)
        ax1.add_patch(circle)
        ax1.text(0.5, 0.5, 'D', fontsize=80, ha='center', va='center', 
                color='#EF4444', fontweight='bold')
        ax1.text(0.5, 0.15, '종합 점수: 53.5점', fontsize=20, ha='center')
        
        # 2. 획별 분석
        ax2 = plt.subplot2grid((5, 3), (1, 0), colspan=3)
        strokes = ['1획\n(세로)', '2획\n(가로상)', '3획\n(가로하)', '4획\n(외곽)']
        accuracies = [55, 52, 47, 64]
        colors = ['#F59E0B', '#F59E0B', '#EF4444', '#F59E0B']
        
        bars = ax2.bar(strokes, accuracies, color=colors, edgecolor='black', linewidth=2)
        ax2.set_ylabel('정확도 (%)', fontsize=12)
        ax2.set_title('획별 정확도 분석', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 100)
        
        for bar, val in zip(bars, accuracies):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val}%', ha='center', fontweight='bold')
        
        # 3. 문제점 리스트
        ax3 = plt.subplot2grid((5, 3), (2, 0), colspan=3)
        ax3.axis('off')
        
        problems = [
            "⚠️ 가로획 수평 맞추기 필요 (2-3° 기울어짐)",
            "⚠️ 좌우 대칭 개선 필요 (좌측 20% 치우침)",
            "⚠️ 상단 가로선 길이 15% 부족",
            "⚠️ 가이드라인 준수율 12% (매우 낮음)"
        ]
        
        for i, problem in enumerate(problems):
            ax3.text(0.05, 0.8 - i*0.2, problem, fontsize=12, 
                    transform=ax3.transAxes, color='#DC2626')
        
        ax3.set_title('주요 개선사항', fontsize=14, fontweight='bold', loc='left')
        
        # 4. 개선 가이드
        ax4 = plt.subplot2grid((5, 3), (3, 0), colspan=3)
        ax4.axis('off')
        
        guides = [
            "✅ 1단계: 세로선만 반복 연습 (50회)",
            "✅ 2단계: 가로선만 반복 연습 (50회)",
            "✅ 3단계: 교차 연습 (30회)",
            "✅ 4단계: 전체 글자 연습 (20회)"
        ]
        
        for i, guide in enumerate(guides):
            ax4.text(0.05, 0.8 - i*0.2, guide, fontsize=12,
                    transform=ax4.transAxes, color='#059669')
        
        ax4.set_title('연습 가이드', fontsize=14, fontweight='bold', loc='left')
        
        # 5. 목표
        ax5 = plt.subplot2grid((5, 3), (4, 0), colspan=3)
        ax5.axis('off')
        
        target_text = """
        🎯 다음 목표: C등급 (70점 이상)
        • 가이드 준수율 30% 이상 달성
        • 형태 유사도 70% 이상 달성
        • 모든 획 각도 오차 ±2° 이내
        """
        
        ax5.text(0.5, 0.5, target_text, fontsize=13, ha='center', va='center',
                transform=ax5.transAxes, bbox=dict(boxstyle="round,pad=0.5", 
                facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=2))
        
        # 타임스탬프
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.5, 0.02, f'생성 시각: {timestamp}', ha='center', fontsize=10, color='gray')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_progress_tracking(self, history_scores, output_path):
        """진도 추적 그래프 생성"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 시간별 점수 변화
        sessions = ['1회', '2회', '3회', '4회', '5회(현재)']
        scores = [42, 48, 51, 49, 53.5]
        
        ax1.plot(sessions, scores, marker='o', markersize=10, linewidth=3, color='#3B82F6')
        ax1.fill_between(range(len(sessions)), scores, alpha=0.3, color='#3B82F6')
        ax1.set_ylim(0, 100)
        ax1.set_ylabel('점수', fontsize=12)
        ax1.set_title('학습 진도 추적', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 목표선
        ax1.axhline(y=70, color='green', linestyle='--', linewidth=2, label='목표(C등급)')
        ax1.axhline(y=85, color='gold', linestyle='--', linewidth=2, label='목표(B등급)')
        ax1.legend()
        
        # 항목별 개선도
        categories = ['가이드', '중심', '크기', '균형', '형태']
        first_attempt = [8, 85, 15, 65, 40]
        current_attempt = [12, 99, 25, 78, 54]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, first_attempt, width, label='첫 시도', color='#94A3B8')
        bars2 = ax2.bar(x + width/2, current_attempt, width, label='현재', color='#3B82F6')
        
        ax2.set_ylabel('점수 (%)', fontsize=12)
        ax2.set_title('항목별 개선도', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories)
        ax2.legend()
        ax2.set_ylim(0, 100)
        
        # 개선도 표시
        for i in range(len(categories)):
            improvement = current_attempt[i] - first_attempt[i]
            if improvement > 0:
                ax2.annotate(f'+{improvement}%', 
                           xy=(i, current_attempt[i]), 
                           xytext=(i, current_attempt[i] + 3),
                           ha='center', fontweight='bold', color='green')
        
        plt.suptitle('학습 진도 및 개선도 분석', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path

def main():
    """메인 실행 함수"""
    print("🎨 서예 분석 시각화 시스템 시작...")
    
    # 시각화 객체 생성
    visualizer = CalligraphyVisualizer()
    
    # 더미 이미지 생성 (실제로는 입력 이미지 사용)
    reference_img = np.ones((300, 300), dtype=np.uint8) * 255
    cv2.rectangle(reference_img, (50, 50), (250, 250), 0, 2)
    cv2.line(reference_img, (150, 50), (150, 250), 0, 2)
    cv2.line(reference_img, (50, 120), (250, 120), 0, 2)
    cv2.line(reference_img, (50, 180), (250, 180), 0, 2)
    
    user_img = np.ones((300, 300), dtype=np.uint8) * 255
    cv2.rectangle(user_img, (45, 55), (245, 255), 0, 2)
    cv2.line(user_img, (145, 55), (148, 255), 0, 2)
    cv2.line(user_img, (45, 125), (245, 128), 0, 2)
    cv2.line(user_img, (50, 185), (240, 183), 0, 2)
    
    # 출력 디렉토리 생성
    output_dir = "/Users/m4_macbook/char-comparison-system/visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 오버레이 비교
    print("📊 오버레이 비교 이미지 생성 중...")
    overlay_path = os.path.join(output_dir, "overlay_comparison.png")
    visualizer.create_overlay_comparison(reference_img, user_img, overlay_path)
    print(f"   ✅ 저장됨: {overlay_path}")
    
    # 2. 히트맵 분석
    print("🔥 히트맵 분석 이미지 생성 중...")
    heatmap_path = os.path.join(output_dir, "heatmap_analysis.png")
    scores = {'guide': 12, 'center': 99, 'size': 25, 'balance': 78, 'shape': 54}
    visualizer.create_heatmap_analysis(scores, heatmap_path)
    print(f"   ✅ 저장됨: {heatmap_path}")
    
    # 3. 벡터 분석
    print("➡️ 획 방향 벡터 분석 생성 중...")
    vector_path = os.path.join(output_dir, "vector_analysis.png")
    visualizer.create_stroke_vector_analysis((300, 300), vector_path)
    print(f"   ✅ 저장됨: {vector_path}")
    
    # 4. 종합 리포트
    print("📋 종합 리포트 생성 중...")
    report_path = os.path.join(output_dir, "comprehensive_report.png")
    visualizer.create_comprehensive_report(report_path)
    print(f"   ✅ 저장됨: {report_path}")
    
    # 5. 진도 추적
    print("📈 진도 추적 그래프 생성 중...")
    progress_path = os.path.join(output_dir, "progress_tracking.png")
    visualizer.create_progress_tracking([42, 48, 51, 49, 53.5], progress_path)
    print(f"   ✅ 저장됨: {progress_path}")
    
    print("\n✨ 모든 시각화 완료!")
    print(f"📁 결과 저장 위치: {output_dir}")
    
    return {
        'overlay': overlay_path,
        'heatmap': heatmap_path,
        'vector': vector_path,
        'report': report_path,
        'progress': progress_path
    }

if __name__ == "__main__":
    results = main()
    print("\n🎯 생성된 파일 목록:")
    for name, path in results.items():
        print(f"  - {name}: {path}")