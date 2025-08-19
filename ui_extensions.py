import customtkinter as ctk

class AutoWidthComboBox(ctk.CTkComboBox):
    """
    A custom CTkComboBox that overrides the dropdown menu creation
    to enforce a specific width and add borders to the options.
    This version uses the after() method and directly configures the
    internal buttons, which is the definitive solution.
    """
    def _open_dropdown_menu(self):
        # Allow the original method to create the dropdown menu
        super()._open_dropdown_menu()

        # Schedule the configuration to run after a short delay
        # to ensure the main widget's geometry is calculated.
        self.after(20, self._configure_dropdown_menu_geometry)

    def _configure_dropdown_menu_geometry(self):
        """(Runs after a short delay) Applies the correct width and styling."""
        if self._dropdown_menu is not None and hasattr(self._dropdown_menu, '_buttons'):
            # Get the final, rendered width of the combobox widget
            widget_width = self.winfo_width()
            
            # --- FIX: Iterate through all buttons and configure them directly ---
            # This forces the parent frame and window to expand correctly.
            for button in self._dropdown_menu._buttons.values():
                button.configure(
                    width=widget_width,      # Force button width
                    anchor="w",              # Align text to the left
                    corner_radius=0,         # Make options look like a standard menu
                    border_width=1,
                    border_color="gray40"
                )