"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { UserWITBItemCreate } from "@/types/schemas";
import { useBrands } from "@/hooks/useBrands";

interface AddEquipmentFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

const CATEGORIES = [
  "Driver",
  "3-Wood",
  "5-Wood",
  "7-Wood",
  "Hybrid",
  "Iron",
  "Wedge",
  "Putter",
  "Ball",
  "Grip",
];

export function AddEquipmentForm({
  onSuccess,
  onCancel,
}: AddEquipmentFormProps) {
  const { brands, isLoading: brandsLoading } = useBrands();
  const [formData, setFormData] = useState<UserWITBItemCreate>({
    category: "",
    brand: "",
    model: "",
    loft: "",
    shaft: "",
    carry_distance: undefined,
    notes: "",
    purchase_date: "",
    purchase_price: undefined,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Clean up form data
      const submitData = {
        ...formData,
        loft: formData.loft || undefined,
        shaft: formData.shaft || undefined,
        notes: formData.notes || undefined,
        purchase_date: formData.purchase_date || undefined,
        carry_distance: formData.carry_distance || undefined,
        purchase_price: formData.purchase_price || undefined,
      };

      await api.post("/user-bag", submitData);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add equipment");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof UserWITBItemCreate, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Category *
          </label>
          <select
            value={formData.category}
            onChange={(e) => handleInputChange("category", e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">Select category</option>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Brand */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Brand *
          </label>
          <input
            type="text"
            list="brand-suggestions"
            value={formData.brand}
            onChange={(e) => handleInputChange("brand", e.target.value)}
            required
            placeholder="e.g., TaylorMade, Callaway"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
            disabled={brandsLoading}
          />
          <datalist id="brand-suggestions">
            {brands.map((brand) => (
              <option key={brand} value={brand} />
            ))}
          </datalist>
        </div>

        {/* Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Model *
          </label>
          <input
            type="text"
            value={formData.model}
            onChange={(e) => handleInputChange("model", e.target.value)}
            required
            placeholder="e.g., Qi10, Stealth 2"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Loft */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Loft
          </label>
          <input
            type="text"
            value={formData.loft}
            onChange={(e) => handleInputChange("loft", e.target.value)}
            placeholder="e.g., 9°, 15°"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Shaft */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Shaft
          </label>
          <input
            type="text"
            value={formData.shaft}
            onChange={(e) => handleInputChange("shaft", e.target.value)}
            placeholder="e.g., Fujikura Ventus Blue"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Carry Distance */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Carry Distance (yards)
          </label>
          <input
            type="number"
            value={formData.carry_distance || ""}
            onChange={(e) =>
              handleInputChange(
                "carry_distance",
                e.target.value ? parseInt(e.target.value) : undefined,
              )
            }
            placeholder="250"
            min="0"
            max="400"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Notes
        </label>
        <textarea
          value={formData.notes}
          onChange={(e) => handleInputChange("notes", e.target.value)}
          placeholder="Any additional notes about this club..."
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
        />
      </div>

      {/* Purchase Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Purchase Date
          </label>
          <input
            type="date"
            value={formData.purchase_date}
            onChange={(e) => handleInputChange("purchase_date", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Purchase Price ($)
          </label>
          <input
            type="number"
            value={formData.purchase_price || ""}
            onChange={(e) =>
              handleInputChange(
                "purchase_price",
                e.target.value ? parseFloat(e.target.value) : undefined,
              )
            }
            placeholder="299.99"
            min="0"
            step="0.01"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-red-600 dark:text-red-400 text-sm">{error}</div>
      )}

      {/* Form Actions */}
      <div className="flex gap-3 pt-4">
        <Button
          type="submit"
          disabled={
            isSubmitting ||
            !formData.category ||
            !formData.brand ||
            !formData.model
          }
          className="flex-1"
        >
          {isSubmitting ? "Adding..." : "Add Equipment"}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
