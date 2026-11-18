import csv
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import deque

from comunicacion import ComunicacionSerial


# ============================================================
# PALETA Y CONFIGURACION
# ============================================================

BG = "#06111d"
PANEL = "#0b1a2a"
PANEL_2 = "#0e2236"
PANEL_3 = "#102a42"
BORDER = "#183b55"
TEXT = "#e8f2ff"
MUTED = "#91a9c2"
BLUE = "#13b9ff"
CYAN = "#16d9e8"
GREEN = "#19e58b"
RED = "#ff4568"
YELLOW = "#ffbd35"
PURPLE = "#b86bff"
FONT = "Segoe UI"


class AirMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Calidad del Aire | ESP32")
        self.root.geometry("1540x960")
        self.root.minsize(1180, 760)
        self.root.configure(bg=BG)

        self.serial = ComunicacionSerial()
        self.connected = False
        self.running = True
        self.mode = "AUTO"
        self.threshold = 1200
        self.gases = 0
        self.temperature = 0.0
        self.humidity = 0.0
        self.buzzer = 0
        self.led_green = 0
        self.led_red = 0
        self.fan = 0
        self.general_state = "ESPERANDO"
        self.last_update = "--:--:--"
        self.port = tk.StringVar()
        self.threshold_var = tk.IntVar(value=self.threshold)
        self.history = deque(maxlen=120)
        self.events = deque(maxlen=100)
        self.active_section = "Inicio"
        self.bottom_tab = "Gráficas en tiempo real"

        self._configure_style()
        self._build_shell()
        self._build_home()
        self._show_section("Inicio")
        self._animate()
        self._poll_serial()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # --------------------------------------------------------
    # ESTILO Y ESTRUCTURA GENERAL
    # --------------------------------------------------------

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=PANEL_2,
            background=PANEL_2,
            foreground=TEXT,
            arrowcolor=CYAN,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", PANEL_2)],
            foreground=[("readonly", TEXT)]
        )

    def _panel(self, parent, bg=PANEL, border=BORDER, radius=16):
        frame = tk.Frame(
            parent, bg=bg, highlightbackground=border,
            highlightthickness=1, bd=0
        )
        return frame

    def _label(self, parent, text, size=10, color=TEXT, weight="normal", **kwargs):
        return tk.Label(
            parent, text=text, bg=kwargs.pop("bg", parent.cget("bg")),
            fg=color, font=(FONT, size, weight), **kwargs
        )

    def _build_shell(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Barra superior
        self.topbar = tk.Frame(self.root, bg="#081725", height=82,
                               highlightbackground=BORDER, highlightthickness=1)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(1, weight=1)

        logo = tk.Canvas(self.topbar, width=62, height=62, bg="#081725", highlightthickness=0)
        logo.grid(row=0, column=0, padx=(18, 10), pady=9)
        logo.create_oval(5, 5, 57, 57, fill="#063c39", outline=GREEN, width=2)
        logo.create_oval(17, 15, 45, 47, fill=GREEN, outline="")
        logo.create_polygon(23, 39, 29, 22, 43, 17, 37, 34, fill="#063c39", outline="")

        title_box = tk.Frame(self.topbar, bg="#081725")
        title_box.grid(row=0, column=1, sticky="w")
        self._label(title_box, "Monitor de Calidad del Aire", 19, TEXT, "bold").pack(anchor="w")
        self._label(title_box, "ESP32  •  Sistema de monitoreo en tiempo real", 9, MUTED).pack(anchor="w")

        self.connection_badge = tk.Label(
            self.topbar, text="●  Desconectado", bg="#102b35", fg=YELLOW,
            font=(FONT, 9, "bold"), padx=12, pady=8
        )
        self.connection_badge.grid(row=0, column=2, padx=(8, 10), pady=18)

        self.port_combo = ttk.Combobox(
            self.topbar, textvariable=self.port, values=self._available_ports(),
            width=12, state="normal", style="Dark.TCombobox", font=(FONT, 10)
        )
        self.port_combo.grid(row=0, column=3, padx=6, pady=18, ipady=5)
        self.connect_button = tk.Button(
            self.topbar, text="Conectar", command=self._toggle_connection,
            bg="#075d91", fg="white", activebackground="#087dbb",
            activeforeground="white", relief="flat", font=(FONT, 9, "bold"),
            padx=16, pady=9, cursor="hand2"
        )
        self.connect_button.grid(row=0, column=4, padx=(4, 18), pady=18)

        # Navegación lateral
        self.sidebar = tk.Frame(self.root, bg="#081725", width=170,
                                highlightbackground=BORDER, highlightthickness=1)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self._label(self.sidebar, "NAVEGACIÓN", 8, "#64839f", "bold").pack(
            anchor="w", padx=20, pady=(24, 14)
        )
        self.nav_buttons = {}
        for name, symbol in [
            ("Inicio", "⌂"), ("Gráficas", "⌁"), ("Historial", "▤"),
            ("Configuración", "⚙"), ("Acerca de", "ⓘ")
        ]:
            btn = tk.Button(
                self.sidebar, text=f"  {symbol}    {name}", anchor="w",
                command=lambda n=name: self._show_section(n),
                bg="#081725", fg="#b7c9dc", activebackground="#103453",
                activeforeground=TEXT, relief="flat", bd=0,
                font=(FONT, 10, "bold"), padx=13, pady=16, cursor="hand2"
            )
            btn.pack(fill="x", padx=9, pady=3)
            self.nav_buttons[name] = btn

        self._label(self.sidebar, "SISTEMA", 8, "#64839f", "bold").pack(
            anchor="w", padx=20, pady=(30, 8)
        )
        self.sidebar_status = self._label(
            self.sidebar, "●  ESP32 listo\n\n●  Sensores activos",
            8, MUTED, justify="left"
        )
        self.sidebar_status.pack(anchor="w", padx=20)

        # Área de contenido
        self.content = tk.Frame(self.root, bg=BG)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _available_ports(self):
        try:
            from serial.tools import list_ports
            return [p.device for p in list_ports.comports()]
        except Exception:
            return []

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _show_section(self, section):
        self.active_section = section
        for name, button in self.nav_buttons.items():
            if name == section:
                button.configure(bg="#0b4770", fg="#ffffff")
            else:
                button.configure(bg="#081725", fg="#b7c9dc")
        self._clear_content()
        if section == "Inicio":
            self._build_home()
        elif section == "Gráficas":
            self._build_graphs_page()
        elif section == "Historial":
            self._build_history_page()
        elif section == "Configuración":
            self._build_settings_page()
        else:
            self._build_about_page()

    # --------------------------------------------------------
    # INICIO: DASHBOARD
    # --------------------------------------------------------

    def _build_home(self):
        page = tk.Frame(self.content, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=17, pady=15)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        page.grid_rowconfigure(3, weight=1)

        heading = tk.Frame(page, bg=BG)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._label(heading, "Panel principal", 17, TEXT, "bold").pack(side="left")
        self._label(heading, "MONITOREO ACTIVO  •  ESP32 DEVKIT", 8, CYAN, "bold").pack(
            side="right", pady=6
        )

        # Cuatro tarjetas superiores
        cards = tk.Frame(page, bg=BG)
        cards.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1, uniform="sensor")
        self.sensor_cards = {}
        self.sensor_cards["gases"] = self._sensor_card(
            cards, 0, "GASES  ·  MQ-135", "0", "ADC", CYAN, "◉"
        )
        self.sensor_cards["temp"] = self._sensor_card(
            cards, 1, "TEMPERATURA  ·  DHT11", "0.0", "°C", BLUE, "♨"
        )
        self.sensor_cards["hum"] = self._sensor_card(
            cards, 2, "HUMEDAD  ·  DHT11", "0.0", "%", PURPLE, "◌"
        )
        self.state_card = self._sensor_card(
            cards, 3, "ESTADO GENERAL", "ESPERANDO", "", GREEN, "✓"
        )

        # Zona central
        center = tk.Frame(page, bg=BG)
        center.grid(row=2, column=0, sticky="nsew", pady=(0, 13))
        center.grid_columnconfigure(0, weight=4)
        center.grid_columnconfigure(1, weight=5)
        center.grid_columnconfigure(2, weight=3)
        center.grid_rowconfigure(0, weight=1)

        self.gauge_panel = self._panel(center, "#081827")
        self.gauge_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._label(self.gauge_panel, "CALIDAD DEL AIRE", 10, MUTED, "bold").pack(
            anchor="w", padx=18, pady=(15, 0)
        )
        self.gauge = tk.Canvas(
            self.gauge_panel, bg="#081827", height=210,
            highlightthickness=0
        )
        self.gauge.pack(fill="both", expand=True, padx=8, pady=2)
        self._draw_gauge()

        self.control_panel = self._panel(center, "#081827")
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=8)
        self._build_controls(self.control_panel)

        self.device_panel = self._panel(center, "#081827")
        self.device_panel.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self._build_device_visual(self.device_panel)

        # Pestañas inferiores
        bottom = self._panel(page, "#081827")
        bottom.grid(row=3, column=0, sticky="nsew")
        bottom.grid_rowconfigure(1, weight=1)
        bottom.grid_columnconfigure(0, weight=1)
        tabbar = tk.Frame(bottom, bg="#081827")
        tabbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        self.bottom_tabs = {}
        for tab in ("Gráficas en tiempo real", "Historial de datos", "Estadísticas"):
            b = tk.Button(
                tabbar, text=tab, command=lambda t=tab: self._select_bottom_tab(t),
                bg="#0d2940" if tab == self.bottom_tab else "#081827",
                fg=CYAN if tab == self.bottom_tab else MUTED,
                activebackground="#0d2940", activeforeground=TEXT,
                relief="flat", font=(FONT, 9, "bold"), padx=13, pady=8,
                cursor="hand2"
            )
            b.pack(side="left", padx=(0, 5))
            self.bottom_tabs[tab] = b
        self.chart_canvases = {}
        self.bottom_area = tk.Frame(bottom, bg="#081827")
        self.bottom_area.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        self._render_bottom_tab()

        # Pie de estado
        footer = tk.Frame(page, bg=BG)
        footer.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.footer_time = self._label(footer, "◷  Última actualización: --:--:--", 8, MUTED)
        self.footer_time.pack(side="left")
        self.footer_records = self._label(footer, "▤  Registros: 0", 8, MUTED)
        self.footer_records.pack(side="right")

    def _sensor_card(self, parent, column, title, value, unit, accent, symbol):
        card = self._panel(parent, "#0b1b2b")
        card.grid(row=0, column=column, sticky="nsew", padx=5)
        card.configure(height=112)
        card.grid_propagate(False)
        top = tk.Frame(card, bg="#0b1b2b")
        top.pack(fill="x", padx=13, pady=(12, 3))
        tk.Label(top, text=symbol, bg="#102d45", fg=accent,
                 font=(FONT, 18, "bold"), width=2, height=1).pack(side="left", padx=(0, 9))
        self._label(top, title, 8, MUTED, "bold").pack(side="left", anchor="center")
        value_label = self._label(card, value, 20, TEXT, "bold")
        value_label.pack(anchor="w", padx=15, pady=(2, 0))
        unit_label = self._label(card, unit, 8, accent)
        unit_label.pack(anchor="w", padx=17)
        bar = tk.Canvas(card, height=5, bg="#172b3e", highlightthickness=0)
        bar.pack(fill="x", padx=14, pady=(7, 0))
        bar.create_rectangle(0, 0, 120, 5, fill=accent, outline="")
        return {"card": card, "value": value_label, "unit": unit_label, "accent": accent}

    def _build_controls(self, parent):
        self._label(parent, "✦  Modo de operación", 11, TEXT, "bold").pack(
            anchor="w", padx=16, pady=(14, 10)
        )
        modes = tk.Frame(parent, bg="#081827")
        modes.pack(fill="x", padx=14)
        self.auto_btn = tk.Button(
            modes, text="▶  Automático", command=lambda: self._set_mode("AUTO"),
            bg="#087c62", fg="white", activebackground="#0a9b75",
            relief="flat", font=(FONT, 9, "bold"), pady=10, cursor="hand2"
        )
        self.auto_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.manual_btn = tk.Button(
            modes, text="✋  Manual", command=lambda: self._set_mode("MANUAL"),
            bg="#122e48", fg=TEXT, activebackground="#1a4567",
            relief="flat", font=(FONT, 9, "bold"), pady=10, cursor="hand2"
        )
        self.manual_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self._label(parent, "Umbral de gases", 9, TEXT, "bold").pack(
            anchor="w", padx=16, pady=(13, 4)
        )
        threshold_row = tk.Frame(parent, bg="#081827")
        threshold_row.pack(fill="x", padx=16)
        self.threshold_scale = tk.Scale(
            threshold_row, from_=100, to=3000, orient="horizontal",
            variable=self.threshold_var, command=self._threshold_changed,
            bg="#081827", fg=CYAN, troughcolor="#1b344a",
            activebackground=GREEN, highlightthickness=0, bd=0,
            showvalue=False, length=220
        )
        self.threshold_scale.pack(side="left", fill="x", expand=True)
        self.threshold_value = self._label(threshold_row, str(self.threshold), 10, TEXT, "bold")
        self.threshold_value.pack(side="right", padx=(8, 0))

        self._label(parent, "♟  Actuadores", 9, MUTED, "bold").pack(
            anchor="w", padx=16, pady=(11, 6)
        )
        actuators = tk.Frame(parent, bg="#081827")
        actuators.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for i, (key, name, symbol, color) in enumerate([
            ("buzzer", "Buzzer", "◖", BLUE),
            ("fan", "Ventilador", "✿", CYAN),
            ("green", "LED verde", "●", GREEN),
            ("red", "LED rojo", "●", RED)
        ]):
            actuators.grid_columnconfigure(i, weight=1, uniform="act")
            box = self._panel(actuators, "#0b1c2d")
            box.grid(row=0, column=i, sticky="nsew", padx=3)
            self._label(box, symbol, 20, color, "bold").pack(pady=(7, 0))
            self._label(box, name, 8, MUTED, "bold").pack(pady=(2, 4))
            state = self._label(box, "OFF", 8, MUTED, "bold")
            state.pack(pady=(0, 7))
            self.actuator_labels = getattr(self, "actuator_labels", {})
            self.actuator_labels[key] = state
            if key in ("buzzer", "fan"):
                btn = tk.Button(
                    box, text="Cambiar", command=lambda k=key: self._toggle_actuator(k),
                    bg="#12324b", fg=TEXT, activebackground="#1b5278",
                    relief="flat", font=(FONT, 7), padx=5, pady=3,
                    cursor="hand2"
                )
                btn.pack(pady=(0, 7))

    def _build_device_visual(self, parent):
        self._label(parent, "UNIDAD DE MONITOREO", 9, MUTED, "bold").pack(
            anchor="w", padx=13, pady=(14, 0)
        )
        self.device_canvas = tk.Canvas(
            parent, bg="#081827", highlightthickness=0, height=260
        )
        self.device_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self._draw_device()

    def _draw_device(self):
        c = self.device_canvas
        c.delete("all")
        w = max(c.winfo_width(), 220)
        h = max(c.winfo_height(), 250)
        cx = w / 2
        c.create_oval(cx-75, h-57, cx+75, h-28, fill="#092c45", outline=CYAN, width=2)
        c.create_rectangle(cx-52, 75, cx+52, h-48, fill="#102d43", outline="#4a7794", width=2)
        c.create_rectangle(cx-43, 88, cx+43, h-58, fill="#0a1d2e", outline="#254a65")
        c.create_oval(cx-52, 58, cx+52, 91, fill="#244c66", outline="#8ab6d0", width=2)
        c.create_oval(cx-39, 65, cx+39, 85, fill="#112c43", outline=CYAN, width=2)
        c.create_rectangle(cx-35, 28, cx+35, 68, fill="#34566c", outline="#9bb5c7", width=2)
        c.create_oval(cx-35, 19, cx+35, 39, fill="#54758a", outline="#b7d0df", width=2)
        for y in range(112, int(h-80), 15):
            c.create_line(cx-34, y, cx+34, y, fill="#3c6d8a", width=2)
        c.create_oval(cx-17, h-78, cx+17, h-44, fill="#0b4965", outline=CYAN, width=2)
        c.create_text(cx, h-61, text="ESP32", fill=TEXT, font=(FONT, 8, "bold"))
        c.create_text(cx, h-12, text="SISTEMA ACTIVO", fill=GREEN, font=(FONT, 8, "bold"))

    def _draw_gauge(self):
        c = self.gauge
        c.delete("all")
        c.update_idletasks()
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 190)
        cx, cy = w / 2, h * .62
        r = min(w * .34, h * .48)
        # arco segmentado
        for i in range(45):
            start = 145 + i * (250 / 45)
            color = GREEN if i < 17 else (YELLOW if i < 31 else RED)
            c.create_arc(cx-r, cy-r, cx+r, cy+r, start=start, extent=4.2,
                         style="arc", outline=color, width=9)
        ratio = min(max(self.gases / max(self.threshold, 1), 0), 1)
        angle = math.radians(145 + ratio * 250)
        x2 = cx + (r-15) * math.cos(angle)
        y2 = cy - (r-15) * math.sin(angle)
        c.create_line(cx, cy, x2, y2, fill=TEXT, width=3, arrow=tk.LAST)
        c.create_oval(cx-8, cy-8, cx+8, cy+8, fill=CYAN, outline="")
        label = "BUENA" if self.general_state != "ALERTA" else "ALERTA"
        color = GREEN if label == "BUENA" else RED
        c.create_text(cx, cy+22, text="Calidad del aire", fill=TEXT, font=(FONT, 10, "bold"))
        c.create_text(cx, cy+49, text=label, fill=color, font=(FONT, 21, "bold"))
        c.create_text(cx, h-10, text=f"Lectura MQ-135: {self.gases}  |  Umbral: {self.threshold}",
                      fill=MUTED, font=(FONT, 8))

    # --------------------------------------------------------
    # PESTAÑAS INFERIORES Y GRAFICAS
    # --------------------------------------------------------

    def _select_bottom_tab(self, tab):
        self.bottom_tab = tab
        for name, button in self.bottom_tabs.items():
            button.configure(
                bg="#0d2940" if name == tab else "#081827",
                fg=CYAN if name == tab else MUTED
            )
        self._render_bottom_tab()

    def _render_bottom_tab(self):
        for child in self.bottom_area.winfo_children():
            child.destroy()
        if self.bottom_tab == "Gráficas en tiempo real":
            for i, (key, title, color, unit) in enumerate([
                ("gases", "Gases (MQ-135)", YELLOW, "ADC"),
                ("temp", "Temperatura (DHT11)", BLUE, "°C"),
                ("hum", "Humedad (DHT11)", PURPLE, "%")
            ]):
                self.bottom_area.grid_columnconfigure(i, weight=1)
                panel = self._panel(self.bottom_area, "#0a1928")
                panel.grid(row=0, column=i, sticky="nsew", padx=4)
                self._label(panel, f"●  {title}", 8, color, "bold").pack(
                    anchor="w", padx=10, pady=(8, 0)
                )
                canvas = tk.Canvas(panel, height=120, bg="#0a1928", highlightthickness=0)
                canvas.pack(fill="both", expand=True, padx=5, pady=5)
                self.chart_canvases[key] = canvas
                self._draw_chart(canvas, key, color, unit)
        elif self.bottom_tab == "Historial de datos":
            self._build_compact_history(self.bottom_area)
        else:
            self._build_stats(self.bottom_area)

    def _draw_chart(self, canvas, key, color, unit):
        canvas.delete("all")
        canvas.update_idletasks()
        w = max(canvas.winfo_width(), 180)
        h = max(canvas.winfo_height(), 110)
        left, right, top, bottom = 28, w-8, 12, h-22
        for i in range(4):
            y = top + i * (bottom-top) / 3
            canvas.create_line(left, y, right, y, fill="#183047")
        values = [row[key] for row in self.history]
        if len(values) < 2:
            canvas.create_text(w/2, h/2, text="Esperando mediciones...",
                               fill=MUTED, font=(FONT, 8))
            return
        low, high = min(values), max(values)
        if high - low < 0.01:
            high += 1
            low -= 1
        points = []
        for i, value in enumerate(values):
            x = left + i * (right-left) / max(len(values)-1, 1)
            y = bottom - (value-low) * (bottom-top) / (high-low)
            points.extend((x, y))
        if len(points) >= 4:
            canvas.create_line(*points, fill=color, width=2, smooth=True)
        canvas.create_text(left, top, text=f"{high:.0f} {unit}", anchor="sw",
                           fill=MUTED, font=(FONT, 7))
        canvas.create_text(left, bottom, text=f"{low:.0f}", anchor="nw",
                           fill=MUTED, font=(FONT, 7))

    def _build_compact_history(self, parent):
        cols = ("hora", "gases", "temp", "hum", "estado")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=5)
        for col, title, width in [
            ("hora", "Hora", 90), ("gases", "Gases", 90),
            ("temp", "Temperatura °C", 120), ("hum", "Humedad %", 100),
            ("estado", "Estado", 100)
        ]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        for row in list(self.history)[-8:][::-1]:
            tree.insert("", "end", values=(
                row["time"], row["gases"], f'{row["temp"]:.1f}',
                f'{row["hum"]:.1f}', row["state"]
            ))

    def _build_stats(self, parent):
        values = [
            ("Mediciones registradas", str(len(self.history))),
            ("Última lectura de gases", str(self.gases)),
            ("Temperatura actual", f"{self.temperature:.1f} °C"),
            ("Humedad actual", f"{self.humidity:.1f} %")
        ]
        for i, (name, value) in enumerate(values):
            box = self._panel(parent, "#0a1928")
            box.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            parent.grid_columnconfigure(i, weight=1)
            self._label(box, name, 8, MUTED).pack(pady=(12, 4))
            self._label(box, value, 16, TEXT, "bold").pack(pady=(0, 12))

    # --------------------------------------------------------
    # PAGINAS DE NAVEGACION
    # --------------------------------------------------------

    def _build_graphs_page(self):
        page = tk.Frame(self.content, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        self._label(page, "Gráficas de monitoreo", 18, TEXT, "bold").pack(anchor="w")
        self._label(page, "Tendencia de las variables recibidas desde el ESP32", 9, MUTED).pack(
            anchor="w", pady=(3, 15)
        )
        self.chart_canvases = {}
        for key, title, color, unit in [
            ("gases", "Gases · MQ-135", YELLOW, "ADC"),
            ("temp", "Temperatura · DHT11", BLUE, "°C"),
            ("hum", "Humedad · DHT11", PURPLE, "%")
        ]:
            panel = self._panel(page, "#0a1928")
            panel.pack(fill="both", expand=True, pady=6)
            self._label(panel, title, 10, color, "bold").pack(anchor="w", padx=14, pady=(10, 0))
            canvas = tk.Canvas(panel, height=150, bg="#0a1928", highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=10, pady=5)
            self.chart_canvases[key] = canvas
            self._draw_chart(canvas, key, color, unit)

    def _build_history_page(self):
        page = tk.Frame(self.content, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        self._label(page, "Historial de mediciones", 18, TEXT, "bold").pack(anchor="w")
        self._label(page, "Registro local de lecturas recibidas durante esta sesión", 9, MUTED).pack(
            anchor="w", pady=(3, 12)
        )
        actions = tk.Frame(page, bg=BG)
        actions.pack(fill="x", pady=(0, 8))
        tk.Button(actions, text="Exportar CSV", command=self._export_csv,
                  bg="#075d91", fg="white", relief="flat", padx=14, pady=7,
                  font=(FONT, 9, "bold"), cursor="hand2").pack(side="right")
        self.history_tree = ttk.Treeview(
            page, columns=("hora", "gases", "temp", "hum", "mode", "state"),
            show="headings"
        )
        for col, title, width in [
            ("hora", "Hora", 110), ("gases", "Gases", 100),
            ("temp", "Temperatura °C", 130), ("hum", "Humedad %", 110),
            ("mode", "Modo", 100), ("state", "Estado", 120)
        ]:
            self.history_tree.heading(col, text=title)
            self.history_tree.column(col, width=width, anchor="center")
        self.history_tree.pack(fill="both", expand=True)
        self._refresh_history_tree()

    def _build_settings_page(self):
        page = tk.Frame(self.content, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        self._label(page, "Configuración", 18, TEXT, "bold").pack(anchor="w")
        self._label(page, "Parámetros de operación del sistema", 9, MUTED).pack(
            anchor="w", pady=(3, 16)
        )
        panel = self._panel(page, "#0b1b2b")
        panel.pack(fill="x", pady=5)
        self._label(panel, "Umbral de gases", 11, TEXT, "bold").pack(anchor="w", padx=18, pady=(16, 4))
        self._label(panel, "Valor a partir del cual el sistema activa el estado de alerta.",
                    9, MUTED).pack(anchor="w", padx=18)
        row = tk.Frame(panel, bg="#0b1b2b")
        row.pack(fill="x", padx=18, pady=12)
        tk.Scale(row, from_=100, to=3000, orient="horizontal",
                 variable=self.threshold_var, command=self._threshold_changed,
                 bg="#0b1b2b", fg=CYAN, troughcolor="#1b344a",
                 activebackground=GREEN, highlightthickness=0,
                 showvalue=True, length=400).pack(side="left")
        self._label(row, "ADC", 9, MUTED).pack(side="left", padx=12)

    def _build_about_page(self):
        page = tk.Frame(self.content, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=20, pady=18)
        self._label(page, "Monitor de Calidad del Aire", 19, TEXT, "bold").pack(anchor="w")
        self._label(page, "Sistema de adquisición y supervisión basado en ESP32", 10, CYAN).pack(
            anchor="w", pady=(4, 18)
        )
        panel = self._panel(page, "#0b1b2b")
        panel.pack(fill="x")
        details = [
            "Microcontrolador: ESP32 DevKit V1",
            "Sensor de gases: MQ-135 (lectura analógica)",
            "Sensor ambiental: DHT11 (temperatura y humedad)",
            "Actuadores: buzzer, LED verde, LED rojo y ventilador",
            "Comunicación: puerto serial USB a 115200 baudios"
        ]
        for item in details:
            self._label(panel, "•  " + item, 10, TEXT).pack(anchor="w", padx=18, pady=8)

    # --------------------------------------------------------
    # COMUNICACION Y CONTROL
    # --------------------------------------------------------

    def _toggle_connection(self):
        if not self.connected:
            port = self.port.get().strip()
            if not port:
                ports = self._available_ports()
                if ports:
                    port = ports[0]
                    self.port.set(port)
                else:
                    messagebox.showwarning("Puerto serial", "No se encontró un puerto COM disponible.")
                    return
            try:
                self.serial.conectar(port)
                self.connected = True
                self.connection_badge.configure(text=f"●  Conectado", fg=GREEN)
                self.connect_button.configure(text="Desconectar", bg="#7b2940")
                self._log_event(f"Conexión establecida en {port}")
            except Exception as exc:
                messagebox.showerror("Error de conexión", str(exc))
        else:
            try:
                self.serial.desconectar()
            except Exception:
                pass
            self.connected = False
            self.connection_badge.configure(text="●  Desconectado", fg=YELLOW)
            self.connect_button.configure(text="Conectar", bg="#075d91")
            self._log_event("Conexión serial cerrada")

    def _send(self, command):
        if not self.connected:
            messagebox.showwarning("Sin conexión", "Conecta el ESP32 antes de enviar comandos.")
            return
        try:
            self.serial.enviar(command)
        except Exception as exc:
            self._log_event(f"Error al enviar comando: {exc}")

    def _set_mode(self, mode):
        self.mode = mode
        self._send(f"MODE,{mode}")
        self._update_mode_buttons()

    def _update_mode_buttons(self):
        self.auto_btn.configure(
            bg="#087c62" if self.mode == "AUTO" else "#122e48",
            fg="white" if self.mode == "AUTO" else TEXT
        )
        self.manual_btn.configure(
            bg="#087c62" if self.mode == "MANUAL" else "#122e48",
            fg="white" if self.mode == "MANUAL" else TEXT
        )

    def _threshold_changed(self, value):
        self.threshold = int(float(value))
        if hasattr(self, "threshold_value"):
            self.threshold_value.configure(text=str(self.threshold))
        self._draw_gauge()
        if self.connected:
            self._send(f"THRESHOLD,{self.threshold}")

    def _toggle_actuator(self, key):
        if self.mode != "MANUAL":
            messagebox.showinfo("Modo automático", "Cambia a modo Manual para controlar los actuadores.")
            return
        current = {"buzzer": self.buzzer, "fan": self.fan}[key]
        value = 0 if current else 1
        self._send(f"{'BUZZER' if key == 'buzzer' else 'FAN'},{value}")

    def _poll_serial(self):
        if not self.running:
            return
        if self.connected:
            try:
                received = self.serial.recibir()
                if received:
                    if isinstance(received, bytes):
                        received = received.decode("utf-8", errors="ignore")
                    if isinstance(received, str):
                        for line in received.splitlines():
                            self._parse_line(line.strip())
                    elif isinstance(received, (list, tuple)):
                        for line in received:
                            self._parse_line(str(line).strip())
            except Exception as exc:
                self._log_event(f"Error serial: {exc}")
        self.root.after(100, self._poll_serial)

    def _parse_line(self, line):
        if not line.startswith("DATA,"):
            return
        parts = line.split(",")
        if len(parts) < 11:
            return
        try:
            self.gases = int(float(parts[1]))
            self.temperature = float(parts[2])
            self.humidity = float(parts[3])
            self.mode = parts[4].strip()
            self.threshold = int(float(parts[5]))
            self.buzzer = int(float(parts[6]))
            self.led_green = int(float(parts[7]))
            self.led_red = int(float(parts[8]))
            self.fan = int(float(parts[9]))
            self.general_state = parts[10].strip().upper()
            self.last_update = datetime.now().strftime("%H:%M:%S")
            record = {
                "time": self.last_update, "gases": self.gases,
                "temp": self.temperature, "hum": self.humidity,
                "state": self.general_state
            }
            self.history.append(record)
            self._update_dashboard()
            self._refresh_visible_data()
        except (ValueError, IndexError):
            return

    def _update_dashboard(self):
        if not hasattr(self, "sensor_cards"):
            return
        self.sensor_cards["gases"]["value"].configure(text=str(self.gases))
        self.sensor_cards["temp"]["value"].configure(text=f"{self.temperature:.1f}")
        self.sensor_cards["hum"]["value"].configure(text=f"{self.humidity:.1f}")
        state_color = GREEN if self.general_state == "NORMAL" else RED
        self.sensor_cards["state"]["value"].configure(
            text="NORMAL" if self.general_state == "NORMAL" else "ALERTA",
            fg=state_color, font=(FONT, 17, "bold")
        )
        self._draw_gauge()
        if hasattr(self, "actuator_labels"):
            for key, value in [
                ("buzzer", self.buzzer), ("fan", self.fan),
                ("green", self.led_green), ("red", self.led_red)
            ]:
                if key in self.actuator_labels:
                    self.actuator_labels[key].configure(
                        text="ON" if value else "OFF",
                        fg=GREEN if value else MUTED
                    )
        if hasattr(self, "footer_time"):
            self.footer_time.configure(text=f"◷  Última actualización: {self.last_update}")
            self.footer_records.configure(text=f"▤  Registros: {len(self.history)}")
        self.sidebar_status.configure(
            text="●  ESP32 conectado\n\n●  Sensores activos" if self.connected
            else "●  ESP32 desconectado"
        )

    def _refresh_visible_data(self):
        if self.active_section == "Inicio":
            if hasattr(self, "bottom_tab") and self.bottom_tab == "Gráficas en tiempo real":
                self._render_bottom_tab()
            elif self.bottom_tab == "Historial de datos":
                self._render_bottom_tab()
            elif self.bottom_tab == "Estadísticas":
                self._render_bottom_tab()
        elif self.active_section == "Gráficas":
            self._show_section("Gráficas")
        elif self.active_section == "Historial":
            self._refresh_history_tree()

    def _refresh_history_tree(self):
        if not hasattr(self, "history_tree"):
            return
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for row in list(self.history)[::-1]:
            self.history_tree.insert("", "end", values=(
                row["time"], row["gases"], f'{row["temp"]:.1f}',
                f'{row["hum"]:.1f}', self.mode, row["state"]
            ))

    def _export_csv(self):
        if not self.history:
            messagebox.showinfo("Historial", "Todavía no hay mediciones para exportar.")
            return
        os.makedirs("registros", exist_ok=True)
        path = os.path.join("registros", "mediciones.csv")
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["hora", "gases_mq135", "temperatura_c", "humedad_pct", "estado"])
            for row in self.history:
                writer.writerow([row["time"], row["gases"], row["temp"], row["hum"], row["state"]])
        messagebox.showinfo("Exportación", f"Historial guardado en:\n{os.path.abspath(path)}")

    def _log_event(self, message):
        self.events.append((datetime.now().strftime("%H:%M:%S"), message))

    # --------------------------------------------------------
    # ANIMACIONES
    # --------------------------------------------------------

    def _animate(self):
        if not self.running:
            return
        if hasattr(self, "device_canvas") and self.device_canvas.winfo_exists():
            self._draw_device()
        if hasattr(self, "gauge") and self.gauge.winfo_exists():
            self._draw_gauge()
        self.root.after(1200, self._animate)

    def _close(self):
        self.running = False
        if self.connected:
            try:
                self.serial.desconectar()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AirMonitorApp(root)
    root.mainloop()
