import os
import glob
import subprocess
from moviepy import VideoFileClip                          # VideoFileClip은 루트에서
from moviepy.video.fx.MultiplySpeed import MultiplySpeed   # v2.x부터 속도 효과는 클래스 형태로 제공 [oai_citation:2‡zulko.github.io](https://zulko.github.io/moviepy/reference/reference/moviepy.video.fx.html)

def convert_gif_to_mp4(input_folder: str):
    """
    지정된 폴더(재귀) 내 모든 GIF → MP4 변환
    """
    gif_files = glob.glob(os.path.join(input_folder, "**", "*.gif"), recursive=True)
    if not gif_files:
        print("❌ GIF 파일을 찾을 수 없습니다.")
        return

    print(f"🔍 총 {len(gif_files)} GIF 발견, 변환 시작")
    succ, fail = 0, 0
    for i, gif in enumerate(gif_files, 1):
        mp4 = os.path.splitext(gif)[0] + ".mp4"
        cmd = [
            "ffmpeg", "-loglevel", "error",
            "-i", gif,
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=720:-2",  # 가로 720 유지, 세로 비율 자동
            "-y", mp4
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"[{i}/{len(gif_files)}] ✅ {mp4}")
            succ += 1
        except subprocess.CalledProcessError as e:
            print(f"[{i}/{len(gif_files)}] ❌ 실패: {e}")
            fail += 1

    print(f"📊 변환 결과: 성공 {succ} / 실패 {fail}")

def get_reference_duration(ref_video_path: str) -> float:
    """기준 영상 길이(초) 반환"""
    with VideoFileClip(ref_video_path) as clip:
        return clip.duration

def adjust_video_duration(video_path: str, target_duration: float, output_path: str):
    """
    모든 비디오를 target_duration에 맞춰 재생 속도 조정
    (_adjusted.mp4 → with_effects + MultiplySpeed)
    """
    with VideoFileClip(video_path) as clip:
        # 길이 차이가 0.1초 이내면 인코딩만
        if abs(clip.duration - target_duration) <= 0.1:
            new_clip = clip
        else:
            speed_factor = clip.duration / target_duration
            # v2.x는 fx 대신 with_effects([...]) 사용
            new_clip = clip.with_effects([MultiplySpeed(speed_factor)])  #  [oai_citation:3‡zulko.github.io](https://zulko.github.io/moviepy/getting_started/updating_to_v2.html?utm_source=chatgpt.com)

        # 결과 저장
        new_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
        if new_clip is not clip:
            new_clip.close()

def process_videos():
    # 기준 영상 가져오기
    refs = glob.glob("rigid/ours/*.mp4")
    if not refs:
        print("❌ 기준 영상(rigid/ours/*.mp4) 없음")
        return

    ref_dur = get_reference_duration(refs[0])
    print(f"📏 기준 길이: {ref_dur:.2f}초")

    # 처리할 폴더들
    folders = [
        "rigid/cogInv", "rigid/rave", "rigid/bivdiff", "rigid/vidtome",
        "rigid/original", "rigid/cogv2v", "rigid/ours",
        "nonrigid/rave", "nonrigid/bivdiff", "nonrigid/vidtome",
        "nonrigid/original", "nonrigid/cogv2v", "nonrigid/coginv", "nonrigid/ours"
    ]
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        print(f"\n▶️ {folder} 처리 중...")
        for mp4 in glob.glob(os.path.join(folder, "*.mp4")):
            out = mp4.replace(".mp4", "_adjusted.mp4")
            try:
                adjust_video_duration(mp4, ref_dur, out)
                print(f"   ✅ {os.path.basename(out)}")
            except Exception as e:
                print(f"   ❌ {os.path.basename(mp4)} 오류: {e}")

if __name__ == "__main__":
    # 예시: process_videos()만 실행
    process_videos()