/**
 * Formats a numeric INR amount using Indian locale conventions.
 *
 * Uses Intl.NumberFormat with:
 *   locale  : en-IN  (produces lakh/crore grouping: 1,00,000)
 *   currency: INR
 *   style   : currency
 *
 * maximumFractionDigits: 0  — no paise displayed for whole-rupee prices.
 *
 * Examples:
 *   formatINR(1200)     → ₹1,200
 *   formatINR(12500)    → ₹12,500
 *   formatINR(125000)   → ₹1,25,000
 *   formatINR(1050000)  → ₹10,50,000
 */
const inrFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

export function formatINR(amount: number): string {
  return inrFormatter.format(amount)
}

/**
 * Returns a compact label like "from ₹1,25,000" suitable for card badges.
 */
export function formatINRFrom(amount: number): string {
  return `from ${formatINR(amount)}`
}
