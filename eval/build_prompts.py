"""Fill {{file}} slots from inputs/ and write rendered prompts to prompts/rendered/."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
def render(text):
    return re.sub(r"\{\{([\w.\-]+)\}\}", lambda m: (ROOT/"inputs"/m.group(1)).read_text().strip(), text)
def instructions_only(text):
    return re.sub(r"\{\{([\w.\-]+)\}\}", "", text)
if __name__ == "__main__":
    out = ROOT/"prompts"/"rendered"; out.mkdir(exist_ok=True)
    for kind in ("original","optimized"):
        for p in sorted((ROOT/"prompts"/kind).glob("*.txt")):
            (out/f"{p.stem}.{kind}.txt").write_text(render(p.read_text()))
    print("rendered ->", out)
