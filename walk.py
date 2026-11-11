"""Walk the whole app and record every piece of text shown. Returns {original: [shown, screen]}"""
import sys
sys.path.insert(0, "/mnt/user-data/outputs/wip/pw")
from harness import FakeSupabase, Session

IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


def walk(lang_locale="en-US"):
    seen = {}

    def snap(s, label):
        for orig, shown in s.text_nodes():
            seen.setdefault(orig, [shown, label])

    fake = FakeSupabase(); fake.onboarded_default = False
    s = Session(fake, locale=lang_locale, user_agent=IPHONE)
    p = s.page
    s.wait_boot("auth"); snap(s, "auth-login")
    p.click("#authTabSignup"); snap(s, "auth-signup"); p.click("#authTabLogin")
    p.fill("#authPhone", "123"); p.fill("#authPassword", "abc"); p.click("#authSubmitBtn"); snap(s, "auth-error-phone")
    p.fill("#authPhone", "0712345678"); p.click("#authSubmitBtn"); snap(s, "auth-error-pw")
    fake.reject_login = True
    p.fill("#authPassword", "password1"); p.click("#authSubmitBtn"); p.wait_for_timeout(500); snap(s, "auth-error-wrong")
    fake.reject_login = False
    s.login(); snap(s, "onboarding")
    p.fill("#onboardShopName", "Test Shop"); p.click(".onboarding-cta"); p.wait_for_selector("#home.active")
    p.wait_for_timeout(400); snap(s, "home-empty")
    for scr in ["customers", "orders", "settings"]:
        p.evaluate(f"show('{scr}')"); snap(s, scr + "-empty")
    p.evaluate("openBusiness()"); snap(s, "business-empty")
    p.evaluate("newExpense()"); snap(s, "expense-form")
    p.evaluate("saveExpense()"); snap(s, "expense-alert"); p.evaluate("closeModal()")
    p.fill("#expenseAmount", "5000"); p.evaluate("saveExpense()"); p.wait_for_timeout(300); snap(s, "expense-saved")
    p.evaluate("newIncome()"); snap(s, "income-form")
    p.fill("#incomeAmount", "7000"); p.evaluate("saveIncomeEntry()"); p.wait_for_timeout(300); snap(s, "income-saved")
    p.evaluate("newCustomer()"); snap(s, "customer-form")
    p.evaluate("saveCustomer()"); snap(s, "customer-alert"); p.evaluate("closeModal()")
    p.fill("#newName", "Juma Mwita"); p.fill("#newPhone", "0798764321"); p.fill("#newNotes", "Prefers slim fit"); p.check("#newVip")
    p.evaluate("saveCustomer()"); p.wait_for_timeout(400); snap(s, "customer-saved-sheet")
    p.evaluate("closeModal(); startMeasurementsChain()"); snap(s, "measurements-suit")
    for tab in ["shirt", "trouser", "kanzu", "dress", "skirt"]:
        p.evaluate(f"switchMeasurementType('{tab}')"); snap(s, "measurements-" + tab)
    p.evaluate("saveMeasurements()"); snap(s, "measurements-alert"); p.evaluate("closeModal()")
    p.evaluate("switchMeasurementType('shirt')"); p.fill("#m_neck", "15.5")
    p.evaluate("saveMeasurements()"); p.wait_for_timeout(400); snap(s, "order-form-new")
    p.fill("#orderGarment", "Two-piece suit"); p.fill("#orderPrice", "350000"); p.fill("#orderPaid", "100000"); p.fill("#orderDue", "2026-12-01")
    p.evaluate("saveOrder()"); p.wait_for_timeout(400); snap(s, "orders-list")
    oid = p.evaluate("database.orders[0].id")
    p.evaluate(f"setOrderStage('{oid}', 2)"); p.wait_for_timeout(300); snap(s, "orders-stage-toast")
    p.evaluate(f"openOrder('{oid}')"); snap(s, "order-details")
    p.evaluate("show('orders')")
    for f in ["In progress", "Ready for fitting", "Done"]:
        p.evaluate(f"setOrderFilter('{f}')"); snap(s, "orders-filter")
    p.evaluate("setOrderFilter('All')")
    cid = p.evaluate("database.customers[0].id")
    p.evaluate(f"openProfile('{cid}')"); snap(s, "profile")
    p.evaluate("openNotesModal()"); snap(s, "notes-modal"); p.evaluate("closeModal()")
    p.evaluate(f"deleteCustomer('{cid}')"); snap(s, "delete-confirm"); p.evaluate("closeModal()")
    p.evaluate("editCustomer(database.customers[0].id)"); snap(s, "customer-edit")
    p.evaluate("openCustomersFor('measurements')"); snap(s, "pick-measurements")
    p.evaluate("show('home')"); p.wait_for_timeout(300); snap(s, "home-nudges")
    p.evaluate("show('customers')"); snap(s, "customers-list")
    p.evaluate("openBusiness()"); snap(s, "business-filled")
    p.evaluate("shiftBusinessMonth(-1)"); snap(s, "business-lastmonth")
    p.evaluate("showInstallHelp()"); snap(s, "install-help"); p.evaluate("closeModal()")
    fake.offline = True
    p.evaluate("newCustomer()"); p.fill("#newName", "Offline Person"); p.fill("#newPhone", "0700"); p.evaluate("saveCustomer()"); p.wait_for_timeout(500)
    p.evaluate("closeModal()"); p.evaluate("show('home')"); snap(s, "home-sync-pill")
    p.evaluate("show('settings')"); snap(s, "settings-sync")
    fake.offline = False
    p.evaluate("manualSync()"); p.wait_for_timeout(800); snap(s, "settings-synced")
    p.evaluate("logout()"); snap(s, "logout-confirm")
    errors = list(s.errors)
    s.close()
    return seen, errors


if __name__ == "__main__":
    import json
    seen, errors = walk()
    json.dump({k: v[1] for k, v in seen.items()}, open("/mnt/user-data/outputs/wip/pw/seen.json", "w"), indent=1, ensure_ascii=False)
    print("strings:", len(seen), "errors:", errors)
