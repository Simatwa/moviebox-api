try {
  self["workbox:core:7.2.0"] && _();
} catch {}
const q = (s, ...e) => {
    let t = s;
    return e.length > 0 && (t += ` :: ${JSON.stringify(e)}`), t;
  },
  K = q;
class h extends Error {
  constructor(e, t) {
    const n = K(e, t);
    super(n), (this.name = e), (this.details = t);
  }
}
const V = (s) =>
  new URL(String(s), location.href).href.replace(
    new RegExp(`^${location.origin}`),
    ""
  );
try {
  self["workbox:cacheable-response:7.2.0"] && _();
} catch {}
function U(s) {
  s.then(() => {});
}
const $ = (s, e) => e.some((t) => s instanceof t);
let T, L;
function Q() {
  return (
    T ||
    (T = [IDBDatabase, IDBObjectStore, IDBIndex, IDBCursor, IDBTransaction])
  );
}
function G() {
  return (
    L ||
    (L = [
      IDBCursor.prototype.advance,
      IDBCursor.prototype.continue,
      IDBCursor.prototype.continuePrimaryKey,
    ])
  );
}
const W = new WeakMap(),
  I = new WeakMap(),
  j = new WeakMap(),
  C = new WeakMap(),
  N = new WeakMap();
function z(s) {
  const e = new Promise((t, n) => {
    const a = () => {
        s.removeEventListener("success", i), s.removeEventListener("error", r);
      },
      i = () => {
        t(f(s.result)), a();
      },
      r = () => {
        n(s.error), a();
      };
    s.addEventListener("success", i), s.addEventListener("error", r);
  });
  return (
    e
      .then((t) => {
        t instanceof IDBCursor && W.set(t, s);
      })
      .catch(() => {}),
    N.set(e, s),
    e
  );
}
function J(s) {
  if (I.has(s)) return;
  const e = new Promise((t, n) => {
    const a = () => {
        s.removeEventListener("complete", i),
          s.removeEventListener("error", r),
          s.removeEventListener("abort", r);
      },
      i = () => {
        t(), a();
      },
      r = () => {
        n(s.error || new DOMException("AbortError", "AbortError")), a();
      };
    s.addEventListener("complete", i),
      s.addEventListener("error", r),
      s.addEventListener("abort", r);
  });
  I.set(s, e);
}
let M = {
  get(s, e, t) {
    if (s instanceof IDBTransaction) {
      if (e === "done") return I.get(s);
      if (e === "objectStoreNames") return s.objectStoreNames || j.get(s);
      if (e === "store")
        return t.objectStoreNames[1]
          ? void 0
          : t.objectStore(t.objectStoreNames[0]);
    }
    return f(s[e]);
  },
  set(s, e, t) {
    return (s[e] = t), !0;
  },
  has(s, e) {
    return s instanceof IDBTransaction && (e === "done" || e === "store")
      ? !0
      : e in s;
  },
};
function X(s) {
  M = s(M);
}
function Y(s) {
  return s === IDBDatabase.prototype.transaction &&
    !("objectStoreNames" in IDBTransaction.prototype)
    ? function (e, ...t) {
        const n = s.call(D(this), e, ...t);
        return j.set(n, e.sort ? e.sort() : [e]), f(n);
      }
    : G().includes(s)
    ? function (...e) {
        return s.apply(D(this), e), f(W.get(this));
      }
    : function (...e) {
        return f(s.apply(D(this), e));
      };
}
function Z(s) {
  return typeof s == "function"
    ? Y(s)
    : (s instanceof IDBTransaction && J(s), $(s, Q()) ? new Proxy(s, M) : s);
}
function f(s) {
  if (s instanceof IDBRequest) return z(s);
  if (C.has(s)) return C.get(s);
  const e = Z(s);
  return e !== s && (C.set(s, e), N.set(e, s)), e;
}
const D = (s) => N.get(s);
function ee(s, e, { blocked: t, upgrade: n, blocking: a, terminated: i } = {}) {
  const r = indexedDB.open(s, e),
    o = f(r);
  return (
    n &&
      r.addEventListener("upgradeneeded", (c) => {
        n(f(r.result), c.oldVersion, c.newVersion, f(r.transaction), c);
      }),
    t && r.addEventListener("blocked", (c) => t(c.oldVersion, c.newVersion, c)),
    o
      .then((c) => {
        i && c.addEventListener("close", () => i()),
          a &&
            c.addEventListener("versionchange", (l) =>
              a(l.oldVersion, l.newVersion, l)
            );
      })
      .catch(() => {}),
    o
  );
}
function te(s, { blocked: e } = {}) {
  const t = indexedDB.deleteDatabase(s);
  return (
    e && t.addEventListener("blocked", (n) => e(n.oldVersion, n)),
    f(t).then(() => {})
  );
}
const se = ["get", "getKey", "getAll", "getAllKeys", "count"],
  ne = ["put", "add", "delete", "clear"],
  E = new Map();
function O(s, e) {
  if (!(s instanceof IDBDatabase && !(e in s) && typeof e == "string")) return;
  if (E.get(e)) return E.get(e);
  const t = e.replace(/FromIndex$/, ""),
    n = e !== t,
    a = ne.includes(t);
  if (
    !(t in (n ? IDBIndex : IDBObjectStore).prototype) ||
    !(a || se.includes(t))
  )
    return;
  const i = async function (r, ...o) {
    const c = this.transaction(r, a ? "readwrite" : "readonly");
    let l = c.store;
    return (
      n && (l = l.index(o.shift())),
      (await Promise.all([l[t](...o), a && c.done]))[0]
    );
  };
  return E.set(e, i), i;
}
X((s) => ({
  ...s,
  get: (e, t, n) => O(e, t) || s.get(e, t, n),
  has: (e, t) => !!O(e, t) || s.has(e, t),
}));
try {
  self["workbox:expiration:7.2.0"] && _();
} catch {}
const ae = "workbox-expiration",
  g = "cache-entries",
  A = (s) => {
    const e = new URL(s, location.href);
    return (e.hash = ""), e.href;
  };
