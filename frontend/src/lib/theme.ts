/** Дизайн-токены v2 — «биржевой терминал»: почти чёрная база с зелёным
 * подтоном, глубокий изумрудный герой-блок и малиновый фирменный акцент.
 * Направление задано референсами пользователя (тёмный фон + зелёные панели
 * + розовые CTA + фильтры-чипсы + метрики-таблетки). */

export interface AccentTokens {
  solid: string;
  text: string;
  chipOn: string;
  soft: string;
  focus: string;
  hover: string;
  border: string;
}

export interface Accent {
  name: string;
  dot: string;
  hex: string;
  dark: AccentTokens;
  light: AccentTokens;
}

export const ACCENTS: Record<string, Accent> = {
  raspberry: {
    name: "Малина", dot: "bg-[#e21b5a]", hex: "#e21b5a",
    dark: { solid: "bg-[#e21b5a] text-white hover:bg-[#f0316d]", text: "text-[#ff5c8f]", chipOn: "bg-[#e21b5a] text-white border-[#e21b5a]", soft: "bg-[#3a0f1e] text-[#ff7ba3]", focus: "focus:border-[#e21b5a]", hover: "hover:text-[#ff5c8f]", border: "border-[#e21b5a]" },
    light: { solid: "bg-[#d61553] text-white hover:bg-[#e21b5a]", text: "text-[#c81050]", chipOn: "bg-[#d61553] text-white border-[#d61553]", soft: "bg-[#fce7ee] text-[#c81050]", focus: "focus:border-[#d61553]", hover: "hover:text-[#c81050]", border: "border-[#d61553]" },
  },
  teal: {
    name: "Бирюза", dot: "bg-[#17b597]", hex: "#17b597",
    dark: { solid: "bg-[#17b597] text-[#04231b] hover:bg-[#2ec9a9]", text: "text-[#2ec9a9]", chipOn: "bg-[#17b597] text-[#04231b] border-[#17b597]", soft: "bg-[#0b2f27] text-[#2ec9a9]", focus: "focus:border-[#17b597]", hover: "hover:text-[#2ec9a9]", border: "border-[#17b597]" },
    light: { solid: "bg-[#0f9c81] text-white hover:bg-[#17b597]", text: "text-[#0b8a72]", chipOn: "bg-[#0f9c81] text-white border-[#0f9c81]", soft: "bg-[#d9f3ec] text-[#0b8a72]", focus: "focus:border-[#0f9c81]", hover: "hover:text-[#0b8a72]", border: "border-[#0f9c81]" },
  },
  violet: {
    name: "Фиолетовый", dot: "bg-[#8b6cf6]", hex: "#8b6cf6",
    dark: { solid: "bg-[#8b6cf6] text-white hover:bg-[#9d84f8]", text: "text-[#a58ffb]", chipOn: "bg-[#8b6cf6] text-white border-[#8b6cf6]", soft: "bg-[#241b45] text-[#b3a1fb]", focus: "focus:border-[#8b6cf6]", hover: "hover:text-[#a58ffb]", border: "border-[#8b6cf6]" },
    light: { solid: "bg-[#7a5af0] text-white hover:bg-[#8b6cf6]", text: "text-[#6a48e8]", chipOn: "bg-[#7a5af0] text-white border-[#7a5af0]", soft: "bg-[#ece7fd] text-[#6a48e8]", focus: "focus:border-[#7a5af0]", hover: "hover:text-[#6a48e8]", border: "border-[#7a5af0]" },
  },
  amber: {
    name: "Янтарь", dot: "bg-[#d9a915]", hex: "#d9a915",
    dark: { solid: "bg-[#d9a915] text-[#241c02] hover:bg-[#eabc2a]", text: "text-[#eabc2a]", chipOn: "bg-[#d9a915] text-[#241c02] border-[#d9a915]", soft: "bg-[#2c2408] text-[#eabc2a]", focus: "focus:border-[#d9a915]", hover: "hover:text-[#eabc2a]", border: "border-[#d9a915]" },
    light: { solid: "bg-[#c79a0e] text-white hover:bg-[#d9a915]", text: "text-[#9a7708]", chipOn: "bg-[#c79a0e] text-white border-[#c79a0e]", soft: "bg-[#f8efd2] text-[#9a7708]", focus: "focus:border-[#c79a0e]", hover: "hover:text-[#9a7708]", border: "border-[#c79a0e]" },
  },
};

