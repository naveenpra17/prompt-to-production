import tkinter as tk
from tkinter import font
from decimal import Decimal, InvalidOperation

# --- THEME VARIABLES ---
# Base colors
BG_COLOR = "#121212"          # Deep dark background
DISPLAY_BG = "#1e1e1e"        # Slightly lighter display background
BTN_ACTIVE_BG = "#3e3e3e"     # Hover/Active state for generic buttons

# Text colors
TEXT_COLOR = "#ffffff"
GHOST_TEXT_COLOR = "#888888"  # Gray for history preview
OPERATOR_TEXT_COLOR = "#121212" # Dark text for pastel buttons

# Pastel colors for buttons
COLOR_OPERATOR = "#bae1ff"          # Pastel Blue
COLOR_OPERATOR_ACTIVE = "#9bc9eb"
COLOR_CLEAR = "#ffdfba"             # Pastel Orange
COLOR_CLEAR_ACTIVE = "#e5c5a0"
COLOR_EQUALS = "#baffc9"            # Pastel Green
COLOR_EQUALS_ACTIVE = "#a0e5af"
COLOR_NUMBERS = "#2c2c2c"           # Dark gray for number buttons

# Spacing
PADDING = 4

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Retailer Calculator")
        self.root.geometry("400x600")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(320, 500)
        
        # State variables
        self.current_input = "0"
        self.history = ""
        self.first_operand = None
        self.operator = None
        self.reset_input = False # Flag to reset input on next digit
        
        # Set up typography
        self.setup_fonts()
        
        # Build UI
        self.create_widgets()
        self.setup_bindings()
        
    def setup_fonts(self):
        """Setup typography with a fallback mechanism."""
        available_fonts = font.families()
        # Prefer Inter or Outfit, fallback to Helvetica or Arial
        base_font = "Helvetica"
        for f in ["Inter", "Outfit", "Segoe UI", "Arial"]:
            if f in available_fonts:
                base_font = f
                break
                
        self.btn_font = (base_font, 18)
        self.display_font = (base_font, 40, "bold")
        self.history_font = (base_font, 16)
        
    def create_widgets(self):
        """Create and place all UI components."""
        # Configure root grid weights for responsive layout
        self.root.rowconfigure(0, weight=2) # Display area gets a bit more space
        for i in range(1, 7):
            self.root.rowconfigure(i, weight=1) # Button rows
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
            
        # Display Area
        self.display_frame = tk.Frame(self.root, bg=DISPLAY_BG)
        self.display_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=PADDING, pady=PADDING)
        
        # Weights for display elements
        self.display_frame.rowconfigure(0, weight=1)
        self.display_frame.rowconfigure(1, weight=1)
        self.display_frame.columnconfigure(0, weight=1)
        
        # History Label (Ghost preview)
        self.history_label = tk.Label(
            self.display_frame, 
            text=self.history, 
            font=self.history_font, 
            bg=DISPLAY_BG, 
            fg=GHOST_TEXT_COLOR, 
            anchor="e", 
            padx=15,
            pady=5
        )
        self.history_label.grid(row=0, column=0, sticky="sew")
        
        # Main Display Label
        self.display_label = tk.Label(
            self.display_frame, 
            text=self.current_input, 
            font=self.display_font, 
            bg=DISPLAY_BG, 
            fg=TEXT_COLOR, 
            anchor="e", 
            padx=15,
            pady=10
        )
        self.display_label.grid(row=1, column=0, sticky="new")
        
        # Button definitions: (text, bg_color, active_bg_color, text_color)
        buttons = [
            ('AC', COLOR_CLEAR, COLOR_CLEAR_ACTIVE, OPERATOR_TEXT_COLOR),
            ('C', COLOR_CLEAR, COLOR_CLEAR_ACTIVE, OPERATOR_TEXT_COLOR),
            ('%', COLOR_OPERATOR, COLOR_OPERATOR_ACTIVE, OPERATOR_TEXT_COLOR),
            ('/', COLOR_OPERATOR, COLOR_OPERATOR_ACTIVE, OPERATOR_TEXT_COLOR),
            
            ('7', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('8', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('9', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('*', COLOR_OPERATOR, COLOR_OPERATOR_ACTIVE, OPERATOR_TEXT_COLOR),
            
            ('4', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('5', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('6', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('-', COLOR_OPERATOR, COLOR_OPERATOR_ACTIVE, OPERATOR_TEXT_COLOR),
            
            ('1', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('2', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('3', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('+', COLOR_OPERATOR, COLOR_OPERATOR_ACTIVE, OPERATOR_TEXT_COLOR),
            
            ('0', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('.', COLOR_NUMBERS, BTN_ACTIVE_BG, TEXT_COLOR),
            ('=', COLOR_EQUALS, COLOR_EQUALS_ACTIVE, OPERATOR_TEXT_COLOR)
        ]
        
        row_val = 1
        col_val = 0
        
        for btn in buttons:
            text, bg, active_bg, fg = btn
            
            # The '0' button takes up 2 columns
            colspan = 2 if text == '0' else 1
            
            b = tk.Button(
                self.root, 
                text=text, 
                font=self.btn_font, 
                bg=bg, 
                fg=fg, 
                activebackground=active_bg,
                activeforeground=fg,
                relief="flat", 
                borderwidth=0,
                cursor="hand2", # Better interaction feedback
                command=lambda t=text: self.on_button_click(t)
            )
            
            # Accessibility: Visual focus indicators for keyboard navigation
            b.bind("<FocusIn>", lambda e, btn=b: btn.config(bg=btn.cget("activebackground")))
            b.bind("<FocusOut>", lambda e, btn=b, original_bg=bg: btn.config(bg=original_bg))
            
            # Enter key triggers the focused button
            b.bind("<Return>", lambda e, t=text: self.on_button_click(t))
            
            b.grid(row=row_val, column=col_val, columnspan=colspan, sticky="nsew", padx=PADDING, pady=PADDING)
            
            col_val += colspan
            if col_val > 3:
                col_val = 0
                row_val += 1
                
    def setup_bindings(self):
        """Keyboard support for physical numpad and keys."""
        self.root.bind("<Key>", self.key_handler)
        
    def key_handler(self, event):
        """Map keyboard keys to calculator functions."""
        char = event.char
        keysym = event.keysym
        
        if char.isdigit():
            self.on_button_click(char)
        elif char in ['+', '-', '*', '/', '.', '%']:
            self.on_button_click(char)
        elif keysym in ['Return', 'KP_Enter']:
            self.on_button_click('=')
        elif keysym == 'BackSpace':
            self.on_button_click('C')
        elif keysym == 'Escape':
            self.on_button_click('AC')

    def update_display(self):
        """Refresh the main display and ghost history."""
        if self.current_input == "Error":
            self.display_label.config(text="Error")
        else:
            try:
                # Use Decimal to format for accurate display
                val = Decimal(self.current_input)
                # Convert to string accurately, removing any weird formatting if plain number
                formatted_str = f"{val:f}"
                if '.' in formatted_str:
                    formatted_str = formatted_str.rstrip('0').rstrip('.')
                if not formatted_str:
                    formatted_str = "0"
                
                # Check if it was just entered with a decimal point e.g., "5."
                if self.current_input.endswith('.'):
                    formatted_str += "."
                    
                self.display_label.config(text=formatted_str)
            except InvalidOperation:
                self.display_label.config(text=self.current_input)
                
        self.history_label.config(text=self.history)

    def on_button_click(self, char):
        """Handle button press logic."""
        if char == 'AC':
            # All Clear
            self.current_input = "0"
            self.history = ""
            self.first_operand = None
            self.operator = None
            self.reset_input = False
            
        elif char == 'C':
            # Clear current entry (Backspace)
            if self.reset_input or self.current_input == "Error":
                self.current_input = "0"
                self.reset_input = False
            else:
                self.current_input = self.current_input[:-1]
                if not self.current_input or self.current_input == "-":
                    self.current_input = "0"
                    
        elif char.isdigit():
            # Numbers
            if self.current_input == "0" or self.reset_input or self.current_input == "Error":
                self.current_input = char
                self.reset_input = False
            else:
                self.current_input += char
                
        elif char == '.':
            # Decimal point
            if self.reset_input or self.current_input == "Error":
                self.current_input = "0."
                self.reset_input = False
            elif '.' not in self.current_input:
                self.current_input += '.'
                
        elif char in ['+', '-', '*', '/']:
            # Arithmetic Operators
            if self.current_input != "Error":
                if self.first_operand is not None and not self.reset_input:
                    # Chained operation: compute intermediate before next operator
                    self.calculate()
                
                self.first_operand = Decimal(self.current_input)
                self.operator = char
                # Add spacing around operator for history display
                op_symbol = '÷' if char == '/' else '×' if char == '*' else char
                self.history = f"{self.first_operand} {op_symbol}"
                self.reset_input = True
                
        elif char == '%':
            # Percentage
            if self.current_input != "Error":
                try:
                    val = Decimal(self.current_input) / Decimal("100")
                    self.current_input = str(val.normalize())
                    self.reset_input = True
                except InvalidOperation:
                    self.current_input = "Error"
                    
        elif char == '=':
            # Calculate final result
            if self.operator and self.current_input != "Error":
                self.calculate()
                self.operator = None
                self.first_operand = None
                
        self.update_display()
        
    def calculate(self):
        """Execute the mathematical operation accurately using Decimal."""
        try:
            second_operand = Decimal(self.current_input)
            
            if self.operator == '+':
                result = self.first_operand + second_operand
            elif self.operator == '-':
                result = self.first_operand - second_operand
            elif self.operator == '*':
                result = self.first_operand * second_operand
            elif self.operator == '/':
                if second_operand == 0:
                    self.current_input = "Error"
                    op_symbol = '÷'
                    self.history = f"{self.first_operand} {op_symbol} 0 ="
                    self.reset_input = True
                    return
                result = self.first_operand / second_operand
                
            # Normalize to strip trailing zeros
            result = result.normalize()
            self.current_input = str(result)
            
            op_symbol = '÷' if self.operator == '/' else '×' if self.operator == '*' else self.operator
            self.history = f"{self.first_operand} {op_symbol} {second_operand} ="
            self.reset_input = True
            
        except (InvalidOperation, Exception):
            self.current_input = "Error"
            self.reset_input = True

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