class re {
  constructor(e) {
    (this._db = null), (this._cacheName = e);
  }
  _upgradeDb(e) {
    const t = e.createObjectStore(g, { keyPath: "id" });
    t.createIndex("cacheName", "cacheName", { unique: !1 }),
      t.createIndex("timestamp", "timestamp", { unique: !1 });
  }
  _upgradeDbAndDeleteOldDbs(e) {
    this._upgradeDb(e), this._cacheName && te(this._cacheName);
  }
  async setTimestamp(e, t) {
    e = A(e);
    const n = {
        url: e,
        timestamp: t,
        cacheName: this._cacheName,
        id: this._getId(e),
      },
      i = (await this.getDb()).transaction(g, "readwrite", {
        durability: "relaxed",
      });
    await i.store.put(n), await i.done;
  }
  async getTimestamp(e) {
    const n = await (await this.getDb()).get(g, this._getId(e));
    return n == null ? void 0 : n.timestamp;
  }
  async expireEntries(e, t) {
    const n = await this.getDb();
    let a = await n
      .transaction(g)
      .store.index("timestamp")
      .openCursor(null, "prev");
    const i = [];
    let r = 0;
    for (; a; ) {
      const c = a.value;
      c.cacheName === this._cacheName &&
        ((e && c.timestamp < e) || (t && r >= t) ? i.push(a.value) : r++),
        (a = await a.continue());
    }
    const o = [];
    for (const c of i) await n.delete(g, c.id), o.push(c.url);
    return o;
  }
  _getId(e) {
    return this._cacheName + "|" + A(e);
  }
  async getDb() {
    return (
      this._db ||
        (this._db = await ee(ae, 1, {
          upgrade: this._upgradeDbAndDeleteOldDbs.bind(this),
        })),
      this._db
    );
  }
}
class ie {
  constructor(e, t = {}) {
    (this._isRunning = !1),
      (this._rerunRequested = !1),
      (this._maxEntries = t.maxEntries),
      (this._maxAgeSeconds = t.maxAgeSeconds),
      (this._matchOptions = t.matchOptions),
      (this._cacheName = e),
      (this._timestampModel = new re(e));
  }
  async expireEntries() {
    if (this._isRunning) {
      this._rerunRequested = !0;
      return;
    }
    this._isRunning = !0;
    const e = this._maxAgeSeconds ? Date.now() - this._maxAgeSeconds * 1e3 : 0,
      t = await this._timestampModel.expireEntries(e, this._maxEntries),
      n = await self.caches.open(this._cacheName);
    for (const a of t) await n.delete(a, this._matchOptions);
    (this._isRunning = !1),
      this._rerunRequested &&
        ((this._rerunRequested = !1), U(this.expireEntries()));
  }
  async updateTimestamp(e) {
    await this._timestampModel.setTimestamp(e, Date.now());
  }
  async isURLExpired(e) {
    if (this._maxAgeSeconds) {
      const t = await this._timestampModel.getTimestamp(e),
        n = Date.now() - this._maxAgeSeconds * 1e3;
      return t !== void 0 ? t < n : !0;
    } else return !1;
  }
  async delete() {
    (this._rerunRequested = !1),
      await this._timestampModel.expireEntries(1 / 0);
  }
}
const d = {
    googleAnalytics: "googleAnalytics",
    precache: "precache-v2",
    prefix: "workbox",
    runtime: "runtime",
    suffix: typeof registration < "u" ? registration.scope : "",
  },
  k = (s) => [d.prefix, s, d.suffix].filter((e) => e && e.length > 0).join("-"),
  oe = (s) => {
    for (const e of Object.keys(d)) s(e);
  },
  P = {
    updateDetails: (s) => {
      oe((e) => {
        typeof s[e] == "string" && (d[e] = s[e]);
      });
    },
    getGoogleAnalyticsName: (s) => s || k(d.googleAnalytics),
    getPrecacheName: (s) => s || k(d.precache),
    getPrefix: () => d.prefix,
    getRuntimeName: (s) => s || k(d.runtime),
    getSuffix: () => d.suffix,
  },
  B = new Set();
