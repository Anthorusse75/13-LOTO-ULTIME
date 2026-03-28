export interface Draw {
  id: number;
  game_id: number;
  draw_date: string;
  draw_number: number | null;
  numbers: number[];
  stars: number[] | null;
}
