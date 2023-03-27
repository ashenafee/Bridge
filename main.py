import tkinter as tk
from tkinter import filedialog as fd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bridge")
        self.geometry("400x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):

        # SPACER #
        self.separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)
        # ------ #

        # Mode Selection
        self._setup_mode_selection()

        # SPACER #
        self.separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)
        # ------ #

        # Options
        self._setup_options()

        # SPACER #
        self.separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)
        # ------ #

        # Text Fields
        self._setup_input_fields()

        # SPACER #
        self.separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)
        # ------ #

        # Buttons
        self._setup_buttons()

    def _setup_input_fields(self):
        """
        Setup the input fields depending on the mode.
        """
        self._setup_search_input_fields()
        self.mode_var.trace("w", self._update_input_fields)

    def _update_input_fields(self, *args):
        """
        Update the input fields depending on the mode.
        """

        # Remove the current fields
        for widget in self.input_fields.winfo_children():
            widget.destroy()
        
        if self.mode_var.get() == "Search":
            self._setup_search_input_fields(update=True)
        elif self.mode_var.get() == "BLAST":
            self._setup_blast_input_fields(update=True)
        elif self.mode_var.get() == "Tree":
            self._setup_tree_input_fields(update=True)
    
    def _setup_search_input_fields(self, update=False):
        """
        Setup the input fields for the Search mode.
        """

        if not update:
            self.input_fields = tk.Frame(self)
            self.input_fields.pack()

        self.gene_input = tk.Text(self.input_fields, height=1, width=30,
                                  foreground="grey", name="gene_input")
        self.gene_input.insert(tk.END, "Gene(s)")
        self.gene_input.bind("<FocusIn>", self.text_field_focused)
        self.gene_input.grid(row=0, column=0)

        self.species_input = tk.Text(self.input_fields, height=1, width=30,
                                     foreground="grey", name="species_input")
        self.species_input.insert(tk.END, "Species")
        self.species_input.bind("<FocusIn>", self.text_field_focused)
        self.species_input.grid(row=1, column=0)
    
    def _setup_blast_input_fields(self, update=False):
        """
        Setup the input fields for the BLAST mode.
        """

        if not update:
            self.input_fields = tk.Frame(self)
            self.input_fields.pack()

        self.gene_input = tk.Text(self.input_fields, height=1, width=30,
                                    foreground="grey", name="gene_input")
        self.gene_input.insert(tk.END, "Gene(s)")
        self.gene_input.bind("<FocusIn>", self.text_field_focused)
        self.gene_input.grid(row=0, column=0)

        self.species_input = tk.Text(self.input_fields, height=1, width=30,
                                    foreground="grey", name="species_input")
        self.species_input.insert(tk.END, "Species")
        self.species_input.bind("<FocusIn>", self.text_field_focused)
        self.species_input.grid(row=1, column=0)

    def _setup_tree_input_fields(self, update=False):
        """
        Setup the input fields for the Tree mode.
        """
        # TODO: Implement this
        self.placeholder = tk.Label(self.input_fields, text="Placeholder")
        self.placeholder.grid(row=0, column=0)

    def _setup_buttons(self):
        self.button_row = tk.Frame(self)
        self.button_row.pack()

        self.exit_button = tk.Button(self.button_row, text="Exit",
                                        name="exit_btn")
        self.exit_button.grid(row=0, column=0)
        self.exit_button.bind("<Button-1>", self.exit_button_clicked)

        self.clear_button = tk.Button(self.button_row, text="Clear", 
                                      name="clear_btn")
        self.clear_button.grid(row=0, column=1)
        self.clear_button.bind("<Button-1>", self.clear_button_clicked)

        self.run_button = tk.Button(self.button_row, text="Run",
                                    name="run_btn")
        self.run_button.grid(row=0, column=2)
        self.run_button.bind("<Button-1>", self.run_button_clicked)

    def _setup_options(self):
        """
        Setup the option configuration menu depending on the mode.
        """

        self._setup_search_options()
        self.mode_var.trace("w", self._update_options)

    def _update_options(self, *args):
        """
        Update the option configuration menu depending on the mode.
        """

        # Remove the current options
        for widget in self.options_row.winfo_children():
            widget.destroy()

        if self.mode_var.get() == "Search":
            self._setup_search_options(update=True)
        elif self.mode_var.get() == "BLAST":
            self._setup_blast_options(update=True)
        elif self.mode_var.get() == "Tree":
            self._setup_tree_options(update=True)

    def _setup_search_options(self, update=False):

        if not update:
            self.options_row = tk.Frame(self)
            self.options_row.pack()
        
        self.search_db_label = tk.Label(self.options_row, text="Database:")
        self.search_db_label.grid(row=0, column=0)

        self.search_db_var = tk.StringVar()
        self.search_db_var.set("GenBank")

        self.genbank_radio = tk.Radiobutton(self.options_row, text="GenBank",
                                            variable=self.search_db_var, value="GenBank")
        self.genbank_radio.grid(row=0, column=1)

        self.ensembl_radio = tk.Radiobutton(self.options_row, text="Ensembl",
                                            variable=self.search_db_var, value="Ensembl")
        self.ensembl_radio.grid(row=0, column=2)

    def _setup_blast_options(self, update=False):
        """
        Setup options for the BLAST mode.
        """      
        if not update:
            self.options_row = tk.Frame(self)
            self.options_row.pack()
    
        # Database Selection
        self.blast_db_label = tk.Label(self.options_row, text="Database:")
        self.blast_db_label.grid(row=0, column=0)

        self.blast_db_var = tk.StringVar()
        self.blast_db_var.set("nr")

        self.nr_radio = tk.Radiobutton(self.options_row, text="nr",
                                        variable=self.blast_db_var, value="nr")
        self.nr_radio.grid(row=0, column=1)

        self.nt_radio = tk.Radiobutton(self.options_row, text="nt",
                                        variable=self.blast_db_var, value="nt")
        self.nt_radio.grid(row=0, column=2)

        # Output Name
        self.output_name_label = tk.Label(self.options_row, text="Output Name:")
        self.output_name_label.grid(row=1, column=0)

        self.blast_output_input = tk.Text(self.options_row, height=1, width=20,
                                          foreground="grey", name="blast_output_input")
        self.blast_output_input.insert(tk.END, "e.g., blast_search")
        self.blast_output_input.bind("<FocusIn>", self.text_field_focused)
        self.blast_output_input.grid(row=1, column=1, columnspan=2)

        # Maximum amount of targets
        self.max_targets_label = tk.Label(self.options_row, text="Max Targets:")
        self.max_targets_label.grid(row=2, column=0)

        self.max_targets_input = tk.Text(self.options_row, height=1, width=20,
                                            foreground="grey", name="max_targets_input")
        self.max_targets_input.insert(tk.END, "e.g., 100")
        self.max_targets_input.bind("<FocusIn>", self.text_field_focused)
        self.max_targets_input.grid(row=2, column=1, columnspan=2)

        # E-value
        self.evalue_label = tk.Label(self.options_row, text="E-value:")
        self.evalue_label.grid(row=3, column=0)

        self.evalue_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="evalue_input")
        self.evalue_input.insert(tk.END, "e.g., 0.001")
        self.evalue_input.bind("<FocusIn>", self.text_field_focused)
        self.evalue_input.grid(row=3, column=1, columnspan=2)

        # Word Size
        self.word_size_label = tk.Label(self.options_row, text="Word Size:")
        self.word_size_label.grid(row=4, column=0)

        self.word_size_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="word_size_input")
        self.word_size_input.insert(tk.END, "e.g., 3")
        self.word_size_input.bind("<FocusIn>", self.text_field_focused)
        self.word_size_input.grid(row=4, column=1, columnspan=2)

        # Gap Open
        self.gap_open_label = tk.Label(self.options_row, text="Gap Open:")
        self.gap_open_label.grid(row=5, column=0)

        self.gap_open_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="gap_open_input")
        self.gap_open_input.insert(tk.END, "e.g., 11")
        self.gap_open_input.bind("<FocusIn>", self.text_field_focused)
        self.gap_open_input.grid(row=5, column=1, columnspan=2)

        # Gap Extend
        self.gap_extend_label = tk.Label(self.options_row, text="Gap Extend:")
        self.gap_extend_label.grid(row=6, column=0)

        self.gap_extend_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="gap_extend_input")
        self.gap_extend_input.insert(tk.END, "e.g., 1")
        self.gap_extend_input.bind("<FocusIn>", self.text_field_focused)
        self.gap_extend_input.grid(row=6, column=1, columnspan=2)

        # Template Length
        self.template_length_label = tk.Label(self.options_row, text="Template Length:")
        self.template_length_label.grid(row=7, column=0)

        self.template_length_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="template_length_input")
        self.template_length_input.insert(tk.END, "e.g., 21")
        self.template_length_input.bind("<FocusIn>", self.text_field_focused)
        self.template_length_input.grid(row=7, column=1, columnspan=2)

        # Template Type
        self.template_type_label = tk.Label(self.options_row, text="Template Type:")
        self.template_type_label.grid(row=8, column=0)

        self.template_type_input = tk.Text(self.options_row, height=1, width=20,
                                    foreground="grey", name="template_type_input")
        self.template_type_input.insert(tk.END, "e.g., coding")
        self.template_type_input.bind("<FocusIn>", self.text_field_focused)
        self.template_type_input.grid(row=8, column=1, columnspan=2)

        # File upload or database search
        self.input_type_label = tk.Label(self.options_row, text="Input Type:")
        self.input_type_label.grid(row=9, column=0)

        self.input_type_var = tk.StringVar()
        self.input_type_var.set("Search")
        self.search_radio = tk.Radiobutton(self.options_row, text="Search",
                                        variable=self.input_type_var, value="Search")
        self.search_radio.grid(row=9, column=1)

        self.file_radio = tk.Radiobutton(self.options_row, text="File",
                                        variable=self.input_type_var, value="File")
        self.file_radio.grid(row=9, column=2)

        self.input_type_var.trace("w", self._setup_blast_input_format)

        # Set all Labels sticky to "E"
        for label in self.options_row.grid_slaves():
            if int(label.grid_info()["column"]) == 0:
                label.grid(sticky="E", padx=(0, 10))

    def _setup_blast_input_format(self, *args):
        """
        Setup the input format options for BLAST.
        """

        # Remove the current fields
        for widget in self.input_fields.grid_slaves():
            widget.destroy()

        if self.input_type_var.get() == "Search":
            self.gene_input = tk.Text(self.input_fields, height=1, width=30,
                                        foreground="grey", name="gene_input")
            self.gene_input.insert(tk.END, "Gene(s)")
            self.gene_input.bind("<FocusIn>", self.text_field_focused)
            self.gene_input.grid(row=0, column=0)

            self.species_input = tk.Text(self.input_fields, height=1, width=30,
                                        foreground="grey", name="species_input")
            self.species_input.insert(tk.END, "Species")
            self.species_input.bind("<FocusIn>", self.text_field_focused)
            self.species_input.grid(row=1, column=0)
        else:
            self.file_select_btn = tk.Button(self.input_fields, text="Select File",
                                            name="file_select_btn")
            self.file_select_btn.grid(row=0, column=0)
            self.file_select_btn.bind("<Button-1>", self._select_file)
    
    def _select_file(self, event):
        """
        Select a file to upload.
        """
        self.file_path = fd.askopenfilename()
        self.file_select_btn.config(text=self.file_path.split("/")[-1])

    def _setup_tree_options(self, update=False):
        """
        Setup options for generating Trees.
        """
        # TODO: Implement this
        self.placeholder = tk.Label(self.options_row, text="Placeholder")
        self.placeholder.grid(row=0, column=0)

    def _setup_mode_selection(self):
        self.mode_selection = tk.Frame(self)
        self.mode_selection.pack()

        self.mode_label = tk.Label(self.mode_selection, text="Mode:")
        self.mode_label.grid(row=0, column=0)

        self.mode_var = tk.StringVar()
        self.mode_var.set("Search")

        self.search_radio = tk.Radiobutton(self.mode_selection, text="Search",
                                            variable=self.mode_var, value="Search")
        self.search_radio.grid(row=0, column=1)

        self.blast_radio = tk.Radiobutton(self.mode_selection, text="BLAST",
                                            variable=self.mode_var, value="BLAST")
        self.blast_radio.grid(row=0, column=2)

        self.tree_radio = tk.Radiobutton(self.mode_selection, text="Tree",
                                            variable=self.mode_var, value="Tree")
        self.tree_radio.grid(row=0, column=3)

    def text_field_focused(self, event):
        """
        Clears the "placeholder" text when a text field is focused.
        """
        widget = event.widget
        if widget.cget("foreground") == "grey":
            widget.delete("1.0", tk.END)
            widget.config(foreground="black")
        
        widget.bind("<FocusOut>", self.text_field_unfocused)
    
    def text_field_unfocused(self, event):
        """
        Replaces the text with a "placeholder" if the text field is empty.
        """
        widget = event.widget
        if not widget.get("1.0", tk.END).strip():

            placeholder = str(widget)[1:]
            
            if placeholder.endswith("gene_input"):
                widget.insert(tk.END, "Gene(s)")
            elif placeholder.endswith("species_input"):
                widget.insert(tk.END, "Species")
            
            widget.config(foreground="grey")

    # Button Events
    def exit_button_clicked(self, event):
        """
        Exits the application.
        """
        self.destroy()

    def clear_button_clicked(self, event):
        """
        Clears the text fields.
        """
        self.gene_input.delete("1.0", tk.END)
        self.gene_input.insert(tk.END, "Gene(s)")
        self.gene_input.config(foreground="grey")

        self.species_input.delete("1.0", tk.END)
        self.species_input.insert(tk.END, "Species")
        self.species_input.config(foreground="grey")

        self.blast_output_input.delete("1.0", tk.END)
        self.blast_output_input.insert(tk.END, "e.g., blast_search")
        self.blast_output_input.config(foreground="grey")

        self.max_targets_input.delete("1.0", tk.END)
        self.max_targets_input.insert(tk.END, "e.g., 100")
        self.max_targets_input.config(foreground="grey")

        self.evalue_input.delete("1.0", tk.END)
        self.evalue_input.insert(tk.END, "e.g., 0.001")
        self.evalue_input.config(foreground="grey")

        self.word_size_input.delete("1.0", tk.END)
        self.word_size_input.insert(tk.END, "e.g., 3")
        self.word_size_input.config(foreground="grey")

        self.gap_open_input.delete("1.0", tk.END)
        self.gap_open_input.insert(tk.END, "e.g., 11")
        self.gap_open_input.config(foreground="grey")

        self.gap_extend_input.delete("1.0", tk.END)
        self.gap_extend_input.insert(tk.END, "e.g., 1")
        self.gap_extend_input.config(foreground="grey")

        self.template_length_input.delete("1.0", tk.END)
        self.template_length_input.insert(tk.END, "e.g., 21")
        self.template_length_input.config(foreground="grey")

        self.templtate_type_input.delete("1.0", tk.END)
        self.templtate_type_input.insert(tk.END, "e.g., coding")
        self.templtate_type_input.config(foreground="grey")
    
    def run_button_clicked(self, event):
        """
        Run the pipeline according to the mode selected.
        """
        mode = self.mode_var.get()
        if mode == "Search":
            print("Search")
        elif mode == "BLAST":
            print("BLAST")
        elif mode == "Tree":
            print("Tree")

if __name__ == "__main__":
    app = App()
    app.mainloop()