function ce(s) {
  B.add(s);
}
class le {
  constructor(e = {}) {
    (this.cachedResponseWillBeUsed = async ({
      event: t,
      request: n,
      cacheName: a,
      cachedResponse: i,
    }) => {
      if (!i) return null;
      const r = this._isResponseDateFresh(i),
        o = this._getCacheExpiration(a);
      U(o.expireEntries());
      const c = o.updateTimestamp(n.url);
      if (t)
        try {
          t.waitUntil(c);
        } catch {}
      return r ? i : null;
    }),
      (this.cacheDidUpdate = async ({ cacheName: t, request: n }) => {
        const a = this._getCacheExpiration(t);
        await a.updateTimestamp(n.url), await a.expireEntries();
      }),
      (this._config = e),
      (this._maxAgeSeconds = e.maxAgeSeconds),
      (this._cacheExpirations = new Map()),
      e.purgeOnQuotaError && ce(() => this.deleteCacheAndMetadata());
  }
  _getCacheExpiration(e) {
    if (e === P.getRuntimeName()) throw new h("expire-custom-caches-only");
    let t = this._cacheExpirations.get(e);
    return (
      t || ((t = new ie(e, this._config)), this._cacheExpirations.set(e, t)), t
    );
  }
  _isResponseDateFresh(e) {
    if (!this._maxAgeSeconds) return !0;
    const t = this._getDateHeaderTimestamp(e);
    if (t === null) return !0;
    const n = Date.now();
    return t >= n - this._maxAgeSeconds * 1e3;
  }
  _getDateHeaderTimestamp(e) {
    if (!e.headers.has("date")) return null;
    const t = e.headers.get("date"),
      a = new Date(t).getTime();
    return isNaN(a) ? null : a;
  }
  async deleteCacheAndMetadata() {
    for (const [e, t] of this._cacheExpirations)
      await self.caches.delete(e), await t.delete();
    this._cacheExpirations = new Map();
  }
}
try {
  self["workbox:precaching:7.2.0"] && _();
} catch {}
let w;
function he() {
  if (w === void 0) {
    const s = new Response("");
    if ("body" in s)
      try {
        new Response(s.body), (w = !0);
      } catch {
        w = !1;
      }
    w = !1;
  }
  return w;
}
async function ue(s, e) {
  let t = null;
  if ((s.url && (t = new URL(s.url).origin), t !== self.location.origin))
    throw new h("cross-origin-copy-response", { origin: t });
  const n = s.clone(),
    i = {
      headers: new Headers(n.headers),
      status: n.status,
      statusText: n.statusText,
    },
    r = he() ? n.body : await n.blob();
  return new Response(r, i);
}
function v(s, e) {
  const t = new URL(s);
  for (const n of e) t.searchParams.delete(n);
  return t.href;
}
async function de(s, e, t, n) {
  const a = v(e.url, t);
  if (e.url === a) return s.match(e, n);
  const i = Object.assign(Object.assign({}, n), { ignoreSearch: !0 }),
    r = await s.keys(e, i);
  for (const o of r) {
    const c = v(o.url, t);
    if (a === c) return s.match(o, n);
  }
}
class fe {
  constructor() {
    this.promise = new Promise((e, t) => {
      (this.resolve = e), (this.reject = t);
    });
  }
}
async function pe() {
  for (const s of B) await s();
}
function me(s) {
  return new Promise((e) => setTimeout(e, s));
}
try {
  self["workbox:strategies:7.2.0"] && _();
} catch {}
function b(s) {
  return typeof s == "string" ? new Request(s) : s;
}
class ge {
  constructor(e, t) {
    (this._cacheKeys = {}),
      Object.assign(this, t),
      (this.event = t.event),
      (this._strategy = e),
      (this._handlerDeferred = new fe()),
      (this._extendLifetimePromises = []),
      (this._plugins = [...e.plugins]),
      (this._pluginStateMap = new Map());
    for (const n of this._plugins) this._pluginStateMap.set(n, {});
    this.event.waitUntil(this._handlerDeferred.promise);
  }
  async fetch(e) {
    const { event: t } = this;
    let n = b(e);
    if (n.mode === "navigate" && t instanceof FetchEvent && t.preloadResponse) {
      const r = await t.preloadResponse;
      if (r) return r;
    }
    const a = this.hasCallback("fetchDidFail") ? n.clone() : null;
    try {
      for (const r of this.iterateCallbacks("requestWillFetch"))
        n = await r({ request: n.clone(), event: t });
    } catch (r) {
      if (r instanceof Error)
        throw new h("plugin-error-request-will-fetch", {
          thrownErrorMessage: r.message,
        });
    }
    const i = n.clone();
    try {
      let r;
      r = await fetch(
        n,
        n.mode === "navigate" ? void 0 : this._strategy.fetchOptions
      );
      for (const o of this.iterateCallbacks("fetchDidSucceed"))
        r = await o({ event: t, request: i, response: r });
      return r;
    } catch (r) {
      throw (
        (a &&
          (await this.runCallbacks("fetchDidFail", {
            error: r,
            event: t,
            originalRequest: a.clone(),
            request: i.clone(),
          })),
        r)
      );
    }
  }
  async fetchAndCachePut(e) {
    const t = await this.fetch(e),
      n = t.clone();
    return this.waitUntil(this.cachePut(e, n)), t;
  }
  async cacheMatch(e) {
    const t = b(e);
    let n;
    const { cacheName: a, matchOptions: i } = this._strategy,
      r = await this.getCacheKey(t, "read"),
      o = Object.assign(Object.assign({}, i), { cacheName: a });
    n = await caches.match(r, o);
    for (const c of this.iterateCallbacks("cachedResponseWillBeUsed"))
      n =
        (await c({
          cacheName: a,
          matchOptions: i,
          cachedResponse: n,
          request: r,
          event: this.event,
        })) || void 0;
    return n;
  }
  async cachePut(e, t) {
    const n = b(e);
    await me(0);
    const a = await this.getCacheKey(n, "write");
    if (!t) throw new h("cache-put-with-no-response", { url: V(a.url) });
    const i = await this._ensureResponseSafeToCache(t);
    if (!i) return !1;
    const { cacheName: r, matchOptions: o } = this._strategy,
      c = await self.caches.open(r),
      l = this.hasCallback("cacheDidUpdate"),
      m = l ? await de(c, a.clone(), ["__WB_REVISION__"], o) : null;
    try {
      await c.put(a, l ? i.clone() : i);
    } catch (u) {
      if (u instanceof Error)
        throw (u.name === "QuotaExceededError" && (await pe()), u);
    }
    for (const u of this.iterateCallbacks("cacheDidUpdate"))
      await u({
        cacheName: r,
        oldResponse: m,
        newResponse: i.clone(),
        request: a,
        event: this.event,
      });
    return !0;
  }
  async getCacheKey(e, t) {
    const n = `${e.url} | ${t}`;
    if (!this._cacheKeys[n]) {
      let a = e;
      for (const i of this.iterateCallbacks("cacheKeyWillBeUsed"))
        a = b(
          await i({
            mode: t,
            request: a,
            event: this.event,
            params: this.params,
          })
        );
      this._cacheKeys[n] = a;
    }
    return this._cacheKeys[n];
  }
  hasCallback(e) {
    for (const t of this._strategy.plugins) if (e in t) return !0;
    return !1;
  }
  async runCallbacks(e, t) {
    for (const n of this.iterateCallbacks(e)) await n(t);
  }
  *iterateCallbacks(e) {
    for (const t of this._strategy.plugins)
      if (typeof t[e] == "function") {
        const n = this._pluginStateMap.get(t);
        yield (i) => {
          const r = Object.assign(Object.assign({}, i), { state: n });
          return t[e](r);
        };
      }
  }
  waitUntil(e) {
    return this._extendLifetimePromises.push(e), e;
  }
  async doneWaiting() {
    let e;
    for (; (e = this._extendLifetimePromises.shift()); ) await e;
  }
  destroy() {
    this._handlerDeferred.resolve(null);
  }
  async _ensureResponseSafeToCache(e) {
    let t = e,
      n = !1;
    for (const a of this.iterateCallbacks("cacheWillUpdate"))
      if (
        ((t =
          (await a({
            request: this.request,
            response: t,
            event: this.event,
          })) || void 0),
        (n = !0),
        !t)
      )
        break;
    return n || (t && t.status !== 200 && (t = void 0)), t;
  }
}
class H {
  constructor(e = {}) {
    (this.cacheName = P.getRuntimeName(e.cacheName)),
      (this.plugins = e.plugins || []),
      (this.fetchOptions = e.fetchOptions),
      (this.matchOptions = e.matchOptions);
  }
  handle(e) {
    const [t] = this.handleAll(e);
    return t;
  }
  handleAll(e) {
    e instanceof FetchEvent && (e = { event: e, request: e.request });
    const t = e.event,
      n = typeof e.request == "string" ? new Request(e.request) : e.request,
      a = "params" in e ? e.params : void 0,
      i = new ge(this, { event: t, request: n, params: a }),
      r = this._getResponse(i, n, t),
      o = this._awaitComplete(r, i, n, t);
    return [r, o];
  }
  async _getResponse(e, t, n) {
    await e.runCallbacks("handlerWillStart", { event: n, request: t });
    let a;
    try {
      if (((a = await this._handle(t, e)), !a || a.type === "error"))
        throw new h("no-response", { url: t.url });
    } catch (i) {
      if (i instanceof Error) {
        for (const r of e.iterateCallbacks("handlerDidError"))
          if (((a = await r({ error: i, event: n, request: t })), a)) break;
      }
      if (!a) throw i;
    }
    for (const i of e.iterateCallbacks("handlerWillRespond"))
      a = await i({ event: n, request: t, response: a });
    return a;
  }
  async _awaitComplete(e, t, n, a) {
    let i, r;
    try {
      i = await e;
    } catch {}
    try {
      await t.runCallbacks("handlerDidRespond", {
        event: a,
        request: n,
        response: i,
      }),
        await t.doneWaiting();
    } catch (o) {
      o instanceof Error && (r = o);
    }
    if (
      (await t.runCallbacks("handlerDidComplete", {
        event: a,
        request: n,
        response: i,
        error: r,
      }),
      t.destroy(),
      r)
    )
      throw r;
  }
}
class p extends H {
  constructor(e = {}) {
    (e.cacheName = P.getPrecacheName(e.cacheName)),
      super(e),
      (this._fallbackToNetwork = e.fallbackToNetwork !== !1),
      this.plugins.push(p.copyRedirectedCacheableResponsesPlugin);
  }
  async _handle(e, t) {
    const n = await t.cacheMatch(e);
    return (
      n ||
      (t.event && t.event.type === "install"
        ? await this._handleInstall(e, t)
        : await this._handleFetch(e, t))
    );
  }
  async _handleFetch(e, t) {
    let n;
    const a = t.params || {};
    if (this._fallbackToNetwork) {
      const i = a.integrity,
        r = e.integrity,
        o = !r || r === i;
      (n = await t.fetch(
        new Request(e, { integrity: e.mode !== "no-cors" ? r || i : void 0 })
      )),
        i &&
          o &&
          e.mode !== "no-cors" &&
          (this._useDefaultCacheabilityPluginIfNeeded(),
          await t.cachePut(e, n.clone()));
    } else
      throw new h("missing-precache-entry", {
        cacheName: this.cacheName,
        url: e.url,
      });
    return n;
  }
  async _handleInstall(e, t) {
    this._useDefaultCacheabilityPluginIfNeeded();
    const n = await t.fetch(e);
    if (!(await t.cachePut(e, n.clone())))
      throw new h("bad-precaching-response", { url: e.url, status: n.status });
    return n;
  }
  _useDefaultCacheabilityPluginIfNeeded() {
    let e = null,
      t = 0;
    for (const [n, a] of this.plugins.entries())
      a !== p.copyRedirectedCacheableResponsesPlugin &&
        (a === p.defaultPrecacheCacheabilityPlugin && (e = n),
        a.cacheWillUpdate && t++);
    t === 0
      ? this.plugins.push(p.defaultPrecacheCacheabilityPlugin)
      : t > 1 && e !== null && this.plugins.splice(e, 1);
  }
}
p.defaultPrecacheCacheabilityPlugin = {
  async cacheWillUpdate({ response: s }) {
    return !s || s.status >= 400 ? null : s;
  },
};
p.copyRedirectedCacheableResponsesPlugin = {
  async cacheWillUpdate({ response: s }) {
    return s.redirected ? await ue(s) : s;
  },
};
try {
  self["workbox:routing:7.2.0"] && _();
} catch {}
const F = "GET",
  R = (s) => (s && typeof s == "object" ? s : { handle: s });
