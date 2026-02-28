"""
video.py 유닛 테스트

테스트 대상:
- _escape_drawtext: FFmpeg drawtext 필터용 특수문자 escape
"""

import sys
from pathlib import Path

# backend 모듈 import를 위해 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from backend.app.services.video import _escape_drawtext


class TestEscapeDrawtext:
    """_escape_drawtext 함수 테스트"""

    def test_escape_backslash(self):
        """백슬래시가 이중 escape 되어야 함"""
        assert _escape_drawtext("a\\b") == "a\\\\b"

    def test_escape_colon(self):
        """콜론이 escape 되어야 함"""
        assert _escape_drawtext("a:b") == "a\\:b"

    def test_escape_single_quote(self):
        """작은따옴표가 escape 되어야 함"""
        assert _escape_drawtext("it's") == "it\\'s"

    def test_escape_percent(self):
        """퍼센트가 escape 되어야 함"""
        assert _escape_drawtext("50%") == "50\\%"

    def test_escape_multiple_special_chars(self):
        """여러 특수문자가 동시에 escape 되어야 함"""
        result = _escape_drawtext("it's 50%: test\\end")
        assert result == "it\\'s 50\\%\\: test\\\\end"

    def test_escape_empty_string(self):
        """빈 문자열은 그대로 반환"""
        assert _escape_drawtext("") == ""

    def test_escape_plain_text(self):
        """특수문자 없는 일반 텍스트는 그대로 반환"""
        assert _escape_drawtext("hello world") == "hello world"

    def test_escape_korean_text(self):
        """한글 텍스트는 영향 없이 그대로 유지"""
        assert _escape_drawtext("맛있는 음식") == "맛있는 음식"

    def test_escape_korean_with_special(self):
        """한글과 특수문자 혼합"""
        result = _escape_drawtext("가격: 9,900원")
        assert result == "가격\\: 9,900원"
