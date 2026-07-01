import { ZoneStatus } from './colours'

export type InspectionEntry = {
  date: string
  defect: boolean
  defectType?: string
}

export type Zone = {
  id: string
  name: string
  position: [number, number, number]
  status: ZoneStatus
  history: InspectionEntry[]
}

const CLEAR_HISTORY: InspectionEntry[] = [
  { date: '20 Jun 2026', defect: false },
  { date: '15 May 2026', defect: false },
  { date: '10 Apr 2026', defect: false },
]

export const ZONES: Zone[] = [

  { id: '5344', name: 'Door Hinge Area',
    position: [-2.4, -0.99, 0],  status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: false },
      { date: '15 May 2026', defect: true, defectType: 'Scratch' },
      { date: '10 Apr 2026', defect: false },
    ]},

  { id: '5311', name: 'Fuselage Frame',
    position: [-1.97, -0.81, 0],  status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5330', name: 'Fuselage Skin / Plate',
    position: [-1.6, -0.642, 0],  status: 'critical',
    history: [
      { date: '20 Jun 2026', defect: true, defectType: 'Crack' },
      { date: '15 May 2026', defect: false },
      { date: '10 Apr 2026', defect: false },
    ]},

  { id: '5313', name: 'Longeron / Stringer',
    position: [-1.3, -0.53, 0],     status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: true, defectType: 'Paint' },
      { date: '15 May 2026', defect: true, defectType: 'Paint' },
      { date: '10 Apr 2026', defect: false },
    ]},

  { id: '5310', name: 'Fuselage Main Structure',
    position: [-0.6, -0.26, 0],   status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5312', name: 'Fuselage Bulkhead',
    position: [0.65, 0.237, 0],   status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: false },
      { date: '15 May 2026', defect: false },
      { date: '10 Apr 2026', defect: true, defectType: 'Scratch' },
    ]},

  { id: '5345', name: 'Equipment Attach Fittings',
    position: [1.23, 0.298, 0],   status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5342', name: 'Stabilizer Attach Fittings',
    position: [2.01, 1.3, 0],   status: 'critical',
    history: [
      { date: '20 Jun 2026', defect: true, defectType: 'Crack' },
      { date: '15 May 2026', defect: true, defectType: 'Crack' },
      { date: '10 Apr 2026', defect: false },
    ]},

  { id: '5315', name: 'Floor Beam',
    position: [-1.8, -0.79, -0.01],  status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5321', name: 'Floor Panel',
    position: [-1.428, -0.64, 0],  status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: false },
      { date: '15 May 2026', defect: true, defectType: 'Dent' },
      { date: '10 Apr 2026', defect: false },
    ]},

  { id: '5314', name: 'Keel Beam',
    position: [0.27, -0.34, 0.25],    status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5343', name: 'Landing Gear Attach Fittings',
    position: [0.42, -0.4, 0.57], status: 'normal',
    history: CLEAR_HISTORY },

  { id: '5341', name: 'Wing Attach Fittings',
    position: [0.5, -0.38, 0.4],    status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: true, defectType: 'Corrosion' },
      { date: '15 May 2026', defect: false },
      { date: '10 Apr 2026', defect: true, defectType: 'Corrosion' },
    ]},

  { id: '5346', name: 'Powerplant Attach Fittings',
    position: [0.28, -0.34, 0.542], status: 'warning',
    history: [
      { date: '20 Jun 2026', defect: false },
      { date: '15 May 2026', defect: false },
      { date: '10 Apr 2026', defect: true, defectType: 'Dent' },
    ]},

  { id: '5350', name: 'Aerodynamic Fairings',
    position: [0.5, -0.326, 0],  status: 'normal',
    history: CLEAR_HISTORY },
]