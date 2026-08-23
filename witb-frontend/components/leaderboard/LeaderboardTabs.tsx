import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface LeaderboardTabsProps {
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  availableCategories: string[];
  children: React.ReactNode;
}

export function LeaderboardTabs({
  selectedCategory,
  onCategoryChange,
  availableCategories,
  children
}: LeaderboardTabsProps) {
  const getDisplayValue = (value: string) => {
    return value === "all" ? "All Categories" : value;
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <label className="block text-sm font-medium text-ink-secondary mb-2">
          Filter by Category
        </label>
        <Select value={selectedCategory} onValueChange={onCategoryChange}>
          <SelectTrigger className="w-full bg-surface border border-hairline">
            <SelectValue placeholder="Select category">
              {getDisplayValue(selectedCategory)}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="bg-surface border border-hairline">
            <SelectItem value="all" className="hover:bg-surface-hover">
              All Categories
            </SelectItem>
            {availableCategories.map(category => (
              <SelectItem 
                key={category} 
                value={category}
                className="hover:bg-surface-hover"
              >
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        {children}
      </div>
    </div>
  );
}