export interface Tokens {
  page: string; header: string; panel: string; card: string; border: string;
  muted: string; faint: string; strong: string; input: string;
  rowEven: string; rowOdd: string; rowHover: string; thead: string;
  chipOff: string; btn: string; soft: string; up: string; down: string;
  grid: string; axis: string; tooltipBg: string;
  /** Зелёный герой-блок (фирменный элемент — одинаков в обеих темах) */
  hero: string; onHero: string; onHeroFaint: string; heroInput: string;
}

/** Изумруд героя: общий для тёмной и светлой темы — это бренд, а не тема. */
const HERO = {
  hero: "bg-[radial-gradient(120%_140%_at_85%_-20%,#17795c_0%,#0e4a38_45%,#0a3a2c_100%)]",
  onHero: "text-white",
  onHeroFaint: "text-[#a9d4c4]",
  heroInput: "bg-white text-zinc-900 placeholder-zinc-500",
};

export const makeTokens = (dark: boolean): Tokens =>
  dark
    ? { page: "bg-[#0c0f0e] text-[#e8ecea]", header: "bg-[#0c0f0e] border-[#1c2420]",
        panel: "bg-[#101412] border-[#222b26]", card: "bg-[#121715] border-[#232d28]",
        border: "border-[#1e2723]", muted: "text-[#93a19a]", faint: "text-[#66746d]",
        strong: "text-[#f2f5f3]",
        input: "bg-[#0c0f0e] border-[#2a352f] text-[#e8ecea] placeholder-[#5a6862]",
        rowEven: "bg-[#101412]", rowOdd: "bg-[#0c0f0e]", rowHover: "hover:bg-[#182019]",
        thead: "bg-[#0c0f0e] text-[#66746d] border-[#1e2723]",
        chipOff: "bg-transparent text-[#93a19a] border-[#2c3831] hover:border-[#4a5a52]",
        btn: "border-[#2c3831] text-[#c4cec9] hover:bg-[#182019]",
        soft: "bg-[#1a221e]", up: "text-[#2ec9a9]", down: "text-[#ff6b8a]",
        grid: "#1e2723", axis: "#66746d", tooltipBg: "#121715", ...HERO }
    : { page: "bg-[#f3f5f4] text-[#17201c]", header: "bg-white border-[#e2e8e5]",
        panel: "bg-white border-[#e2e8e5] shadow-sm", card: "bg-white border-[#e2e8e5] shadow-sm",
        border: "border-[#e2e8e5]", muted: "text-[#5d6b64]", faint: "text-[#8b988f]",
        strong: "text-[#101815]",
        input: "bg-white border-[#cfd8d3] text-[#17201c] placeholder-[#9aa69f]",
        rowEven: "bg-[#f8faf9]", rowOdd: "bg-white", rowHover: "hover:bg-[#eef3f0]",
        thead: "bg-[#f3f5f4] text-[#8b988f] border-[#e2e8e5]",
        chipOff: "bg-transparent text-[#5d6b64] border-[#cfd8d3] hover:border-[#9aa69f]",
        btn: "border-[#cfd8d3] text-[#44514a] hover:bg-[#eef3f0]",
        soft: "bg-[#e9efec]", up: "text-[#0b8a72]", down: "text-[#d61553]",
        grid: "#e2e8e5", axis: "#8b988f", tooltipBg: "#ffffff", ...HERO };

export type AccentStyle = AccentTokens & { hex: string };

export const getAccent = (key: string, dark: boolean): AccentStyle => {
  const a = ACCENTS[key] ?? ACCENTS.raspberry;
  return { ...(dark ? a.dark : a.light), hex: a.hex };
};

