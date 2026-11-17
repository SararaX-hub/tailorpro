# Step 4: public directory slice — first screen (what do you do), find-a-maker, public profiles.
import re
p = "/home/claude/pwa/index.html"
src = open("/mnt/user-data/outputs/wip/base-v16-language.html", encoding="utf-8").read()
failed = []

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        failed.append((n, old[:100])); return
    src = src.replace(old, new)

SWITCH = '''<div class="lang-switch" data-no-i18n><button data-lang="en" onclick="setLanguage('en')">EN</button><button data-lang="sw" onclick="setLanguage('sw')">SW</button></div>'''

CRAFT_OPTIONS = '''<option value="Tailor">Tailor</option>
      <option value="Leather maker">Leather maker</option>
      <option value="Boutique">Boutique</option>
      <option value="Fabric store">Fabric store</option>
      <option value="Other">Other</option>'''

# ---------- head: makers keep the brand splash; first-time visitors and browsers don't see it ----------
rep('<meta charset="UTF-8">', '''<meta charset="UTF-8">
<script>try { if (localStorage.getItem("nyuzi_role") !== "maker") document.documentElement.classList.add("no-splash"); } catch (e) {}</script>''')

# ---------- CSS ----------
rep('''#onboarding.active,
#auth.active {''', '''#onboarding.active,
#welcome.active,
#auth.active {''')

rep('.lang-switch {', '''html.no-splash #splash {
  display: none;
}

.welcome-hint {
  text-align: center;
  color: rgba(255,255,255,0.75);
  font-size: 12px;
  margin: 8px 0 22px;
  animation: riseIn 0.5s ease-out 0.55s both;
}

.btn.welcome-alt {
  background: rgba(255,255,255,0.16);
  color: white;
  margin-top: 0;
  animation: riseIn 0.5s ease-out 0.7s both;
}

.link-btn {
  border: none;
  background: none;
  color: var(--primary);
  font-weight: 600;
  font-size: 13px;
  padding: 6px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.two-col select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 11px;
  font-size: 16px;
  font-family: inherit;
  background: white;
}

.maker-card {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 16px;
  margin-bottom: 10px;
  background: white;
}

.maker-thumb {
  width: 64px;
  height: 64px;
  border-radius: 14px;
  background: var(--primary-light);
  display: grid;
  place-items: center;
  font-size: 26px;
  overflow: hidden;
  flex-shrink: 0;
}

.maker-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.maker-info {
  flex: 1;
  min-width: 0;
}

.maker-name {
  font-weight: 700;
}

.maker-bio {
  font-size: 12px;
  color: #555;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.craft-pill {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
}

.portfolio-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 10px 0 18px;
}

.portfolio-grid img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 12px;
  display: block;
}

.portfolio-edit {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 10px;
}

.portfolio-edit .pe-item {
  position: relative;
}

.portfolio-edit img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 10px;
  display: block;
}

.portfolio-edit .pe-x {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.6);
  color: white;
  font-size: 12px;
}

.btn.wa-btn {
  background: #25D366;
  color: white;
}

.lang-switch {''')

# ---------- HTML: Home gets Explore + My profile ----------
rep('''    <div style="color:#888">›</div>
  </button>
''', '''    <div style="color:#888">›</div>
  </button>

  <div class="grid" style="margin-top:12px">
    <button class="card action" onclick="openExplore('maker')" style="height:auto; padding:16px">
      🔎
      <b>Explore</b>
      <span>Find other makers</span>
    </button>
    <button class="card action" onclick="openMyProfile()" style="height:auto; padding:16px">
      🏪
      <b>My profile</b>
      <span id="homeProfileStatus">Let customers find you</span>
    </button>
  </div>
''')

# ---------- HTML: login screen escape hatch ----------
src, n = re.subn(r'(onclick="submitAuth\(\)">Log In</button>\s*</div>\s*</div>)',
                 r'''\1

    <button class="onboarding-skip" onclick="chooseRole('browser')">Looking for a maker instead?</button>''', src, count=1)
if n != 1: failed.append((n, "auth escape hatch"))

