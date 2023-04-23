# gui.py

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
from converter import UnitConverter

class UnitConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unit Converter")
        self.geometry("500x500")
        self.create_widgets()

        # Add theme selector
        style = ThemedStyle(self)
        self.available_themes = style.get_themes()
        self.theme_var = tk.StringVar()
        self.theme_var.trace("w", self.change_theme)
        theme_menu = ttk.OptionMenu(self, self.theme_var, self.available_themes[0], *self.available_themes)
        theme_menu.grid(column=0, row=6, padx=5, pady=5, sticky="ew", columnspan=2)

    # Method to change themes
    def change_theme(self, *args):
        selected_theme = self.theme_var.get()
        style = ThemedStyle(self)
        style.set_theme(selected_theme)

    def create_widgets(self):
        self.value_var = tk.DoubleVar()
        self.category_var = tk.StringVar()
        self.from_unit_var = tk.StringVar()
        self.to_unit_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self.category_var.trace("w", self.update_units)

        ttk.Label(self, text="Value:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.value_var).grid(column=1, row=0, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Category:").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        category_combobox = ttk.Combobox(self, textvariable=self.category_var, state="readonly")
        category_combobox["values"] = ["length", "weight", "temperature"]  # Add other categories here
        category_combobox.grid(column=1, row=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="From:").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.from_unit_combobox = ttk.Combobox(self, textvariable=self.from_unit_var, state="readonly")
        self.from_unit_combobox.grid(column=1, row=2, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="To:").grid(column=0, row=3, padx=5, pady=5, sticky="w")
        self.to_unit_combobox = ttk.Combobox(self, textvariable=self.to_unit_var, state="readonly")
        self.to_unit_combobox.grid(column=1, row=3, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Convert", command=self.convert).grid(column=0, row=4, padx=5, pady=5, sticky="ew", columnspan=2)

        ttk.Label(self, text="Result:").grid(column=0, row=5, padx=5, pady=5, sticky="w")
        ttk.Label(self, textvariable=self.result_var).grid(column=1, row=5, padx=5, pady=5, sticky="ew")

        # Trigger the initial units update
        self.update_units()

        # Make elements expand and resize with the window
        self.columnconfigure(1, weight=1)

    def update_units(self, *args):
        try:
            category = self.category_var.get()
            units = UnitConverter.get_units(category)
            self.from_unit_combobox["values"] = units
            self.to_unit_combobox["values"] = units
        except ValueError:
            pass

    def convert(self):
        try:
            value = self.value_var.get()
            from_unit = self.from_unit_var.get()
            to_unit = self.to_unit_var.get()
            result = UnitConverter.convert(value, from_unit, to_unit)
            self.result_var.set(result)
        except ValueError as e:
            self.result_var.set(str(e))

if __name__ == "__main__":
    app = UnitConverterApp()
    app.mainloop()

