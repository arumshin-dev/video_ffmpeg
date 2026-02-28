import os
import requests
import streamlit as st
from typing import List, Dict, Any, Optional

class VideoAPI:
    """백엔드 API 호출을 전담하는 클래스"""
    
    def __init__(self):
        # Server-side connection (Docker Network)
        self.api_base = os.getenv("INTERNAL_API_URL", "http://backend:8000")
        
        # Client-side connection (Browser)
        host = os.getenv("PUBLIC_API_URL")
        if not host:
            host = "http://localhost:18000"
        self.public_api_url = host

    def generate_video(self, files: List[tuple], data: Dict[str, Any], endpoint: str = "/api/generate") -> Dict[str, Any]:
        """비디오 생성을 요청하고 결과를 반환합니다.
        
        Args:
            files: 전송할 파일 리스트 (이미지, BGM 등)
            data: 전송할 텍스트 데이터
            endpoint: API 엔드포인트 경로 (기본값: /api/generate)
        """
        try:
            # POST 요청 전송 (최대 10분 대기)
            r = requests.post(f"{self.api_base}{endpoint}", files=files, data=data, timeout=600)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            st.error(f"백엔드 요청 중 오류가 발생했습니다: {e}")
            st.stop()
            return {}

    def get_public_video_url(self, video_url: Optional[str]) -> Optional[str]:
        """상대 경로인 video_url을 외부 접근 가능한 전체 URL로 변환합니다."""
        if not video_url:
            return None
        return f"{self.public_api_url}{video_url}"

# 싱글톤처럼 사용할 수 있게 인스턴스 생성
api = VideoAPI()
