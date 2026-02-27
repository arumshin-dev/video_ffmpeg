"""
Streamlit Page - Basic 버전 (목소리 없이 BGM만)
"""
import streamlit as st
from streamlit_sortables import sort_items

from frontend.modules.api import api
from frontend.modules.ui_components import (
    render_store_info_inputs, 
    render_generation_results, 
    render_instruction_caption
)

st.set_page_config(page_title="🍜 AI 유튜브 숏폼 광고영상 제작 프로그램", layout="centered")

st.title("🍜 AI 유튜브 숏폼 광고 영상 프로그램")
render_instruction_caption()

# 1. 파일 업로드
images = st.file_uploader(
    "가게/음식 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# 최종적으로 API에 보낼 파일 리스트
selected_files = []

# 2. 드래그 앤 드롭 정렬 (기존 로직 유지)
if images:
    st.subheader("📸 영상에 나올 사진 순서 정하기!")
    st.info("사진을 마우스로 드래그해서 원하는 순서로 배치해주세요. 왼쪽부터 영상에 먼저 나옵니다.")
    
    img_names = [img.name for img in images]
    sorted_names = sort_items(img_names, direction="horizontal")
    
    for name in sorted_names:
        target_img = next(img for img in images if img.name == name)
        selected_files.append(target_img)

    st.write("---")
    st.caption("현재 설정된 순서:")
    cols = st.columns(5)
    for idx, img_obj in enumerate(selected_files):
        with cols[idx % 5]:
            st.image(img_obj, caption=f"{idx+1}번", use_container_width=True)
    st.write("---")
else:
    selected_files = []

# 3. 정보 입력 (모듈화된 컴포넌트 사용)
data = render_store_info_inputs()

make_btn = st.button("🎬 영상 만들기", type="primary")

if make_btn:
    if not images:
        st.error("이미지를 1장 이상 올려주세요.")
        st.stop()
    if not data["menu_name"]:
        st.error("메뉴 이름은 필수입니다.")
        st.stop()

    # 백엔드 전송용 파일 리스트 구성
    files = []
    for img in selected_files:
        img.seek(0)
        files.append(("images", (img.name, img.getvalue(), img.type)))

    with st.spinner("영상을 생성 중입니다... (수 초~수십 초)"):
        # API 호출 (모듈화된 api 사용)
        out = api.generate_video(files=files, data=data)

    # 4. 결과 노출 (모듈화된 컴포넌트 사용)
    full_video_url = api.get_public_video_url(out.get("video_url"))
    render_generation_results(out, full_video_url)
