import glob
import os
import shutil
from acdh_tei_pyutils.tei import TeiReader

editions = os.path.join("data", "editions")
os.makedirs(editions, exist_ok=True)

files = sorted(glob.glob("./*/*.xml"))

for x in files:
    doc = TeiReader(x)
    filename = os.path.basename(x)
    target = os.path.join(editions, filename)
    shutil.copyfile(x, target)
