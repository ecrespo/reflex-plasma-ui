"""JavaScript glue compiled into every page that uses a plasma component.

Plasma UI is React-first: it hands out its runtime (``pulse``, ``bump``)
through hooks and takes DOM elements / ref objects for ``bounds`` and
``background``. Reflex props are serialisable values, so three small wrapper
components bridge the gap:

* ``ReflexPlasmaProvider`` resolves ``backgroundSelector`` to a live element
  and mounts ``ReflexPlasmaBridge``, which publishes the provider runtime on
  ``window.__reflexPlasma`` under the provider ``name`` and fires ``onReady``.
* ``ReflexPlasma`` turns ``boundsSelector`` into a ref-like object.
* ``ReflexPlasmaCanvas`` forwards ``canvasStyle`` as the real inline ``style``
  (Reflex turns ``style=`` into an emotion class, which cannot beat the
  canvas's own inline ``position: fixed``).

The registry also tracks the last pointer-down position, so ``pulse()`` with
no coordinates lands where the user just clicked, and it pulses automatically
on elements marked with ``data-plasma-pulse``.
"""

NPM_PACKAGE = "@cruxgarden/plasma-ui"
NPM_VERSION = "0.7.0"
NPM_SPEC = f"{NPM_PACKAGE}@{NPM_VERSION}"

REGISTRY_CODE = r"""
const __rxPlasma = (() => {
  if (typeof window === "undefined") return null;
  if (window.__reflexPlasma) return window.__reflexPlasma;
  const reg = {
    runtimes: {},
    last: { x: window.innerWidth / 2, y: window.innerHeight / 2 },
    get(name) {
      if (name && reg.runtimes[name]) return reg.runtimes[name];
      return reg.runtimes.default || Object.values(reg.runtimes)[0] || null;
    },
    pulse(x, y, strength, name) {
      const rt = reg.get(name);
      if (!rt) return;
      rt.pulse(x ?? reg.last.x, y ?? reg.last.y, strength ?? 1);
    },
    bump(energy, name) {
      const rt = reg.get(name);
      if (rt) rt.bump(energy ?? 0.6);
    },
    info(name) {
      const rt = reg.get(name);
      return rt ? { supported: rt.supported, reduced_motion: rt.reducedMotion } : null;
    },
  };
  window.addEventListener("pointerdown", (e) => {
    reg.last = { x: e.clientX, y: e.clientY };
    const t = e.target;
    if (t && t.hasAttribute && t.hasAttribute("data-plasma-pulse")) {
      const s = Number(t.getAttribute("data-plasma-pulse-strength") ?? 1);
      reg.pulse(e.clientX, e.clientY, Number.isFinite(s) ? s : 1, t.getAttribute("data-plasma-pulse") || undefined);
    }
  }, true);
  window.__reflexPlasma = reg;
  return reg;
})();
"""

BRIDGE_CODE = r"""
function ReflexPlasmaBridge({ name, onReady }) {
  const rt = usePlasmaRuntime();
  const readyRef = useRef(onReady);
  useEffect(() => { readyRef.current = onReady; });
  useEffect(() => {
    if (!__rxPlasma) return;
    __rxPlasma.runtimes[name] = rt;
    return () => { if (__rxPlasma.runtimes[name] === rt) delete __rxPlasma.runtimes[name]; };
  }, [rt, name]);
  useEffect(() => {
    if (rt.renderer || !rt.supported) {
      readyRef.current?.({ supported: rt.supported, reduced_motion: rt.reducedMotion });
    }
  }, [rt.renderer, rt.supported, rt.reducedMotion]);
  return null;
}
"""

PROVIDER_CODE = r"""
function ReflexPlasmaProvider({ name = "default", backgroundSelector, background, onReady, children, ...props }) {
  const [bgEl, setBgEl] = useState(null);
  useEffect(() => {
    if (!backgroundSelector) { setBgEl(null); return; }
    let raf = 0;
    const find = () => {
      const el = document.querySelector(backgroundSelector);
      if (el) setBgEl(el); else raf = requestAnimationFrame(find);
    };
    find();
    return () => cancelAnimationFrame(raf);
  }, [backgroundSelector]);
  const bg = backgroundSelector ? (bgEl ?? undefined) : (background || undefined);
  return createElement(
    PlasmaProvider,
    { ...props, background: bg },
    createElement(ReflexPlasmaBridge, { name, onReady }),
    children,
  );
}
"""

SURFACE_CODE = r"""
const ReflexPlasma = forwardRef(function ReflexPlasma({ boundsSelector, ...props }, ref) {
  const bounds = useMemo(
    () => boundsSelector ? { get current() { return document.querySelector(boundsSelector); } } : undefined,
    [boundsSelector],
  );
  return createElement(Plasma, { ...props, bounds, ref });
});
"""

CANVAS_CODE = r"""
function ReflexPlasmaCanvas({ canvasStyle, className, zIndex }) {
  return createElement(PlasmaCanvas, { className, zIndex, style: canvasStyle });
}
"""
