import streamlit as st
from frontend.common.header import show_header
from frontend.common.footer import show_footer
from frontend.modules.condition1 import render_condition1
from frontend.modules.condition2 import render_condition2
from frontend.modules.images import show_images

def main():
    show_header()
    st.write("메인 콘텐츠 영역입니다.")
    render_condition1()
    render_condition2()
    show_images()
    show_footer()

if __name__ == "__main__":
    main()
