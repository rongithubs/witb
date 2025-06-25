export type WITBItem = {
  category: string;
  brand: string;
  model: string;
  loft?: string;
  shaft?: string;
};

export type Player = {
  id: string;
  name: string;
  country: string;
  tour: string;
  witb_items: WITBItem[];
};
