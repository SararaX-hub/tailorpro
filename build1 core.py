# Step 1: language switch (CSS + placements) and the translation engine.
import sys
p = "/home/claude/pwa/index.html"
src = open("/mnt/user-data/outputs/wip/base-v15.html", encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"expected {count} but found {n} for:\n{old[:200]}"
    src = src.replace(old, new)

rep('.pro-badge {', '''.lang-switch {
  display: inline-flex;
  background: #f0f0f0;
  border-radius: 20px;
  padding: 3px;
}

.lang-switch button {
  border: none;
  background: none;
  padding: 6px 11px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 700;
  color: #777;
}

.lang-switch button.active {
  background: var(--primary);
  color: white;
}

.auth-lang {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
}

.auth-lang .lang-switch {
  background: rgba(255,255,255,0.18);
}

.auth-lang .lang-switch button {
  color: rgba(255,255,255,0.85);
}

.auth-lang .lang-switch button.active {
  background: white;
  color: var(--brand-blue);
}

.pro-badge {''')

SWITCH = '''<div class="lang-switch" data-no-i18n><button data-lang="en" onclick="setLanguage('en')">EN</button><button data-lang="sw" onclick="setLanguage('sw')">SW</button></div>'''

rep('''    <div class="muted" id="homeEyebrow">TAILOR</div>
    <button class="gear" onclick="show('settings')">⚙</button>''', '''    <div class="muted" id="homeEyebrow" data-no-i18n>TAILOR</div>
    <div style="display:flex; align-items:center; gap:8px">
      ''' + SWITCH + '''
      <button class="gear" onclick="show('settings')">⚙</button>
    </div>''')

rep('''<section id="auth" class="screen onboarding-screen">
''', '''<section id="auth" class="screen onboarding-screen">

  <div class="auth-lang">''' + SWITCH + '''</div>
''')

rep('''  <h2>Shop settings</h2>
''', '''  <h2>Shop settings</h2>

  <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px">
    <b>Language</b>
    ''' + SWITCH + '''
  </div>
''')

rep('<div class="splash" id="splash">', '<div class="splash" id="splash" data-no-i18n>')

for cat in ["Fabric/Material", "Food", "Rent", "Transport", "Wages", "Utilities", "Other"]:
    rep(f"<option>{cat}</option>", f'<option value="{cat}">{cat}</option>')

rep('<label>PRICE (<span class="curr">TSh</span>)</label>', '<label><span>PRICE</span> (<span class="curr">TSh</span>)</label>')
rep('<label>AMOUNT PAID SO FAR (<span class="curr">TSh</span>)</label>', '<label><span>AMOUNT PAID SO FAR</span> (<span class="curr">TSh</span>)</label>')
assert src.count('<label>AMOUNT (<span class="curr">TSh</span>)</label>') == 2
src = src.replace('<label>AMOUNT (<span class="curr">TSh</span>)</label>', '<label><span>AMOUNT</span> (<span class="curr">TSh</span>)</label>')

ENGINE = r'''<script>

/* -----------------------------
   LANGUAGE (English / Swahili)

   The Swahili dictionary is keyed by the exact English text. Anything on
   screen whose text matches a key is shown in Swahili, including things
   that appear later (lists, pop-ups, messages). Text that has no entry is
   simply left as it is, so a missing phrase can never break a screen.
   Stored data (order stages, expense categories...) always stays in
   English underneath; only what is shown changes.
----------------------------- */

const LANG_KEY = "nyuzi_lang";
const I18N_SKIP = "script, style, textarea, [data-no-i18n]";

/* I18N-DICTIONARY-START */
const SW = {};
/* I18N-DICTIONARY-END */

function detectLanguage() {

  let saved = null;

  try { saved = localStorage.getItem(LANG_KEY); } catch (e) {}

  if (saved === "en" || saved === "sw") return saved;

  // First time: follow the phone's own language
  const phone = ((navigator.languages && navigator.languages[0]) || navigator.language || "en").toLowerCase();

  return phone.startsWith("sw") ? "sw" : "en";

}

let currentLang = detectLanguage();

// t("Some text") -> Swahili when the app is in Swahili and a phrase exists.
// Phrases with blanks use {name}: t("{name} is saved", { name: "Juma" })
function t(key, vars) {

  let text = (currentLang === "sw" && SW[key] !== undefined) ? SW[key] : key;

  if (vars) text = text.replace(/\{(\w+)\}/g, (match, k) => vars[k] !== undefined ? vars[k] : match);

  return text;

}

let dateLocaleCache = null;

function dateLocale() {

  if (currentLang !== "sw") return "en-GB";

  if (dateLocaleCache === null) {
    dateLocaleCache = (Intl.DateTimeFormat.supportedLocalesOf(["sw-TZ"]).length ? "sw-TZ" : "en-GB");
  }

  return dateLocaleCache;

}

function i18nNormalize(text) {

  return text.replace(/\s+/g, " ").trim();

}

function applyTextNode(node) {

  const parent = node.parentElement;
  if (!parent || parent.closest(I18N_SKIP)) return;

  const original = node.__en !== undefined ? node.__en : node.nodeValue;
  const key = i18nNormalize(original);
  if (!key) return;

  const translated = currentLang === "sw" ? SW[key] : undefined;

  if (translated !== undefined) {

    if (node.__en === undefined) node.__en = original;

    const lead = original.match(/^\s*/)[0];
    const trail = original.match(/\s*$/)[0];
    const next = lead + translated + trail;

    if (node.nodeValue !== next) node.nodeValue = next;

  } else if (node.__en !== undefined) {

    // Back to English: restore exactly what was there
    node.nodeValue = node.__en;
    delete node.__en;

  }

}

function applyPlaceholder(el) {

  const original = el.__enPh !== undefined ? el.__enPh : el.getAttribute("placeholder");
  if (!original) return;

  const translated = currentLang === "sw" ? SW[i18nNormalize(original)] : undefined;

  if (translated !== undefined) {

    if (el.__enPh === undefined) el.__enPh = original;
    el.setAttribute("placeholder", translated);

  } else if (el.__enPh !== undefined) {

    el.setAttribute("placeholder", el.__enPh);
    delete el.__enPh;

  }

}

function translateTree(root) {

  if (root.nodeType === 3) { applyTextNode(root); return; }
  if (root.nodeType !== 1) return;
  if (root.closest && root.closest(I18N_SKIP)) return;

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];

  let node;
  while ((node = walker.nextNode())) nodes.push(node);

  nodes.forEach(applyTextNode);

  if (root.hasAttribute && root.hasAttribute("placeholder")) applyPlaceholder(root);
  root.querySelectorAll("[placeholder]").forEach(applyPlaceholder);

}

function applyLanguage() {

  document.documentElement.lang = currentLang;

  translateTree(document.body);

  document.querySelectorAll(".lang-switch button").forEach(button => {
    button.classList.toggle("active", button.dataset.lang === currentLang);
  });

}

function setLanguage(lang) {

  if (lang !== "en" && lang !== "sw") return;

  currentLang = lang;

  try { localStorage.setItem(LANG_KEY, lang); } catch (e) {}

  applyLanguage();
  refreshLanguageDependentUI();

}

// Things built from pieces of text need rebuilding in the new language
function refreshLanguageDependentUI() {

  renderInstallNudge();
  renderBackupNudge();
  renderSyncStatus();
  renderBackupStatus();

  if (!dbReady) return;

  const active = document.querySelector(".screen.active");
  if (!active) return;

  if (active.id === "customers") renderCustomers(customerSearch.value);
  if (active.id === "orders") renderOrders();
  if (active.id === "business") renderBusinessScreen();
  if (active.id === "home") applyShopBranding();

}

// Anything added to the page later (lists, pop-ups, messages) is translated as it appears
new MutationObserver(mutations => {

  if (currentLang !== "sw") return;

  mutations.forEach(mutation => mutation.addedNodes.forEach(translateTree));

}).observe(document.body, { childList: true, subtree: true });

applyLanguage();


/* -----------------------------
   SUPABASE CONNECTION (Nyuzi House project)
----------------------------- */'''

rep('''<script>

/* -----------------------------
   SUPABASE CONNECTION (Nyuzi House project)
----------------------------- */''', ENGINE)

open(p, "w", encoding="utf-8").write(src)
print("stage 1 ok", len(src))
