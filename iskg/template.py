"""HTML page builder and JS bridge for ISKG widgets."""

from __future__ import annotations

from typing import Any

from .fonts import font_css

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

    // Replace a widget's outer element (by id) with fresh rendered HTML,
    // preserving the same id so subsequent JS bindings re-attach correctly.
    window.iskg_replace_widget = function(id, html) {
        var el = document.getElementById(id);
        if (!el) return;
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var neu = tmp.firstElementChild;
        if (neu) el.replaceWith(neu);
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

    window.iskg_bind_key = function(id, eventType, keyFilter, mods, _retry) {
        var el = document.getElementById(id);
        if (!el) {
            // Widget may not be mounted yet; retry at most once to avoid an
            // infinite loop if the widget is destroyed before the element is
            // ever created.
            if (!_retry) setTimeout(function(){iskg_bind_key(id,eventType,keyFilter,mods,1);},50);
            return;
        }
        var fn = function(e) {
            if (keyFilter && e.key !== keyFilter && e.code !== keyFilter && e.key.toLowerCase() !== keyFilter.toLowerCase()) return;
            if (mods) {
                if (mods.ctrl && !e.ctrlKey) return;
                if (mods.alt && !e.altKey) return;
                if (mods.shift && !e.shiftKey) return;
            }
            var data = JSON.stringify({key:e.key,code:e.code,ctrl:e.ctrlKey,alt:e.altKey,shift:e.shiftKey});
            iskg_bridge_event(id, eventType, data);
        };
        el.addEventListener(eventType === 'keyrelease' ? 'keyup' : 'keydown', fn);
        el._iskg_key_fn = fn;
    };

    window.iskg_unbind_key = function(id, eventType) {
        var el = document.getElementById(id);
        if (el && el._iskg_key_fn) {
            el.removeEventListener(eventType === 'keyrelease' ? 'keyup' : 'keydown', el._iskg_key_fn);
            delete el._iskg_key_fn;
        }
    };

    // Remove a destroyed widget from the DOM and tear down its listeners.
    window.iskg_cleanup = function(id) {
        var el = document.getElementById(id);
        if (el) {
            if (el._iskg_key_fn) {
                el.removeEventListener('keydown', el._iskg_key_fn);
                el.removeEventListener('keyup', el._iskg_key_fn);
                delete el._iskg_key_fn;
            }
            el.remove();
        }
        // Tear down tooltips attached to this widget (created via _render_tooltip_js).
        var tips = document.querySelectorAll('.iskg-tooltip[data-tipfor="' + id + '"]');
        for (var i = 0; i < tips.length; i++) { tips[i].remove(); }
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

    // Theme switching at runtime
    window._ISKG_THEMES = {};

    window.iskg_register_themes = function(themes) {
        window._ISKG_THEMES = themes;
    };

    window.iskg_apply_theme = function(vars) {
        var root = document.documentElement;
        for (var key in vars) {
            if (vars.hasOwnProperty(key)) {
                root.style.setProperty(key, vars[key]);
            }
        }
    };

    window.iskg_set_theme = function(name) {
        var theme = window._ISKG_THEMES[name];
        if (theme) {
            iskg_apply_theme(theme);
            return true;
        }
        return false;
    };

    // Right-click / context-menu support.
    window.__iskg_ctx_pos = { x: 0, y: 0 };
    window.iskg_bind_contextmenu = function(id, _retry) {
        var el = document.getElementById(id);
        if (!el) {
            if (!_retry) setTimeout(function(){ iskg_bind_contextmenu(id, 1); }, 60);
            return;
        }
        el.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            window.__iskg_ctx_pos = { x: e.clientX, y: e.clientY };
            iskg_bridge_event(id, 'contextmenu', JSON.stringify({ x: e.clientX, y: e.clientY }));
        });
    };

    window.iskg_open_contextmenu = function(ownerId, itemsHtml) {
        iskg_close_contextmenu();
        if (!itemsHtml) return;
        var d = document.createElement('div');
        d.id = 'iskg-ctx-popup';
        d.className = 'iskg-menu-dd';
        d.style.position = 'fixed';
        d.style.display = 'block';
        d.style.zIndex = '2000';
        d.style.left = '0px';
        d.style.top = '0px';
        d.innerHTML = itemsHtml;
        document.body.appendChild(d);
        var pos = window.__iskg_ctx_pos;
        var vw = document.documentElement.clientWidth;
        var vh = document.documentElement.clientHeight;
        var w = d.offsetWidth || 160;
        var h = d.offsetHeight || 40;
        var left = pos.clamped ? pos.x : Math.min(pos.x, Math.max(0, vw - w - 4));
        var top = pos.clamped ? pos.y : Math.min(pos.y, Math.max(0, vh - h - 4));
        d.style.left = left + 'px';
        d.style.top = top + 'px';
        window._iskg_ctx_owner = ownerId;
        d.querySelectorAll('.iskg-menu-sub[data-sub]').forEach(function(sub) {
            var subEl = document.getElementById(sub.getAttribute('data-sub'));
            if (!subEl) return;
            sub.onmouseenter = function() { subEl.style.display = 'block'; };
            sub.onmouseleave = function() { setTimeout(function(){ if (!sub.matches(':hover') && !subEl.matches(':hover')) subEl.style.display = 'none'; }, 200); };
        });
        d.querySelectorAll('.iskg-menu-item[data-cmd]').forEach(function(it) {
            it.onclick = function() {
                var path = it.getAttribute('data-cmd');
                iskg_close_contextmenu();
                iskg_bridge_event(ownerId, 'contextcmd', path);
            };
        });
    };
    window.iskg_close_contextmenu = function() {
        var old = document.getElementById('iskg-ctx-popup');
        if (old) old.remove();
    };
    document.addEventListener('mousedown', function(e) {
        var p = document.getElementById('iskg-ctx-popup');
        if (p && !(e.target && p.contains(e.target))) iskg_close_contextmenu();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') iskg_close_contextmenu();
    });

    // Drag & drop between widgets (HTML5 DnD).
    window._iskg_dnd = { sources: {}, targets: {} };
    window.iskg_register_dnd = function(id, role) {
        if (role === 'source' || role === 'both') window._iskg_dnd.sources[id] = true;
        if (role === 'target' || role === 'both') window._iskg_dnd.targets[id] = true;
    };
    document.addEventListener('dragstart', function(e) {
        var el = e.target && e.target.closest ? e.target.closest('[draggable="true"]') : null;
        if (!el || !el.id) return;
        window._iskg_drag_widget = el.id;
        try { e.dataTransfer.setData('text/plain', el.id); } catch(err) {}
        e.dataTransfer.effectAllowed = 'move';
    });
    document.addEventListener('dragend', function() { window._iskg_drag_widget = null; });
    document.addEventListener('dragover', function(e) {
        var el = e.target && e.target.closest ? e.target.closest('.iskg-drop-target') : null;
        if (!el || !el.id) return;
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    document.addEventListener('drop', function(e) {
        var el = e.target && e.target.closest ? e.target.closest('.iskg-drop-target') : null;
        if (!el || !el.id) return;
        e.preventDefault();
        var src = window._iskg_drag_widget || (e.dataTransfer.getData ? e.dataTransfer.getData('text/plain') : '');
        var r = el.getBoundingClientRect();
        var data = JSON.stringify({
            source: src,
            x: Math.round(e.clientX - r.left),
            y: Math.round(e.clientY - r.top),
            target: el.id,
        });
        iskg_bridge_event(el.id, 'drop', data);
    });

    // Global (window-wide) key bindings, e.g. <Control-s>. Listens on
    // document so they fire regardless of which widget has focus.
    window._iskg_global_keys = [];
    window.iskg_bind_global_key = function(evt, keyFilter, mods) {
        var entry = { t: evt, k: keyFilter, m: mods };
        window._iskg_global_keys.push(entry);
        if (!window._iskg_global_keys_bound) {
            window._iskg_global_keys_bound = true;
            document.addEventListener('keydown', function(e) {
                if (window._iskg_global_keys_bound) { /* keep */ }
                for (var i = 0; i < window._iskg_global_keys.length; i++) {
                    var ent = window._iskg_global_keys[i];
                    if (ent.t !== 'keypress') continue;
                    if (ent.k && e.key !== ent.k && e.code !== ent.k &&
                        e.key.toLowerCase() !== String(ent.k).toLowerCase()) continue;
                    if (ent.m) {
                        if (ent.m.ctrl && !e.ctrlKey) continue;
                        if (ent.m.alt && !e.altKey) continue;
                        if (ent.m.shift && !e.shiftKey) continue;
                    }
                    var data = JSON.stringify({key:e.key,code:e.code,ctrl:e.ctrlKey,alt:e.altKey,shift:e.shiftKey});
                    iskg_bridge_event('__iskg_global__', 'key', data);
                    return;
                }
            });
            document.addEventListener('keyup', function(e) {
                for (var i = 0; i < window._iskg_global_keys.length; i++) {
                    var ent = window._iskg_global_keys[i];
                    if (ent.t !== 'keyrelease') continue;
                    if (ent.k && e.key !== ent.k && e.code !== ent.k &&
                        e.key.toLowerCase() !== String(ent.k).toLowerCase()) continue;
                    if (ent.m) {
                        if (ent.m.ctrl && !e.ctrlKey) continue;
                        if (ent.m.alt && !e.altKey) continue;
                        if (ent.m.shift && !e.shiftKey) continue;
                    }
                    var data = JSON.stringify({key:e.key,code:e.code,ctrl:e.ctrlKey,alt:e.altKey,shift:e.shiftKey});
                    iskg_bridge_event('__iskg_global__', 'global', data);
                    return;
                }
            });
        }
        return true;
    };
})();
"""


def build_html(
    root_widgets: list[Any],
    ifaz_css: str,
    extra_js: str = "",
    extra_css: str = "",
    theme_name: str = "ifaz",
    font_ids: list[str] | None = None,
) -> str:
    all_widgets: list[Any] = []
    for w in root_widgets:
        all_widgets.extend(w._collect_widgets())

    rendered_html = "".join(w._render() for w in root_widgets if not w._destroyed)

    all_js_parts: list[str] = []
    for w in root_widgets:
        if not w._destroyed:
            all_js_parts.append(w._render_js())
            all_js_parts.append(w._render_children_js())
    # Include base JS (tooltips, key bindings, context menus) for every widget
    for _, w in all_widgets:
        if not w._destroyed:
            all_js_parts.append(w._render_tooltip_js())
            all_js_parts.append(w._render_key_bindings_js())
            all_js_parts.append(w._render_contextmenu_js())
            all_js_parts.append(w._render_dnd_js())
    all_js = "\n".join(p for p in all_js_parts if p)
    if extra_js:
        all_js += "\n" + extra_js

    # Embed theme data for runtime switching
    import json as _json

    from .themes import THEMES as _THEMES

    theme_data = _json.dumps(_THEMES, indent=2)

    theme_init = f"iskg_register_themes({theme_data});\niskg_set_theme('{theme_name}');\n"

    extra_css_block = f"<style>{extra_css}</style>" if extra_css else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ISKG App</title>
<style>{font_css(font_ids)}</style>
<style>
body {{ margin:0; padding:0; overflow:auto; width:100vw; height:100vh;
       background:var(--bg-primary, #0c111a); color:var(--text, #c8d6e5); }}
#iskg-root {{ min-height:100vh; display:flex; flex-direction:column;
              background:var(--bg-primary, #0c111a); }}
</style>
<style>{ifaz_css}</style>
{extra_css_block}
</head>
<body>
<div id="iskg-root">{rendered_html}</div>
<script>
{BRIDGE_JS}
</script>
<script>
// Theme registration & init
{theme_init}
// Widget initialization
{all_js}
</script>
</body>
</html>"""
