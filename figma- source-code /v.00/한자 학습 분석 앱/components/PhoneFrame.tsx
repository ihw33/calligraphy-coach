import React from 'react';

interface PhoneFrameProps {
  children: React.ReactNode;
}

export function PhoneFrame({ children }: PhoneFrameProps) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-8">
      {/* 아이폰 14 Pro 프레임 */}
      <div className="relative">
        {/* 외부 프레임 (메탈 베젤) */}
        <div className="relative w-[375px] h-[812px] bg-gray-900 rounded-[50px] p-2 shadow-2xl">
          {/* 내부 스크린 영역 */}
          <div className="relative w-full h-full bg-black rounded-[42px] overflow-hidden">
            
            {/* 노치 */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 z-50">
              <div className="w-[150px] h-[30px] bg-black rounded-b-[20px] flex items-center justify-center">
                {/* 스피커 */}
                <div className="w-[50px] h-[4px] bg-gray-800 rounded-full mr-2"></div>
                {/* 카메라 */}
                <div className="w-[12px] h-[12px] bg-gray-800 rounded-full"></div>
              </div>
            </div>

            {/* 앱 콘텐츠 */}
            <div className="w-full h-full bg-white relative overflow-hidden">
              {children}
              
              {/* 홈 인디케이터 */}
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 z-50">
                <div className="w-[134px] h-[5px] bg-black rounded-full opacity-60"></div>
              </div>
            </div>
          </div>
          
          {/* 사이드 버튼들 */}
          {/* 볼륨 버튼 */}
          <div className="absolute left-[-3px] top-[120px] w-[3px] h-[28px] bg-gray-700 rounded-r-sm"></div>
          <div className="absolute left-[-3px] top-[160px] w-[3px] h-[28px] bg-gray-700 rounded-r-sm"></div>
          
          {/* 전원 버튼 */}
          <div className="absolute right-[-3px] top-[140px] w-[3px] h-[40px] bg-gray-700 rounded-l-sm"></div>
        </div>

        {/* 브랜드 라벨 */}
        <div className="absolute bottom-[-40px] left-1/2 transform -translate-x-1/2 text-center">
          <p className="text-gray-600 text-sm font-medium">붓글씨 결구 평가 앱</p>
          <p className="text-gray-400 text-xs">iOS 모바일 프리뷰</p>
        </div>
      </div>
    </div>
  );
}