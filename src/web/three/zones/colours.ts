export const STATUS_COLOR = {
  normal:   '#22c55e',
  warning:  '#eab308',
  critical: '#ef4444',
} as const

export type ZoneStatus = keyof typeof STATUS_COLOR