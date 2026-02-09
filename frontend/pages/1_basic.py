"""
Streamlit Page - Basic 버전 (목소리 없이 BGM만)
"""
import os
import requests
import streamlit as st
from streamlit_sortables import sort_items

# Server-side connection (Docker Network)
API_BASE = os.getenv("INTERNAL_API_URL", "http://backend:8000")

# Client-side connection (Browser)
_host = os.getenv("PUBLIC_API_URL")
if not _host:
    _host = "http://localhost:18000"
PUBLIC_API_URL = _host

st.set_page_config(page_title="🍜 AI 유튜브 숏폼 광고영상 제작 프로그램", layout="centered")

st.title("🍜 AI 유튜브 숏폼 광고 영상 프로그램")
st.caption(
    "✅ 사용 설명서\n"
    "1. 📸 사진은 최소 10~15장을 준비해주세요. 가게/음식/리뷰 캡쳐본 등 다양할수록 좋아요!\n"
    "2. 업로드된 사진들을 드래그 앤 드롭으로 순서를 정해주세요.\n"
    "3. 가게/메뉴 이름과 광고 톤을 선택해주세요.\n"
    "4. 소비자들이 매장을 방문하고 싶도록 혜택이나 방문유도 문구를 작성해주세요.\n"
    "5. 🎥 '영상 만들기' 버튼을 누르면 영상 제작이 시작됩니다.\n"
    "6. 영상이 제작되면, 다운로드 받으셔서 유튜브/인스타그램/당근 숏폼에 업로드 해주세요!"
)

# 1. 파일 업로드
images = st.file_uploader(
    "가게/음식 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# 최종적으로 API에 보낼 파일 리스트
selected_files = []

# 2. 업로드된 사진이 있을 때만 드래그 섹션 노출
if images:
    st.subheader("📸 영상에 나올 사진 순서 정하기!")
    st.info("사진을 마우스로 드래그해서 원하는 순서로 배치해주세요. 왼쪽부터 영상에 먼저 나옵니다.")
    
    # 파일명 리스트 생성
    img_names = [img.name for img in images]
    
    # 드래그 앤 드롭 위젯 (라이브러리 필요: pip install streamlit-sortables)
    sorted_names = sort_items(img_names, direction="horizontal")
    
    # 사용자가 드래그해서 맞춘 순서대로 파일 객체 재정렬
    for name in sorted_names:
        target_img = next(img for img in images if img.name == name)
        selected_files.append(target_img)

    # 3. 배치된 순서대로 미리보기 (확인용)
    st.write("---")
    st.caption("현재 설정된 순서:")
    cols = st.columns(5)
    for idx, img_obj in enumerate(selected_files):
        with cols[idx % 5]:
            st.image(img_obj, caption=f"{idx+1}번", use_container_width=True)
    st.write("---")
else:
    # 사진이 없을 때는 빈 리스트 유지
    selected_files = []

col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("가게 이름", value="")
    menu_name = st.text_input("메뉴 이름", value="")
    tone = st.selectbox("광고 톤", ["힙", "감성", "고급", "가성비"], index=0)

with col2:
    price = st.text_input("가격 예: 9,900원", value="")
    location = st.text_input("위치 예: 망원동/홍대입구", value="")
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

    # 백엔드 전송용 파일 리스트 구성 (고객이 드래그한 사진 순서대로)
    files = []
    # 드래그 정렬된 순서(selected_files)로 전송
    for img in selected_files:
        img.seek(0)  # 파일 포인터 초기화 (미리보기에서 읽었으므로)
        files.append(("images", (img.name, img.getvalue(), img.type)))

    # 전송할 텍스트 데이터
    data = {
        "menu_name": menu_name.strip(),
        "store_name": store_name.strip() or "",
        "tone": tone,
        "price": price.strip() or "",
        "location": location.strip() or "",
        "benefit": benefit.strip() or "",
        "cta": cta.strip() or "",
    }

    with st.spinner("사용자가 정한 순서대로 영상을 생성 중입니다... (수 초~수십 초)"):
        try:
            # POST 요청 전송
            r = requests.post(f"{API_BASE}/api/generate", files=files, data=data, timeout=600)
            r.raise_for_status()
            out = r.json()
        except Exception as e:
            st.error(f"요청 실패: {e}")
            st.stop()

    # 4. 결과 노출 구간
    st.success("영상 제작 완료!")
    
    st.write("**📝 생성 문구 (내레이션/자막):**")
    st.text(out.get("caption_text", ""))

    st.write("**#️⃣ 해시태그:**", " ".join(out.get("hashtags", [])))

    video_url = out.get("video_url")
    if video_url:
        full_url = f"{PUBLIC_API_URL}{video_url}"
        st.video(full_url)
        st.markdown(f"🔗 [결과 영상 직접 열기]({full_url})")
