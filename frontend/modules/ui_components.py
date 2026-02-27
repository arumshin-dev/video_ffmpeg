import streamlit as st
from typing import Dict, Any, List

def render_store_info_inputs():
    """가게 및 메뉴 정보 입력 폼을 렌더링합니다."""
    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("가게 이름", value="", placeholder="예: 백종원의 골목식당")
        menu_name = st.text_input("메뉴 이름", value="", placeholder="예: 치즈 돈까스")
        tone = st.selectbox("광고 톤", ["힙", "감성", "고급", "가성비"], index=0)

    with col2:
        price = st.text_input("가격 예: 9,900원", value="")
        location = st.text_input("위치 예: 망원동/홍대입구", value="")
        benefit = st.text_input("혜택 예: 오픈이벤트/1+1/사이드 증정", value="")
        cta = st.text_input("방문/주문 유도 문구 예: 네이버예약 ㄱㄱ?", value="")
    
    return {
        "menu_name": menu_name.strip(),
        "store_name": store_name.strip(),
        "tone": tone,
        "price": price.strip(),
        "location": location.strip(),
        "benefit": benefit.strip(),
        "cta": cta.strip()
    }

def render_generation_results(out: Dict[str, Any], public_video_url: str):
    """생성된 비디오와 텍스트 결과를 표시합니다."""
    st.success("영상 제작 완료!")
    
    st.write("**📝 생성 문구 (내레이션/자막):**")
    st.text(out.get("caption_text", ""))

    hashtags = out.get("hashtags", [])
    if hashtags:
        st.write("**#️⃣ 해시태그:**", " ".join(hashtags))

    if public_video_url:
        st.video(public_video_url)
        st.markdown(f"🔗 [결과 영상 직접 열기]({public_video_url})")

def render_instruction_caption():
    """사용 설명서 캡션을 렌더링합니다."""
    st.caption(
        "✅ 사용 설명서
"
        "1. 📸 사진은 최소 2~6장을 준비해주세요. 다양할수록 영상이 풍성해집니다!
"
        "2. 업로드된 사진들을 드래그 앤 드롭으로 순서를 정할 수 있습니다.
"
        "3. 가게/메뉴 정보와 광고 톤을 입력해주세요.
"
        "4. '영상 만들기' 버튼을 누르면 제작이 시작됩니다.
"
        "5. 결과 영상을 확인하고 다운로드 받아 활용하세요!"
    )
