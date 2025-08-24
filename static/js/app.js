"use strict";

(function attachUnitConverter() {
	const API_BASE = "/api/v1";
	const DEBOUNCE_MS = 300;

	function sleep(ms) {
		return new Promise((r) => setTimeout(r, ms));
	}

	async function fetchJSON(url, options = {}) {
		const res = await fetch(url, options);
		let payload = null;
		try {
			payload = await res.json();
		} catch (_) {
			// ignore JSON parse errors; will throw below
		}
		if (!res.ok) {
			const msg =
				(payload &&
					payload.error &&
					(payload.error.message || payload.error)) ||
				`HTTP ${res.status}`;
			const err = new Error(msg);
			err.status = res.status;
			err.payload = payload;
			throw err;
		}
		if (payload && payload.ok === false) {
			const msg =
				(payload.error &&
					(payload.error.message || payload.error.code)) ||
				"Request failed";
			const err = new Error(msg);
			err.status = res.status;
			err.payload = payload;
			throw err;
		}
		return payload;
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
			currencyFallbackActive: false,

			_debounceTimer: null,
			_convertCtrl: null,

			// Initialize
			async init() {
				this.loadPreferences();
				this.applyTheme();
				try {
					await this.fetchCategories();
				} catch (e) {
					this.showToast("Failed to load categories", "error");
				}
				this.setupKeyboardShortcuts();
			},

			// API Methods
			async fetchCategories() {
				const payload = await fetchJSON(`${API_BASE}/categories`, {
					method: "GET",
				});
				this.categories = Array.isArray(payload.result)
					? payload.result
					: payload.data || [];
			},

			async fetchUnits(category) {
				const payload = await fetchJSON(
					`${API_BASE}/units?category=${encodeURIComponent(
						category
					)}`,
					{ method: "GET" }
				);
				this.units = Array.isArray(payload.result)
					? payload.result
					: payload.data || [];
			},

			async performConversion() {
				if (!this.fromValue || !this.fromUnit || !this.toUnit) return;
				// Debounce
				if (this._debounceTimer) clearTimeout(this._debounceTimer);
				this._debounceTimer = setTimeout(
					() => this._doConvert(),
					DEBOUNCE_MS
				);
			},

			async _doConvert() {
				// Cancel in-flight
				if (this._convertCtrl) this._convertCtrl.abort();
				this._convertCtrl = new AbortController();

				this.loading = true;
				try {
					const payload = await fetchJSON(`${API_BASE}/convert`, {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({
							value: this.fromValue,
							from_unit: this.fromUnit,
							to_unit: this.toUnit,
						}),
						signal: this._convertCtrl.signal,
					});

					// payload uses envelope { ok, data, meta }
					this.result = (payload && payload.data) || payload;
					this._updateFallbackIndicator(payload && payload.meta);

					// Add to history
					this.addToHistory();

					// Quick conversions
					await this.fetchQuickConversions();

					// Visualization
					this.updateVisualization();
				} catch (e) {
					if (e.name === "AbortError") return;
					this.showToast(e.message || "Conversion failed", "error");
				} finally {
					this.loading = false;
				}
			},

			async fetchQuickConversions() {
				if (!this.fromValue || !this.fromUnit) return;
				try {
					const payload = await fetchJSON(
						`${API_BASE}/quick-conversions?value=${encodeURIComponent(
							this.fromValue
						)}&unit=${encodeURIComponent(this.fromUnit)}`,
						{ method: "GET" }
					);
					const list =
						(payload && (payload.data || payload.result)) ||
						payload ||
						[];
					this.quickConversions = Array.isArray(list) ? list : [];
					// Reset batch conversion when units change
					this.showBatchConvert = false;
					this.batchResults = [];
				} catch (e) {
					console.error("Failed to fetch quick conversions:", e);
				}
			},

			async performBatchConversion() {
				if (!this.fromValue || !this.fromUnit) return;
				this.loading = true;
				try {
					const allUnits = this.units
						.filter((u) => u.id !== this.fromUnit)
						.map((u) => u.id);
					const payload = await fetchJSON(
						`${API_BASE}/batch-convert`,
						{
							method: "POST",
							headers: { "Content-Type": "application/json" },
							body: JSON.stringify({
								value: this.fromValue,
								from_unit: this.fromUnit,
								to_units: allUnits,
							}),
						}
					);
					const data =
						payload.result || payload.data || payload || {};
					const conversions = data.conversions || data || [];
					this.batchResults = conversions.map((conv) => ({
						...conv,
						unit_name:
							this.units.find((u) => u.id === conv.to_unit)
								?.name || conv.to_unit,
					}));
				} catch (e) {
					this.showToast(
						e.message || "Batch conversion failed",
						"error"
					);
				} finally {
					this.loading = false;
				}
			},

			// UI Methods
			selectCategory(category) {
				this.selectedCategory = category;
				this.fetchUnits(category.id).catch(() => {
					this.showToast("Failed to load units", "error");
				});
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
				if (this.result && typeof this.result.result !== "undefined") {
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
				const text =
					this.result.formatted || String(this.result.result || "");
				navigator.clipboard
					.writeText(text)
					.then(() =>
						this.showToast("Result copied to clipboard", "success")
					)
					.catch(() =>
						this.showToast("Failed to copy result", "error")
					);
			},

			copyBatchResult(result) {
				const text = `${result.formatted} ${result.unit_name}`;
				navigator.clipboard
					.writeText(text)
					.then(() =>
						this.showToast("Copied to clipboard", "success")
					)
					.catch(() => this.showToast("Failed to copy", "error"));
			},

			downloadBatchResults() {
				if (!this.batchResults.length) return;
				const csv = [
					["From", "To", "Result"],
					...this.batchResults
						.filter((r) => r.success)
						.map((r) => [
							`${this.fromValue} ${this.fromUnit}`,
							r.unit_name,
							r.formatted,
						]),
				]
					.map((row) => row.join(","))
					.join("\n");
				const blob = new Blob([csv], { type: "text/csv" });
				const url = URL.createObjectURL(blob);
				const a = document.createElement("a");
				a.href = url;
				a.download = `conversion_${this.fromValue}_${
					this.fromUnit
				}_${new Date().toISOString()}.csv`;
				a.click();
				URL.revokeObjectURL(url);
				this.showToast("Results downloaded", "success");
			},

			// Share
			async shareConversion() {
				if (!this.result) return;
				const text = `${this.fromValue} ${this.result.from_unit} = ${this.result.formatted} ${this.result.to_unit}`;
				const shareData = {
					title: "Unit Conversion",
					text,
					url: window.location.href,
				};
				if (navigator.share) {
					try {
						await navigator.share(shareData);
						this.showToast("Shared successfully", "success");
					} catch (err) {
						if (err.name !== "AbortError") {
							this.copyShareText(text);
						}
					}
				} else {
					this.copyShareText(text);
				}
			},

			copyShareText(text) {
				navigator.clipboard
					.writeText(text)
					.then(() =>
						this.showToast(
							"Conversion copied to clipboard",
							"success"
						)
					)
					.catch(() => this.showToast("Failed to copy", "error"));
			},

			// History & Favorites
			addToHistory() {
				if (!this.result) return;
				const item = {
					id: Date.now(),
					category: this.selectedCategory?.name || "",
					fromValue: this.fromValue,
					fromUnit: this.fromUnit,
					toUnit: this.toUnit,
					result:
						this.result.formatted ||
						String(this.result.result || ""),
					timestamp: new Date().toISOString(),
					isFavorite: false,
				};
				this.history.unshift(item);
				if (this.history.length > 50) {
					this.history = this.history.slice(0, 50);
				}
				this.savePreferences();
			},

			restoreFromHistory(item) {
				const category = this.categories.find(
					(c) => c.name === item.category
				);
				if (category) {
					this.selectCategory(category);
					setTimeout(() => {
						this.fromValue = item.fromValue;
						this.fromUnit = item.fromUnit;
						this.toUnit = item.toUnit;
						this.performConversion();
					}, 100);
				}
				this.showHistory = false;
				this.showFavorites = false;
			},

			toggleFavorite(item) {
				item.isFavorite = !item.isFavorite;
				this.savePreferences();
			},

			get favorites() {
				return this.history.filter((item) => item.isFavorite);
			},

			clearHistory() {
				if (
					confirm(
						"Are you sure you want to clear all conversion history?"
					)
				) {
					this.history = [];
					this.savePreferences();
					this.showToast("History cleared", "success");
				}
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
				if (!this.result || this.selectedCategory?.id === "currency") {
					this.showVisualization = false;
					return;
				}
				this.showVisualization = true;
				this.$nextTick(() => {
					const ctx = document.getElementById("conversionChart");
					if (!ctx) return;
					if (this.chart) this.chart.destroy();
					this.chart = new Chart(ctx, {
						type: "bar",
						data: {
							labels: [
								this.result.from_unit,
								this.result.to_unit,
							],
							datasets: [
								{
									label: "Value",
									data: [
										parseFloat(this.fromValue),
										parseFloat(this.result.result),
									],
									backgroundColor: [
										"rgba(59,130,246,0.5)",
										"rgba(16,185,129,0.5)",
									],
									borderColor: [
										"rgba(59,130,246,1)",
										"rgba(16,185,129,1)",
									],
									borderWidth: 2,
								},
							],
						},
						options: {
							responsive: true,
							maintainAspectRatio: false,
							plugins: { legend: { display: false } },
							scales: {
								y: {
									beginAtZero: true,
									grid: {
										color: this.darkMode
											? "rgba(255,255,255,0.1)"
											: "rgba(0,0,0,0.1)",
									},
									ticks: {
										color: this.darkMode ? "#fff" : "#000",
									},
								},
								x: {
									grid: { display: false },
									ticks: {
										color: this.darkMode ? "#fff" : "#000",
									},
								},
							},
						},
					});
				});
				this.$watch("showBatchConvert", (value) => {
					if (value && this.batchResults.length === 0) {
						this.performBatchConversion();
					}
				});
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
				}, 3000);
			},

			setupKeyboardShortcuts() {
				document.addEventListener("keydown", (e) => {
					if ((e.ctrlKey || e.metaKey) && e.key === "s") {
						e.preventDefault();
						this.swapUnits();
					}
					if (
						(e.ctrlKey || e.metaKey) &&
						e.key === "c" &&
						this.result
					) {
						e.preventDefault();
						this.copyResult();
					}
					if ((e.ctrlKey || e.metaKey) && e.key === "h") {
						e.preventDefault();
						this.showHistory = !this.showHistory;
						this.showFavorites = false;
					}
					if ((e.ctrlKey || e.metaKey) && e.key === "d") {
						e.preventDefault();
						this.toggleTheme();
					}
					if ((e.ctrlKey || e.metaKey) && e.key === "b") {
						e.preventDefault();
						if (this.quickConversions.length > 0) {
							this.showBatchConvert = true;
							this.performBatchConversion();
						}
					}
					if (
						(e.ctrlKey || e.metaKey) &&
						e.shiftKey &&
						e.key === "s"
					) {
						e.preventDefault();
						this.shareConversion();
					}
				});
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

			// Internal
			_updateFallbackIndicator(meta) {
				const src =
					(meta && meta.currency && meta.currency.source) ||
					(meta && meta.rates_source);
				this.currencyFallbackActive = src === "fallback";
				if (this.currencyFallbackActive) {
					this.showToast("Using fallback currency rates", "error");
				}
			},
		};
	};
})();
