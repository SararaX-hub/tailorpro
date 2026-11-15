import sys, re
sys.path.insert(0, "/mnt/user-data/outputs/wip/pw")
from harness import FakeSupabase, Session
from walk import walk

ok = fail = 0
def check(name, cond, extra=""):
    global ok, fail
    if cond: ok += 1
    else: fail += 1
    print(("PASS " if cond else "FAIL ") + name + ((" -> " + str(extra)) if (extra and not cond) else ""))

def shown(s):
    return [shown for _, shown in s.text_nodes()]

# 1) a Swahili phone opens the app in Swahili by itself
s = Session(FakeSupabase(), locale="sw-TZ")
s.wait_boot("auth")
txt = shown(s)
check("Swahili phone: login screen opens in Swahili", "Ingia" in txt and "NAMBA YA SIMU" in txt and "NENOSIRI" in txt, txt[:12])
check("Swahili phone: switch shows SW as active", s.page.evaluate("document.querySelector('.auth-lang .lang-switch button.active').dataset.lang") == "sw")
check("Swahili phone: placeholder translated", s.page.get_attribute("#authPassword", "placeholder") == "Angalau herufi 6")
check("Swahili phone: page language set", s.page.evaluate("document.documentElement.lang") == "sw")
s.close()

# 2) an English phone opens in English; the switch flips it and flips it back exactly
s = Session(FakeSupabase(), locale="en-US")
s.wait_boot("auth")
english_before = s.text_nodes()
check("English phone: opens in English", "Log In" in shown(s) and "PASSWORD" in shown(s))
s.page.click(".auth-lang button[data-lang='sw']")
txt = shown(s)
check("tap SW: login screen becomes Swahili", "Ingia" in txt and "NAMBA YA SIMU" in txt and "Log In" not in txt, txt[:10])
check("tap SW: placeholder changes", s.page.get_attribute("#authPhone", "placeholder") in ("0712 345 678",))
s.page.click(".auth-lang button[data-lang='en']")
english_after = s.text_nodes()
check("tap EN: everything is back to exactly the original English", [x[1] for x in english_after] == [x[1] for x in english_before])
check("tap EN: placeholder restored", s.page.get_attribute("#authPassword", "placeholder") == "At least 6 characters")

# 3) the choice is remembered after closing and reopening
s.page.click(".auth-lang button[data-lang='sw']")
s.page.reload(); s.wait_boot("auth")
check("choice is remembered after reopening", "Ingia" in shown(s))
s.close()

# 4) walk the whole app in Swahili: nothing of ours should be left in English
seen, errors = walk(lang_locale="sw-TZ")
check("no page errors while using the whole app in Swahili", not errors, errors)
user_data = {"Test Shop", "Juma Mwita", "Prefers slim fit", "Two-piece suit", "Offline Person", "JM", "OP", "VIP", "PRO", "NYUZI", "HOUSE", "WhatsApp", "TSh", "EN", "SW"}
left = []
for orig, (shown_text, label) in seen.items():
    if orig.startswith("PLACEHOLDER:"): continue
    if shown_text == orig and re.search(r"[A-Za-z]{3,}", orig):
        stripped = re.sub(r"TSh [\d,]+|[\d,.]+|\d{1,2} \w{3} \d{4}", "", orig).strip(" ·-+:()")
        if orig in user_data or stripped in user_data or not re.search(r"[A-Za-z]{3,}", stripped):
            continue
        left.append((orig, label))
print("\nText still in English while the app is in Swahili:", len(left))
for orig, label in left: print(f"   [{label}] {orig}")
check("nothing of the app's own text is left untranslated", len(left) == 0)

print(f"\n{ok} passed, {fail} failed")