# ---------- HTML: new screens ----------
rep('<!-- BUSINESS (PRO) -->', '''<!-- WELCOME: what do you do? -->
<section id="welcome" class="screen onboarding-screen">

  <div class="auth-lang">''' + SWITCH + '''</div>

  <div class="onboarding-inner">

    <h1 class="auth-title">NYUZI<br>HOUSE</h1>
    <p class="auth-sub">What do you do?</p>

    <button class="btn onboarding-cta" style="margin-top:0" onclick="chooseRole('maker')">I make or sell things</button>
    <p class="welcome-hint">Tailors, leather makers, boutiques, fabric stores</p>

    <button class="btn welcome-alt" onclick="chooseRole('browser')">I'm looking for a maker</button>

  </div>

</section>


<!-- EXPLORE: find a maker -->
<section id="explore" class="screen">

  <div class="top">
    <button class="back" id="exploreBack" onclick="show('home')">‹ Home</button>
    <div style="display:flex; align-items:center; gap:8px; padding-bottom:20px">
      ''' + SWITCH + '''
      <button class="link-btn" id="exploreMakerLink" onclick="chooseRole('maker')">I'm a maker ›</button>
    </div>
  </div>

  <h2>Find a maker</h2>

  <div class="search" style="margin-top:0">
    🔍
    <input id="exploreSearch" placeholder="e.g. Morogoro, Kihonda" oninput="renderExplore()">
  </div>

  <div class="two-col">
    <select id="exploreRegion" onchange="renderExplore()">
      <option value="">All regions</option>
    </select>
    <select id="exploreCraft" onchange="renderExplore()">
      <option value="">All crafts</option>
      ''' + CRAFT_OPTIONS + '''
    </select>
  </div>

  <div id="exploreList"></div>

</section>


<!-- A MAKER'S PUBLIC PROFILE (what customers see) -->
<section id="makerProfile" class="screen">

  <button class="back" onclick="closeMakerProfile()">‹ Back</button>

  <div id="makerProfileContent"></div>

</section>


<!-- MY PUBLIC PROFILE (editor) -->
<section id="myProfile" class="screen">

  <button class="back" onclick="show('home')">‹ Home</button>

  <h2>My public profile</h2>

  <p class="muted" style="margin-top:-8px">This is what customers see when they search. Your customers, orders and money are never shown.</p>

  <div class="form">

    <label>SHOP NAME</label>
    <input id="profShopName" placeholder="e.g. SARARA Tailoring">

    <label>CRAFT</label>
    <select id="profCraft">
      ''' + CRAFT_OPTIONS + '''
    </select>

    <label>REGION</label>
    <select id="profRegion">
      <option value="">Choose region</option>
    </select>

    <label>AREA (OPTIONAL)</label>
    <input id="profArea" placeholder="e.g. Kihonda">

    <label>WHATSAPP NUMBER</label>
    <input id="profWhatsapp" inputmode="tel" placeholder="0712 345 678">

    <label>ABOUT YOU (OPTIONAL)</label>
    <textarea id="profBio" maxlength="240" placeholder="e.g. Suits and kanzu, 8 years of experience"></textarea>

    <label>PORTFOLIO PHOTOS (UP TO 6)</label>
    <div id="profPhotos" class="portfolio-edit"></div>
    <input id="profPhotoInput" type="file" accept="image/*" style="display:none" onchange="handlePortfolioPhoto(event)">
    <button class="btn secondary" id="profAddPhotoBtn" onclick="profPhotoInput.click()">＋ Add a photo</button>

    <div class="checkbox-row" style="margin-top:20px">
      <input type="checkbox" id="profPublished">
      <label for="profPublished">Show me in the directory</label>
    </div>
    <p class="muted" style="margin:6px 0 0">Off means only you can see this profile.</p>

    <br>

    <button class="btn" onclick="saveMyProfile()">Save profile</button>
    <button class="btn secondary" style="margin-top:10px" onclick="previewMyProfile()">Preview</button>

  </div>

</section>


<!-- BUSINESS (PRO) -->''')

