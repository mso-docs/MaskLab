"""TASK-014 / REQ-025. Encode local captured UI, verify duration, emit review frames/captions.
Uses a temporary FFmpeg install; never uploads the recording.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/release'


def main():
    if len(sys.argv)!=2:raise SystemExit('Pass the locally installed FFmpeg executable path.')
    ffmpeg=sys.argv[1]
    source=OUT/'masklab-walkthrough.webm'
    target=OUT/'masklab-walkthrough.mp4'
    command=[ffmpeg,'-y','-i',str(source),'-map_metadata','-1','-an','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    encoded=subprocess.run(command,capture_output=True,text=True)
    (OUT/'video-encode.log').write_text(encoded.stderr)
    if encoded.returncode:raise SystemExit(encoded.returncode)
    probe=subprocess.run([ffmpeg,'-i',str(target)],capture_output=True,text=True)
    match=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',probe.stderr)
    assert match,'Unable to measure video duration'
    duration=int(match[1])*3600+int(match[2])*60+float(match[3])
    assert 140<duration<180, 'Recording does not meet the reviewed duration window'
    assert 'Audio:' not in probe.stderr, 'Unexpected audio stream'
    for i,second in enumerate([5,25,49,74,97,117,138,155]):
        subprocess.run([ffmpeg,'-y','-ss',str(second),'-i',str(target),'-frames:v','1',str(OUT/f'video-review-{i}.png')],check=True,capture_output=True)
    scenes=json.loads((OUT/'video-scenes.json').read_text())
    def stamp(second):
        return f'{int(second)//3600:02}:{int(second)//60%60:02}:{int(second)%60:02},000'
    (OUT/'masklab-walkthrough.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s["start"])} --> {stamp(s["end"])}\n{s["title"]}\n{s["text"]}' for i,s in enumerate(scenes['scenes']))+'\n',encoding='utf-8')
    (OUT/'NARRATION.txt').write_text('Optional narration script. Delivered MP4 has burned-in captions and no spoken audio.\n\n'+'\n\n'.join(s['title']+'\n'+s['text'] for s in scenes['scenes']),encoding='utf-8')
    result={'status':'PASS','duration_seconds':duration,'strictly_under_180_seconds':True,'format':'MP4 / H.264 / yuv420p','audio':'none; burned-in English captions','capture':'actual browser UI; saved live and simulated scenes labeled separately','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frame_review_required':True}
    (OUT/'video-verification.json').write_text(json.dumps(result,indent=2))
    files=['masklab-test-build.zip','masklab-walkthrough.mp4','masklab-walkthrough.srt','NARRATION.txt']
    (OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256((OUT/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in files))
    with zipfile.ZipFile(OUT/'masklab-pages.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((OUT/'pages').rglob('*')):
            if p.is_file():z.write(p,p.relative_to(OUT/'pages'))
    print(json.dumps(result))


if __name__=='__main__':main()
