/**
 * Фирменный знак: процент, прочитанный как снежный ком.
 * Слэш — склон, два круга — ком, который растёт, катясь вниз:
 * метафора сложного процента («снежный ком» капитала, FIRE).
 */
export function LogoMark({ size = 18, className }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true" className={className}>
      <line x1="23.5" y1="5.5" x2="8.5" y2="26.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" />
      <circle cx="9.5" cy="9" r="4.1" fill="currentColor" />
      <circle cx="22" cy="22.5" r="6.2" fill="currentColor" />
    </svg>
  );
}
