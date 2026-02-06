"""
Streamlit Page - Basic 버전 (목소리 없이 BGM만)
"""
import os
import requests
import streamlit as st

# Server-side connection (Docker Network)
API_BASE = os.getenv("INTERNAL_API_URL", "http://backend:8000")

# Client-side connection (Browser)
_host = os.getenv("PUBLIC_API_URL")
if not _host:
    _host = "http://localhost:18000"
PUBLIC_API_URL = _host

st.set_page_config(page_title="🎵 Basic (BGM만)", layout="centered")

st.title("🎵 Basic 버전 (BGM만)")
st.caption("✅ 목소리 없이 BGM과 자막만 포함된 영상을 생성합니다.")

images = st.file_uploader(
    "가게/음식 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", value="")
    menu_name = st.text_input("메뉴 이름", value="")
    tone = st.selectbox("광고 톤", ["힙", "감성", "고급", "가성비"], index=0)

with col2:
    price = st.text_input("가격 예: 9,900원", value="")
    location = st.text_input("위치 예: 오픈 위치", value="")
    benefit = st.text_input("혜택 예: 오픈이벤트/1+1/사이드 증정", value="")
    cta = st.text_input("방문/주문 유도 문구 예: 네이버예약 ㄱㄱ?", value="")

make_btn = st.button("🎬 영상 만들기 (BGM만)", type="primary")

if make_btn:
    if not images:
        st.error("이미지를 1장 이상 올려주세요.")
        st.stop()
    if not menu_name.strip():
        st.error("메뉴 이름은 필수입니다.")
        st.stop()

    files = []
    for img in images:
        files.append(("images", (img.name, img.getvalue(), img.type)))

    data = {
        "menu_name": menu_name.strip(),
        "store_name": store_name.strip() or "",
        "tone": tone,
        "price": price.strip() or "",
        "location": location.strip() or "",
        "benefit": benefit.strip() or "",
        "cta": cta.strip() or "",
    }

    with st.spinner("영상 생성 중... (수 초~수십 초)"):
        try:
            # /api/generate-basic 호출 (TTS 없이)
            r = requests.post(f"{API_BASE}/api/generate-basic", files=files, data=data, timeout=600)
            r.raise_for_status()
            out = r.json()
        except Exception as e:
            st.error(f"요청 실패: {e}")
            st.stop()

    st.success("완료!")
    st.write("**생성 문구(자막):**")
    st.text(out.get("caption_text", ""))

    st.write("**해시태그:**", " ".join(out.get("hashtags", [])))

    video_url = out.get("video_url")
    if video_url:
        full_url = f"{PUBLIC_API_URL}{video_url}"
        st.video(full_url)
        st.markdown(f"[결과 영상 열기]({full_url})")
