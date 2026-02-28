"""
Streamlit Page - Voice 버전 (목소리 + BGM)
"""
import streamlit as st

from frontend.modules.api import api
from frontend.modules.ui_components import (
    render_store_info_inputs, 
    render_generation_results, 
    render_instruction_caption
)

st.set_page_config(page_title="🔊 Voice (목소리 포함)", layout="centered")

st.title("🔊 Voice 버전 (목소리 + BGM)")
st.caption("✅ AI 성우 목소리와 BGM이 모두 포함된 영상을 생성합니다.")
render_instruction_caption()

# 1. 파일 업로드
images = st.file_uploader(
    "가게/음식 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# 2. 정보 입력 (모듈화된 컴포넌트 사용)
data = render_store_info_inputs()

make_btn = st.button("🎬 영상 만들기 (목소리 포함)", type="primary")

if make_btn:
    if not images:
        st.error("이미지를 1장 이상 올려주세요.")
        st.stop()
    if not data["menu_name"]:
        st.error("메뉴 이름은 필수입니다.")
        st.stop()

    # 백엔드 전송용 파일 리스트 구성
    files = []
    for img in images:
        img.seek(0)
        files.append(("images", (img.name, img.getvalue(), img.type)))

    with st.spinner("목소리가 포함된 영상을 생성 중입니다... (수 초~수십 초)"):
        # API 호출 (모듈화된 api 사용)
        out = api.generate_video(files=files, data=data)

    # 3. 결과 노출 (모듈화된 컴포넌트 사용)
    full_video_url = api.get_public_video_url(out.get("video_url"))
    render_generation_results(out, full_video_url)
