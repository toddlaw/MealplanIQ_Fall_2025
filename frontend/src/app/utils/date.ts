export function weekSpanFor(baseDate: Date, weekStart: number = 6): { start: string; end: string } {
  const d = stripTime(baseDate);
  const day = d.getDay();
  const delta = (day - weekStart + 7) % 7;

  const startDate = addDays(d, -delta);
  const endDate = addDays(startDate, 6);

  return {
    start: formatYmd(startDate),
    end: formatYmd(endDate),
  };
}

export function stripTime(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export function addDays(date: Date, days: number): Date {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}

export function formatYmd(date: Date): string {
  const y = date.getFullYear();
  const m = (date.getMonth() + 1).toString().padStart(2, '0');
  const d = date.getDate().toString().padStart(2, '0');
  return `${y}-${m}-${d}`;
}
