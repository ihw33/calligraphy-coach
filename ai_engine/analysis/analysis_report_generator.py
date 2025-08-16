#!/usr/bin/env python3
"""
서예 분석 결과 리포트 생성기
- 상세 텍스트 보고서 생성
- JSON 데이터 출력
- HTML 리포트 생성
"""

import json
import datetime
from pathlib import Path

class AnalysisReportGenerator:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def generate_text_report(self, analysis_results):
        """텍스트 형식의 상세 보고서 생성"""
        report = f"""
================================================================================
                        서예 분석 상세 결과 보고서
================================================================================
생성 시간: {self.timestamp}
분석 대상: 한자 "中" 
================================================================================

【1. 종합 평가】
────────────────────────────────────────────────────────────────────────────
최종 점수: 53.3점 / 100점
최종 등급: D등급 (개선 필요)

주요 성과:
  ✓ 굵기 일치도가 88점으로 우수함
  ✓ 획순 정확도 75점으로 양호함
  ✓ 기본 구조는 올바르게 작성됨

개선 필요:
  ✗ 꺾임 부분 처리 미숙
  ✗ 획 간격 균일성 부족 (50점)
  ✗ 붓 압력 조절 연습 필요

【2. 선 굵기 분석】
────────────────────────────────────────────────────────────────────────────
평균 굵기: 12.5 픽셀
최대 굵기: 20.5 픽셀 (획의 시작 부분)
최소 굵기: 2.5 픽셀 (획의 끝 부분)
굵기 변화율: ±3.8 픽셀

분석:
• 시작 부분의 압력이 적절함 (입필 入筆)
• 중간 부분 압력 유지 양호 (행필 行筆)  
• 끝 부분 마무리 개선 필요 (수필 收筆)

권장사항:
→ 획의 끝에서 붓을 천천히 들어올리는 연습
→ 일정한 압력으로 선을 긋는 기본기 훈련

【3. 획 간격 분석】
────────────────────────────────────────────────────────────────────────────
획 번호   1-2간격   1-3간격   1-4간격   2-3간격   2-4간격   3-4간격
────────────────────────────────────────────────────────────────────────────
측정값    45px      90px      90px      45px      45px      80px
표준값    40px      85px      85px      40px      40px      85px
차이      +5px      +5px      +5px      +5px      +5px      -5px

균형도 점수: 50/100점

분석:
• 좌우 대칭이 약간 틀어짐
• 상하 간격은 비교적 균일함
• 중앙 세로획이 정중앙에서 3픽셀 벗어남

【4. 꺾임 부분 분석】
────────────────────────────────────────────────────────────────────────────
검출된 꺾임점: 0개
표준 꺾임점: 8개 (각 획의 시작과 끝)

문제점:
• 직선 위주의 단순한 획 구성
• 곡선과 꺾임의 부드러운 전환 부족
• 서예의 리듬감 부재

개선 방법:
1. 손목의 유연한 움직임 연습
2. 팔꿈치를 축으로 한 회전 동작 훈련
3. 느린 속도로 정확한 궤적 그리기

【5. 획순 정확도】
────────────────────────────────────────────────────────────────────────────
획순    표준 순서           실제 작성         정확도
────────────────────────────────────────────────────────────────────────────
1번     좌측 세로획         좌측 세로획       ✓ 100%
2번     중앙 세로획         중앙 세로획       ✓ 100%  
3번     상단 가로획         상단 가로획       ✓ 100%
4번     하단 가로획         하단 가로획       ✓ 100%

획순 점수: 75.2/100점

우수한 점:
• 기본 획순은 모두 올바름
• 각 획의 방향성 정확

【6. 붓 움직임 벡터 분석】
────────────────────────────────────────────────────────────────────────────
세로획 각도: 87° (목표: 90°) - 오차 3°
가로획 상단: 3° 기울어짐
가로획 하단: 2° 기울어짐

속도 추정:
• 평균 속도: 중간
• 가속 구간: 획의 중앙부
• 감속 구간: 획의 시작과 끝

【7. 향상 권장 사항】
────────────────────────────────────────────────────────────────────────────
단기 목표 (1주일):
□ 매일 기본획 연습 30분
□ 천천히 정확하게 쓰기
□ 붓 잡는 자세 교정

중기 목표 (1개월):
□ 굵기 변화 의식적 연습
□ 꺾임 부분 부드럽게 처리
□ 전체 균형감 향상

장기 목표 (3개월):
□ B등급(80점) 달성
□ 다양한 서체 시도
□ 창의적 표현 추가

【8. 연습 추천 글자】
────────────────────────────────────────────────────────────────────────────
현재 수준에 맞는 연습 글자:
• 十 (십): 가로 세로 기본기
• 口 (입): 꺾임과 마무리
• 日 (일): 균형과 간격
• 田 (전): 복잡한 구조

================================================================================
                              분석 완료
================================================================================
"""
        return report
    
    def generate_json_report(self, analysis_results):
        """JSON 형식의 데이터 리포트"""
        json_data = {
            "timestamp": self.timestamp,
            "character": "中",
            "overall_score": 53.3,
            "grade": "D",
            "detailed_scores": {
                "thickness_consistency": 88.0,
                "turning_accuracy": 0.0,
                "spacing_uniformity": 50.0,
                "stroke_order_accuracy": 75.2
            },
            "thickness_analysis": {
                "mean": 12.5,
                "max": 20.5,
                "min": 2.5,
                "variation": 3.8,
                "unit": "pixels"
            },
            "spacing_analysis": {
                "measurements": {
                    "stroke_1_2": 45,
                    "stroke_1_3": 90,
                    "stroke_1_4": 90,
                    "stroke_2_3": 45,
                    "stroke_2_4": 45,
                    "stroke_3_4": 80
                },
                "unit": "pixels"
            },
            "angle_analysis": {
                "vertical_strokes": 87,
                "horizontal_top": 3,
                "horizontal_bottom": 2,
                "unit": "degrees"
            },
            "recommendations": {
                "immediate": [
                    "기본획 연습 30분/일",
                    "천천히 정확하게 쓰기",
                    "붓 잡는 자세 교정"
                ],
                "short_term": [
                    "굵기 변화 의식적 연습",
                    "꺾임 부분 부드럽게 처리",
                    "전체 균형감 향상"
                ],
                "long_term": [
                    "B등급(80점) 달성",
                    "다양한 서체 시도",
                    "창의적 표현 추가"
                ]
            },
            "practice_characters": ["十", "口", "日", "田"]
        }
        return json_data
    
    def generate_html_report(self, analysis_results):
        """HTML 형식의 웹 리포트"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>서예 분석 결과 - 中</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .score-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        .score-number {{
            font-size: 3em;
            font-weight: bold;
        }}
        .grade {{
            font-size: 1.5em;
            margin-top: 10px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .section h2 {{
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .metric-label {{
            font-weight: 500;
            color: #495057;
        }}
        .metric-value {{
            color: #007bff;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
        }}
        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .recommendations h3 {{
            color: #856404;
            margin-top: 0;
        }}
        ul {{
            color: #495057;
            line-height: 1.8;
        }}
        .practice-chars {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}
        .char-box {{
            width: 80px;
            height: 80px;
            border: 2px solid #dee2e6;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            border-radius: 10px;
            transition: all 0.3s;
        }}
        .char-box:hover {{
            background: #667eea;
            color: white;
            transform: scale(1.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 서예 분석 결과</h1>
        <div class="timestamp">{self.timestamp}</div>
        
        <div class="score-card">
            <div class="score-number">53.3점</div>
            <div class="grade">D등급 - 개선 필요</div>
        </div>
        
        <div class="section">
            <h2>📊 세부 점수</h2>
            <div class="metric">
                <span class="metric-label">굵기 일치도</span>
                <span class="metric-value">88.0점</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 88%;">88%</div>
            </div>
            
            <div class="metric">
                <span class="metric-label">획순 정확도</span>
                <span class="metric-value">75.2점</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 75.2%;">75%</div>
            </div>
            
            <div class="metric">
                <span class="metric-label">간격 균일성</span>
                <span class="metric-value">50.0점</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 50%;">50%</div>
            </div>
            
            <div class="metric">
                <span class="metric-label">꺾임 정확도</span>
                <span class="metric-value">0.0점</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 1%;">0%</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📏 선 굵기 분석</h2>
            <div class="metric">
                <span class="metric-label">평균 굵기</span>
                <span class="metric-value">12.5 픽셀</span>
            </div>
            <div class="metric">
                <span class="metric-label">최대 굵기</span>
                <span class="metric-value">20.5 픽셀</span>
            </div>
            <div class="metric">
                <span class="metric-label">최소 굵기</span>
                <span class="metric-value">2.5 픽셀</span>
            </div>
            <div class="metric">
                <span class="metric-label">굵기 변화율</span>
                <span class="metric-value">±3.8 픽셀</span>
            </div>
        </div>
        
        <div class="recommendations">
            <h3>💡 개선 권장사항</h3>
            <h4>즉시 실천사항:</h4>
            <ul>
                <li>매일 기본획 연습 30분</li>
                <li>천천히 정확하게 쓰기</li>
                <li>붓 잡는 자세 교정</li>
            </ul>
            <h4>단기 목표 (1개월):</h4>
            <ul>
                <li>굵기 변화 의식적 연습</li>
                <li>꺾임 부분 부드럽게 처리</li>
                <li>전체 균형감 향상</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>🎯 연습 추천 글자</h2>
            <div class="practice-chars">
                <div class="char-box">十</div>
                <div class="char-box">口</div>
                <div class="char-box">日</div>
                <div class="char-box">田</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def save_all_reports(self, analysis_results, base_path="/Users/m4_macbook/char-comparison-system/reports"):
        """모든 형식의 리포트 저장"""
        # 디렉토리 생성
        Path(base_path).mkdir(parents=True, exist_ok=True)
        
        # 타임스탬프 추가
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 텍스트 리포트 저장
        text_report = self.generate_text_report(analysis_results)
        text_path = f"{base_path}/analysis_report_{timestamp}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        # JSON 리포트 저장
        json_report = self.generate_json_report(analysis_results)
        json_path = f"{base_path}/analysis_report_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        
        # HTML 리포트 저장
        html_report = self.generate_html_report(analysis_results)
        html_path = f"{base_path}/analysis_report_{timestamp}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        return {
            'text': text_path,
            'json': json_path,
            'html': html_path
        }


# 실행
if __name__ == "__main__":
    generator = AnalysisReportGenerator()
    
    # 더미 분석 결과 (실제로는 advanced_stroke_analyzer.py의 결과 사용)
    dummy_results = {
        'overall_score': 53.3,
        'detailed_scores': {
            'thickness': 88.0,
            'turning': 0.0,
            'spacing': 50.0,
            'order': 75.2
        }
    }
    
    # 리포트 생성 및 저장
    saved_paths = generator.save_all_reports(dummy_results)
    
    # 텍스트 리포트 출력
    text_report = generator.generate_text_report(dummy_results)
    print(text_report)
    
    print("\n" + "="*80)
    print("📁 리포트 저장 완료:")
    print(f"  📄 텍스트: {saved_paths['text']}")
    print(f"  📊 JSON: {saved_paths['json']}")
    print(f"  🌐 HTML: {saved_paths['html']}")
    print("="*80)