#!/data/data/com.termux/files/usr/bin/python
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Button


class Display(Static):
    """Calculator display showing current value."""

    DEFAULT_CSS = """
    Display {
        width: 1fr;
        height: 3;
        content-align: right middle;
        background: $surface;
        border: solid $primary;
        text-style: bold;
    }
    """

    def __init__(self):
        super().__init__("0")
        self.value = "0"

    def update_display(self, text: str) -> None:
        """Update display text."""
        self.value = text
        self.update(text)


class Calculator(Static):
    """Calculator application."""

    DEFAULT_CSS = """
    Calculator {
        width: 50;
        height: auto;
        border: solid $accent;
        background: $panel;
    }
    
    #button-grid {
        width: 1fr;
        height: auto;
        grid-size: 4 5;
        grid-gutter: 1 1;
        padding: 1;
    }
    
    Button {
        width: 1fr;
        height: 3;
    }
    
    Button.operator {
        background: $accent 80%;
    }
    
    Button.equals {
        background: $success 80%;
    }
    
    Button.clear {
        background: $error 80%;
    }
    """

    def __init__(self):
        super().__init__()
        self.display_widget = Display()
        self.left_operand = None
        self.operator = None
        self.new_input = True

    def compose(self) -> ComposeResult:
        yield self.display_widget

        with Grid(id="button-grid"):
            # Row 1
            yield Button("C", id="clear", classes="clear")
            yield Button("÷", id="divide", classes="operator")
            yield Button("×", id="multiply", classes="operator")
            yield Button("−", id="minus", classes="operator")

            # Row 2
            yield Button("7")
            yield Button("8")
            yield Button("9")
            yield Button("+", id="plus", classes="operator")

            # Row 3
            yield Button("4")
            yield Button("5")
            yield Button("6")
            yield Button("=", id="equals", classes="equals")

            # Row 4
            yield Button("1")
            yield Button("2")
            yield Button("3")
            yield Button(".", id="decimal")

            # Row 5
            yield Button("0", id="zero")
            yield Button("", disabled=True)  # Spacer
            yield Button("", disabled=True)  # Spacer
            yield Button("", disabled=True)  # Spacer

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        button_label = str(event.button.label)

        # 1. Handle clear (C)
        if button_id == "clear":
            self.display_widget.update_display("0")
            self.left_operand = None
            self.operator = None
            self.new_input = True
            return

        # 2. Handle equals (=)
        if button_id == "equals":
            if self.left_operand is not None and self.operator is not None:
                right_operand = float(self.display_widget.value)
                result = self._calculate(self.left_operand, self.operator, right_operand)
                self.display_widget.update_display(result)
                self.left_operand = None
                self.operator = None
                self.new_input = True
            return

        # 3. Handle operators (+, −, ×, ÷)
        if button_id in ("plus", "minus", "multiply", "divide"):
            current_value = float(self.display_widget.value)

            # If we already have an operator, calculate the pending operation first
            if self.left_operand is not None and self.operator is not None and not self.new_input:
                result = self._calculate(self.left_operand, self.operator, current_value)
                self.display_widget.update_display(result)
                self.left_operand = float(result)
            else:
                self.left_operand = current_value

            # Map button IDs to operators
            operator_map = {"plus": "+", "minus": "−", "multiply": "×", "divide": "÷"}
            self.operator = operator_map[button_id]
            self.new_input = True
            return

        # 4. Handle number input (0-9) and decimal
        if button_label in "0123456789" or button_id == "decimal":
            if button_id == "decimal":
                # Prevent multiple decimals
                if "." in self.display_widget.value:
                    return
                button_label = "."

            if self.new_input:
                # Start new number
                if button_label == ".":
                    self.display_widget.update_display("0.")
                else:
                    self.display_widget.update_display(button_label)
                self.new_input = False
            else:
                # Append to current number
                current = self.display_widget.value
                # Limit display length
                if len(current) < 12:
                    self.display_widget.update_display(current + button_label)

    def _calculate(self, left: float, operator: str, right: float) -> str:
        """Perform the calculation and return result as string."""
        try:
            if operator == "+":
                result = left + right
            elif operator == "−":
                result = left - right
            elif operator == "×":
                result = left * right
            elif operator == "÷":
                if right == 0:
                    return "Error"
                result = left / right
            else:
                return "Error"

            # Format result nicely
            if result == int(result):
                return str(int(result))
            else:
                # Limit to 10 significant digits
                return f"{result:.10g}"
        except Exception:
            return "Error"


if __name__ == "__main__":

    class CalcApp(App):
        BINDINGS = [("q", "quit", "Quit")]

        def compose(self) -> ComposeResult:
            yield Calculator()

    app = CalcApp()
    app.run()
