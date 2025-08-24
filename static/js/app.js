"use strict";

// Externalized from index.html inline script. Exposes unitConverter() globally for Alpine.js.
(function attachUnitConverter() {
  const API_BASE = "/api/v1";

  window.unitConverter = function unitConverter() {
    return {
      // State
      categories: [],
      selectedCategory: null,
      units: [],
      fromValue: "",
      fromUnit: "",
      toUnit: "",
      result: null,
      loading: false,
      history: [],
      showHistory: false,
      showFavorites: false,
      darkMode: false,
      toasts: [],
      quickConversions: [],
      showVisualization: false,
      chart: null,
      showBatchConvert: false,
      batchResults: [],

      // Initialize
      async init() {
        // Load saved preferences
        this.loadPreferences();

        // Fetch categories
        await this.fetchCategories();

        // Set up keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Initialize theme
        this.applyTheme();
      },

      // API Methods
      async fetchCategories() {
        try {
          const response = await fetch(`${API_BASE}/categories`);
          this.categories = await response.json().then(r => (r.ok ? r.data : r));
        } catch (error) {
          this.showToast("Failed to load categories", "error");
        }
      },

      async fetchUnits(category) {
        try {
          const response = await fetch(`${API_BASE}/units?category=${encodeURIComponent(category)}`);
          this.units = await response.json().then(r => (r.ok ? r.data : r));
        } catch (error) {
          this.showToast("Failed to load units", "error");
        }
      },

      async performConversion() {
        if (!this.fromValue || !this.fromUnit || !this.toUnit) return;

        this.loading = true;
        try {
          const formData = new FormData();
          formData.append("value", this.fromValue);
          formData.append("from_unit", this.fromUnit);
          formData.append("to_unit", this.toUnit);

          const response = await fetch(`${API_BASE}/convert`, {
            method: "POST",
            body: formData,
          });

          const payload = await response.json();
          if (!response.ok || payload.ok === false) {
            const message = payload?.error?.message || payload?.error || "Conversion failed";
            throw new Error(message);
          }

          // v1 envelope
          this.result = payload.ok === true ? payload.data : payload;

          // Add to history
          this.addToHistory();

          // Get quick conversions
          await this.fetchQuickConversions();

          // Update visualization
          this.updateVisualization();
        } catch (error) {
          this.showToast(error.message, "error");
        } finally {
          this.loading = false;
        }
      },

      async fetchQuickConversions() {
        if (!this.fromValue || !this.fromUnit) return;

        try {
          const response = await fetch(
            `${API_BASE}/quick-conversions?value=${encodeURIComponent(this.fromValue)}&unit=${encodeURIComponent(this.fromUnit)}`
          );
          const payload = await response.json();
          // v1 envelope
          this.quickConversions = payload?.ok === true ? payload.data : payload;

          // Reset batch conversion when units change
          this.showBatchConvert = false;
          this.batchResults = [];
        } catch (error) {
          console.error("Failed to fetch quick conversions:", error);
        }
      },

      // UI Methods
      selectCategory(category) {
        this.selectedCategory = category;
        this.fetchUnits(category.id);
        this.fromUnit = "";
        this.toUnit = "";
        this.result = null;
        this.quickConversions = [];
        this.showBatchConvert = false;
        this.batchResults = [];
      },

      swapUnits() {
        if (!this.fromUnit || !this.toUnit) return;

        [this.fromUnit, this.toUnit] = [this.toUnit, this.fromUnit];
        if (this.result) {
          this.fromValue = this.result.result;
        }
        this.performConversion();
      },

      selectQuickConversion(qc) {
        this.toUnit = qc.unit;
        this.performConversion();
      },

      copyResult() {
        if (!this.result) return;

        navigator.clipboard
          .writeText(this.result.formatted)
          .then(() => {
            this.showToast("Result copied to clipboard", "success");
          })
          .catch(() => {
            this.showToast("Failed to copy result", "error");
          });
      },

      // Batch Conversion
      async performBatchConversion() {
        if (!this.fromValue || !this.fromUnit) return;

        this.loading = true;
        try {
          // Get all units in the same category
          const allUnits = this.units.filter((u) => u.id !== this.fromUnit).map((u) => u.id);

          const response = await fetch(`${API_BASE}/batch-convert`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              value: this.fromValue,
              from_unit: this.fromUnit,
              to_units: allUnits,
            }),
          });

          const payload = await response.json();
          if (!response.ok || payload.ok === false) {
            const message = payload?.error?.message || payload?.error || "Batch conversion failed";
            throw new Error(message);
          }

          const data = payload.ok === true ? payload.data : payload;
          const conversions = data.conversions || data; // support both shapes
          this.batchResults = conversions.map((conv) => ({
            ...conv,
            unit_name: this.units.find((u) => u.id === conv.to_unit)?.name || conv.to_unit,
          }));
        } catch (error) {
          this.showToast(error.message, "error");
        } finally {
          this.loading = false;
        }
      },

      copyBatchResult(result) {
        const text = `${result.formatted} ${result.unit_name}`;
        navigator.clipboard
          .writeText(text)
          .then(() => {
            this.showToast("Copied to clipboard", "success");
          })
          .catch(() => {
            this.showToast("Failed to copy", "error");
          });
      },

      downloadBatchResults() {
        if (!this.batchResults.length) return;

        const csv = [
          ["From", "To", "Result"],
          ...this.batchResults.filter((r) => r.success).map((r) => [`${this.fromValue} ${this.fromUnit}`, r.unit_name, r.formatted]),
        ]
          .map((row) => row.join(","))
          .join("\n");

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `conversion_${this.fromValue}_${this.fromUnit}_${new Date().toISOString()}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast("Results downloaded", "success");
      },

      // Share functionality
      async shareConversion() {
        if (!this.result) return;

        const shareData = {
          title: "Unit Conversion",
          text: `${this.fromValue} ${this.result.from_unit} = ${this.result.formatted} ${this.result.to_unit}`,
          url: window.location.href,
        };

        if (navigator.share) {
          try {
            await navigator.share(shareData);
            this.showToast("Shared successfully", "success");
          } catch (err) {
            if (err.name !== "AbortError") {
              this.copyShareText(shareData.text);
            }
          }
        } else {
          this.copyShareText(shareData.text);
        }
      },

      copyShareText(text) {
        navigator.clipboard
          .writeText(text)
          .then(() => {
            this.showToast("Conversion copied to clipboard", "success");
          })
          .catch(() => {
            this.showToast("Failed to copy", "error");
          });
      },

      // History & Favorites
      addToHistory() {
        const item = {
          id: Date.now(),
          category: this.selectedCategory.name,
          fromValue: this.fromValue,
          fromUnit: this.fromUnit,
          toUnit: this.toUnit,
          result: this.result.formatted,
          timestamp: new Date().toISOString(),
          isFavorite: false,
        };

        this.history.unshift(item);
        if (this.history.length > 50) {
          this.history = this.history.slice(0, 50);
        }

        this.savePreferences();
      },

      get favorites() {
        return this.history.filter((item) => item.isFavorite);
      },

      clearHistory() {
        if (confirm("Are you sure you want to clear all conversion history?")) {
          this.history = [];
          this.savePreferences();
          this.showToast("History cleared", "success");
        }
      },

      toggleFavorite(item) {
        item.isFavorite = !item.isFavorite;
        this.savePreferences();
      },

      // Theme
      toggleTheme() {
        this.darkMode = !this.darkMode;
        this.applyTheme();
        this.savePreferences();
      },

      applyTheme() {
        if (this.darkMode) {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      },

      // Visualization
      updateVisualization() {
        if (!this.result || this.selectedCategory.id === "currency") {
          this.showVisualization = false;
          return;
        }

        this.showVisualization = true;

        // Wait for DOM update
        this.$nextTick(() => {
          const ctx