class x {
  constructor(e, t, n = F) {
    (this.handler = R(t)), (this.match = e), (this.method = n);
  }
  setCatchHandler(e) {
    this.catchHandler = R(e);
  }
}
class we extends x {
  constructor(e, t, n) {
    const a = ({ url: i }) => {
      const r = e.exec(i.href);
      if (r && !(i.origin !== location.origin && r.index !== 0))
        return r.slice(1);
    };
    super(a, t, n);
  }
}
class ye {
  constructor() {
    (this._routes = new Map()), (this._defaultHandlerMap = new Map());
  }
  get routes() {
    return this._routes;
  }
  addFetchListener() {
    self.addEventListener("fetch", (e) => {
      const { request: t } = e,
        n = this.handleRequest({ request: t, event: e });
      n && e.respondWith(n);
    });
  }
  addCacheListener() {
    self.addEventListener("message", (e) => {
      if (e.data && e.data.type === "CACHE_URLS") {
        const { payload: t } = e.data,
          n = Promise.all(
            t.urlsToCache.map((a) => {
              typeof a == "string" && (a = [a]);
              const i = new Request(...a);
              return this.handleRequest({ request: i, event: e });
            })
          );
        e.waitUntil(n),
          e.ports && e.ports[0] && n.then(() => e.ports[0].postMessage(!0));
      }
    });
  }
  handleRequest({ request: e, event: t }) {
    const n = new URL(e.url, location.href);
    if (!n.protocol.startsWith("http")) return;
    const a = n.origin === location.origin,
      { params: i, route: r } = this.findMatchingRoute({
        event: t,
        request: e,
        sameOrigin: a,
        url: n,
      });
    let o = r && r.handler;
    const c = e.method;
    if (
      (!o &&
        this._defaultHandlerMap.has(c) &&
        (o = this._defaultHandlerMap.get(c)),
      !o)
    )
      return;
    let l;
    try {
      l = o.handle({ url: n, request: e, event: t, params: i });
    } catch (u) {
      l = Promise.reject(u);
    }
    const m = r && r.catchHandler;
    return (
      l instanceof Promise &&
        (this._catchHandler || m) &&
        (l = l.catch(async (u) => {
          if (m)
            try {
              return await m.handle({
                url: n,
                request: e,
                event: t,
                params: i,
              });
            } catch (S) {
              S instanceof Error && (u = S);
            }
          if (this._catchHandler)
            return this._catchHandler.handle({ url: n, request: e, event: t });
          throw u;
        })),
      l
    );
  }
  findMatchingRoute({ url: e, sameOrigin: t, request: n, event: a }) {
    const i = this._routes.get(n.method) || [];
    for (const r of i) {
      let o;
      const c = r.match({ url: e, sameOrigin: t, request: n, event: a });
      if (c)
        return (
          (o = c),
          ((Array.isArray(o) && o.length === 0) ||
            (c.constructor === Object && Object.keys(c).length === 0) ||
            typeof c == "boolean") &&
            (o = void 0),
          { route: r, params: o }
        );
    }
    return {};
  }
  setDefaultHandler(e, t = F) {
    this._defaultHandlerMap.set(t, R(e));
  }
  setCatchHandler(e) {
    this._catchHandler = R(e);
  }
  registerRoute(e) {
    this._routes.has(e.method) || this._routes.set(e.method, []),
      this._routes.get(e.method).push(e);
  }
  unregisterRoute(e) {
    if (!this._routes.has(e.method))
      throw new h("unregister-route-but-not-found-with-method", {
        method: e.method,
      });
    const t = this._routes.get(e.method).indexOf(e);
    if (t > -1) this._routes.get(e.method).splice(t, 1);
    else throw new h("unregister-route-route-not-registered");
  }
}
let y;
const _e = () => (
  y || ((y = new ye()), y.addFetchListener(), y.addCacheListener()), y
);
function be(s, e, t) {
  let n;
  if (typeof s == "string") {
    const i = new URL(s, location.href),
      r = ({ url: o }) => o.href === i.href;
    n = new x(r, e, t);
  } else if (s instanceof RegExp) n = new we(s, e, t);
  else if (typeof s == "function") n = new x(s, e, t);
  else if (s instanceof x) n = s;
  else
    throw new h("unsupported-route-type", {
      moduleName: "workbox-routing",
      funcName: "registerRoute",
      paramName: "capture",
    });
  return _e().registerRoute(n), n;
}
class xe extends H {
  async _handle(e, t) {
    let n = await t.cacheMatch(e),
      a;
    if (!n)
      try {
        n = await t.fetchAndCachePut(e);
      } catch (i) {
        i instanceof Error && (a = i);
      }
    if (!n) throw new h("no-response", { url: e.url, error: a });
    return n;
  }
}
self.addEventListener("message", (s) => {
  s.data && s.data.type === "SKIP_WAITING" && self.skipWaiting();
});
[
  { revision: null, url: "_nuxt/_id_.BPJghXKu.css" },
  { revision: null, url: "_nuxt/_id_.C44NwQ6v.css" },
  { revision: null, url: "_nuxt/_id_.D8FxJB3k.css" },
  { revision: null, url: "_nuxt/_id_.De_hnJS-.css" },
  { revision: null, url: "_nuxt/_id_.nA-byXiq.css" },
  { revision: null, url: "_nuxt/123movies.BlfzU9Da.css" },
  { revision: null, url: "_nuxt/1in4HGdu.js" },
  { revision: null, url: "_nuxt/5N0eSuEN.js" },
  { revision: null, url: "_nuxt/64udgyt0.js" },
  { revision: null, url: "_nuxt/aawjT3Om.js" },
  { revision: null, url: "_nuxt/adiOuWNm.js" },
  { revision: null, url: "_nuxt/aKXcLsm_.js" },
  { revision: null, url: "_nuxt/allImg.DvKT39P8.css" },
  { revision: null, url: "_nuxt/animated-series.Bv6NH-EB.css" },
  { revision: null, url: "_nuxt/apk-download.BsXVshUu.svg" },
  { revision: null, url: "_nuxt/AppleTV.CBjhcGDs.png" },
  { revision: null, url: "_nuxt/AppleTVLogo.Z5pj4az9.png" },
  { revision: null, url: "_nuxt/B_HYICW5.js" },
  { revision: null, url: "_nuxt/B_UQHEW_.js" },
  { revision: null, url: "_nuxt/B_v9lswc.js" },
  { revision: null, url: "_nuxt/B00wVEIv.js" },
  { revision: null, url: "_nuxt/B0ydNsj-.js" },
  { revision: null, url: "_nuxt/B1O3RBQO.js" },
  { revision: null, url: "_nuxt/B2d_WKrs.js" },
  { revision: null, url: "_nuxt/B3DhXes-.js" },
  { revision: null, url: "_nuxt/B9K5rw8f.js" },
  { revision: null, url: "_nuxt/Ba1fBnxs.js" },
  { revision: null, url: "_nuxt/BaAk-xzy.js" },
  { revision: null, url: "_nuxt/BC-tNRgF.js" },
  { revision: null, url: "_nuxt/BFsgK4lG.js" },
  { revision: null, url: "_nuxt/bg.CEefRPl4.png" },
  { revision: null, url: "_nuxt/BgYFnW2V.js" },
  { revision: null, url: "_nuxt/BGZmeVjU.js" },
  { revision: null, url: "_nuxt/Bho_Rj0L.js" },
  { revision: null, url: "_nuxt/BI181Tai.js" },
  { revision: null, url: "_nuxt/BIikcD21.js" },
  { revision: null, url: "_nuxt/BkijaWuO.js" },
  { revision: null, url: "_nuxt/BM5thzF8.js" },
  { revision: null, url: "_nuxt/BmsdeWJ2.js" },
  { revision: null, url: "_nuxt/BNyPH0ZE.js" },
  { revision: null, url: "_nuxt/BoOAatLA.js" },
  { revision: null, url: "_nuxt/bottomNav.9d7lWjHc.css" },
  { revision: null, url: "_nuxt/BtzMH38w.js" },
  {
    revision: "517f0c1b843b9e7bea7f82585ad3c4cd",
    url: "_nuxt/builds/latest.json",
  },
  {
    revision: null,
    url: "_nuxt/builds/meta/50440ab6-e30a-4b9a-ad04-a4493aa23c79.json",
  },
  { revision: null, url: "_nuxt/BUkMBrXV.js" },
  { revision: null, url: "_nuxt/BUywZoB1.js" },
  { revision: null, url: "_nuxt/BvQkG6nA.js" },
  { revision: null, url: "_nuxt/BvzLn3ha.js" },
  { revision: null, url: "_nuxt/BwHytCVX.js" },
  { revision: null, url: "_nuxt/BxKsV4ta.js" },
  { revision: null, url: "_nuxt/C-PGV1qE.js" },
  { revision: null, url: "_nuxt/C-te_uTy.js" },
  { revision: null, url: "_nuxt/C1KCudr5.js" },
  { revision: null, url: "_nuxt/C3YGruzo.js" },
  { revision: null, url: "_nuxt/C5uQ6hsT.js" },
  { revision: null, url: "_nuxt/category.DwJBDNKK.css" },
  { revision: null, url: "_nuxt/CDpHsR8K.js" },
  { revision: null, url: "_nuxt/CeluCGgU.js" },
  { revision: null, url: "_nuxt/CfYON71f.js" },
  { revision: null, url: "_nuxt/CGht4m14.js" },
  { revision: null, url: "_nuxt/CHSSE-zO.js" },
  { revision: null, url: "_nuxt/Cijjt-Nx.js" },
  { revision: null, url: "_nuxt/Cit18Zv_.js" },
  { revision: null, url: "_nuxt/CkC461sm.js" },
  { revision: null, url: "_nuxt/class-list.Bt1rX4PF.css" },
  { revision: null, url: "_nuxt/class-month.BsUexZK0.css" },
  { revision: null, url: "_nuxt/CLEfbVU3.js" },
  { revision: null, url: "_nuxt/clip.CQY2J2kO.css" },
  { revision: null, url: "_nuxt/CnKNxPJE.js" },
  { revision: null, url: "_nuxt/COym3-R6.js" },
  { revision: null, url: "_nuxt/CPZgjF-K.js" },
  { revision: null, url: "_nuxt/CrAoW8Yy.js" },
  { revision: null, url: "_nuxt/CRjG7NVz.js" },
  { revision: null, url: "_nuxt/Ct3446Fy.js" },
  { revision: null, url: "_nuxt/CTE9kVqy.js" },
  { revision: null, url: "_nuxt/CtsnUzqX.js" },
  { revision: null, url: "_nuxt/CvmfAuZC.js" },
  { revision: null, url: "_nuxt/D5TZkSSM.js" },
  { revision: null, url: "_nuxt/DC5hBLOP.js" },
  { revision: null, url: "_nuxt/DCouejex.js" },
  { revision: null, url: "_nuxt/default.CQYMdln9.css" },
  { revision: null, url: "_nuxt/detail.D33WCiCo.css" },
  { revision: null, url: "_nuxt/DF1E1wFS.js" },
  { revision: null, url: "_nuxt/Dh4FHC8P.js" },
  { revision: null, url: "_nuxt/Disney.hfYeiBhX.png" },
  { revision: null, url: "_nuxt/DisneyLogo.tCn0kn6m.png" },
  { revision: null, url: "_nuxt/Diy8B7Pq.js" },
  { revision: null, url: "_nuxt/Dj03poO2.js" },
  { revision: null, url: "_nuxt/DLA7qPxd.js" },
  { revision: null, url: "_nuxt/DlAUqK2U.js" },
  { revision: null, url: "_nuxt/DntQ-F8v.js" },
  { revision: null, url: "_nuxt/DojvuLS6.js" },
  { revision: null, url: "_nuxt/download-apk-app.CYQQdL00.png" },
  { revision: null, url: "_nuxt/downloadBtn.BJx6DZ3P.css" },
  { revision: null, url: "_nuxt/DpQA05AO.js" },
  { revision: null, url: "_nuxt/DpUAmIyq.js" },
  { revision: null, url: "_nuxt/DRnqEFqG.js" },
  { revision: null, url: "_nuxt/Ds0xFP5G.js" },
  { revision: null, url: "_nuxt/DtFtEmlB.js" },
  { revision: null, url: "_nuxt/DTJ-xvWY.js" },
  { revision: null, url: "_nuxt/DtovRKn5.js" },
  { revision: null, url: "_nuxt/DUPr27Fw.js" },
  { revision: null, url: "_nuxt/DUpXti4f.js" },
  { revision: null, url: "_nuxt/DWddmWq7.js" },
  { revision: null, url: "_nuxt/DWKU_le6.js" },
  { revision: null, url: "_nuxt/DZwNmG9J.js" },
  { revision: null, url: "_nuxt/empty-icon.DPExyKDB.svg" },
  { revision: null, url: "_nuxt/empty-img.B-BBLac5.svg" },
  { revision: null, url: "_nuxt/empty.BYiQnTeF.svg" },
  { revision: null, url: "_nuxt/entry.BbOw-97N.css" },
  { revision: null, url: "_nuxt/filter.CMat4YQ7.css" },
  { revision: null, url: "_nuxt/FilterPage.BEOwdAG1.css" },
  { revision: null, url: "_nuxt/FnkoIU3M.js" },
  { revision: null, url: "_nuxt/footer.D5So5rBv.css" },
  { revision: null, url: "_nuxt/footer.TTKm1vqt.css" },
  { revision: null, url: "_nuxt/GkeYeIfm.js" },
  { revision: null, url: "_nuxt/gkPYXf5G.js" },
  { revision: null, url: "_nuxt/guid-btm-img.Czus0DtA.png" },
  { revision: null, url: "_nuxt/guide-book.BsR8T2mr.png" },
  { revision: null, url: "_nuxt/guide-top-bg.DV6YnRWB.png" },
  { revision: null, url: "_nuxt/HBO.CNk7MWlq.png" },
  { revision: null, url: "_nuxt/HBOLogo.C9ZN90I7.png" },
  { revision: null, url: "_nuxt/head-back.Cxkgcat7.css" },
  { revision: null, url: "_nuxt/head.DBtZJeYQ.css" },
  { revision: null, url: "_nuxt/Hoichoi.DFkomyPu.png" },
  { revision: null, url: "_nuxt/HoichoiLogo.BUXMKSvi.png" },
  { revision: null, url: "_nuxt/home.BEFBZk2O.css" },
  { revision: null, url: "_nuxt/Hulu.B9LJ74ur.png" },
  { revision: null, url: "_nuxt/HuluLogo.U0-hiEPk.png" },
  { revision: null, url: "_nuxt/hz1lbLnt.js" },
  { revision: null, url: "_nuxt/ImageView.C7pQwQhS.css" },
  { revision: null, url: "_nuxt/index.BQevdZ2g.css" },
  { revision: null, url: "_nuxt/index.DbIupMjn.css" },
  { revision: null, url: "_nuxt/index.DnBS2LoF.css" },
  { revision: null, url: "_nuxt/index.DopTslFq.css" },
  { revision: null, url: "_nuxt/index.DYW91Llc.css" },
  { revision: null, url: "_nuxt/index.iGsiMr_r.css" },
  { revision: null, url: "_nuxt/index.MK7zKr2m.css" },
  { revision: null, url: "_nuxt/INdoyDGT.js" },
  { revision: null, url: "_nuxt/JNxDn-jw.js" },
  { revision: null, url: "_nuxt/KUDRivXv.js" },
  { revision: null, url: "_nuxt/left-ranking-icon.BD2OfvBb.svg" },
  { revision: null, url: "_nuxt/likeCard.CmdXzMdc.css" },
  { revision: null, url: "_nuxt/list.BbXHlxB2.css" },
  { revision: null, url: "_nuxt/list.D9MqcjCQ.css" },
  { revision: null, url: "_nuxt/LiveLogo.D_ZHPMXB.png" },
  { revision: null, url: "_nuxt/load-more.B0Oq9HN7.svg" },
  { revision: null, url: "_nuxt/loading-green-light.duPoTdIQ.webp" },
  { revision: null, url: "_nuxt/localesBtn.ev5OxBX4.css" },
  { revision: null, url: "_nuxt/match-empty.CsnU3sf2.svg" },
  { revision: null, url: "_nuxt/movie.Q8cYfO8Z.css" },
  { revision: null, url: "_nuxt/MXNFvWql.js" },
  { revision: null, url: "_nuxt/nav.C--OPkew.css" },
  { revision: null, url: "_nuxt/nav.Kej__8Z_.css" },
  { revision: null, url: "_nuxt/Netflix.COywD1df.png" },
  { revision: null, url: "_nuxt/NetflixLogo.4p4FdOAE.png" },
  { revision: null, url: "_nuxt/newList.DtTT7n9e.css" },
  { revision: null, url: "_nuxt/newsback.gla2Z0oW.css" },
  { revision: null, url: "_nuxt/newsFilterH5.C28ie8dm.css" },
  { revision: null, url: "_nuxt/newsH5.CWG4qDeK.css" },
  { revision: null, url: "_nuxt/newsLabel.BnNhymcy.css" },
  { revision: null, url: "_nuxt/no-comments-icon.DCAg9eGP.svg" },
  { revision: null, url: "_nuxt/novel.C-nS1tIt.css" },
  { revision: null, url: "_nuxt/official_logo.BXS1BVq0.png" },
  { revision: null, url: "_nuxt/official-mobild-main-img.D4o0XloV.png" },
  { revision: null, url: "_nuxt/PageNotFound.CSglubR0.css" },
  { revision: null, url: "_nuxt/pc-download-main.CWy1V9Z4.png" },
  { revision: null, url: "_nuxt/pc-home-living-bg.DIBVlAYL.svg" },
  { revision: null, url: "_nuxt/pc-ranking-2.g9Xk4j8p.svg" },
  { revision: null, url: "_nuxt/post.Cy4zN077.css" },
  { revision: null, url: "_nuxt/postImgText.CoL-AMrV.css" },
  { revision: null, url: "_nuxt/PrimeVideo.BP15GnzL.png" },
  { revision: null, url: "_nuxt/PrimeVideoLogo.d3BPTiOQ.png" },
  { revision: null, url: "_nuxt/Qf73l97u.js" },
  { revision: null, url: "_nuxt/QkqDd2bX.js" },
  { revision: null, url: "_nuxt/qr-logo.C4FQ4H7K.png" },
  { revision: null, url: "_nuxt/qvbIs-AE.js" },
  { revision: null, url: "_nuxt/ranking-list.B8JG8vpZ.css" },
  { revision: null, url: "_nuxt/right-ranking-icon.DGRxStsZ.svg" },
  { revision: null, url: "_nuxt/searchResult.ZJzN_1uo.css" },
  { revision: null, url: "_nuxt/share.B39E9BV9.css" },
  { revision: null, url: "_nuxt/shorts.BP0gM-U9.css" },
  { revision: null, url: "_nuxt/Showmax.BKyWy8Wz.png" },
  { revision: null, url: "_nuxt/ShowmaxLogo.BGppjzuE.png" },
  { revision: null, url: "_nuxt/SlideNav.NDhWEWHq.css" },
  { revision: null, url: "_nuxt/squidgame3.6W5gz5RW.css" },
  { revision: null, url: "_nuxt/subject.D1rrWY7V.css" },
  { revision: null, url: "_nuxt/subject.HXfm4f5Y.css" },
  { revision: null, url: "_nuxt/subjectH5.BqxdR9Iy.css" },
  { revision: null, url: "_nuxt/test.Cd7LQrTa.css" },
  { revision: null, url: "_nuxt/video-re-play.B_aAIgLA.webp" },
  { revision: null, url: "_nuxt/Vidio.CCVKxeDe.png" },
  { revision: null, url: "_nuxt/VidioLogo.CR8GStVS.png" },
  { revision: null, url: "_nuxt/Viu.C0ihRc_A.png" },
  { revision: null, url: "_nuxt/ViuLogo.f55Gm9dZ.png" },
  { revision: null, url: "_nuxt/Vivamax.Scnm_Fpe.png" },
  { revision: null, url: "_nuxt/VivamaxLogo.Dz1TgblZ.png" },
  { revision: null, url: "_nuxt/web-logo.apJjVir2.svg" },
  { revision: null, url: "_nuxt/WPjL7ShT.js" },
  { revision: null, url: "_nuxt/WvO8OPPa.js" },
  { revision: null, url: "_nuxt/x-light.min.Bd_2qZiG.svg" },
  { revision: null, url: "_nuxt/x.min.D3ggbSnd.svg" },
  { revision: null, url: "_nuxt/xSNkGoon.js" },
  { revision: null, url: "_nuxt/Zee5.iWW2aZYt.png" },
  { revision: null, url: "_nuxt/Zee5Logo.CoMEAfHG.png" },
  { revision: null, url: "_nuxt/zxdPfbho.js" },
  { revision: "0182d08754a03eae527efc2bc4ae8725", url: "apple-touch-icon.png" },
  { revision: "6add9e78ff262f0dc61a415d901a086e", url: "favicon.ico" },
  { revision: "05be6d60523b67e41d44bcb681bc57f2", url: "favicon.png" },
  { revision: "05be6d60523b67e41d44bcb681bc57f2", url: "logo.png" },
  { revision: "0182d08754a03eae527efc2bc4ae8725", url: "pwa-152x152.png" },
  { revision: "a87c132a471a963fa3075b40fdbc2f2b", url: "pwa-512x512.png" },
  { revision: "bda48072dad30fbd42ca761b2cd35366", url: "rem.js" },
  { revision: "48b6d6a32eb550e45e07d9b11b67fd98", url: "manifest.webmanifest" },
].filter((s) => {
  const e = s.url.toString();
  return !(
    e.endsWith(".json") ||
    e.endsWith(".css") ||
    e.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)
  );
});
const Re =
    self.location.hostname === "h5-test.aoneroom.com"
      ? 5 * 60
      : 3 * 24 * 60 * 60,
  Ce = (s, e) => {
    const t =
        (e.origin === "https://h5-static-test.aoneroom.com" &&
          s.destination === "style" &&
          e.pathname.startsWith("/oneroomStatic/public/_nuxt/")) ||
        (e.origin === "https://h5-static.aoneroom.com" &&
          s.destination === "style" &&
          e.pathname.startsWith("/oneroomStatic/public/_nuxt/")),
      n =
        (e.origin === "https://h5-static-test.aoneroom.com" &&
          s.destination === "script" &&
          e.pathname.startsWith("/oneroomStatic/public/_nuxt/")) ||
        (e.origin === "https://h5-static.aoneroom.com" &&
          s.destination === "script" &&
          e.pathname.startsWith("/oneroomStatic/public/_nuxt/"));
    return t || n;
  };
be(
  ({ request: s, url: e }) => Ce(s, e),
  new xe({
    cacheName: "static-resources",
    plugins: [
      new le({ maxAgeSeconds: Re, maxEntries: 200, purgeOnQuotaError: !0 }),
    ],
  })
);
