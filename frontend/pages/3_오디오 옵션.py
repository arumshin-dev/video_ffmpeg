"""
Streamlit Page - 오디오 옵션 선택
무음 / BGM만 / 나래이션만 / BGM+나래이션
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

st.set_page_config(page_title="🎛️ 오디오 옵션 선택", layout="centered")

st.title("🎛️ 오디오 옵션 선택")
st.caption("✅ 원하는 오디오 조합을 선택하세요.")

# 오디오 옵션 라디오 버튼
audio_option = st.radio(
    "오디오 설정",
    options=[
        "🔇 무음 (자막만)",
        "🎵 BGM만",
        "🎙️ 나래이션만",
        "🔊 BGM + 나래이션",
    ],
    index=3,  # 기본값: BGM + 나래이션
    horizontal=True,
)

# 옵션에 따라 use_tts, use_bgm 결정
if audio_option == "🔇 무음 (자막만)":
    use_tts, use_bgm = False, False
elif audio_option == "🎵 BGM만":
    use_tts, use_bgm = False, True
elif audio_option == "🎙️ 나래이션만":
    use_tts, use_bgm = True, False
else:  # BGM + 나래이션
    use_tts, use_bgm = True, True

st.divider()

# 사용자 지정 BGM 업로드 (선택)
bgm_file = None
if use_bgm:
    bgm_file = st.file_uploader(
        "🎵 BGM 파일 업로드 (선택 - 없으면 기본 BGM 사용)",
        type=["mp3", "wav"],
        accept_multiple_files=False
    )

st.divider()

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

make_btn = st.button("🎬 영상 만들기", type="primary")

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
    
    # BGM 파일 추가 (업로드 시)
    if bgm_file:
        files.append(("bgm_file", (bgm_file.name, bgm_file.getvalue(), bgm_file.type)))

    data = {
        "menu_name": menu_name.strip(),
        "store_name": store_name.strip() or "",
        "tone": tone,
        "price": price.strip() or "",
        "location": location.strip() or "",
        "benefit": benefit.strip() or "",
        "cta": cta.strip() or "",
        "use_tts": str(use_tts).lower(),  # bool을 문자열로 변환
        "use_bgm": str(use_bgm).lower(),
    }

    with st.spinner("영상 생성 중... (수 초~수십 초)"):
        try:
            # /api/generate-flex 호출
            r = requests.post(f"{API_BASE}/api/generate-flex", files=files, data=data, timeout=600)
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
