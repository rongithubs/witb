import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import styles from "@/components/ui/glassmorphism.module.css";

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
  // Use flexbox for even distribution of tabs
  const tabsListClassName = `${styles.glassTabsList} flex w-full mb-6`;
  
  return (
    <Tabs value={selectedCategory} onValueChange={onCategoryChange} className="w-full">
      <TabsList className={tabsListClassName}>
        <TabsTrigger value="all" className={styles.glassTab}>
          All
        </TabsTrigger>
        {availableCategories.map(category => (
          <TabsTrigger key={category} value={category} className={styles.glassTab}>
            {category}
          </TabsTrigger>
        ))}
      </TabsList>

      <TabsContent value={selectedCategory} className="mt-0">
        {children}
      </TabsContent>
    </Tabs>
  );
}