"use strict";

/*
Externalized Alpine.js data provider for the SPA.
Note: The current index.html still contains the original inline script.
This module is a scaffold and does not alter runtime unless index.html is updated to reference it.
*/

(function attachUnitConverter() {
	const API_BASE = "/api/v1";

	function notImplementedToast(ctx) {
		try {
			ctx.showToast(
				"Feature pending externalization (using inline script)",
				"success"
			);
		} catch (_) {
			// no-op
		}
	}

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
				this.loadPreferences();
				// Best-effort call to v1; if 404 (local dev Flask), this will be ignored
				try {
					await this.fetchCategories();
				} catch (_) {}
				this.applyTheme();
			},

			// API Methods (minimal)
			async fetchCategories() {
				const res = await fetch(`${API_BASE}/categories`);
				const payload = await res.json();
				this.categories = payload?.ok ? payload.data : payload;
			},

			async fetchUnits(category) {
				const res = await fetch(
					`${API_BASE}/units?category=${encodeURIComponent(category)}`
				);
				const payload = await res.json();
				this.units = payload?.ok ? payload.data : payload;
			},

			async performConversion() {
				// Delegate to inline implementation; this is a placeholder
				notImplementedToast(this);
			},

			async fetchQuickConversions() {
				// Delegate to inline implementation; this is a placeholder
				notImplementedToast(this);
			},

			// UI Methods (stubs)
			selectCategory(category) {
				this.selectedCategory = category;
				this.fetchUnits(category.id).catch(() => {});
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
				// Leave to inline handler for now
			},

			// Utilities
			showToast(message, type = "success") {
				const toast = { id: Date.now(), message, type, visible: true };
				this.toasts.push(toast);
				setTimeout(() => {
					toast.visible = false;
					setTimeout(() => {
						this.toasts = this.toasts.filter(
							(t) => t.id !== toast.id
						);
					}, 300);
				}, 1500);
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

			// Persistence
			savePreferences() {
				const preferences = {
					darkMode: this.darkMode,
					history: this.history,
				};
				try {
					localStorage.setItem(
						"unitConverterPreferences",
						JSON.stringify(preferences)
					);
				} catch (_) {}
			},

			loadPreferences() {
				try {
					const saved = localStorage.getItem(
						"unitConverterPreferences"
					);
					if (saved) {
						const preferences = JSON.parse(saved);
						this.darkMode = !!preferences.darkMode;
						this.history = Array.isArray(preferences.history)
							? preferences.history
							: [];
					}
				} catch (_) {}
			},
		};
	};
})();
