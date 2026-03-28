export interface GameDefinition {
  id: number;
  name: string;
  slug: string;
  numbers_pool: number;
  numbers_drawn: number;
  min_number: number;
  max_number: number;
  stars_pool: number | null;
  stars_drawn: number | null;
  star_name: string | null;
  draw_frequency: string;
  is_active: boolean;
}
