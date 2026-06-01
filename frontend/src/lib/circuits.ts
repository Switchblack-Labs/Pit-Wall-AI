







export type Circuit = {
  id: string;             
  name: string;
  shortName: string;      
  country: string;
  city: string;
  length_km: number;
  laps: number;
  corners: number;
  pit_loss_s: number;     
  drs_zones: number;
  drs_detection: number[];
  sectors: [number, number, number]; 
  
  svgPath: string;
  
  reference_lap_s: number;
  flag: string; 
};

export const CIRCUITS: Circuit[] = [
  {
    id: "imola",
    name: "Autodromo Enzo e Dino Ferrari",
    shortName: "Imola",
    country: "Italy",
    city: "Imola",
    length_km: 4.909,
    laps: 63,
    corners: 19,
    pit_loss_s: 22.4,
    drs_zones: 1,
    drs_detection: [0.92],
    sectors: [0.33, 0.36, 0.31],
    svgPath:
      "M 80 220 C 80 120 180 80 280 80 L 460 80 C 540 80 580 130 580 180 L 580 220 C 580 280 540 320 480 320 L 360 320 C 320 320 300 340 300 380 L 300 420 C 300 460 260 480 220 480 L 160 480 C 110 480 80 450 80 400 Z",
    reference_lap_s: 78.7,
    flag: "IT",
  },
  {
    id: "monaco",
    name: "Circuit de Monaco",
    shortName: "Monaco",
    country: "Monaco",
    city: "Monte Carlo",
    length_km: 3.337,
    laps: 78,
    corners: 19,
    pit_loss_s: 22.7,
    drs_zones: 1,
    drs_detection: [0.88],
    sectors: [0.35, 0.32, 0.33],
    svgPath:
      "M 120 460 C 120 410 90 380 90 320 L 110 200 C 130 150 180 130 230 140 L 320 170 C 360 150 400 130 430 150 L 470 200 L 510 200 C 540 220 540 260 510 280 L 470 290 L 440 320 L 460 350 L 480 380 C 470 420 430 440 380 440 L 320 440 L 280 460 L 200 470 C 160 480 120 470 120 460 Z",
    reference_lap_s: 76.1,
    flag: "MC",
  },
  {
    id: "monza",
    name: "Autodromo Nazionale Monza",
    shortName: "Monza",
    country: "Italy",
    city: "Monza",
    length_km: 5.793,
    laps: 53,
    corners: 11,
    pit_loss_s: 20.1,
    drs_zones: 2,
    drs_detection: [0.42, 0.86],
    sectors: [0.30, 0.40, 0.30],
    svgPath:
      "M 80 320 L 540 220 C 580 215 600 230 590 260 L 470 320 L 430 340 L 480 380 L 540 420 C 560 440 540 470 510 470 L 240 470 C 210 470 190 450 200 420 L 220 380 L 180 360 L 100 360 C 75 355 70 335 80 320 Z",
    reference_lap_s: 81.5,
    flag: "IT",
  },
  {
    id: "spa",
    name: "Circuit de Spa-Francorchamps",
    shortName: "Spa",
    country: "Belgium",
    city: "Stavelot",
    length_km: 7.004,
    laps: 44,
    corners: 19,
    pit_loss_s: 20.6,
    drs_zones: 2,
    drs_detection: [0.32, 0.78],
    sectors: [0.31, 0.39, 0.30],
    svgPath:
      "M 100 420 C 80 400 90 360 130 350 L 230 320 C 260 290 250 250 220 240 L 160 220 C 130 200 140 160 180 150 L 320 130 C 380 130 420 160 430 200 L 460 280 C 480 320 530 320 560 290 L 580 240 C 600 230 600 280 570 320 L 520 380 C 480 440 410 460 350 450 L 220 440 C 160 450 120 440 100 420 Z",
    reference_lap_s: 107.0,
    flag: "BE",
  },
  {
    id: "silverstone",
    name: "Silverstone Circuit",
    shortName: "Silverstone",
    country: "United Kingdom",
    city: "Silverstone",
    length_km: 5.891,
    laps: 52,
    corners: 18,
    pit_loss_s: 21.2,
    drs_zones: 2,
    drs_detection: [0.36, 0.80],
    sectors: [0.34, 0.36, 0.30],
    svgPath:
      "M 110 280 C 100 230 140 190 200 180 L 320 170 C 380 160 430 200 440 250 L 460 320 C 470 360 510 380 540 360 L 560 320 C 580 320 580 360 560 400 L 510 460 C 460 480 400 470 360 450 L 280 440 L 210 460 C 150 460 110 430 110 380 Z",
    reference_lap_s: 88.0,
    flag: "GB",
  },
  {
    id: "suzuka",
    name: "Suzuka International Racing Course",
    shortName: "Suzuka",
    country: "Japan",
    city: "Suzuka",
    length_km: 5.807,
    laps: 53,
    corners: 18,
    pit_loss_s: 21.9,
    drs_zones: 1,
    drs_detection: [0.94],
    sectors: [0.35, 0.34, 0.31],
    svgPath:
      "M 120 440 C 100 400 130 360 170 350 L 240 320 L 200 270 C 170 230 200 180 250 180 L 360 200 C 380 160 430 150 460 180 L 500 220 C 510 260 480 290 450 290 L 400 320 L 460 360 C 490 380 490 420 460 440 L 350 460 C 290 460 230 450 200 460 L 160 470 C 140 470 120 460 120 440 Z",
    reference_lap_s: 92.0,
    flag: "JP",
  },
  {
    id: "cota",
    name: "Circuit of the Americas",
    shortName: "COTA",
    country: "United States",
    city: "Austin",
    length_km: 5.513,
    laps: 56,
    corners: 20,
    pit_loss_s: 21.8,
    drs_zones: 2,
    drs_detection: [0.30, 0.76],
    sectors: [0.32, 0.38, 0.30],
    svgPath:
      "M 100 280 C 90 240 130 210 180 220 L 240 240 L 290 200 C 320 170 380 170 410 200 L 450 250 C 470 280 510 280 540 260 L 570 240 C 590 250 590 290 570 320 L 510 380 C 480 420 430 430 380 420 L 320 410 C 280 430 230 450 190 440 L 130 420 C 100 410 90 360 100 320 Z",
    reference_lap_s: 96.0,
    flag: "US",
  },
  {
    id: "interlagos",
    name: "Autódromo José Carlos Pace",
    shortName: "Interlagos",
    country: "Brazil",
    city: "São Paulo",
    length_km: 4.309,
    laps: 71,
    corners: 15,
    pit_loss_s: 21.5,
    drs_zones: 2,
    drs_detection: [0.34, 0.82],
    sectors: [0.33, 0.34, 0.33],
    svgPath:
      "M 120 380 C 100 340 130 290 180 280 L 280 260 C 320 220 380 220 410 250 L 450 290 C 480 310 520 310 540 290 L 560 260 C 580 270 580 310 550 340 L 500 410 C 460 450 380 460 320 440 L 240 430 C 180 450 130 440 120 410 Z",
    reference_lap_s: 71.5,
    flag: "BR",
  },
];

export function getCircuit(id: string): Circuit {
  return CIRCUITS.find((c) => c.id === id) ?? CIRCUITS[0];
}
