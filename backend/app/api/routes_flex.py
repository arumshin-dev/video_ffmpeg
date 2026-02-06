"""
API 라우터 - Flexible (오디오 옵션 선택 가능)

- use_tts: 나래이션 포함 여부
- use_bgm: 배경음악 포함 여부
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from backend.app.core.logger import get_logger
from backend.app.core.config import settings
from backend.app.schemas import GenerateResponse

from backend.app.services.storage import make_job_dir, public_video_path
from backend.app.services.llm import generate_copy
from backend.app.services.tts import synthesize_voice_lines
from backend.app.services.video import (
    build_slideshow,
    burn_text_overlays,
    mix_audio,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["generator-flex"])


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _normalize_for_tts(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("…", ".")
    s = s.replace("·", " ")
    return s.strip()


def _safe_segments() -> int:
    try:
        v = int(getattr(settings, "VIDEO_SEGMENTS", 6))
    except Exception:
        v = 6
    return max(1, min(12, v))


@router.post("/generate-flex", response_model=GenerateResponse)
async def generate_flex(
    images: list[UploadFile] = File(..., description="음식 사진들 (2~6장 권장)"),
    bgm_file: Optional[UploadFile] = File(None, description="사용자 지정 BGM 파일 (선택)"),
    menu_name: str = Form(..., description="메뉴 이름"),

    store_name: str = Form("", description="가게 이름(선택)"),
    tone: str = Form("감성", description="광고 톤(힙/감성/고급/가성비)"),

    price: str = Form("", description="가격(선택)"),
    location: str = Form("", description="위치(선택)"),
    benefit: str = Form("", description="혜택(선택)"),
    cta: str = Form("", description="콜투액션(선택)"),
    
    # 새로운 오디오 옵션
    use_tts: bool = Form(True, description="나래이션 포함 여부"),
    use_bgm: bool = Form(True, description="배경음악 포함 여부"),
):
    """오디오 옵션을 선택할 수 있는 영상 생성"""
   
    # 0) 입력 검증
    if len(images) < 1:
        raise HTTPException(400, "이미지를 1장 이상 업로드해주세요.")
    if not (menu_name or "").strip():
        raise HTTPException(400, "메뉴 이름은 필수입니다.")

    menu_name = menu_name.strip()
    store_name = (store_name or "").strip() or None
    tone = (tone or "감성").strip()

    price = (price or "").strip() or None
    location = (location or "").strip() or None
    benefit = (benefit or "").strip() or None
    cta = (cta or "").strip() or None

    # 1) 작업 디렉토리 생성
    job_dir = make_job_dir()
    inputs_dir = job_dir / "inputs"
    artifacts_dir = job_dir / "artifacts"

    # 2) 이미지 저장
    img_paths: list[Path] = []
    for i, uf in enumerate(images, start=1):
        suffix = Path(uf.filename).suffix.lower() or ".jpg"
        save_path = inputs_dir / f"img_{i}{suffix}"
        save_path.write_bytes(await uf.read())
        img_paths.append(save_path)

    # 3) 쇼츠 템포용 컷 수 확정
    target_cuts = _safe_segments()
    image_paths_for_video = [img_paths[i % len(img_paths)] for i in range(target_cuts)]

    # 4) LLM 카피 생성
    llm_out = generate_copy(
        menu_name=menu_name,
        store_name=store_name,
        tone=tone,
        n_lines=target_cuts,
        price=price,
        location=location,
        benefit=benefit,
        cta=cta,
    )

    caption_lines = (llm_out.caption_lines or [])[:target_cuts]
    if len(caption_lines) < target_cuts:
        caption_lines += [""] * (target_cuts - len(caption_lines))

    caption_lines_clean = [_normalize_for_tts(s) for s in caption_lines if s and s.strip()]

    if not caption_lines_clean:
        fallback = _normalize_for_tts(llm_out.promo_text) if getattr(llm_out, "promo_text", "") else ""
        caption_lines_clean = [fallback] if fallback else ["지금 바로 방문해보세요!"]

    tts_text = "\n".join(caption_lines_clean)

    # 5) TTS (조건부)
    voice_path = None
    timings = None
    if use_tts:
        voice_path, timings = synthesize_voice_lines(
            caption_lines_clean,
            artifacts_dir / "voice_parts",
        )

    # 6) 슬라이드쇼(무음) 생성
    silent_video = build_slideshow(image_paths_for_video, artifacts_dir / "silent.mp4")

    # 7) drawtext로 자막 burn-in
    sub_video = burn_text_overlays(
        in_video=silent_video,
        image_paths=image_paths_for_video,
        lines=caption_lines_clean,
        out_video=artifacts_dir / "subtitled.mp4",
        timings=timings,
    )

    # 8) BGM 선택 (조건부)
    bgm_path = None
    if use_bgm:
        # 사용자가 업로드한 BGM이 있으면 우선 사용
        if bgm_file and bgm_file.filename:
            suffix = Path(bgm_file.filename).suffix.lower() or ".mp3"
            custom_bgm_path = artifacts_dir / f"custom_bgm{suffix}"
            custom_bgm_path.write_bytes(await bgm_file.read())
            bgm_path = custom_bgm_path
            logger.info("Using custom BGM: %s", bgm_path)
        else:
            # 기본 BGM 사용
            bgm_dir = _project_root() / "assets" / "bgm"
            bgm_candidates = list(bgm_dir.glob("*.mp3")) + list(bgm_dir.glob("*.wav"))
            bgm_path = bgm_candidates[0] if bgm_candidates else None

    logger.info(
        "AUDIO DEBUG (Flex) | use_tts=%s voice_path=%s | use_bgm=%s bgm_path=%s",
        use_tts, voice_path,
        use_bgm, bgm_path,
    )

    # 9) 오디오 믹스
    final_path = mix_audio(sub_video, voice_path, bgm_path, public_video_path(job_dir))

    # 10) 결과 반환
    job_id = job_dir.name
    video_url = f"/outputs/{job_id}/artifacts/final.mp4"

    return GenerateResponse(
        job_id=job_id,
        video_url=video_url,
        caption_text=tts_text,
        hashtags=llm_out.hashtags,
    )
