import * as React from "react"
import * as TabsPrimitive from "@radix-ui/react-tabs"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const tabsListVariants = cva(
  "inline-flex h-9 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground",
  {
    variants: {
      variant: {
        default: "bg-muted",
        underline: "bg-transparent border-b border-border p-0 h-10",
        pills: "bg-secondary/30 gap-1 p-1",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const tabsTriggerVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px] focus-visible:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-xs hover:bg-background/60 hover:text-foreground",
        underline:
          "rounded-none border-b-2 border-transparent bg-transparent px-4 py-2 data-[state=active]:border-primary data-[state=active]:text-primary hover:text-primary/80",
        pills:
          "data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-xs hover:bg-accent hover:text-accent-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const Tabs = TabsPrimitive.Root

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List> &
    VariantProps<typeof tabsListVariants>
>(({ className, variant, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(tabsListVariants({ variant }), className)}
    {...props}
  />
))
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger> &
    VariantProps<typeof tabsTriggerVariants>
>(({ className, variant, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(tabsTriggerVariants({ variant }), className)}
    {...props}
  />
))
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      "mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      className
    )}
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent, tabsListVariants, tabsTriggerVariants }