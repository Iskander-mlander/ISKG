BRIDGE_JS = """
// ISKG Client Bridge for pywebview
(function() {
    window.iskg_bridge_event = function(widgetId, eventName, eventData) {
        try {
            if (typeof pywebview === 'undefined' || !pywebview.api || !pywebview.api.on_event) {
                console.log('[ISKG:bridge] pywebview not ready', widgetId, eventName, eventData);
                return;
            }
            pywebview.api.on_event(widgetId, eventName, JSON.stringify(eventData || ''));
        } catch(e) {
            console.warn('[ISKG:bridge]', e.message);
        }
    };

    window.iskg_set_text = function(id, text) {
        var el = document.getElementById(id);
        if (el) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.value = text;
            } else {
                el.innerText = text;
            }
        }
    };

    window.iskg_set_html = function(id, html) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = html;
    };

    window.iskg_set_value = function(id, value) {
        var el = document.getElementById(id);
        if (el) {
            if (el.tagName === 'INPUT' && el.type === 'range') {
                el.value = value;
                var evt = new Event('input', { bubbles: true });
                el.dispatchEvent(evt);
            } else {
                el.value = value;
            }
        }
    };

    window.iskg_set_attr = function(id, attr, value) {
        var el = document.getElementById(id);
        if (el) el.setAttribute(attr, value);
    };

    window.iskg_set_enabled = function(id, enabled) {
        var el = document.getElementById(id);
        if (el) {
            el.disabled = !enabled;
            el.classList.toggle('disabled', !enabled);
        }
    };

    window.iskg_set_visible = function(id, visible) {
        var el = document.getElementById(id);
        if (el) el.style.display = visible ? '' : 'none';
    };

    window.iskg_add_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.add(cls);
    };

    window.iskg_remove_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.remove(cls);
    };

    window.iskg_toggle_class = function(id, cls) {
        var el = document.getElementById(id);
        if (el) el.classList.toggle(cls);
    };

    window.iskg_focus = function(id) {
        var el = document.getElementById(id);
        if (el) el.focus();
    };

    window.iskg_set_style = function(id, cssText) {
        var el = document.getElementById(id);
        if (!el) return;
        var props = cssText.split(';');
        for (var i = 0; i < props.length; i++) {
            var p = props[i].trim();
            if (!p) continue;
            var colon = p.indexOf(':');
            if (colon > 0) {
                var name = p.substring(0, colon).trim();
                var value = p.substring(colon + 1).trim();
                el.style[name] = value;
            }
        }
    };
})();
"""


def build_html(root_widgets, ifaz_css, extra_js=""):
    all_widgets = []
    for w in root_widgets:
        all_widgets.extend(w._collect_widgets())

    rendered_html = "".join(w._render() for w in root_widgets if not w._destroyed)

    all_js_parts = []
    for w in root_widgets:
        if not w._destroyed:
            all_js_parts.append(w._render_js())
            all_js_parts.append(w._render_children_js())
    all_js = "\n".join(p for p in all_js_parts if p)
    if extra_js:
        all_js += "\n" + extra_js

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ISKG App</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>{ifaz_css}</style>
</head>
<body>
<div id="iskg-scanlines"></div>
<div id="iskg-vignette"></div>
<div id="iskg-root">{rendered_html}</div>
<script>
{BRIDGE_JS}
</script>
<script>
// Widget initialization
{all_js}
</script>
</body>
</html>"""
