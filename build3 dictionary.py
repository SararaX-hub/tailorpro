# Step 3: put the Swahili dictionary (and the Swahili install instructions) into the app.
import sys, json, re
sys.path.insert(0, "/mnt/user-data/outputs/wip")
import importlib, sw_dict
importlib.reload(sw_dict)

p = "/home/claude/pwa/index.html"
src = open(p, encoding="utf-8").read()
start = src.index("/* I18N-DICTIONARY-START */")
end = src.index("/* I18N-DICTIONARY-END */") + len("/* I18N-DICTIONARY-END */")

lines = ["/* I18N-DICTIONARY-START */", "const SW = {"]
for k, v in sw_dict.SW.items():
    lines.append(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},")
lines.append("};")
lines.append("const INSTALL_IOS_SW = " + json.dumps(sw_dict.INSTALL_IOS_SW, ensure_ascii=False) + ";")
lines.append("const INSTALL_ANDROID_SW = " + json.dumps(sw_dict.INSTALL_ANDROID_SW, ensure_ascii=False) + ";")
lines.append("/* I18N-DICTIONARY-END */")

src = src[:start] + "\n".join(lines) + src[end:]
open(p, "w", encoding="utf-8").write(src)
print("dictionary installed:", len(sw_dict.SW), "phrases")