# ---------- JS: data model ----------
rep('''  income: [],
  meta: { lastBackup: null, installDismissed: false, onboarded: false }
};''', '''  income: [],
  publicProfile: null,
  meta: { lastBackup: null, installDismissed: false, onboarded: false }
};''')
rep('  database.income = Array.isArray(loaded.income) ? loaded.income : [];',
    '  database.income = Array.isArray(loaded.income) ? loaded.income : [];\n  database.publicProfile = loaded.publicProfile || null;')
rep('    database.meta.onboarded = shopRes.data.onboarded;', '''    database.meta.onboarded = shopRes.data.onboarded;

    // The public profile is optional and never allowed to break loading
    try {
      const profileRes = await sb.from("public_profiles").select("*").eq("shop_id", uid);
      if (!profileRes.error && Array.isArray(profileRes.data)) {
        database.publicProfile = profileRes.data[0] ? dbProfileToLocal(profileRes.data[0]) : null;
      }
    } catch (e) {}''')

# ---------- JS: REST client learns "upsert" ----------
rep('    let wantSingle = false;', '    let wantSingle = false;\n    let upsertFlag = false;')
rep('      insert(obj) { mode = "insert"; payload = obj; return builder; },',
    '      insert(obj) { mode = "insert"; payload = obj; return builder; },\n      upsert(obj) { mode = "insert"; payload = obj; upsertFlag = true; return builder; },')
rep('        if (mode === "insert" || mode === "update") headers.Prefer = "return=representation";',
    '        if (upsertFlag) headers.Prefer = "resolution=merge-duplicates,return=representation";\n        else if (mode === "insert" || mode === "update") headers.Prefer = "return=representation";')
rep('''      const { error } = op.isInsert
        ? await sb.from(op.table).insert(op.payload)
        : await sb.from(op.table).update(op.payload).eq("id", op.rowId);''', '''      const { error } = op.isInsert
        ? (op.upsert ? await sb.from(op.table).upsert(op.payload) : await sb.from(op.table).insert(op.payload))
        : await sb.from(op.table).update(op.payload).eq("id", op.rowId);''')

# ---------- JS: screens that work before login, and where the bottom bar hides ----------
rep('const screensBeforeLogin = ["loading", "auth"];', 'const screensBeforeLogin = ["loading", "auth", "welcome", "explore", "makerProfile"];')
rep('  document.getElementById("app").classList.toggle("onboarding-active", screen === "onboarding");', '''  const hideBar = screen === "onboarding" || screen === "welcome" ||
    (exploreMode === "browser" && (screen === "explore" || screen === "makerProfile"));

  document.getElementById("app").classList.toggle("onboarding-active", hideBar);''')

# language switch must also refresh the new screens
rep('  renderBackupStatus();\n\n  if (!dbReady) return;', '''  renderBackupStatus();
  updateHomeProfileStatus();

  if (document.querySelector("#explore.active")) renderExplore();
  if (document.querySelector("#makerProfile.active") && shownProfile) renderMakerProfile(shownProfile);

  if (!dbReady) return;''')

