import asyncio
import customtkinter as ctk
from ttbzrs_millionaire.ui.splash_screen import SplashScreen
from ttbzrs_millionaire.ui.main_window import MainWindow

async def main():
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and show splash screen
    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    
    # Create main window but don't show it yet
    app = MainWindow()
    app.withdraw()
    
    # Show splash screen
    splash = SplashScreen()
    splash.lift()  # Ensure splash screen is on top
    
    # Schedule the transition
    root.after(3000, lambda: transition_to_main(splash, app))
    
    # Start the main event loop
    root.mainloop()

def transition_to_main(splash, app):
    splash.destroy()  # Close splash screen
    app.deiconify()  # Show main window

if __name__ == "__main__":
    asyncio.run(main())
