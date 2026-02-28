"""
Streamlit Page - 오디오 옵션 선택
무음 / BGM만 / 나래이션만 / BGM+나래이션
"""
import streamlit as st
from streamlit_sortables import sort_items

from frontend.modules.api import api
from frontend.modules.ui_components import (
    render_store_info_inputs, 
    render_generation_results, 
    render_instruction_caption
)

st.set_page_config(page_title="🎛️ 오디오 옵션 선택", layout="centered")

st.title("🎛️ 오디오 옵션 선택")
render_instruction_caption()

# 1. 파일 업로드
images = st.file_uploader(
    "가게/음식 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# 최종적으로 API에 보낼 파일 리스트
selected_files = []

# 2. 드래그 앤 드롭 정렬
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

# 3. 오디오 옵션 (이 페이지 고유 로직)
st.caption("✅ 원하는 오디오 조합을 선택하세요.")
audio_option = st.radio(
    "오디오 설정",
    options=[
        "🔇 무음 (자막만)",
        "🎵 BGM만",
        "🎙️ 나래이션만",
        "🔊 BGM + 나래이션",
    ],
    index=3,
    horizontal=True,
)

if audio_option == "🔇 무음 (자막만)":
    use_tts, use_bgm = False, False
elif audio_option == "🎵 BGM만":
    use_tts, use_bgm = False, True
elif audio_option == "🎙️ 나래이션만":
    use_tts, use_bgm = True, False
else:
    use_tts, use_bgm = True, True

# 사용자 지정 BGM 업로드
bgm_file = None
if use_bgm:
    bgm_file = st.file_uploader(
        "🎵 BGM 파일 업로드 (선택 - 없으면 기본 BGM 사용)",
        type=["mp3", "wav"],
        accept_multiple_files=False
    )

st.divider()

# 4. 정보 입력
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
    
    if bgm_file:
        files.append(("bgm_file", (bgm_file.name, bgm_file.getvalue(), bgm_file.type)))

    # 옵션 데이터 추가
    data.update({
        "use_tts": str(use_tts).lower(),
        "use_bgm": str(use_bgm).lower(),
    })

    with st.spinner("요청하신 옵션으로 영상을 생성 중입니다... (수 초~수십 초)"):
        # API 호출 (/api/generate-flex 사용)
        out = api.generate_video(files=files, data=data, endpoint="/api/generate-flex")

    # 5. 결과 노출
    full_video_url = api.get_public_video_url(out.get("video_url"))
    render_generation_results(out, full_video_url)
