"use client";

import { useState, useRef, useCallback } from "react";
import {
  ChevronLeft, ChevronRight, Download, RotateCcw,
  Loader2, AlertCircle, Sparkles, Copy, Check,
  RefreshCw, X, Settings, Type,
} from "lucide-react";

const API = "http://localhost:8001";
const SLIDE_FULL = 1080;

// ─── Types ────────────────────────────────────────────────────────────────────

interface Takeaway {
  headline: string;
  body: string;
  slideImageUrl?: string;
  slideImagePath?: string;
}

interface SlideColors {
  slideBg: string;
  headline: string;
  body: string;
  progressBar: string;
}

interface SlideTypography {
  headlineFont: string;
  bodyFont: string;
  headlineSize: number;
  bodySize: number;
}

interface CarouselState {
  id: string;
  title: string;
  coverImage: string | null;
  coverImagePath: string | null;
  takeaways: Takeaway[];
  caption: string;
  hashtags: string[];
  colors: SlideColors;
  typography: SlideTypography;
}

type Phase = "idle" | "scraping" | "generating" | "rendering" | "done" | "error";

const DEFAULT_COLORS: SlideColors = {
  slideBg: "#E8EDF4",
  headline: "#555555",
  body: "#6B6B6B",
  progressBar: "#E8A838",
};

const DEFAULT_TYPOGRAPHY: SlideTypography = {
  headlineFont: "Source Serif 4",
  bodyFont: "Plus Jakarta Sans",
  headlineSize: 32,
  bodySize: 22,
};

const FONT_OPTIONS = [
  "Source Serif 4", "Plus Jakarta Sans", "DM Sans",
  "Inter", "Lora", "Merriweather", "Roboto", "Open Sans",
];

const FONT_CSS: Record<string, string> = {
  "Plus Jakarta Sans": "var(--font-jakarta, 'Plus Jakarta Sans', sans-serif)",
  "DM Sans":           "var(--font-dm, 'DM Sans', sans-serif)",
  "Source Serif 4":    "var(--font-serif, 'Source Serif 4', serif)",
  "Inter":             "var(--font-inter, 'Inter', sans-serif)",
  "Lora":              "var(--font-lora, 'Lora', serif)",
  "Merriweather":      "var(--font-merriweather, 'Merriweather', serif)",
  "Roboto":            "var(--font-roboto, 'Roboto', sans-serif)",
  "Open Sans":         "var(--font-opensans, 'Open Sans', sans-serif)",
};

const PHASE_LABELS = {
  scraping:   "Lendo o artigo...",
  generating: "Gerando conteúdo com IA...",
  rendering:  "Construindo os slides...",
};

// ─── Slide components ─────────────────────────────────────────────────────────

const COVER_BG = "#F5F5F8";

