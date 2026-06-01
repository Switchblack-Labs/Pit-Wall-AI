









export type RaceResult = {
  circuit_id: string;     
  year: number;
  round: number;
  date: string;           
  pole: { driver: string; team: string; time_s: number };
  fastest_lap: { driver: string; team: string; time_s: number; lap: number };
  weather: "dry" | "wet" | "mixed";
  podium: {
    pos: 1 | 2 | 3 | 4 | 5;
    driver: string;
    team: string;
    grid: number;
    strategy: string;     
    stops: number;
    pit_laps: number[];
    delta_to_winner_s: number; 
  }[];
  narrative: string;
  optimal_strategy: string;
  
  reference_window: {
    lap: number;
    leader: string;
    gap_to_p2_s: number;
    leader_compound: "S" | "M" | "H" | "I" | "W";
  }[];
};

export const RESULTS_2024: RaceResult[] = [
  {
    circuit_id: "imola",
    year: 2024,
    round: 7,
    date: "2024-05-19",
    pole: { driver: "VER", team: "Red Bull", time_s: 74.746 },
    fastest_lap: { driver: "RUS", team: "Mercedes", time_s: 78.589, lap: 63 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "VER", team: "Red Bull",     grid: 1, strategy: "Medium > Hard",   stops: 1, pit_laps: [27],     delta_to_winner_s: 0 },
      { pos: 2, driver: "NOR", team: "McLaren",      grid: 3, strategy: "Medium > Hard",   stops: 1, pit_laps: [28],     delta_to_winner_s: 0.7 },
      { pos: 3, driver: "LEC", team: "Ferrari",      grid: 4, strategy: "Medium > Hard",   stops: 1, pit_laps: [25],     delta_to_winner_s: 7.9 },
      { pos: 4, driver: "PIA", team: "McLaren",      grid: 2, strategy: "Medium > Hard",   stops: 1, pit_laps: [29],     delta_to_winner_s: 14.1 },
      { pos: 5, driver: "SAI", team: "Ferrari",      grid: 5, strategy: "Medium > Hard",   stops: 1, pit_laps: [25],     delta_to_winner_s: 22.3 },
    ],
    narrative:
      "Verstappen controlled from pole. McLaren stretched the medium, threatening Norris's late-charge undercut, but couldn't make the pass at a track where overtaking is nearly impossible.",
    optimal_strategy: "1-stop - Medium > Hard - pit window L26-L29",
    reference_window: [
      { lap: 14, leader: "VER", gap_to_p2_s: 2.4, leader_compound: "M" },
      { lap: 15, leader: "VER", gap_to_p2_s: 3.1, leader_compound: "M" },
      { lap: 16, leader: "VER", gap_to_p2_s: 3.8, leader_compound: "M" },
      { lap: 17, leader: "VER", gap_to_p2_s: 4.2, leader_compound: "M" },
      { lap: 18, leader: "VER", gap_to_p2_s: 4.8, leader_compound: "M" },
      { lap: 19, leader: "VER", gap_to_p2_s: 5.5, leader_compound: "M" },
    ],
  },
  {
    circuit_id: "monaco",
    year: 2024,
    round: 8,
    date: "2024-05-26",
    pole: { driver: "LEC", team: "Ferrari", time_s: 70.270 },
    fastest_lap: { driver: "HAM", team: "Mercedes", time_s: 74.165, lap: 76 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "LEC", team: "Ferrari",      grid: 1, strategy: "Medium > Hard (under red flag)", stops: 1, pit_laps: [1], delta_to_winner_s: 0 },
      { pos: 2, driver: "PIA", team: "McLaren",      grid: 2, strategy: "Medium > Hard (under red flag)", stops: 1, pit_laps: [1], delta_to_winner_s: 7.1 },
      { pos: 3, driver: "SAI", team: "Ferrari",      grid: 3, strategy: "Medium > Hard (under red flag)", stops: 1, pit_laps: [1], delta_to_winner_s: 7.4 },
      { pos: 4, driver: "NOR", team: "McLaren",      grid: 4, strategy: "Medium > Hard (under red flag)", stops: 1, pit_laps: [1], delta_to_winner_s: 8.0 },
      { pos: 5, driver: "RUS", team: "Mercedes",     grid: 5, strategy: "Medium > Hard (under red flag)", stops: 1, pit_laps: [1], delta_to_winner_s: 13.6 },
    ],
    narrative:
      "Leclerc won at home. A lap-1 red flag (Perez/Magnussen crash) handed everyone a free pit stop and froze the order. Overtaking at Monaco is functionally impossible, so the strategy game collapsed.",
    optimal_strategy: "Hold position. Pit only on safety car / red flag.",
    reference_window: [
      { lap: 14, leader: "LEC", gap_to_p2_s: 2.6, leader_compound: "H" },
      { lap: 15, leader: "LEC", gap_to_p2_s: 2.7, leader_compound: "H" },
      { lap: 16, leader: "LEC", gap_to_p2_s: 2.9, leader_compound: "H" },
      { lap: 17, leader: "LEC", gap_to_p2_s: 2.8, leader_compound: "H" },
      { lap: 18, leader: "LEC", gap_to_p2_s: 2.9, leader_compound: "H" },
      { lap: 19, leader: "LEC", gap_to_p2_s: 3.0, leader_compound: "H" },
    ],
  },
  {
    circuit_id: "monza",
    year: 2024,
    round: 16,
    date: "2024-09-01",
    pole: { driver: "NOR", team: "McLaren", time_s: 79.223 },
    fastest_lap: { driver: "RUS", team: "Mercedes", time_s: 84.183, lap: 48 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "LEC", team: "Ferrari",      grid: 4, strategy: "Medium > Hard",         stops: 1, pit_laps: [15],          delta_to_winner_s: 0 },
      { pos: 2, driver: "PIA", team: "McLaren",      grid: 2, strategy: "Medium > Hard > Hard",  stops: 2, pit_laps: [14, 33],       delta_to_winner_s: 2.7 },
      { pos: 3, driver: "NOR", team: "McLaren",      grid: 1, strategy: "Medium > Hard > Hard",  stops: 2, pit_laps: [14, 33],       delta_to_winner_s: 6.2 },
      { pos: 4, driver: "SAI", team: "Ferrari",      grid: 5, strategy: "Medium > Hard",         stops: 1, pit_laps: [15],          delta_to_winner_s: 15.6 },
      { pos: 5, driver: "HAM", team: "Mercedes",     grid: 6, strategy: "Medium > Hard",         stops: 1, pit_laps: [14],          delta_to_winner_s: 22.7 },
    ],
    narrative:
      "Leclerc won by staying out on a one-stop while McLaren over-pitted (2-stop). The tyre-saving call against grid expectations turned a fourth-place start into a home win.",
    optimal_strategy: "1-stop - Medium > Hard - stretch the medium to L16+",
    reference_window: [
      { lap: 14, leader: "NOR", gap_to_p2_s: 1.4, leader_compound: "M" },
      { lap: 15, leader: "LEC", gap_to_p2_s: 0.6, leader_compound: "M" },
      { lap: 16, leader: "LEC", gap_to_p2_s: 1.1, leader_compound: "M" },
      { lap: 17, leader: "LEC", gap_to_p2_s: 1.7, leader_compound: "M" },
      { lap: 18, leader: "LEC", gap_to_p2_s: 2.3, leader_compound: "M" },
      { lap: 19, leader: "LEC", gap_to_p2_s: 2.8, leader_compound: "M" },
    ],
  },
  {
    circuit_id: "spa",
    year: 2024,
    round: 14,
    date: "2024-07-28",
    pole: { driver: "VER", team: "Red Bull", time_s: 104.706 },
    fastest_lap: { driver: "PER", team: "Red Bull", time_s: 108.097, lap: 35 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "HAM", team: "Mercedes",     grid: 3, strategy: "Medium > Hard",       stops: 1, pit_laps: [10],   delta_to_winner_s: 0 },
      { pos: 2, driver: "PIA", team: "McLaren",      grid: 6, strategy: "Medium > Hard",       stops: 1, pit_laps: [11],   delta_to_winner_s: 0.6 },
      { pos: 3, driver: "LEC", team: "Ferrari",      grid: 4, strategy: "Medium > Hard",       stops: 1, pit_laps: [9],    delta_to_winner_s: 8.2 },
      { pos: 4, driver: "VER", team: "Red Bull",     grid: 11, strategy: "Medium > Hard",      stops: 1, pit_laps: [10],   delta_to_winner_s: 11.3 },
      { pos: 5, driver: "NOR", team: "McLaren",      grid: 4, strategy: "Medium > Hard",       stops: 1, pit_laps: [10],   delta_to_winner_s: 11.6 },
    ],
    narrative:
      "Russell crossed first but was disqualified for an underweight car, handing Hamilton the win. A 1-stop strategy with aggressive Hard-compound saving worked across the field.",
    optimal_strategy: "1-stop - Medium > Hard - early stop L9-L11 (undercut)",
    reference_window: [
      { lap: 14, leader: "HAM", gap_to_p2_s: 0.8, leader_compound: "H" },
      { lap: 15, leader: "HAM", gap_to_p2_s: 1.2, leader_compound: "H" },
      { lap: 16, leader: "HAM", gap_to_p2_s: 1.4, leader_compound: "H" },
      { lap: 17, leader: "HAM", gap_to_p2_s: 1.6, leader_compound: "H" },
      { lap: 18, leader: "HAM", gap_to_p2_s: 1.9, leader_compound: "H" },
      { lap: 19, leader: "HAM", gap_to_p2_s: 2.1, leader_compound: "H" },
    ],
  },
  {
    circuit_id: "silverstone",
    year: 2024,
    round: 12,
    date: "2024-07-07",
    pole: { driver: "RUS", team: "Mercedes", time_s: 85.819 },
    fastest_lap: { driver: "SAI", team: "Ferrari", time_s: 88.293, lap: 52 },
    weather: "mixed",
    podium: [
      { pos: 1, driver: "HAM", team: "Mercedes",     grid: 2, strategy: "Medium > Inters > Soft",  stops: 2, pit_laps: [17, 39],  delta_to_winner_s: 0 },
      { pos: 2, driver: "VER", team: "Red Bull",     grid: 4, strategy: "Medium > Inters > Soft",  stops: 2, pit_laps: [18, 38],  delta_to_winner_s: 1.5 },
      { pos: 3, driver: "NOR", team: "McLaren",      grid: 1, strategy: "Medium > Inters > Hard",  stops: 2, pit_laps: [17, 39],  delta_to_winner_s: 7.6 },
      { pos: 4, driver: "PIA", team: "McLaren",      grid: 3, strategy: "Medium > Inters > Soft",  stops: 2, pit_laps: [18, 38],  delta_to_winner_s: 12.0 },
      { pos: 5, driver: "SAI", team: "Ferrari",      grid: 7, strategy: "Medium > Inters > Soft",  stops: 2, pit_laps: [18, 41],  delta_to_winner_s: 17.8 },
    ],
    narrative:
      "A rain shower split the race in two. Mercedes called the switch to inters earlier than McLaren, costing Norris the lead. A late switch back to slicks brought Hamilton home for his record 9th Silverstone win.",
    optimal_strategy: "Reactive - Medium > Inters lap 17 > Soft lap 39",
    reference_window: [
      { lap: 14, leader: "NOR", gap_to_p2_s: 2.1, leader_compound: "M" },
      { lap: 15, leader: "NOR", gap_to_p2_s: 1.8, leader_compound: "M" },
      { lap: 16, leader: "NOR", gap_to_p2_s: 1.0, leader_compound: "M" },
      { lap: 17, leader: "HAM", gap_to_p2_s: 0.4, leader_compound: "I" },
      { lap: 18, leader: "HAM", gap_to_p2_s: 0.8, leader_compound: "I" },
      { lap: 19, leader: "HAM", gap_to_p2_s: 1.3, leader_compound: "I" },
    ],
  },
  {
    circuit_id: "suzuka",
    year: 2024,
    round: 4,
    date: "2024-04-07",
    pole: { driver: "VER", team: "Red Bull", time_s: 88.197 },
    fastest_lap: { driver: "VER", team: "Red Bull", time_s: 93.706, lap: 47 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "VER", team: "Red Bull",     grid: 1, strategy: "Medium > Hard > Hard", stops: 2, pit_laps: [13, 30],  delta_to_winner_s: 0 },
      { pos: 2, driver: "PER", team: "Red Bull",     grid: 2, strategy: "Medium > Hard > Hard", stops: 2, pit_laps: [13, 30],  delta_to_winner_s: 12.5 },
      { pos: 3, driver: "SAI", team: "Ferrari",      grid: 4, strategy: "Medium > Hard > Hard", stops: 2, pit_laps: [13, 31],  delta_to_winner_s: 20.9 },
      { pos: 4, driver: "LEC", team: "Ferrari",      grid: 8, strategy: "Hard > Medium",        stops: 1, pit_laps: [27],      delta_to_winner_s: 26.1 },
      { pos: 5, driver: "NOR", team: "McLaren",      grid: 6, strategy: "Medium > Hard > Hard", stops: 2, pit_laps: [13, 32],  delta_to_winner_s: 30.7 },
    ],
    narrative:
      "Verstappen dominated front to back. Leclerc proved a one-stop was viable from outside the top 5 by stretching the hard to lap 27, slower but compromised by his grid position.",
    optimal_strategy: "2-stop - Medium > Hard > Hard - stops L13 and L30",
    reference_window: [
      { lap: 14, leader: "VER", gap_to_p2_s: 3.4, leader_compound: "H" },
      { lap: 15, leader: "VER", gap_to_p2_s: 4.0, leader_compound: "H" },
      { lap: 16, leader: "VER", gap_to_p2_s: 4.6, leader_compound: "H" },
      { lap: 17, leader: "VER", gap_to_p2_s: 5.3, leader_compound: "H" },
      { lap: 18, leader: "VER", gap_to_p2_s: 6.1, leader_compound: "H" },
      { lap: 19, leader: "VER", gap_to_p2_s: 6.8, leader_compound: "H" },
    ],
  },
  {
    circuit_id: "cota",
    year: 2024,
    round: 19,
    date: "2024-10-20",
    pole: { driver: "NOR", team: "McLaren", time_s: 92.330 },
    fastest_lap: { driver: "NOR", team: "McLaren", time_s: 97.106, lap: 56 },
    weather: "dry",
    podium: [
      { pos: 1, driver: "LEC", team: "Ferrari",      grid: 4, strategy: "Medium > Hard",          stops: 1, pit_laps: [21], delta_to_winner_s: 0 },
      { pos: 2, driver: "SAI", team: "Ferrari",      grid: 3, strategy: "Medium > Hard",          stops: 1, pit_laps: [21], delta_to_winner_s: 8.1 },
      { pos: 3, driver: "VER", team: "Red Bull",     grid: 2, strategy: "Medium > Hard",          stops: 1, pit_laps: [20], delta_to_winner_s: 19.7 },
      { pos: 4, driver: "NOR", team: "McLaren",      grid: 1, strategy: "Medium > Hard",          stops: 1, pit_laps: [21], delta_to_winner_s: 24.4 },
      { pos: 5, driver: "RUS", team: "Mercedes",     grid: 6, strategy: "Medium > Hard",          stops: 1, pit_laps: [22], delta_to_winner_s: 30.8 },
    ],
    narrative:
      "Ferrari one-two. Leclerc cleared Verstappen at the lights and managed tyres through the long second stint. Norris dropped after a late time penalty for off-track pass on Verstappen.",
    optimal_strategy: "1-stop - Medium > Hard - stop L20-L22",
    reference_window: [
      { lap: 14, leader: "VER", gap_to_p2_s: 1.6, leader_compound: "M" },
      { lap: 15, leader: "VER", gap_to_p2_s: 1.8, leader_compound: "M" },
      { lap: 16, leader: "VER", gap_to_p2_s: 2.0, leader_compound: "M" },
      { lap: 17, leader: "LEC", gap_to_p2_s: 0.4, leader_compound: "M" },
      { lap: 18, leader: "LEC", gap_to_p2_s: 0.9, leader_compound: "M" },
      { lap: 19, leader: "LEC", gap_to_p2_s: 1.5, leader_compound: "M" },
    ],
  },
  {
    circuit_id: "interlagos",
    year: 2024,
    round: 21,
    date: "2024-11-03",
    pole: { driver: "NOR", team: "McLaren", time_s: 70.727 },
    fastest_lap: { driver: "ALO", team: "Aston Martin", time_s: 73.652, lap: 67 },
    weather: "wet",
    podium: [
      { pos: 1, driver: "VER", team: "Red Bull",     grid: 17, strategy: "Inters > Inters",       stops: 1, pit_laps: [29], delta_to_winner_s: 0 },
      { pos: 2, driver: "OCO", team: "Alpine",       grid: 5,  strategy: "Inters > Inters",       stops: 1, pit_laps: [28], delta_to_winner_s: 19.5 },
      { pos: 3, driver: "GAS", team: "Alpine",       grid: 7,  strategy: "Inters > Inters",       stops: 1, pit_laps: [29], delta_to_winner_s: 22.7 },
      { pos: 4, driver: "RUS", team: "Mercedes",     grid: 4,  strategy: "Inters > Inters",       stops: 1, pit_laps: [30], delta_to_winner_s: 30.0 },
      { pos: 5, driver: "LEC", team: "Ferrari",      grid: 2,  strategy: "Inters > Inters",       stops: 1, pit_laps: [29], delta_to_winner_s: 30.4 },
    ],
    narrative:
      "Verstappen drove from P17 to victory in monsoon conditions. One of the greatest wet-weather drives of the modern era. Alpine's 2-3 reset the constructors' battle.",
    optimal_strategy: "Inters only - pit for fresh inters at the SC window L28-L30",
    reference_window: [
      { lap: 14, leader: "NOR", gap_to_p2_s: 1.0, leader_compound: "I" },
      { lap: 15, leader: "NOR", gap_to_p2_s: 1.4, leader_compound: "I" },
      { lap: 16, leader: "NOR", gap_to_p2_s: 1.9, leader_compound: "I" },
      { lap: 17, leader: "NOR", gap_to_p2_s: 2.3, leader_compound: "I" },
      { lap: 18, leader: "NOR", gap_to_p2_s: 2.6, leader_compound: "I" },
      { lap: 19, leader: "NOR", gap_to_p2_s: 3.0, leader_compound: "I" },
    ],
  },
];

export function getRaceResult(circuit_id: string) {
  return RESULTS_2024.find((r) => r.circuit_id === circuit_id);
}
