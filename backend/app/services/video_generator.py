from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile, HTTPException

from backend.app.core.logger import get_logger
from backend.app.schemas import GenerateResponse
from backend.app.services.storage import make_job_dir, public_video_path
from backend.app.services.llm import generate_copy
from backend.app.services.tts import synthesize_voice_lines
from backend.app.services.video import (
    build_slideshow,
    burn_text_overlays,
    mix_audio,
)
from backend.app.utils.video_utils import project_root, normalize_for_tts, safe_segments

logger = get_logger(__name__)

async def generate_video(
    images: list[UploadFile],
    menu_name: str,
    store_name: Optional[str] = None,
    tone: str = "감성",
    price: Optional[str] = None,
    location: Optional[str] = None,
    benefit: Optional[str] = None,
    cta: Optional[str] = None,
    use_tts: bool = True,
    use_bgm: bool = True,
    bgm_file: Optional[UploadFile] = None,
) -> GenerateResponse:
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
    target_cuts = safe_segments()
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

    caption_lines_clean = [normalize_for_tts(s) for s in caption_lines if s and s.strip()]

    if not caption_lines_clean:
        fallback = normalize_for_tts(llm_out.promo_text) if getattr(llm_out, "promo_text", "") else ""
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
            bgm_dir = project_root() / "assets" / "bgm"
            bgm_candidates = list(bgm_dir.glob("*.mp3")) + list(bgm_dir.glob("*.wav"))
            bgm_path = bgm_candidates[0] if bgm_candidates else None

    logger.info(
        "AUDIO DEBUG | use_tts=%s voice_path=%s | use_bgm=%s bgm_path=%s",
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
