from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
for engine in ['chromium','firefox','chrome','edge']:
    canvas=Image.new('RGB',(2560,1180),'#111827')
    draw=ImageDraw.Draw(canvas)
    for i,side in enumerate(['base','head']):
        folder=root/f'ui-{side}-{engine}'
        facts=json.loads((folder/'facts.json').read_text())
        version=json.loads((folder/'browser.json').read_text())['version']
        x=i*1280
        draw.text((x+20,12),f'{"BEFORE 03af220ac" if side=="base" else "AFTER bd516c952"} | {engine} {version}',font=font,fill='white')
        canvas.paste(Image.open(folder/'chat.png'),(x,55))
        draw.text((x+20,978),'Observed downloads from Export chat (evidence annotation)',font=font,fill='white')
        draw.text((x+20,1020),'Selected on screen: first reply (Apples), branch 1/2',font=small,fill='white')
        draw.text((x+20,1060),'ShareGPT assistant turns: '+', '.join(facts['sharegpt_gpt_turns']),font=small,fill='#fca5a5' if side=='base' else '#86efac')
        draw.text((x+20,1100),'Training JSONL assistant turns: '+', '.join(facts['training_assistant_turns']),font=small,fill='#fca5a5' if side=='base' else '#86efac')
    canvas.save(root/f'before-after-{engine}.png',optimize=True)

canvas=Image.new('RGB',(2560,1180),'#111827')
draw=ImageDraw.Draw(canvas)
for i,side in enumerate(['base','head']):
    folder=root/f'gpu-{side}-chromium'
    facts=json.loads((folder/'facts.json').read_text())
    x=i*1280
    draw.text((x+20,12),f'{"BEFORE 03af220ac" if side=="base" else "AFTER bd516c952"} | actual GPU regeneration and prompt edit',font=font,fill='white')
    canvas.paste(Image.open(folder/'gpu-edited.png'),(x,55))
    draw.text((x+20,978),'Observed ShareGPT downloads (evidence annotation)',font=font,fill='white')
    for y,key,title in [(1020,'during_regeneration_export_turns','While regeneration request is pending'),(1060,'regenerated_export_turns','After regeneration'),(1100,'edited_export_turns','After editing the prompt')]:
        draw.text((x+20,y),title+': '+str(facts[key])+' turns',font=small,fill='#fca5a5' if side=='base' else '#86efac')
canvas.save(root/'before-after-gpu.png',optimize=True)
