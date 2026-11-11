import json, re, urllib.parse
from playwright.sync_api import sync_playwright

APP_URL = "file:///home/claude/pwa/index.html"
HOST_RE = re.compile(r"https://iygsxhvoxsbywuhnblmq\.supabase\.co/.*")
CORS = {"access-control-allow-origin": "*", "access-control-allow-headers": "*",
        "access-control-allow-methods": "GET,POST,PATCH,DELETE,OPTIONS"}


class FakeSupabase:
    """A stand-in for Supabase's Auth, REST and Storage APIs."""

    def __init__(self):
        self.tables = {"shops": [], "customers": [], "orders": [], "expenses": [], "income_entries": []}
        self.uploads = []
        self.offline = False
        self.persistent_fail = False
        self.reject_login = False
        self.onboarded_default = True
        self.counter = 1000

    def install(self, context):
        context.route(HOST_RE, self.handle)
        context.route(re.compile(r"https://fonts\.(googleapis|gstatic)\.com/.*"), lambda r: r.abort())

    def reply(self, route, status, body=None):
        h = dict(CORS); h["content-type"] = "application/json"
        route.fulfill(status=status, headers=h, body=json.dumps(body) if body is not None else "")

    def handle(self, route):
        req = route.request
        parsed = urllib.parse.urlparse(req.url)
        path, query = parsed.path, urllib.parse.parse_qs(parsed.query)
        if req.method == "OPTIONS":
            return route.fulfill(status=204, headers=CORS)
        if self.offline:
            return route.abort("internetdisconnected")
        body = {}
        if req.post_data and "application/json" in (req.headers.get("content-type") or ""):
            try: body = json.loads(req.post_data)
            except Exception: body = {}
        if path == "/auth/v1/token":
            if self.reject_login:
                return self.reply(route, 400, {"error_description": "Invalid login credentials"})
            email = body.get("email", "x@x"); uid = "uid-" + email
            if not any(s["id"] == uid for s in self.tables["shops"]):
                self.tables["shops"].append({"id": uid, "name": "Nyuzi House", "currency": "TSh",
                                             "cover_photo_path": None, "onboarded": self.onboarded_default})
            return self.reply(route, 200, {"access_token": "tok-" + uid, "refresh_token": "ref-" + uid,
                                           "user": {"id": uid, "email": email}})
        if path.endswith("/functions/v1/signup"):
            return self.reply(route, 200, {"success": True})
        if path.startswith("/storage/v1/object/"):
            self.uploads.append(path)
            return self.reply(route, 200, {"Key": path})
        if path.startswith("/rest/v1/"):
            table = path[len("/rest/v1/"):]
            rows = self.tables[table]
            filters = {k: urllib.parse.unquote(v[0][3:]) for k, v in query.items() if v and v[0].startswith("eq.")}
            match = lambda r: all(str(r.get(k)) == v for k, v in filters.items())
            if self.persistent_fail:
                return self.reply(route, 400, {"message": "simulated server error", "code": "SIM"})
            if req.method == "GET":
                found = [r for r in rows if match(r)]
                if "vnd.pgrst.object" in (req.headers.get("accept") or ""):
                    return self.reply(route, 200, found[0]) if found else self.reply(route, 406, {"message": "no rows"})
                return self.reply(route, 200, found)
            if req.method == "POST":
                items = body if isinstance(body, list) else [body]
                for item in items:
                    row = {"created_at": "2026-11-02T10:00:00Z", "updated_at": "2026-11-02T10:00:00Z", **item}
                    if "id" not in row:
                        self.counter += 1; row["id"] = f"row{self.counter}"
                    rows.append(row)
                return self.reply(route, 201, items)
            if req.method == "PATCH":
                found = [r for r in rows if match(r)]
                for r in found: r.update(body)
                return self.reply(route, 200, found)
            if req.method == "DELETE":
                removed = [r for r in rows if match(r)]
                self.tables[table] = [r for r in rows if not match(r)]
                if table == "customers":
                    ids = {r["id"] for r in removed}
                    self.tables["orders"] = [o for o in self.tables["orders"] if o.get("customer_id") not in ids]
                return route.fulfill(status=204, headers=CORS)
        return self.reply(route, 404, {"message": "unhandled " + path})


class Session:
    def __init__(self, fake, locale="en-US", viewport=(390, 844), user_agent=None):
        self.fake = fake
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch()
        kw = {"user_agent": user_agent} if user_agent else {}
        self.ctx = self.browser.new_context(viewport={"width": viewport[0], "height": viewport[1]}, locale=locale, **kw)
        fake.install(self.ctx)
        self.errors = []
        self.page = None
        self.open()

    def open(self):
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append("PAGEERROR: " + str(e)))
        self.page.goto(APP_URL)
        return self.page

    def close(self):
        self.browser.close(); self.pw.stop()

    def wait_boot(self, screen):
        self.page.wait_for_selector(f"#{screen}.active", timeout=15000)

    def login(self, phone="0712345678", password="password1"):
        p = self.page
        p.fill("#authPhone", phone); p.fill("#authPassword", password); p.click("#authSubmitBtn")
        p.wait_for_selector("#home.active, #onboarding.active", timeout=15000)

    def text_nodes(self):
        """Visible-text nodes as currently shown (skipping brand/protected areas)."""
        return self.page.evaluate("""() => {
            const out = [];
            const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let n;
            while ((n = w.nextNode())) {
                const el = n.parentElement;
                if (!el || el.closest('script,style,textarea,[data-no-i18n]')) continue;
                const shown = n.nodeValue.replace(/\\s+/g, ' ').trim();
                const orig = (n.__en !== undefined ? n.__en : n.nodeValue).replace(/\\s+/g, ' ').trim();
                if (shown) out.push([orig, shown]);
            }
            document.querySelectorAll('[placeholder]').forEach(e => out.push([(e.__enPh !== undefined ? e.__enPh : e.getAttribute('placeholder')), e.getAttribute('placeholder')]));
            return out;
        }""")
