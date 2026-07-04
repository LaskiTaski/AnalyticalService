import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { Header } from "./components/layout/Header";
import { BondDrawer } from "./components/bonds/BondDrawer";
import { ScreenerPage } from "./pages/ScreenerPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PricingPage } from "./pages/PricingPage";
import { ACCENTS, getAccent, makeTokens } from "./lib/theme";

/** /bonds/:secid — прямая ссылка на бумагу открывает скринер с панелью деталей. */
function BondRedirect({ onOpen }: { onOpen: (secid: string) => void }) {
  const { secid } = useParams();
  useEffect(() => {
    if (secid) onOpen(secid.toUpperCase());
  }, [secid, onOpen]);
  return <Navigate to="/screener" replace />;
}

export default function App() {
  const [dark, setDark] = useState(() => localStorage.getItem("theme") !== "light");
  const [accent, setAccent] = useState(() => {
    const stored = localStorage.getItem("accent");
    // Миграция после редизайна: старые акценты (emerald/sky/rose) больше не существуют
    return stored && stored in ACCENTS ? stored : "raspberry";
  });
  const [selected, setSelected] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => localStorage.setItem("theme", dark ? "dark" : "light"), [dark]);
  useEffect(() => localStorage.setItem("accent", accent), [accent]);

  const t = makeTokens(dark);
  const A = getAccent(accent, dark);

  return (
    <div className={`min-h-screen font-sans transition-colors ${t.page}`}
      style={{ colorScheme: dark ? "dark" : "light" }}>
      <Header dark={dark} setDark={setDark} accent={accent} setAccent={setAccent} t={t} A={A} />
      {/* На десктопе открытая панель бумаги сдвигает контент, а не перекрывает его */}
      <div className={`transition-[padding-right] duration-200 ${selected ? "lg:pr-[28rem]" : ""}`}>
        <Routes>
          <Route path="/" element={<Navigate to="/screener" replace />} />
          <Route path="/screener"
            element={<ScreenerPage t={t} A={A} dark={dark} openBond={setSelected} selected={selected} />} />
          <Route path="/dashboard" element={<DashboardPage t={t} A={A} openBond={setSelected} />} />
          <Route path="/pricing" element={<PricingPage t={t} A={A} />} />
          <Route path="/bonds/:secid" element={<BondRedirect onOpen={setSelected} />} />
          <Route path="*" element={<Navigate to="/screener" replace />} />
        </Routes>
      </div>
      {selected && (
        <BondDrawer secid={selected} onClose={() => setSelected(null)}
          onSelect={(s) => { setSelected(s); navigate("/screener"); }} t={t} A={A} dark={dark} />
      )}
    </div>
  );
}
