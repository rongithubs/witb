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
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Filter by Category
        </label>
        <Select value={selectedCategory} onValueChange={onCategoryChange}>
          <SelectTrigger className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
            <SelectValue placeholder="Select category">
              {getDisplayValue(selectedCategory)}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
            <SelectItem value="all" className="hover:bg-gray-50 dark:hover:bg-gray-700">
              All Categories
            </SelectItem>
            {availableCategories.map(category => (
              <SelectItem 
                key={category} 
                value={category}
                className="hover:bg-gray-50 dark:hover:bg-gray-700"
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