# Step 2: sentences that are built from pieces now go through t(), dates follow the language,
# and the install instructions have a full Swahili version.
import re
p = "/home/claude/pwa/index.html"
src = open(p, encoding="utf-8").read()
failed = []

def rep(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        failed.append((n, old[:90]))
        return
    src = src.replace(old, new)

rep('${n} change${n === 1 ? "" : "s"} waiting to sync',
    '${t(n === 1 ? "{n} change waiting to sync" : "{n} changes waiting to sync", { n })}')
rep('<p><b>Notes for ${escapeHtml(customer.name)}</b></p>',
    '<p><b>${t("Notes for {name}", { name: escapeHtml(customer.name) })}</b></p>')
rep('confirmPhotoSheet("Use this photo for " + customer.name + "?", dataUrl, "circle"',
    'confirmPhotoSheet(t("Use this photo for {name}?", { name: customer.name }), dataUrl, "circle"')
rep('<p><b>${escapeHtml(customer.name)} is saved</b></p>',
    '<p><b>${t("{name} is saved", { name: escapeHtml(customer.name) })}</b></p>')
rep('📦 ${orderCount} order${orderCount === 1 ? "" : "s"}',
    '📦 ${t(orderCount === 1 ? "{n} order" : "{n} orders", { n: orderCount })}')
rep('showToast(order.garment + ": " + STAGES[stage]);',
    'showToast(order.garment + ": " + t(STAGES[stage]));')
rep('${dueText}${dueOverdue ? " (overdue)" : ""}',
    '${dueText}${dueOverdue ? " " + t("(overdue)") : ""}')
rep('New order for ${escapeHtml(customer.name)}</button>',
    '${t("New order for {name}", { name: escapeHtml(customer.name) })}</button>')
rep('${label}${saved[key] ? " ✓" : ""}', '${t(label)}${saved[key] ? " ✓" : ""}')
rep('<label>${label.toUpperCase()} (IN)</label>', '<label>${t(label).toUpperCase()} (${t("IN")})</label>')
rep('Save ${typeLabel.toLowerCase()} measurements',
    '${t("Save {type} measurements", { type: t(typeLabel).toLowerCase() })}')
rep('showToast(measurementTypeLabel(type) + " measurements saved");',
    'showToast(t("{type} measurements saved", { type: t(measurementTypeLabel(type)) }));')
rep('${label}: ${draft[key].trim()} in`', '${t(label)}: ${draft[key].trim()} ${t("in")}`')
rep('const text = `${measurementTypeLabel(type)} measurements for ${customer.name} (${draft.date || todayLabel()}):\\n` + lines.join("\\n");',
    'const text = t("{type} measurements for {name} ({date}):", { type: t(measurementTypeLabel(type)), name: customer.name, date: draft.date || todayLabel() }) + "\\n" + lines.join("\\n");')
rep('let text = `Hi ${customer.name}, an update on your ${order.garment}: status is "${order.status}".`;',
    'let text = t("Hi {name}, an update on your {garment}: status is \\"{status}\\".", { name: customer.name, garment: order.garment, status: t(order.status) });')
rep('if (balance > 0) text += ` Balance remaining: ${money(balance)}.`;',
    'if (balance > 0) text += " " + t("Balance remaining: {amount}.", { amount: money(balance) });')
rep('${e.kind === "expense" ? escapeHtml(e.category) : "Income"}',
    '${e.kind === "expense" ? escapeHtml(t(e.category)) : t("Income")}')
rep('"Includes " + money(orderIncome) + " from order payments"',
    't("Includes {amount} from order payments", { amount: money(orderIncome) })')
rep('escapeHtml(customer.name) : "Unknown customer"', 'escapeHtml(customer.name) : t("Unknown customer")')
rep('" · due " + order.dueDate', '" · " + t("due {date}", { date: order.dueDate })')
rep('Balance owed: ${money(balance)}', '${t("Balance owed: {amount}", { amount: money(balance) })}')
rep('"Last backup: " + formatDay(last) + ". Your data lives on this phone only, so save a backup often."',
    't("Last backup: {date}. Your data lives on this phone only, so save a backup often.", { date: formatDay(last) })')
rep('`Replace everything on this phone with this backup (${data.customers.length} customers, ${data.orders.length} orders)? What is on this phone now will be lost.`',
    't("Replace everything on this phone with this backup ({customers} customers, {orders} orders)? What is on this phone now will be lost.", { customers: data.customers.length, orders: data.orders.length })')

# dates follow the language
before = src.count('toLocaleDateString("en-GB"')
src = src.replace('toLocaleDateString("en-GB"', 'toLocaleDateString(dateLocale()')
print("date formats switched:", before)

# install instructions: full Swahili version
rep('''    openModalHtml(`
      <p><b>Install on iPhone</b></p>''', '''    openModalHtml(currentLang === "sw" ? INSTALL_IOS_SW : `
      <p><b>Install on iPhone</b></p>''')
rep('''    openModalHtml(`
      <p><b>Install on Android</b></p>''', '''    openModalHtml(currentLang === "sw" ? INSTALL_ANDROID_SW : `
      <p><b>Install on Android</b></p>''')

open(p, "w", encoding="utf-8").write(src)
print("not applied:", len(failed))
for n, o in failed: print("   found", n, "x:", o)
