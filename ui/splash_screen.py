import tkinter as tk
from PIL import Image, ImageTk
import math
import time

class SplashScreen(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("")
        self.geometry("800x600")
        self.overrideredirect(True)  # Remove window decorations
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"600x400+{x}+{y}")
        
        # Initialize colors
        self.neon_blue = "#00ffff"
        self.neon_pink = "#ff1493"
        self.warm_brown = "#8b4513"
        self.deep_blue = "#000080"
        
        # Create canvas
        self.canvas = tk.Canvas(self, 
                              width=600,
                              height=400,
                              bg='black',
                              highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Store animation callbacks
        self._callbacks = []
        
        # Create decorative elements
        self.create_decorative_elements()
        
        # Start animations
        self.start_animations()
        
        # Schedule closing
        self._callbacks.append(self.after(3000, self.cleanup_and_close))
        
        # Bring to front
        self.lift()
        self.attributes('-topmost', True)
    
    def cleanup_and_close(self):
        """Clean up animations and close the window"""
        for callback in self._callbacks:
            self.after_cancel(callback)
        self._callbacks.clear()
        self.destroy()
    
    def start_animations(self):
        """Start all animations"""
        self.animate_dots()
    
    def create_decorative_elements(self):
        # Calculate center position
        center_x, center_y = 300, 200
        
        # Create outer rings with gradient
        for i in range(5):
            radius = 80 - i * 15
            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=self.neon_blue if i % 2 == 0 else self.neon_pink,
                width=2
            )
        
        # Create title with gradient effect
        title_text = "ttbzrs\nMillion\nDollars\nAdvisor"
        y_offset = 100
        
        for line in title_text.split('\n'):
            # Create shadow effect
            self.canvas.create_text(
                center_x + 2, y_offset + 2,
                text=line,
                fill=self.deep_blue,
                font=('Helvetica', 36, 'bold'),
                anchor='center'
            )
            
            # Create main text
            self.canvas.create_text(
                center_x, y_offset,
                text=line,
                fill=self.neon_blue,
                font=('Helvetica', 36, 'bold'),
                anchor='center'
            )
            y_offset += 50
        
        # Create pulsing dots
        self.dots = []
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x = center_x + math.cos(angle) * 120
            y = center_y + math.sin(angle) * 120
            
            dot = self.canvas.create_oval(
                x-5, y-5, x+5, y+5,
                fill=self.neon_pink if i % 2 == 0 else self.warm_brown,
                outline=self.neon_blue
            )
            self.dots.append({'dot': dot, 'angle': angle, 'center_x': center_x, 'center_y': center_y})
    
    def animate_dots(self):
        """Animate the pulsing dots"""
        if not hasattr(self, 'dots'):
            return
            
        t = time.time() * 2
        for dot_info in self.dots:
            angle = dot_info['angle'] + t
            radius = 120 + math.sin(t + dot_info['angle']) * 10
            x = dot_info['center_x'] + math.cos(angle) * radius
            y = dot_info['center_y'] + math.sin(angle) * radius
            self.canvas.coords(
                dot_info['dot'],
                x-5, y-5, x+5, y+5
            )
        
        callback = self.after(20, self.animate_dots)
        self._callbacks.append(callback)