# ---------- JS: the directory itself ----------
DIRECTORY_JS = r'''/* -----------------------------
   PUBLIC DIRECTORY — profiles anyone can browse, and each maker's own profile
----------------------------- */

const ROLE_KEY = "nyuzi_role";
const PORTFOLIO_MAX = 6;
const TZ_REGIONS = [
  "Arusha", "Dar es Salaam", "Dodoma", "Geita", "Iringa", "Kagera", "Katavi", "Kigoma", "Kilimanjaro",
  "Lindi", "Manyara", "Mara", "Mbeya", "Morogoro", "Mtwara", "Mwanza", "Njombe", "Pwani", "Rukwa",
  "Ruvuma", "Shinyanga", "Simiyu", "Singida", "Songwe", "Tabora", "Tanga",
  "Mjini Magharibi", "Kaskazini Unguja", "Kusini Unguja", "Kaskazini Pemba", "Kusini Pemba"
];
const CRAFT_ICONS = { "Tailor": "🧵", "Leather maker": "👜", "Boutique": "👗", "Fabric store": "🧶", "Other": "✨" };

let exploreMode = "maker";
let exploreData = [];
let exploreState = "idle";     // idle | loading | ok | error
let exploreFromCache = false;
let makerBackTarget = "explore";
let editingPhotos = [];
let shownProfile = null;
let makerFlowStarted = false;

function savedRole() {

  try { return localStorage.getItem(ROLE_KEY); } catch (e) { return null; }

}

function saveRole(role) {

  try { localStorage.setItem(ROLE_KEY, role); } catch (e) {}

}

// wa.me needs the number with the country code and no leading 0
function waNumber(phone) {

  let digits = (phone || "").replace(/\D/g, "");

  if (digits.startsWith("00")) digits = digits.slice(2);
  if (digits.startsWith("0")) digits = "255" + digits.slice(1);
  if (digits.length === 9) digits = "255" + digits;

  return digits;

}

function dbProfileToLocal(row) {

  return {
    shopId: row.shop_id,
    shopName: row.shop_name || "",
    craft: row.craft || "Tailor",
    region: row.region || "",
    area: row.area || "",
    whatsapp: row.whatsapp || "",
    bio: row.bio || "",
    photos: Array.isArray(row.photo_paths) ? row.photo_paths : [],
    published: !!row.published,
  };

}

function fillRegionSelects() {

  const options = TZ_REGIONS.map(r => `<option value="${r}">${r}</option>`).join("");

  exploreRegion.insertAdjacentHTML("beforeend", options);
  profRegion.insertAdjacentHTML("beforeend", options);

}

fillRegionSelects();

function chooseRole(role) {

  saveRole(role);

  if (role === "browser") {

    document.documentElement.classList.add("no-splash");
    openExplore("browser");

  } else {

    // Makers get the brand moment, then the usual start
    const splash = document.getElementById("splash");

    document.documentElement.classList.remove("no-splash");
    splash.classList.remove("fade-out");

    setTimeout(startMakerFlow, 1600);

  }

}

async function startMakerFlow() {

  document.getElementById("splash").classList.add("fade-out");

  const { data } = await sb.auth.getSession();

  if (data.session) {

    currentSession = data.session;
    await loadDatabase();

  } else {

    show("auth");

  }

}

async function bootApp() {

  connectSupabase();

  // Reading the saved login uses this phone's own storage, so it works offline
  const { data } = await sb.auth.getSession();
  const role = savedRole();

  if (data.session) {

    // A maker who was already using the app before this update
    if (role !== "maker") saveRole("maker");

    document.documentElement.classList.remove("no-splash");
    setTimeout(startMakerFlow, 1600);
    return;

  }

  if (role === "maker") {

    setTimeout(startMakerFlow, 1600);
    return;

  }

  // First-time visitors and browsers: no brand splash, straight to the point
  if (role === "browser") openExplore("browser");
  else show("welcome");

}

async function openExplore(mode) {

  exploreMode = mode;

  exploreBack.style.display = mode === "maker" ? "" : "none";
  exploreMakerLink.style.display = mode === "browser" ? "" : "none";

  show("explore");
  renderExplore();

  await loadExplore();

}

async function loadExplore() {

  exploreState = "loading";
  exploreFromCache = false;
  renderExplore();

  const { data, error } = await sb.from("public_profiles").select("*").eq("published", "true").order("updated_at", { ascending: false });

  if (error) {

    const raw = await storageGet("explore_cache");

    if (raw) {
      try { exploreData = JSON.parse(raw); exploreFromCache = true; } catch (e) {}
    }

    exploreState = "error";

  } else {

    exploreData = data.map(dbProfileToLocal);
    exploreState = "ok";

    await storageSet("explore_cache", JSON.stringify(exploreData));

  }

  renderExplore();

}

function renderExplore() {

  const query = exploreSearch.value.trim().toLowerCase();
  const region = exploreRegion.value;
  const craft = exploreCraft.value;

  if (exploreState === "loading" && !exploreData.length) {
    exploreList.innerHTML = `<div class="empty">${t("Looking for makers…")}</div>`;
    return;
  }

  if (exploreState === "error" && !exploreData.length) {
    exploreList.innerHTML = `<div class="empty">${t("Couldn't load makers. Check your internet and try again.")}<br><br><button class="btn secondary" onclick="loadExplore()">${t("Try again")}</button></div>`;
    return;
  }

  const matches = exploreData.filter(p =>
    (!region || p.region === region) &&
    (!craft || p.craft === craft) &&
    (!query || [p.shopName, p.region, p.area, p.craft, t(p.craft), p.bio].join(" ").toLowerCase().includes(query))
  );

  const note = exploreFromCache ? `<p class="muted" style="margin:0 0 10px">${t("Showing makers saved on this phone.")}</p>` : "";

  if (!matches.length) {

    const message = exploreData.length ? "No makers found. Try another area or craft." : "No makers have joined yet. Check back soon!";

    exploreList.innerHTML = note + `<div class="empty">${t(message)}</div>`;
    return;

  }

  exploreList.innerHTML = note + matches.map(p => `
    <div class="maker-card" onclick="openMakerProfile('${p.shopId}')">
      <div class="maker-thumb">${p.photos[0] ? `<img src="${escapeAttr(publicPhotoUrl(p.photos[0]))}">` : (CRAFT_ICONS[p.craft] || "✨")}</div>
      <div class="maker-info">
        <div class="maker-name">${escapeHtml(p.shopName)}</div>
        <div class="muted">${escapeHtml(t(p.craft))} · ${escapeHtml(p.region)}${p.area ? ", " + escapeHtml(p.area) : ""}</div>
        ${p.bio ? `<div class="maker-bio">${escapeHtml(p.bio)}</div>` : ""}
      </div>
      <div class="chev">›</div>
    </div>
  `).join("");

}

function openMakerProfile(shopId) {

  shownProfile = exploreData.find(p => p.shopId === shopId);
  if (!shownProfile) return;

  makerBackTarget = "explore";
  renderMakerProfile(shownProfile);
  show("makerProfile");

}

function photoSrc(path) {

  return path.startsWith("data:") ? path : publicPhotoUrl(path);

}

function renderMakerProfile(p) {

  const greeting = encodeURIComponent(t("Hello, I found you on Nyuzi House."));
  const photos = (p.photos || []).map(path => `<img src="${escapeAttr(photoSrc(path))}">`).join("");

  makerProfileContent.innerHTML = `
    <div class="maker-thumb" style="width:84px; height:84px; font-size:34px; margin:0 auto 10px">${p.photos && p.photos[0] ? `<img src="${escapeAttr(photoSrc(p.photos[0]))}">` : (CRAFT_ICONS[p.craft] || "✨")}</div>
    <h2 style="margin:0 0 6px; text-align:center">${escapeHtml(p.shopName)}</h2>
    <div style="text-align:center"><span class="craft-pill">${escapeHtml(t(p.craft))}</span></div>
    <p class="muted" style="text-align:center; margin:8px 0 18px">📍 ${escapeHtml(p.region)}${p.area ? ", " + escapeHtml(p.area) : ""}</p>

    ${p.bio ? `<p style="line-height:1.5">${escapeHtml(p.bio)}</p>` : ""}

    <a class="btn wa-btn" href="https://wa.me/${waNumber(p.whatsapp)}?text=${greeting}" target="_blank" rel="noopener" style="margin:16px 0 10px">💬 ${t("Message on WhatsApp")}</a>
    <a class="btn secondary" href="tel:${escapeAttr(p.whatsapp)}">${t("Call")}</a>

    <div style="margin:22px 0 4px"><b>${t("Portfolio")}</b></div>
    ${photos ? `<div class="portfolio-grid">${photos}</div>` : `<p class="muted">${t("No photos yet")}</p>`}
  `;

}

function closeMakerProfile() {

  show(makerBackTarget === "myProfile" ? "myProfile" : "explore");

}

function phoneFromLogin() {

  const email = (currentSession && currentSession.user && currentSession.user.email) || "";
  let digits = email.split("@")[0].replace(/\D/g, "");

  if (digits.startsWith("255")) digits = "0" + digits.slice(3);

  return digits;

}

function openMyProfile() {

  const p = database.publicProfile || {};

  profShopName.value = p.shopName || database.shop.name || "";
  profCraft.value = p.craft || "Tailor";
  profRegion.value = p.region || "";
  profArea.value = p.area || "";
  profWhatsapp.value = p.whatsapp || phoneFromLogin();
  profBio.value = p.bio || "";
  profPublished.checked = !!p.published;

  editingPhotos = (p.photos || []).slice();
  renderPortfolioEditor();

  show("myProfile");

}

function renderPortfolioEditor() {

  profPhotos.innerHTML = editingPhotos.map((path, i) => `
    <div class="pe-item">
      <img src="${escapeAttr(photoSrc(path))}">
      <button class="pe-x" onclick="removePortfolioPhoto(${i})">✕</button>
    </div>
  `).join("");

  profAddPhotoBtn.style.display = editingPhotos.length >= PORTFOLIO_MAX ? "none" : "block";

}

function removePortfolioPhoto(index) {

  editingPhotos.splice(index, 1);
  renderPortfolioEditor();

}

function handlePortfolioPhoto(event) {

  const file = event.target.files[0];
  event.target.value = "";

  if (!file) return;

  if (editingPhotos.length >= PORTFOLIO_MAX) {
    showAlert(t("You can add up to 6 photos."));
    return;
  }

  readAndCompressImage(file, 900, 0.65, async dataUrl => {

    showToast(t("Uploading photo…"));

    try {

      const path = await uploadPhoto(dataUrl, "portfolio");

      editingPhotos.push(path);
      renderPortfolioEditor();

    } catch (err) {

      showAlert(t("Photos need an internet connection. Connect and try again."));

    }

  });

}

function readProfileForm() {

  return {
    shopId: currentSession ? currentSession.user.id : null,
    shopName: profShopName.value.trim(),
    craft: profCraft.value,
    region: profRegion.value,
    area: profArea.value.trim(),
    whatsapp: profWhatsapp.value.trim(),
    bio: profBio.value.trim(),
    photos: editingPhotos.slice(),
    published: profPublished.checked,
  };

}

async function saveMyProfile() {

  const profile = readProfileForm();

  const complete = profile.shopName && profile.region && waNumber(profile.whatsapp).length >= 11;

  if (profile.published && !complete) {
    showAlert(t("To appear in the directory, add your shop name, region and WhatsApp number."));
    return;
  }

  const uid = currentSession.user.id;

  const payload = {
    shop_id: uid,
    shop_name: profile.shopName,
    craft: profile.craft,
    region: profile.region,
    area: profile.area || null,
    whatsapp: profile.whatsapp,
    bio: profile.bio || null,
    photo_paths: profile.photos,
    published: profile.published,
    updated_at: new Date().toISOString(),
  };

  database.publicProfile = profile;

  await saveDatabase();
  await enqueue({ kind: "upsert", table: "public_profiles", isInsert: true, upsert: true, payload });

  updateHomeProfileStatus();
  showToast(t("Profile saved"));
  show("home");

}

function previewMyProfile() {

  shownProfile = readProfileForm();
  makerBackTarget = "myProfile";

  renderMakerProfile(shownProfile);
  show("makerProfile");

}

function updateHomeProfileStatus() {

  const p = database.publicProfile;

  homeProfileStatus.textContent = p && p.published
    ? t("Visible to customers")
    : p ? t("Hidden — only you can see it") : t("Let customers find you");

}


/* -----------------------------
   BUSINESS (PRO) — income, expenses, monthly totals
----------------------------- */'''

rep('''/* -----------------------------
   BUSINESS (PRO) — income, expenses, monthly totals
----------------------------- */''', DIRECTORY_JS)

# ---------- JS: boot now decides between the welcome question, browsing, and the maker flow ----------
src, n = re.subn(r'setTimeout\(async \(\) => \{\s*document\.getElementById\("splash"\)\.classList\.add\("fade-out"\);.*?\}, 1600\);',
                 'bootApp();', src, count=1, flags=re.S)
if n != 1: failed.append((n, "boot block"))

# status line on Home after data loads
rep('''  applyShopBranding();

  document.getElementById("loading").classList.remove("active");

  if (database.meta.onboarded) {''', '''  applyShopBranding();
  updateHomeProfileStatus();

  document.getElementById("loading").classList.remove("active");

  if (database.meta.onboarded) {''', count=2) if False else None

open(p, "w", encoding="utf-8").write(src)
print("not applied:", len(failed))
for n, o in failed: print("   found", n, "x:", o)
