# importing libraries
import os
import textwrap
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import t
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# declaring the Graphic class
class Graphic(tk.Tk):
    # delcaring the constructor for the Graphic class
    def __init__(self, storage, analysis):
        super().__init__()
        self.title("VectraLab Analysis GUI")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.storage  = storage
        self.analysis = analysis

        # ─── Data mappings ─────────────────────   
        # These are the mappings for the datasets     
        self.dataset_map = {
            "Solar 1":    ("time1", "angle1"),
            "Solar 2":    ("time2", "angle2"),
            "Solar 3":    ("time3", "angle3"),
            "Sidereal 1": ("time4", "angle4"),
            "Sidereal 2": ("time5", "angle5"),
            "Sidereal 3": ("time6", "angle6"),
        }

        # These are the mappings for the describe function
        self.describe_map = {
            "Solar 1":    "data1",
            "Solar 2":    "data2",
            "Solar 3":    "data3",
            "Sidereal 1": "data4",
            "Sidereal 2": "data5",
            "Sidereal 3": "data6",
        }

        # ─── Placeholders for figures/canvases ────────────
        self.canvas_fit = None; self.fig_fit = None
        self.canvas_chi = None; self.fig_chi = None
        self.canvas_chv = None; self.fig_chv = None
        self.canvas_t   = None; self.fig_t   = None
        self.tree_desc  = None

        # initialize the GUI
        self._build_ui()

    # the _on_close function is called when the window is closed
    def _on_close(self):
        self.quit()
        self.destroy()

    # the _build_ui function is used to build the GUI
    def _build_ui(self):
        # 1) Notebook
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill='both', expand=True)

        # ─── Home Tab ───────────────────────────────
        home_tab = ttk.Frame(self._notebook)
        self._notebook.add(home_tab, text="Home")

        # Introductory text
        intro_text = textwrap.dedent("""\
            Welcome to VectraLab!

            VectraLab is your all-in-one toolkit for gnomon data:
              • Explore summary statistics
              • Fit linear models (ω & period)
              • Compare datasets via χ²
              • Detect outliers with Chauvenet
              • Run t-tests vs expected solar (24 h) or sidereal (≈23 h 56 m)

            Solar time measures the passage of time based on the Sun’s position in the sky, with a full solar day lasting 
            about 24 hours, from one noon to the next. Sidereal time, on the other hand, tracks Earth's rotation relative to 
            distant stars rather than the Sun, resulting in a slightly shorter day of about 23 hours and 56 minutes. The 
            difference arises because Earth not only rotates on its axis but also moves along its orbit around the Sun, 
            requiring a little extra rotation each day to realign the Sun's position. While solar time governs our daily lives and 
            calendars, sidereal time is essential for astronomy and tracking celestial objects. The figures below illustate the 
            celestial phenomena of solar and sidereal time.
        """)

        # Create a label for the intro text
        lbl_intro = ttk.Label(
            home_tab,
            text=intro_text,
            wraplength=600,
            justify="left",
            anchor="w"
        )
        lbl_intro.pack(fill="x", padx=20, pady=(20,10))

        # Images side by side, equal half-size
        img_frame = ttk.Frame(home_tab)
        img_frame.pack(pady=10)
        common_size = None
        img_dir = os.path.join(os.path.dirname(__file__), "image")
        pairs = [
            ("Solar",    "solar.png",    "_solar_img"),
            ("Sidereal", "sidereal.png", "_sidereal_img"),
        ]

        # Load originals
        loaded = {}
        for name, fname, _ in pairs:
            path = os.path.join(img_dir, fname)
            if os.path.isfile(path):
                try:
                    loaded[name] = Image.open(path)
                except Exception as e:
                    print(f"[HomeTab] error loading {name}: {e}")

        # Compute common half-size
        if loaded:
            half_sizes = [(img.width//2, img.height//2) for img in loaded.values()]
            w_min, h_min = min(half_sizes)
            common_size = (w_min, h_min)

        # Resize & display
        for name, pil_img, attr in pairs:
            if name in loaded and common_size:
                try:
                    resized = loaded[name].resize(common_size, resample=Image.Resampling.LANCZOS)
                    tk_img  = ImageTk.PhotoImage(resized)
                    setattr(self, attr, tk_img)  # keep reference
                    ttk.Label(img_frame, image=tk_img).pack(side="left", padx=10)
                except Exception as e:
                    print(f"[HomeTab] failed to process {name}: {e}")

        # Usage instructions
        wrap_px = common_size[0]*2 + 40 if common_size else 600
        instr_text = textwrap.dedent("""\
            Use the tabs to:
              • Describe: summary stats of raw data
              • Fitting: linear fits & angular velocity
              • Chi-square: dataset comparison
              • Chauvenet: outlier detection
              • T-test: measured vs expected period

            Click a tab above to get started.
        """)
        # Create a label for the instructions
        lbl_instr = ttk.Label(
            home_tab,
            text=instr_text,
            wraplength=wrap_px,
            justify="left",
            anchor="w"
        )
        lbl_instr.pack(fill="x", padx=20, pady=(10,20))

        # Image citations
        cite_text = textwrap.dedent("""\
            Image sources:
              • Solar:    https://www.quora.com/Why-does-the-duration-of-day-and-night-keep-changing-What-is-its-importance
              • Sidereal: https://chadorzel.com/principles/2015/01/16/semi-competent-astrophotography-and-sidereal-days/
        """)
        # Create a label for the citations
        lbl_cite = ttk.Label(
            home_tab,
            text=cite_text,
            wraplength=wrap_px,
            justify="left",
            anchor="w"
        )
        lbl_cite.pack(side="bottom", fill="x", padx=20, pady=(0,10))

        # ─── Describe Tab ──────────────────────────────────────────
        # This tab is used to describe the dataset
        # It shows the summary statistics of the dataset
        self.desc_tab = ttk.Frame(self._notebook)
        self._notebook.add(self.desc_tab, text="Describe")
        sel = ttk.Frame(self.desc_tab); sel.pack(pady=5, fill='x', padx=10)
        ttk.Label(sel, text="Dataset:").grid(row=0, column=0, sticky='e')
        self.combo_desc = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        # set the default value to the first dataset
        self.combo_desc.current(0)
        self.combo_desc.grid(row=0, column=1, padx=5)
        bf = ttk.Frame(self.desc_tab); bf.pack(pady=5)
        ttk.Button(bf, text="Run Describe", command=self._run_describe).pack(side='left', padx=2)
        ttk.Button(bf, text="Clear",        command=self._clear_describe).pack(side='left', padx=2)
        self.tree_desc = ttk.Treeview(self.desc_tab, show='headings')
        self.tree_desc.pack(fill='both', expand=True)

        # ─── Fitting Tab ───────────────────────────────────────────
        # This tab is used to fit the dataset to a linear model
        self.fit_tab = ttk.Frame(self._notebook)
        self._notebook.add(self.fit_tab, text="Fitting")
        sel = ttk.Frame(self.fit_tab); sel.pack(pady=5, fill='x', padx=10)
        ttk.Label(sel, text="Dataset:").grid(row=0, column=0, sticky='e')
        self.combo_fit = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        self.combo_fit.current(0)
        self.combo_fit.grid(row=0, column=1, padx=5)
        bf = ttk.Frame(self.fit_tab); bf.pack(pady=5)
        ttk.Button(bf, text="Run Fit",   command=self._run_fit).pack(side='left', padx=2)
        ttk.Button(bf, text="Clear",     command=self._clear_fit).pack(side='left', padx=2)
        ttk.Button(bf, text="Save Plot", command=self._save_fit).pack(side='left', padx=2)
        self.lbl_fit = ttk.Label(
            self.fit_tab, text="", anchor="w", justify="left"
        )
        self.lbl_fit.pack(fill="x", padx=20, pady=(5,10))

        # ─── Chi-square Tab ────────────────────────────────────────
        # This tab is used to compare two datasets using the chi-square test
        self.chi_tab = ttk.Frame(self._notebook)
        self._notebook.add(self.chi_tab, text="Chi-square")
        sel = ttk.Frame(self.chi_tab); sel.pack(pady=5, fill='x', padx=10)
        ttk.Label(sel, text="Dataset A:").grid(row=0, column=0, sticky='e')
        self.combo_a = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        self.combo_a.current(0)
        self.combo_a.grid(row=0, column=1, padx=5)
        ttk.Label(sel, text="Dataset B:").grid(row=0, column=2, sticky='e')
        self.combo_b = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        self.combo_b.current(3)
        self.combo_b.grid(row=0, column=3, padx=5)
        bf = ttk.Frame(self.chi_tab); bf.pack(pady=5)
        ttk.Button(bf, text="Run χ²",   command=self._run_chi).pack(side='left', padx=3)
        ttk.Button(bf, text="Clear",    command=self._clear_chi).pack(side='left', padx=3)
        ttk.Button(bf, text="Save Plot",command=self._save_chi).pack(side='left', padx=3)
        self.lbl_chi = ttk.Label(self.chi_tab, text="", anchor="w", justify="left")
        self.lbl_chi.pack(fill="x", padx=20, pady=(5,10))
        self.tree_chi = ttk.Treeview(self.chi_tab, show='headings')
        self.tree_chi.pack(fill='both', expand=True)

        # ─── Chauvenet Tab ──────────────────────────────────────────
        # This tab is used to detect outliers using Chauvenet's criterion
        self.chv_tab = ttk.Frame(self._notebook)
        self._notebook.add(self.chv_tab, text="Chauvenet")
        sel = ttk.Frame(self.chv_tab); sel.pack(pady=5, fill='x', padx=10)
        ttk.Label(sel, text="Dataset:").grid(row=0, column=0, sticky='e')
        self.combo_chv = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        self.combo_chv.current(0)
        self.combo_chv.grid(row=0, column=1, padx=5)
        bf = ttk.Frame(self.chv_tab); bf.pack(pady=5)
        ttk.Button(bf, text="Run Chauvenet", command=self._run_chv).pack(side='left', padx=2)
        ttk.Button(bf, text="Clear",         command=self._clear_chv).pack(side='left', padx=2)
        ttk.Button(bf, text="Save Plot",     command=self._save_chv).pack(side='left', padx=2)
        self.lbl_chv = ttk.Label(self.chv_tab, text="", anchor="w", justify="left")
        self.lbl_chv.pack(fill="x", padx=20, pady=(5,10))
        self.tree_chv = ttk.Treeview(self.chv_tab, show='headings')
        self.tree_chv.pack(fill='both', expand=True)

        # ─── T-test Tab ─────────────────────────────────────────────
        # This tab is used to perform a t-test on the dataset
        self.ttest_tab = ttk.Frame(self._notebook)
        self._notebook.add(self.ttest_tab, text="T-test")
        sel = ttk.Frame(self.ttest_tab); sel.pack(pady=5, fill='x', padx=10)
        ttk.Label(sel, text="Dataset:").grid(row=0, column=0, sticky='e')
        self.combo_t = ttk.Combobox(
            sel,
            values=list(self.dataset_map.keys()),
            state='readonly'
        )
        self.combo_t.current(0)
        self.combo_t.grid(row=0, column=1, padx=5)
        bf = ttk.Frame(self.ttest_tab); bf.pack(pady=5)
        ttk.Button(bf, text="Run t-test", command=self._run_t).pack(side='left', padx=2)
        ttk.Button(bf, text="Clear",      command=self._clear_t).pack(side='left', padx=2)
        ttk.Button(bf, text="Save Plot",  command=self._save_t).pack(side='left', padx=2)
        self.lbl_t = ttk.Label(self.ttest_tab, text="", anchor="w", justify="left")
        self.lbl_t.pack(fill="x", padx=20, pady=(5,10))
        self.tree_t = ttk.Treeview(self.ttest_tab, show='headings')
        self.tree_t.pack(fill='both', expand=True)

    # the _draw_canvas function is used to draw the canvas for the figures
    def _draw_canvas(self, fig, attr, parent):
        fig.tight_layout()
        old = getattr(self, attr)
        if old:
            old.get_tk_widget().destroy()
            setattr(self, attr, None)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        w = canvas.get_tk_widget()
        w.pack(fill='both', expand=True, padx=20, pady=10)
        canvas.draw()
        setattr(self, attr, canvas)

    # ─── Clear methods ─────────────────────────────────────────────
    def _clear_describe(self):
        for r in self.tree_desc.get_children():
            self.tree_desc.delete(r)
        self.tree_desc["columns"] = []

    def _clear_fit(self):
        if self.canvas_fit:
            self.canvas_fit.get_tk_widget().destroy()
        self.canvas_fit = None
        self.lbl_fit.config(text="")
        self.fig_fit = None

    def _clear_chi(self):
        if self.canvas_chi:
            self.canvas_chi.get_tk_widget().destroy()
        self.canvas_chi = None
        self.lbl_chi.config(text="")
        for r in self.tree_chi.get_children():
            self.tree_chi.delete(r)
        self.tree_chi["columns"] = []
        self.fig_chi = None

    def _clear_chv(self):
        if self.canvas_chv:
            self.canvas_chv.get_tk_widget().destroy()
        self.canvas_chv = None
        self.lbl_chv.config(text="")
        for r in self.tree_chv.get_children():
            self.tree_chv.delete(r)
        self.tree_chv["columns"] = []
        self.fig_chv = None

    def _clear_t(self):
        if self.canvas_t:
            self.canvas_t.get_tk_widget().destroy()
        self.canvas_t = None
        self.lbl_t.config(text="")
        for r in self.tree_t.get_children():
            self.tree_t.delete(r)
        self.tree_t["columns"] = []
        self.fig_t = None

    # ─── Describe ────────────────────────────────────────────────
    def _run_describe(self):
        # 1) clear old results
        self._clear_describe()

        # 2) grab the right DataFrame
        name = self.combo_desc.get()
        df   = getattr(self.storage, self.describe_map[name])

        # 3) describe → stats as rows, vars as columns
        descr = df.describe().reset_index().rename(columns={'index': 'Statistic'})

        # 4) configure Treeview
        cols = list(descr.columns)   # ['Statistic', 'col1', 'col2', ...]
        self.tree_desc["columns"] = cols
        for c in cols:
            self.tree_desc.heading(c, text=c)
            self.tree_desc.column(c, anchor='center')

        # 5) insert each stat‐row
        for _, row in descr.iterrows():
            self.tree_desc.insert("", "end", values=list(row))

    # ─── Fitting ─────────────────────────────────────────────────
    # This function is used to fit the data to a linear model
    def _run_fit(self):
        self._clear_fit()
        name = self.combo_fit.get()
        x = getattr(self.storage, self.dataset_map[name][0])
        y = getattr(self.storage, self.dataset_map[name][1])

        popt, perr = self.storage.model.linear_fit(x, y, yerr=None)
        a0, a1    = popt if len(popt)==2 else (0.0, popt[0])
        δa0, δa1  = perr if len(perr)==2 else (0.0, perr[0])
        t0, dt0   = self.storage.model.calculate_t0(abs(a1), δa1)

        self.lbl_fit.config(
            text=(f"Intercept = {a0:.3e} ± {δa0:.3e} rad\n"
                  f"ω = {a1:.3e} ± {δa1:.3e} rad/s\n"
                  f"t₀ = {t0:.3f} ± {dt0:.3f} hours")
        )

        fig, ax = plt.subplots(figsize=(6,3))
        if name.startswith("Solar"):
            σ = np.radians(0.5)
            ax.errorbar(x, y, yerr=np.full_like(x,σ), fmt='o', label='data ±0.5°')
        else:
            ax.scatter(x, y, s=10, label='data')
        T = np.linspace(x.min(), x.max(), 500)
        ax.plot(T, self.storage.model.linear_model(T, a0, a1),
                '--r', label=f"θ={a0:.2e}+{a1:.2e}·t")
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Δθ (rad)"); ax.legend()

        self._draw_canvas(fig, 'canvas_fit', parent=self.fit_tab)
        self.fig_fit = fig

    # This function is used to save the fit plot and the fit parameters
    # It saves the plot as a PNG file and the parameters as a text file
    def _save_fit(self):
        if not self.fig_fit:
            return
        os.makedirs('results', exist_ok=True)
        base = self.combo_fit.get().replace(' ','_')
        png  = f"results/{base}_fit.png"
        txt  = f"results/{base}_fit.txt"
        self.fig_fit.savefig(png, dpi=300, bbox_inches='tight')
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(self.lbl_fit.cget('text'))
        self.lbl_fit.config(text=f"Saved → {png} & {txt}")

    # ─── Chi-square ───────────────────────────────────────────────
    # This function is used to run the chi-square test on two datasets
    def _run_chi(self):
        self._clear_chi()
        a, b = self.combo_a.get(), self.combo_b.get()
        df1 = pd.DataFrame({'time': getattr(self.storage, self.dataset_map[a][0]),
                            'value': getattr(self.storage, self.dataset_map[a][1])})
        df2 = pd.DataFrame({'time': getattr(self.storage, self.dataset_map[b][0]),
                            'value': getattr(self.storage, self.dataset_map[b][1])})
        res = self.analysis.chi_square_analysis(df1, df2, bin_width=300)
        tbl = res['table']

        fig, ax = plt.subplots(figsize=(6,3))
        ax.scatter(tbl['Time Bin'], tbl['Obs1'], label=f'Obs ({a})')
        ax.scatter(tbl['Time Bin'], tbl['Exp1'], marker='x', label=f'Exp ({a})')
        ax.scatter(tbl['Time Bin'], tbl['Obs2'], marker='s', label=f'Obs ({b})')
        ax.scatter(tbl['Time Bin'], tbl['Exp2'], marker='d', label=f'Exp ({b})')
        ax.set_xlabel('Time (s)'); ax.set_ylabel('Counts'); ax.legend()

        self._draw_canvas(fig, 'canvas_chi', parent=self.chi_tab)
        self.fig_chi = fig

        χ2, dof, p = res['chi2_total'], res['dof'], res['pvalue']
        concl = "correlated" if p>0.05 else "not correlated"
        self.lbl_chi.config(text=f"χ²={χ2:.1f}, dof={dof}, p={p:.3e}\nThere is {concl}.")

        cols = list(tbl.columns)
        self.tree_chi["columns"] = cols
        for c in cols:
            self.tree_chi.heading(c, text=c)
            self.tree_chi.column(c, anchor='center', width=80)
        for _, row in tbl.iterrows():
            self.tree_chi.insert('', 'end', values=[row[c] for c in cols])

    # This function is used to save the chi-square plot and the chi-square parameters
    # It saves the plot as a PNG file and the parameters as a text file
    def _save_chi(self):
        if not self.fig_chi:
            return
        os.makedirs('results', exist_ok=True)
        a, b  = self.combo_a.get(), self.combo_b.get()
        base  = f"{a.replace(' ','_')}_vs_{b.replace(' ','_')}_chi2"
        png   = f"results/{base}.png"
        txt   = f"results/{base}.txt"
        self.fig_chi.savefig(png, dpi=300, bbox_inches='tight')
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(self.lbl_chi.cget('text'))
        self.lbl_chi.config(text=f"Saved → {png} & {txt}")

    # ─── Chauvenet ───────────────────────────────────────────────
    # This function is used to run the Chauvenet's criterion on a dataset
    # It detects outliers in the dataset and returns the outliers
    def _run_chv(self):
        self._clear_chv()
        name = self.combo_chv.get()
        data = getattr(self.storage, self.dataset_map[name][1])
        res  = self.analysis.chauvenet(data)

        vals, PNs = zip(*res)
        fig, ax = plt.subplots(figsize=(6,3))
        ax.scatter(vals, PNs)
        ax.set_xlabel('Value'); ax.set_ylabel('P-Value')

        self._draw_canvas(fig, 'canvas_chv', parent=self.chv_tab)
        self.fig_chv = fig

        out = [v for v,p in res if p<0.5]
        self.lbl_chv.config(text=f"{name}: {len(out)} outliers")

        cols = ['Value','P-Value']
        self.tree_chv["columns"] = cols
        for c in cols:
            self.tree_chv.heading(c, text=c)
            self.tree_chv.column(c, anchor='center', width=100)
        for v, pn in res:
            self.tree_chv.insert('', 'end', values=(v, pn))

    # This function is used to save the Chauvenet's criterion plot and the Chauvenet's criterion parameters
    # It saves the plot as a PNG file and the parameters as a text file
    def _save_chv(self):
        if not self.fig_chv:
            return
        os.makedirs('results', exist_ok=True)
        base = f"{self.combo_chv.get().replace(' ','_')}_chauvenet"
        png  = f"results/{base}.png"
        txt  = f"results/{base}.txt"
        self.fig_chv.savefig(png, dpi=300, bbox_inches='tight')
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(self.lbl_chv.cget('text'))
        self.lbl_chv.config(text=f"Saved → {png} & {txt}")

    # ─── T-test ───────────────────────────────────────────────
    # This function is used to run the t-test on a dataset
    # It compares the dataset with the expected solar or sidereal period
    def _run_t(self):
        self._clear_t()
        name = self.combo_t.get()
        x = getattr(self.storage, self.dataset_map[name][0])
        y = getattr(self.storage, self.dataset_map[name][1])
        popt, perr = self.storage.model.linear_fit(x, y, yerr=None)
        a1  = popt[1] if len(popt)==2 else popt[0]
        δa1 = perr[1] if len(perr)==2 else perr[0]
        t0, dt0 = self.storage.model.calculate_t0(abs(a1), δa1)
        t0_exp  = 24.0 if name.startswith("Solar") else (23 + 56/60)
        t_stat  = (t0 - t0_exp) / dt0
        pval    = 2 * (1 - t.cdf(abs(t_stat), df=1))

        cols = ["Dataset","t₀ (h)","±δt₀","Expected","t-stat","p-value"]
        self.tree_t["columns"] = cols
        for c in cols:
            self.tree_t.heading(c, text=c)
            self.tree_t.column(c, anchor='center', width=110)
        self.tree_t.insert("", "end", values=(
            name, f"{t0:.4f}", f"{dt0:.4f}", f"{t0_exp:.4f}",
            f"{t_stat:.3f}", f"{pval:.3e}"
        ))

        fig, ax = plt.subplots(figsize=(5,3))
        ax.bar(["measured","expected"], [t0, t0_exp], yerr=[dt0,0], capsize=5)
        ax.set_ylabel("Period t₀ (h)")
        ax.set_title(f"{name} vs expected")

        self._draw_canvas(fig, 'canvas_t', parent=self.ttest_tab)
        self.fig_t = fig

        conclusion = (
            "We are confident that the result is accurate."
            if pval > 0.05 else
            "We are not confident that the result is accurate."
        )
        self.lbl_t.config(text=conclusion)

    # This function is used to save the t-test plot and the t-test parameters
    # It saves the plot as a PNG file and the parameters as a text file
    def _save_t(self):
        if not self.fig_t:
            return
        os.makedirs('results', exist_ok=True)
        base = f"{self.combo_t.get().replace(' ','_')}_ttest"
        png  = f"results/{base}.png"
        txt  = f"results/{base}.txt"
        self.fig_t.savefig(png, dpi=300, bbox_inches='tight')
        with open(txt, 'w', encoding='utf-8') as f:
            f.write(self.lbl_t.cget('text'))
        self.lbl_t.config(text=f"Saved → {png} & {txt}")