function SlideScaler({ displaySize, children }: { displaySize: number; children: React.ReactNode }) {
  const scale = displaySize / SLIDE_FULL;
  return (
    <div style={{ width: displaySize, height: displaySize, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", top: 0, left: 0, width: SLIDE_FULL, height: SLIDE_FULL, transformOrigin: "top left", transform: `scale(${scale})` }}>
        {children}
      </div>
    </div>
  );
}

function EditableDiv({ value, onChange, style }: {
  value: string;
  onChange: (v: string) => void;
  style?: React.CSSProperties;
}) {
  return (
    <div
      contentEditable
      suppressContentEditableWarning
      onBlur={(e) => onChange(e.currentTarget.textContent || "")}
      dangerouslySetInnerHTML={{ __html: value }}
      title="Clique para editar"
      style={{ outline: "none", cursor: "text", borderRadius: 4, transition: "background 0.15s", ...style }}
      onFocus={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(232,168,56,0.08)"; }}
      onBlurCapture={(e) => { (e.currentTarget as HTMLElement).style.background = ""; }}
    />
  );
}

function CoverSlide({ title, coverImage, colors, typography, onTitleChange, onImageUrlChange, onImageUpload }: {
  title: string;
  coverImage: string | null;
  colors: SlideColors;
  typography: SlideTypography;
  onTitleChange: (v: string) => void;
  onImageUrlChange: (v: string) => void;
  onImageUpload?: (file: File) => void;
}) {
  const topH = Math.round(SLIDE_FULL * 0.65);
  const botH = SLIDE_FULL - topH;
  const [showImgInput, setShowImgInput] = useState(false);
  const [imgUrl, setImgUrl] = useState(coverImage || "");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hf = FONT_CSS[typography.headlineFont] || "'Source Serif 4', serif";

  return (
    <div style={{ width: SLIDE_FULL, height: SLIDE_FULL, display: "flex", flexDirection: "column", background: COVER_BG }}>
      <div style={{
        width: SLIDE_FULL, height: topH, flexShrink: 0, position: "relative",
        background: coverImage ? undefined : colors.slideBg,
        backgroundImage: coverImage ? `url(${coverImage})` : undefined,
        backgroundSize: "cover", backgroundPosition: "center",
      }}>
        <div
          onClick={() => setShowImgInput(v => !v)}
          style={{ position: "absolute", top: 20, right: 20, background: "rgba(0,0,0,0.5)", color: "#fff", fontSize: 18, padding: "8px 18px", borderRadius: 8, cursor: "pointer", fontFamily: "var(--font-dm)" }}
        >
          Trocar imagem
        </div>
        {showImgInput && (
          <div style={{ position: "absolute", top: 64, right: 20, background: "#fff", borderRadius: 12, padding: 16, boxShadow: "0 4px 20px rgba(0,0,0,0.18)", display: "flex", flexDirection: "column", gap: 10, zIndex: 10, minWidth: 340 }}>
            {onImageUpload && (
              <>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={e => { const f = e.target.files?.[0]; if (f) { onImageUpload(f); setShowImgInput(false); } }}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{ background: "#E8712A", color: "#fff", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontSize: 16, fontWeight: 600 }}
                >
                  Upload do computador
                </button>
                <div style={{ textAlign: "center", fontSize: 13, color: "#aaa" }}>ou cole uma URL</div>
              </>
            )}
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="url"
                value={imgUrl}
                onChange={e => setImgUrl(e.target.value)}
                placeholder="URL da imagem..."
                style={{ border: "1px solid #ddd", borderRadius: 8, padding: "6px 12px", fontSize: 14, flex: 1, outline: "none" }}
              />
              <button
                onClick={() => { onImageUrlChange(imgUrl); setShowImgInput(false); }}
                style={{ background: "#E8712A", color: "#fff", border: "none", borderRadius: 8, padding: "6px 16px", cursor: "pointer", fontSize: 14 }}
              >OK</button>
            </div>
          </div>
        )}
      </div>
      <div style={{ width: SLIDE_FULL, height: botH, background: COVER_BG, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 80px", flexShrink: 0 }}>
        <EditableDiv
          value={title}
          onChange={onTitleChange}
          style={{ fontFamily: hf, fontSize: typography.headlineSize, fontWeight: 400, color: colors.headline, textAlign: "center", lineHeight: 1.3, marginBottom: 24, width: "100%" }}
        />
        <div style={{ width: 40, height: 4, background: colors.progressBar, borderRadius: 2 }} />
      </div>
    </div>
  );
}

function ContentSlide({ headline, body, index, total, colors, typography, slideImage, onHeadlineChange, onBodyChange, onImageUpload, onImageRemove }: {
  headline: string; body: string; index: number; total: number;
  colors: SlideColors; typography: SlideTypography;
  slideImage?: string;
  onHeadlineChange: (v: string) => void;
  onBodyChange: (v: string) => void;
  onImageUpload?: (file: File) => void;
  onImageRemove?: () => void;
}) {
  const pct = ((index + 1) / total) * 100;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hf = FONT_CSS[typography.headlineFont] || "'Source Serif 4', serif";
  const bf = FONT_CSS[typography.bodyFont] || "'Plus Jakarta Sans', sans-serif";

  return (
    <div style={{ width: SLIDE_FULL, height: SLIDE_FULL, position: "relative", background: colors.slideBg }}>
      <div style={{ padding: "100px 65px 0 65px" }}>
        <EditableDiv
          value={headline}
          onChange={onHeadlineChange}
          style={{ fontFamily: hf, fontSize: typography.headlineSize, fontWeight: 500, color: colors.headline, lineHeight: 1.3, marginBottom: 32 }}
        />
        <EditableDiv
          value={body}
          onChange={onBodyChange}
          style={{ fontFamily: bf, fontSize: typography.bodySize, fontWeight: 400, color: colors.body, lineHeight: 1.65 }}
        />
        {slideImage && (
          <div style={{ marginTop: 28 }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={slideImage} alt="" style={{ width: "100%", maxHeight: 260, objectFit: "cover", borderRadius: 12, display: "block" }} />
          </div>
        )}
        {onImageUpload && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={e => { const f = e.target.files?.[0]; if (f) onImageUpload(f); e.target.value = ""; }}
            />
            <div style={{ marginTop: 24 }}>
              {!slideImage ? (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{ fontSize: 18, padding: "8px 20px", background: "rgba(255,255,255,0.85)", border: "1px dashed #ccc", borderRadius: 10, cursor: "pointer", color: "#777", fontFamily: "var(--font-dm)" }}
                >
                  + Adicionar imagem
                </button>
              ) : (
                <button
                  onClick={onImageRemove}
                  style={{ fontSize: 18, padding: "8px 20px", background: "rgba(254,226,226,0.9)", border: "1px solid #fca5a5", borderRadius: 10, cursor: "pointer", color: "#dc2626", fontFamily: "var(--font-dm)" }}
                >
                  × Remover imagem
                </button>
              )}
            </div>
          </>
        )}
      </div>
      <div style={{ position: "absolute", bottom: 0, left: 0, width: `${pct}%`, height: 8, background: colors.progressBar }} />
    </div>
  );
}

function CTASlide({ index, total, colors }: { index: number; total: number; colors: SlideColors }) {
  const pct = ((index + 1) / total) * 100;
  return (
    <div style={{ width: SLIDE_FULL, height: SLIDE_FULL, position: "relative" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/cta-slide.png" alt="CTA" style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, width: `${pct}%`, height: 8, background: colors.progressBar }} />
    </div>
  );
}

// ─── Small reusable UI pieces ─────────────────────────────────────────────────

function ColorField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
      <span style={{ fontSize: 13, color: "#555" }}>{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <input type="color" value={value} onChange={e => onChange(e.target.value)} style={{ width: 32, height: 28, border: "none", borderRadius: 6, cursor: "pointer", padding: 2 }} />
        <span style={{ fontSize: 12, color: "#888", fontFamily: "monospace" }}>{value}</span>
      </div>
    </label>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "#2B5EA7", background: "none", border: "none", cursor: "pointer", padding: "2px 6px" }}>
      {copied ? <Check size={13} /> : <Copy size={13} />}
      {copied ? "Copiado!" : "Copiar"}
    </button>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function Home() {
  const [url, setUrl] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [carousel, setCarousel] = useState<CarouselState | null>(null);
  const [current, setCurrent] = useState(0);
  const [showColors, setShowColors] = useState(false);
  const [showTypography, setShowTypography] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [newHashtag, setNewHashtag] = useState("");
  const [regenerating, setRegenerating] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const isLoading = phase === "scraping" || phase === "generating" || phase === "rendering";
  const totalSlides = carousel ? carousel.takeaways.length + 2 : 0;

  // ── Generate ────────────────────────────────────────────────────────────────

  async function generate() {
    const trimmed = url.trim();
    if (!trimmed) return;
    setPhase("scraping");
    setError(null);
    setCarousel(null);
    setCurrent(0);

    const t1 = setTimeout(() => setPhase("generating"), 8_000);
    const t2 = setTimeout(() => setPhase("rendering"), 20_000);

    try {
      const res = await fetch(`${API}/api/carousel/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmed }),
      });
      clearTimeout(t1); clearTimeout(t2);
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        throw new Error(b.detail ?? `Erro ${res.status}`);
      }
      const data = await res.json();
      setCarousel({
        id: data.carousel_id,
        title: data.title,
        coverImage: data.cover_image ?? null,
        coverImagePath: null,
        takeaways: data.takeaways,
        caption: data.caption,
        hashtags: data.hashtags,
        colors: { ...DEFAULT_COLORS },
        typography: { ...DEFAULT_TYPOGRAPHY },
      });
      setPhase("done");
    } catch (e: unknown) {
      clearTimeout(t1); clearTimeout(t2);
      setError(e instanceof Error ? e.message : "Erro inesperado.");
      setPhase("error");
    }
  }

  function reset() {
    setPhase("idle"); setError(null); setCarousel(null); setCurrent(0); setUrl("");
    setTimeout(() => inputRef.current?.focus(), 50);
  }

  // ── Slide editing helpers ───────────────────────────────────────────────────

  const updateTitle = useCallback((v: string) => setCarousel(c => c ? { ...c, title: v } : c), []);
  const updateCoverImageUrl = useCallback((v: string) => setCarousel(c => c ? { ...c, coverImage: v, coverImagePath: null } : c), []);
  const updateHeadline = useCallback((i: number, v: string) =>
    setCarousel(c => { if (!c) return c; const t = [...c.takeaways]; t[i] = { ...t[i], headline: v }; return { ...c, takeaways: t }; }), []);
  const updateBody = useCallback((i: number, v: string) =>
    setCarousel(c => { if (!c) return c; const t = [...c.takeaways]; t[i] = { ...t[i], body: v }; return { ...c, takeaways: t }; }), []);
  const updateColor = useCallback((key: keyof SlideColors, v: string) =>
    setCarousel(c => c ? { ...c, colors: { ...c.colors, [key]: v } } : c), []);
  const updateTypography = useCallback((key: keyof SlideTypography, v: string | number) =>
    setCarousel(c => c ? { ...c, typography: { ...c.typography, [key]: v } } : c), []);
  const updateCaption = useCallback((v: string) => setCarousel(c => c ? { ...c, caption: v } : c), []);

  function removeHashtag(tag: string) {
    setCarousel(c => c ? { ...c, hashtags: c.hashtags.filter(h => h !== tag) } : c);
  }
  function addHashtag() {
    if (!newHashtag.trim()) return;
    const tag = newHashtag.startsWith("#") ? newHashtag.trim() : `#${newHashtag.trim()}`;
    setCarousel(c => c ? { ...c, hashtags: [...c.hashtags, tag] } : c);
    setNewHashtag("");
  }

  // ── Image upload helpers ────────────────────────────────────────────────────

  async function handleCoverImageUpload(file: File) {
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API}/api/upload/image`, { method: "POST", body: form });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setCarousel(c => c ? { ...c, coverImage: `${API}${data.url}`, coverImagePath: data.path } : c);
    } catch {
      alert("Erro ao fazer upload da imagem.");
    }
  }

  async function handleSlideImageUpload(takeawayIndex: number, file: File) {
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API}/api/upload/image`, { method: "POST", body: form });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setCarousel(c => {
        if (!c) return c;
        const t = [...c.takeaways];
        t[takeawayIndex] = { ...t[takeawayIndex], slideImageUrl: `${API}${data.url}`, slideImagePath: data.path };
        return { ...c, takeaways: t };
      });
    } catch {
      alert("Erro ao fazer upload da imagem.");
    }
  }

  function removeSlideImage(takeawayIndex: number) {
    setCarousel(c => {
      if (!c) return c;
      const t = [...c.takeaways];
      t[takeawayIndex] = { ...t[takeawayIndex], slideImageUrl: undefined, slideImagePath: undefined };
      return { ...c, takeaways: t };
    });
  }

  // ── AI Regenerate ───────────────────────────────────────────────────────────

  async function regenerateAI(update: "caption" | "hashtags") {
    if (!carousel) return;
    setRegenerating(true);
    try {
      const res = await fetch(`${API}/api/carousel/regenerate-ai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: carousel.title, takeaways: carousel.takeaways }),
      });
      if (!res.ok) return;
      const data = await res.json();
      setCarousel(c => {
        if (!c) return c;
        if (update === "caption") return { ...c, caption: data.caption };
        return { ...c, hashtags: data.hashtags };
      });
    } finally {
      setRegenerating(false);
    }
  }

  // ── Download ────────────────────────────────────────────────────────────────

  async function download(format: "pdf" | "zip") {
    if (!carousel) return;
    setDownloading(true);
    try {
      const body = {
        title: carousel.title,
        cover_image: carousel.coverImagePath ?? carousel.coverImage,
        takeaways: carousel.takeaways.map(t => ({
          headline: t.headline,
          body: t.body,
          slide_image: t.slideImagePath ?? t.slideImageUrl ?? null,
        })),
        colors: {
          slide_bg:     carousel.colors.slideBg,
          headline:     carousel.colors.headline,
          body:         carousel.colors.body,
          progress_bar: carousel.colors.progressBar,
        },
        typography: {
          headline_font: carousel.typography.headlineFont,
          body_font:     carousel.typography.bodyFont,
          headline_size: carousel.typography.headlineSize,
          body_size:     carousel.typography.bodySize,
        },
      };
      const res = await fetch(`${API}/api/carousel/render-custom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("Erro ao gerar arquivo");
      const data = await res.json();
      const fileUrl = format === "zip"
        ? `${API}/api/carousel/${data.carousel_id}/zip`
        : `${API}/api/carousel/${data.carousel_id}/pdf`;
      window.open(fileUrl, "_blank");
    } catch {
      alert("Erro ao baixar. Tente novamente.");
    } finally {
      setDownloading(false);
    }
  }

  // ── Slide rendering logic ───────────────────────────────────────────────────

  function renderCurrentSlide() {
    if (!carousel) return null;
    const c = carousel.colors;
    const ty = carousel.typography;

    if (current === 0) {
      return (
        <CoverSlide
          title={carousel.title}
          coverImage={carousel.coverImage}
          colors={c}
          typography={ty}
          onTitleChange={updateTitle}
          onImageUrlChange={updateCoverImageUrl}
          onImageUpload={handleCoverImageUpload}
        />
      );
    }
    if (current === totalSlides - 1) {
      return <CTASlide index={current} total={totalSlides} colors={c} />;
    }
    const t = carousel.takeaways[current - 1];
    return (
      <ContentSlide
        headline={t.headline}
        body={t.body}
        index={current}
        total={totalSlides}
        colors={c}
        typography={ty}
        slideImage={t.slideImageUrl}
        onHeadlineChange={v => updateHeadline(current - 1, v)}
        onBodyChange={v => updateBody(current - 1, v)}
        onImageUpload={f => handleSlideImageUpload(current - 1, f)}
        onImageRemove={() => removeSlideImage(current - 1)}
      />
    );
  }

  function renderThumb(i: number) {
    if (!carousel) return null;
    const c = carousel.colors;
    const ty = carousel.typography;
    if (i === 0) return (
      <CoverSlide
        title={carousel.title}
        coverImage={carousel.coverImage}
        colors={c}
        typography={ty}
        onTitleChange={() => {}}
        onImageUrlChange={() => {}}
      />
    );
    if (i === totalSlides - 1) return <CTASlide index={i} total={totalSlides} colors={c} />;
    const t = carousel.takeaways[i - 1];
    return (
      <ContentSlide
        headline={t.headline}
        body={t.body}
        index={i}
        total={totalSlides}
        colors={c}
        typography={ty}
        slideImage={t.slideImageUrl}
        onHeadlineChange={() => {}}
        onBodyChange={() => {}}
      />
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  const DISPLAY = 520;
  const THUMB = 64;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "#F7F7F7" }}>
      {/* Header */}
      <header style={{ backgroundColor: "#1A1A2E", padding: "16px 32px", display: "flex", alignItems: "center", gap: 10 }}>
        <Sparkles size={18} color="#E8712A" />
        <span style={{ color: "#fff", fontFamily: "var(--font-jakarta)", fontSize: 17, fontWeight: 700 }}>
          Clearer Thinking <span style={{ color: "#E8712A" }}>Carousel</span>
        </span>
        <span style={{ background: "#2B5EA7", color: "#fff", fontSize: 11, fontWeight: 600, padding: "2px 10px", borderRadius: 99, marginLeft: 4 }}>Marketing</span>
      </header>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 16px", gap: 32 }}>

        {/* ── Input card ── */}
        {phase !== "done" && (
          <div style={{ width: "100%", maxWidth: 680 }}>
            <div style={{ background: "#fff", borderRadius: 20, border: "1px solid #eee", boxShadow: "0 1px 4px rgba(0,0,0,0.06)", padding: 36 }}>
              <h1 style={{ fontFamily: "var(--font-jakarta)", fontSize: 22, fontWeight: 800, color: "#1A1A2E", marginBottom: 6 }}>Gerar carousel do Instagram</h1>
              <p style={{ fontSize: 14, color: "#737373", marginBottom: 24 }}>Cole o link de um post do blog Clearer Thinking para criar um carousel em segundos.</p>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  ref={inputRef}
                  type="url"
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !isLoading && generate()}
                  placeholder="https://www.clearerthinking.org/post/..."
                  disabled={isLoading}
                  style={{ flex: 1, borderRadius: 12, border: "1px solid #ddd", padding: "12px 16px", fontSize: 14, outline: "none", opacity: isLoading ? 0.5 : 1 }}
                />
                <button
                  onClick={generate}
                  disabled={isLoading || !url.trim()}
                  style={{ display: "flex", alignItems: "center", gap: 8, borderRadius: 12, padding: "12px 24px", background: "#E8712A", color: "#fff", border: "none", fontSize: 14, fontWeight: 600, cursor: isLoading || !url.trim() ? "not-allowed" : "pointer", opacity: isLoading || !url.trim() ? 0.6 : 1, fontFamily: "var(--font-jakarta)" }}
                >
                  {isLoading ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
                  {isLoading ? "Gerando..." : "Gerar Carousel"}
                </button>
              </div>
              {phase === "error" && error && (
                <div style={{ marginTop: 16, display: "flex", gap: 10, background: "#fff5f5", border: "1px solid #fecaca", borderRadius: 12, padding: 14 }}>
                  <AlertCircle size={15} color="#ef4444" style={{ flexShrink: 0, marginTop: 1 }} />
                  <p style={{ fontSize: 13, color: "#b91c1c" }}>{error}</p>
                </div>
              )}
            </div>
            {isLoading && (
              <div style={{ marginTop: 24, display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
                <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                  {(["scraping", "generating", "rendering"] as const).map((p, i) => {
                    const order = ["scraping", "generating", "rendering"];
                    const ci = order.indexOf(phase);
                    const done = i < ci, active = i === ci;
                    return (
                      <div key={p} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ width: 28, height: 28, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#fff", background: done ? "#2B5EA7" : active ? "#E8712A" : "#ddd" }}>
                          {done ? "✓" : i + 1}
                        </div>
                        <span style={{ fontSize: 12, fontWeight: 500, color: active ? "#E8712A" : done ? "#2B5EA7" : "#aaa" }}>{PHASE_LABELS[p]}</span>
                        {i < 2 && <span style={{ color: "#ddd", marginLeft: 4 }}>—</span>}
                      </div>
                    );
                  })}
                </div>
                <p style={{ fontSize: 12, color: "#999" }}>Isso costuma levar entre 30 e 60 segundos.</p>
              </div>
            )}
          </div>
        )}

        {/* ── Editor ── */}
        {phase === "done" && carousel && (
          <div style={{ width: "100%", maxWidth: 1100, display: "flex", flexDirection: "column", gap: 20 }}>

            {/* Top bar */}
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
              <div>
                <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", color: "#E8712A", marginBottom: 4 }}>Carousel gerado</p>
                <h2 style={{ fontFamily: "var(--font-jakarta)", fontSize: 20, fontWeight: 800, color: "#1A1A2E" }}>{carousel.title}</h2>
                <p style={{ fontSize: 13, color: "#999", marginTop: 2 }}>{totalSlides} slides · clique nos textos para editar</p>
              </div>
              <button
                onClick={reset}
                style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 12, border: "1px solid #ddd", background: "#fff", cursor: "pointer", color: "#303030", flexShrink: 0 }}
              >
                <RotateCcw size={13} /> Novo carousel
              </button>
            </div>

            {/* Main grid */}
            <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>

              {/* Left: slide viewer */}
              <div style={{ flex: "0 0 auto", display: "flex", flexDirection: "column", gap: 16 }}>
                <div style={{ borderRadius: 16, overflow: "hidden", boxShadow: "0 4px 24px rgba(0,0,0,0.12)", position: "relative" }}>
                  <SlideScaler displaySize={DISPLAY}>
                    {renderCurrentSlide()}
                  </SlideScaler>
                  {current > 0 && (
                    <button onClick={() => setCurrent(c => c - 1)} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", width: 36, height: 36, borderRadius: "50%", background: "rgba(255,255,255,0.92)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
                      <ChevronLeft size={18} color="#1A1A2E" />
                    </button>
                  )}
                  {current < totalSlides - 1 && (
                    <button onClick={() => setCurrent(c => c + 1)} style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", width: 36, height: 36, borderRadius: "50%", background: "rgba(255,255,255,0.92)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
                      <ChevronRight size={18} color="#1A1A2E" />
                    </button>
                  )}
                  <div style={{ position: "absolute", bottom: 10, right: 12, background: "rgba(0,0,0,0.45)", color: "#fff", fontSize: 12, fontWeight: 500, padding: "3px 10px", borderRadius: 99, backdropFilter: "blur(4px)" }}>
                    {current + 1} / {totalSlides}
                  </div>
                </div>

                {/* Thumbnails */}
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
                  {Array.from({ length: totalSlides }, (_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrent(i)}
                      style={{ border: i === current ? "2px solid #E8712A" : "2px solid transparent", borderRadius: 8, overflow: "hidden", cursor: "pointer", padding: 0, background: "none", opacity: i === current ? 1 : 0.55, transition: "opacity 0.15s", boxShadow: i === current ? "0 0 0 2px rgba(232,113,42,0.25)" : "none" }}
                    >
                      <SlideScaler displaySize={THUMB}>
                        {renderThumb(i)}
                      </SlideScaler>
                    </button>
                  ))}
                </div>
              </div>

              {/* Right: editing panel */}
              <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 16 }}>

                {/* Colors panel */}
                <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #eee", overflow: "hidden" }}>
                  <button
                    onClick={() => setShowColors(v => !v)}
                    style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 18px", background: "none", border: "none", cursor: "pointer" }}
                  >
                    <span style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 600, color: "#1A1A2E" }}><Settings size={14} /> Cores dos slides</span>
                    <span style={{ fontSize: 12, color: "#999" }}>{showColors ? "▲" : "▼"}</span>
                  </button>
                  {showColors && (
                    <div style={{ padding: "4px 18px 18px", display: "flex", flexDirection: "column", gap: 14, borderTop: "1px solid #f0f0f0" }}>
                      <ColorField label="Fundo dos slides" value={carousel.colors.slideBg} onChange={v => updateColor("slideBg", v)} />
                      <ColorField label="Cor do título" value={carousel.colors.headline} onChange={v => updateColor("headline", v)} />
                      <ColorField label="Cor do texto" value={carousel.colors.body} onChange={v => updateColor("body", v)} />
                      <ColorField label="Barra de progresso" value={carousel.colors.progressBar} onChange={v => updateColor("progressBar", v)} />
                    </div>
                  )}
                </div>

                {/* Typography panel */}
                <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #eee", overflow: "hidden" }}>
                  <button
                    onClick={() => setShowTypography(v => !v)}
                    style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 18px", background: "none", border: "none", cursor: "pointer" }}
                  >
                    <span style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, fontWeight: 600, color: "#1A1A2E" }}><Type size={14} /> Tipografia</span>
                    <span style={{ fontSize: 12, color: "#999" }}>{showTypography ? "▲" : "▼"}</span>
                  </button>
                  {showTypography && (
                    <div style={{ padding: "4px 18px 18px", display: "flex", flexDirection: "column", gap: 16, borderTop: "1px solid #f0f0f0" }}>
                      <div>
                        <div style={{ fontSize: 13, color: "#555", marginBottom: 6 }}>Fonte do título</div>
                        <select
                          value={carousel.typography.headlineFont}
                          onChange={e => updateTypography("headlineFont", e.target.value)}
                          style={{ width: "100%", fontSize: 13, border: "1px solid #ddd", borderRadius: 8, padding: "7px 10px", outline: "none", background: "#fff" }}
                        >
                          {FONT_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                        </select>
                      </div>
                      <div>
                        <div style={{ fontSize: 13, color: "#555", display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                          <span>Tamanho do título</span>
                          <span style={{ fontWeight: 600, color: "#1A1A2E" }}>{carousel.typography.headlineSize}px</span>
                        </div>
                        <input
                          type="range" min={24} max={48}
                          value={carousel.typography.headlineSize}
                          onChange={e => updateTypography("headlineSize", +e.target.value)}
                          style={{ width: "100%", accentColor: "#E8712A" }}
                        />
                      </div>
                      <div>
                        <div style={{ fontSize: 13, color: "#555", marginBottom: 6 }}>Fonte do texto</div>
                        <select
                          value={carousel.typography.bodyFont}
                          onChange={e => updateTypography("bodyFont", e.target.value)}
                          style={{ width: "100%", fontSize: 13, border: "1px solid #ddd", borderRadius: 8, padding: "7px 10px", outline: "none", background: "#fff" }}
                        >
                          {FONT_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                        </select>
                      </div>
                      <div>
                        <div style={{ fontSize: 13, color: "#555", display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                          <span>Tamanho do texto</span>
                          <span style={{ fontWeight: 600, color: "#1A1A2E" }}>{carousel.typography.bodySize}px</span>
                        </div>
                        <input
                          type="range" min={16} max={28}
                          value={carousel.typography.bodySize}
                          onChange={e => updateTypography("bodySize", +e.target.value)}
                          style={{ width: "100%", accentColor: "#E8712A" }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Caption */}
                <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #eee", padding: 18 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#1A1A2E" }}>Caption do Instagram</span>
                    <div style={{ display: "flex", gap: 8 }}>
                      <CopyButton text={carousel.caption} />
                      <button
                        onClick={() => regenerateAI("caption")}
                        disabled={regenerating}
                        style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "#2B5EA7", background: "none", border: "none", cursor: "pointer" }}
                      >
                        <RefreshCw size={13} className={regenerating ? "animate-spin" : ""} />
                        Regerar
                      </button>
                    </div>
                  </div>
                  <textarea
                    value={carousel.caption}
                    onChange={e => updateCaption(e.target.value)}
                    rows={4}
                    style={{ width: "100%", fontSize: 13, color: "#303030", border: "1px solid #e8e8e8", borderRadius: 10, padding: "10px 12px", resize: "vertical", outline: "none", lineHeight: 1.6, fontFamily: "var(--font-dm)" }}
                  />
                  <p style={{ fontSize: 11, color: "#aaa", marginTop: 4 }}>{carousel.caption.length}/200 caracteres</p>
                </div>

                {/* Hashtags */}
                <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #eee", padding: 18 }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#1A1A2E" }}>Hashtags</span>
                    <div style={{ display: "flex", gap: 8 }}>
                      <CopyButton text={carousel.hashtags.join(" ")} />
                      <button
                        onClick={() => regenerateAI("hashtags")}
                        disabled={regenerating}
                        style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, color: "#2B5EA7", background: "none", border: "none", cursor: "pointer" }}
                      >
                        <RefreshCw size={13} className={regenerating ? "animate-spin" : ""} />
                        Regerar
                      </button>
                    </div>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
                    {carousel.hashtags.map(tag => (
                      <span key={tag} style={{ display: "flex", alignItems: "center", gap: 4, background: "#EEF2FF", color: "#2B5EA7", fontSize: 12, fontWeight: 500, padding: "4px 10px", borderRadius: 99 }}>
                        {tag}
                        <button onClick={() => removeHashtag(tag)} style={{ background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center", color: "#93A5D4" }}>
                          <X size={11} />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <input
                      value={newHashtag}
                      onChange={e => setNewHashtag(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && addHashtag()}
                      placeholder="#novahashtag"
                      style={{ flex: 1, fontSize: 12, border: "1px solid #e8e8e8", borderRadius: 8, padding: "6px 10px", outline: "none" }}
                    />
                    <button onClick={addHashtag} style={{ fontSize: 12, padding: "6px 14px", background: "#E8712A", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer" }}>Adicionar</button>
                  </div>
                </div>

                {/* Download buttons */}
                <div style={{ display: "flex", gap: 10 }}>
                  <button
                    onClick={() => download("zip")}
                    disabled={downloading}
                    style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "13px 0", borderRadius: 14, background: "#E8712A", color: "#fff", border: "none", fontSize: 14, fontWeight: 600, cursor: downloading ? "not-allowed" : "pointer", opacity: downloading ? 0.7 : 1, fontFamily: "var(--font-jakarta)" }}
                  >
                    {downloading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
                    {downloading ? "Gerando..." : "Baixar PNGs (ZIP)"}
                  </button>
                  <button
                    onClick={() => download("pdf")}
                    disabled={downloading}
                    style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "13px 0", borderRadius: 14, background: "#2B5EA7", color: "#fff", border: "none", fontSize: 14, fontWeight: 600, cursor: downloading ? "not-allowed" : "pointer", opacity: downloading ? 0.7 : 1, fontFamily: "var(--font-jakarta)" }}
                  >
                    {downloading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
                    {downloading ? "Gerando..." : "Baixar PDF com edições"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer style={{ padding: "16px 0", textAlign: "center", fontSize: 12, color: "#999" }}>
        Clearer Thinking Carousel Generator · uso interno
      </footer>
    </div>
  );
}
