import pydub
from pathlib import Path

hitsound = pydub.AudioSegment.from_file(Path(__file__).parent/'yssb_roaring.wav') + 20
hitsound.export(Path(__file__).parent/'yssb_roaring.wav', format='wav')