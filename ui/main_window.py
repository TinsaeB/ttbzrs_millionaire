import customtkinter as ctk
from tkinter import filedialog, messagebox
import asyncio
import os
from datetime import datetime
from typing import Dict, List
import threading
import queue
import re

from ttbzrs_millionaire.services.llm_service import LLMService
from ttbzrs_millionaire.services.document_service import DocumentService
from ttbzrs_millionaire.services.session_service import SessionService

class MainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize services
        self.llm_service = LLMService()
        self.document_service = DocumentService()
        self.session_service = SessionService()
        
        # Message queue for thread-safe communication
        self.message_queue = queue.Queue()
        self._callbacks = []
        
        # Session data
        self.session_data = []
        
        # Help panel state
        self.help_panel_visible = False
        self.help_panel = None
        self.main_content = None
        self.sidebar = None
        
        # Keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.clear_chat())
        self.bind("<Control-s>", lambda e: self.handle_save_session())
        self.bind("<Control-o>", lambda e: self.handle_load_pdf())
        self.bind("<Control-h>", lambda e: self.toggle_help_panel())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<F1>", lambda e: self.toggle_help_panel())
        self.bind("<Escape>", lambda e: self.hide_help_panel())
        
        # Configure window
        self.title("You Won a Million Dollars, Now What?")
        self.geometry("1000x700")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI components
        self.create_sidebar()
        self.create_main_content()
        self.create_help_panel()
        self._start_message_processing()
    
    def _create_ui(self):
        self.create_sidebar()
        self.create_main_content()
    
    def _start_message_processing(self):
        """Start the message processing loop with a stored reference"""
        callback = self.after(100, self.process_message_queue)
        self._callbacks.append(callback)
    
    def process_message_queue(self):
        """Process messages from the queue"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'chat':
                    self._add_chat_message(message['sender'], message['message'])
                elif message['type'] == 'status':
                    self.update_status(message['status'], message['color'])
                
                self.message_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.after(100, self.process_message_queue)
    
    def _add_chat_message(self, sender: str, message: str):
        """Add a message to the chat display with proper styling"""
        self.chat_display.configure(state="normal")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Style based on sender
        if sender == "You":
            prefix = "👤"
            sender_style = {
                "fg": "#00ffff",  # Neon blue
                "font": ("Helvetica", 12, "bold")
            }
            base_style = {
                "fg": "#ffffff",  # White
                "font": ("Helvetica", 11)
            }
            highlight_color = "#00ffff"  # Neon blue
        elif sender == "Assistant":
            prefix = "🤖"
            sender_style = {
                "fg": "#ff1493",  # Neon pink
                "font": ("Helvetica", 12, "bold")
            }
            base_style = {
                "fg": "#ffffff",  # White
                "font": ("Helvetica", 11)
            }
            highlight_color = "#ff1493"  # Neon pink
        else:  # System messages
            prefix = "ℹ️"
            sender_style = {
                "fg": "#ffd700",  # Gold
                "font": ("Helvetica", 12, "bold")
            }
            base_style = {
                "fg": "#ffa500",  # Orange
                "font": ("Helvetica", 11)
            }
            highlight_color = "#ffd700"  # Gold
        
        # Insert timestamp with style
        self.chat_display.insert("end", f"[{timestamp}] ", {"fg": "#808080", "font": ("Helvetica", 10)})
        
        # Insert prefix and sender with style
        self.chat_display.insert("end", f"{prefix} {sender}: ", sender_style)
        
        # Process markdown formatting
        lines = message.split('\n')
        in_list = False
        in_code_block = False
        code_block_buffer = []
        
        for line in lines:
            # Handle code blocks with triple backticks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    if code_block_buffer:
                        self.chat_display.insert("end", '\n'.join(code_block_buffer) + '\n', {
                            "fg": "#ffd700",  # Gold for code
                            "font": ("Courier", 11),
                            "bg": "#2d2d2d"  # Darker background for code
                        })
                    code_block_buffer = []
                    in_code_block = False
                else:
                    # Start code block
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block_buffer.append(line)
                continue
            
            # Handle bullet points
            if line.strip().startswith('- '):
                if not in_list:
                    in_list = True
                line = '  • ' + line[2:]
            elif in_list and not line.strip():
                in_list = False
            
            # Process inline formatting
            current_style = base_style.copy()
            parts = []
            current_text = ''
            i = 0
            
            while i < len(line):
                if line[i:i+2] == '**' and i+2 < len(line):  # Bold
                    if current_text:
                        parts.append((current_text, current_style.copy()))
                        current_text = ''
                    current_style['font'] = ("Helvetica", 11, "bold")
                    current_style['fg'] = highlight_color
                    i += 2
                    continue
                elif line[i] == '`':  # Inline code
                    if current_text:
                        parts.append((current_text, current_style.copy()))
                        current_text = ''
                    current_style = {
                        "fg": "#ffd700",  # Gold for code
                        "font": ("Courier", 11),
                        "bg": "#2d2d2d"  # Darker background for code
                    }
                    i += 1
                    continue
                elif line[i] == '*' and not line[i:i+2] == '**':  # Italic
                    if current_text:
                        parts.append((current_text, current_style.copy()))
                        current_text = ''
                    if 'bold' in str(current_style.get('font', '')):
                        current_style['font'] = ("Helvetica", 11, "bold italic")
                    else:
                        current_style['font'] = ("Helvetica", 11, "italic")
                    i += 1
                    continue
                
                current_text += line[i]
                i += 1
            
            if current_text:
                parts.append((current_text, current_style))
            
            # Insert processed line
            for text, style in parts:
                self.chat_display.insert("end", text, style)
            self.chat_display.insert("end", "\n", base_style)
        
        # Add extra newline at the end
        self.chat_display.insert("end", "\n", base_style)
        
        # Store in session data
        self.session_data.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message
        })
        
        # Scroll to bottom
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def post_message(self, msg_type: str, **kwargs):
        """Post a message to the queue"""
        self.message_queue.put({'type': msg_type, **kwargs})
    
    def _format_financial_terms(self, message: str) -> str:
        """Automatically format common financial terms and numbers"""
        import re
        
        # Format currency amounts
        # Matches patterns like $1000, $1,000, $1000.00, $1,000.00
        message = re.sub(
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'**$\1**',
            message
        )
        
        # Format percentages
        # Matches patterns like 10%, 10.5%, 0.5%
        message = re.sub(
            r'(\d+(?:\.\d+)?%)(?!\*\*)',
            r'`\1`',
            message
        )
        
        # Format common financial terms
        financial_terms = {
            r'\b(ETF|IRA|401k|ROI|APR|APY)\b': '`\1`',  # Technical terms
            r'\b(stock market|bull market|bear market)\b': '*\1*',  # Market terms
            r'\b(high-risk|low-risk|medium-risk)\b': '**\1**',  # Risk levels
            r'\b(dividend|yield|portfolio|diversification)\b': '*\1*',  # Investment terms
        }
        
        for pattern, replacement in financial_terms.items():
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        return message

    def handle_send(self):
        """Handle sending a message"""
        message = self.user_input.get("1.0", "end-1c").strip()
        if not message:
            return
        
        # Clear input
        self.user_input.delete("1.0", "end")
        
        # Format financial terms in user's message
        formatted_message = self._format_financial_terms(message)
        
        # Add user message
        self._add_chat_message("You", formatted_message)
        
        # Update status to thinking
        self.update_status("thinking", "#ffd700")
        
        # Get chat history before starting the thread
        context = self.get_chat_history()
        
        # Process message in background
        threading.Thread(target=self._process_message, args=(message, context), daemon=True).start()
    
    def _process_message(self, message: str, context: str):
        """Process message in background thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Update status to processing
            self.post_message('status', status="processing", color="#00ffff")
            
            response = loop.run_until_complete(self.llm_service.get_response(message, context))
            
            if response['status'] == 'success':
                formatted_response = self._format_financial_terms(response['message'])
                self.post_message('chat', sender="Assistant", message=formatted_response)
                self.post_message('status', status="ready", color="#00ff00")
            else:
                self.post_message('chat', sender="System", message=f"Error: {response['message']}")
                self.post_message('status', status="error", color="#ff0000")
            
        except Exception as e:
            self.post_message('chat', sender="System", message=f"Error: {str(e)}")
            self.post_message('status', status="error", color="#ff0000")
        finally:
            loop.close()
    
    def update_status(self, status: str = "ready", color: str = "#00ff00"):
        """Update the status indicator"""
        status_icons = {
            "ready": "🟢",
            "thinking": "🤔",
            "processing": "⏳",
            "error": "🔴"
        }
        
        icon = status_icons.get(status.lower(), "🟡")
        self.status_label.configure(
            text=f"{icon} {status.title()}",
            text_color=color
        )

    def create_sidebar(self):
        # Sidebar with gradient border
        self.sidebar = ctk.CTkFrame(self, 
                             width=200,
                             fg_color="#1a1a1a",
                             border_width=2,
                             border_color="#ff1493",
                             corner_radius=15)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.sidebar.grid_propagate(False)
        
        # Title with neon effect
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=(20, 30), padx=10)
        
        title = ctk.CTkLabel(
            title_frame,
            text="ttbzrs\nMillionaire",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color="#ff1493"
        )
        title.pack()
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Financial Advisor",
            font=ctk.CTkFont(size=14),
            text_color="#ffd700"
        )
        subtitle.pack(pady=(5, 0))
        
        # Function to create styled buttons with tooltips
        def create_button(text, icon, command, tooltip_text):
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.pack(pady=(0, 15), padx=10)
            
            button = ctk.CTkButton(
                btn_frame,
                text=f"{icon} {text}",
                width=160,
                height=40,
                corner_radius=10,
                border_width=2,
                hover_color="#1a1a1a",
                fg_color="#2d2d2d",
                border_color="#ff1493",
                text_color="#ffffff",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=command
            )
            button.pack()
            
            # Create tooltip
            tooltip = ctk.CTkLabel(
                btn_frame,
                text=tooltip_text,
                font=ctk.CTkFont(size=11),
                text_color="#ffd700",
                fg_color="#1a1a1a",
                corner_radius=5,
                padx=10,
                pady=5
            )
            
            def show_tooltip(event):
                tooltip.place(x=button.winfo_width() + 5, y=0)
            
            def hide_tooltip(event):
                tooltip.place_forget()
            
            button.bind("<Enter>", show_tooltip)
            button.bind("<Leave>", hide_tooltip)
            
            return button
        
        # Create buttons with tooltips
        self.new_chat_btn = create_button(
            "New Chat", "✨",
            self.clear_chat,
            "Start a fresh conversation (Ctrl+N)"
        )
        
        self.load_pdf_btn = create_button(
            "Load PDF", "📄",
            self.handle_load_pdf,
            "Analyze financial documents (Ctrl+O)"
        )
        
        self.save_session_btn = create_button(
            "Save Chat", "💾",
            self.handle_save_session,
            "Save this conversation (Ctrl+S)"
        )
        
        self.help_btn = create_button(
            "Help", "❓",
            self.toggle_help_panel,
            "Show help and shortcuts (F1)"
        )
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.pack(side="bottom", pady=20, padx=10)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="🟢 Ready",
            font=ctk.CTkFont(size=12),
            text_color="#00ff00"
        )
        self.status_label.pack()
        
        # Version info
        version_label = ctk.CTkLabel(
            self.status_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="#808080"
        )
        version_label.pack(pady=(5, 0))
    
    def create_main_content(self):
        # Main content area with gradient border
        self.main_content = ctk.CTkFrame(self, 
                                  fg_color="#1a1a1a",
                                  border_width=2,
                                  border_color="#00ffff",
                                  corner_radius=15)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Chat display area with custom styling
        self.chat_display = ctk.CTkTextbox(
            self.main_content,
            wrap="word",
            font=ctk.CTkFont(size=12),
            fg_color="#2d2d2d",
            text_color="#ffffff",
            border_width=1,
            border_color="#404040",
            corner_radius=10
        )
        self.chat_display.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.chat_display.configure(state="disabled")
        
        # Input area with modern styling
        input_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.user_input = ctk.CTkTextbox(
            input_frame,
            height=60,
            wrap="word",
            font=ctk.CTkFont(size=12),
            fg_color="#2d2d2d",
            text_color="#ffffff",
            border_width=1,
            border_color="#404040",
            corner_radius=10
        )
        self.user_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=100,
            command=self.handle_send,
            corner_radius=10,
            border_width=2,
            hover_color="#1a1a1a",
            fg_color="#2d2d2d",
            border_color="#00ffff",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        send_button.grid(row=0, column=1)
        
        # Bind Enter key to send message
        self.user_input.bind("<Return>", lambda e: self.handle_send())
        
        # Add initial greeting with enhanced markdown
        welcome_message = (
            "**Welcome to ttbzrs Million Dollar Advisor!** 🎉\n\n"
            "*Congratulations on your hypothetical million-dollar win!* "
            "I'm here to help you explore various financial scenarios and make informed decisions.\n\n"
            "Here are some things you can do:\n"
            "- Ask questions about **financial planning**\n"
            "- Load PDF documents for *detailed analysis*\n"
            "- Discuss **investment strategies**\n"
            "- Explore *exciting scenarios* with your million dollars\n\n"
            "Here's a quick tip for using our chat:\n"
            "```\n"
            "Use markdown formatting for better readability:\n"
            "**bold text** for emphasis\n"
            "*italic text* for descriptions\n"
            "`code` for technical terms\n"
            "- dashes for bullet points\n"
            "```\n\n"
            "Let's start by discussing your **first financial goal**! 🎯"
        )
        self._add_chat_message("Assistant", welcome_message)
        
        # Add example user message
        example_message = (
            "I'm interested in exploring some **investment options**. "
            "I've heard about:\n"
            "- *Real estate* investments\n"
            "- `ETFs` and mutual funds\n"
            "- **Startup** opportunities\n\n"
            "Could you help me understand the *pros and cons* of each?"
        )
        self._add_chat_message("You", example_message)
        
        # Add example response
        response_message = (
            "I'll help you analyze these **investment options**:\n\n"
            "1. **Real Estate Investments**:\n"
            "- *Pros*: Stable income, property appreciation\n"
            "- *Cons*: High initial costs, maintenance\n\n"
            "2. **ETFs and Mutual Funds**:\n"
            "```\n"
            "Key Benefits:\n"
            "- Diversification\n"
            "- Professional management\n"
            "- Lower minimum investment\n"
            "```\n\n"
            "3. **Startup Investments**:\n"
            "- *High potential* returns\n"
            "- Requires *due diligence*\n"
            "- Consider `risk tolerance`\n\n"
            "Would you like to explore any of these options in **more detail**?"
        )
        self._add_chat_message("Assistant", response_message)
    
    def create_help_panel(self):
        """Create sliding help panel"""
        panel_width = 300  # Back to original width
        
        self.help_panel = ctk.CTkFrame(
            self,
            fg_color="#1a1a1a",
            border_width=2,
            border_color="#ffd700",
            corner_radius=15,
            width=panel_width
        )
        
        # Header with close button
        header = ctk.CTkFrame(self.help_panel, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 0))
        
        title = ctk.CTkLabel(
            header,
            text="Help & Tips",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffd700"
        )
        title.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(
            header,
            text="×",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#2d2d2d",
            hover_color="#ff1493",
            command=self.hide_help_panel
        )
        close_btn.pack(side="right", padx=10)
        
        # Create tabview
        tabview = ctk.CTkTabview(self.help_panel)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Shortcuts tab
        shortcuts_tab = tabview.add("Shortcuts")
        shortcuts = [
            ("New Chat", "Ctrl + N"),
            ("Save Session", "Ctrl + S"),
            ("Load PDF", "Ctrl + O"),
            ("Show/Hide Help", "F1 or Ctrl + H"),
            ("Close Help", "Esc"),
            ("Quit", "Ctrl + Q"),
            ("Send Message", "Enter"),
            ("New Line", "Shift + Enter")
        ]
        
        for i, (action, key) in enumerate(shortcuts):
            frame = ctk.CTkFrame(shortcuts_tab, fg_color="transparent")
            frame.pack(pady=5, fill="x")
            
            ctk.CTkLabel(
                frame,
                text=action,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffd700"
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                frame,
                text=key,
                font=ctk.CTkFont(size=12, family="Courier"),
                text_color="#00ffff"
            ).pack(side="right", padx=10)
        
        # Formatting tab
        format_tab = tabview.add("Formatting")
        format_examples = [
            ("Bold Text", "**text**", "Makes text **bold**"),
            ("Italic Text", "*text*", "Makes text *italic*"),
            ("Code", "`text`", "Shows text as `code`"),
            ("Code Block", "```\ntext\n```", "Creates a code block"),
            ("Bullet Points", "- text", "Creates a bullet point")
        ]
        
        for title, syntax, desc in format_examples:
            frame = ctk.CTkFrame(format_tab, fg_color="transparent")
            frame.pack(pady=10, fill="x", padx=10)
            
            ctk.CTkLabel(
                frame,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffd700"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                frame,
                text=syntax,
                font=ctk.CTkFont(size=12, family="Courier"),
                text_color="#00ffff"
            ).pack(anchor="w", padx=20)
            
            ctk.CTkLabel(
                frame,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color="#ffffff"
            ).pack(anchor="w", padx=20)
        
        # Tips tab
        tips_tab = tabview.add("Tips")
        tips_text = (
            "• Currency amounts like **$1,000** are automatically highlighted\n\n"
            "• Percentages like `7.5%` are shown in code style\n\n"
            "• Terms like *stock market* and *portfolio* are italicized\n\n"
            "• Risk levels like **high-risk** are shown in bold\n\n"
            "• Technical terms like `ETF` and `IRA` use code style\n\n"
            "Try using these in your messages!"
        )
        
        tips_label = ctk.CTkLabel(
            tips_tab,
            text=tips_text,
            font=ctk.CTkFont(size=12),
            text_color="#ffffff",
            justify="left",
            wraplength=250
        )
        tips_label.pack(anchor="w", padx=20, pady=20)
        
        # Select first tab
        tabview.set("Shortcuts")
        
        # Initially hide the panel
        self.help_panel.place(x=-panel_width, y=0, relheight=1)
        
        # Store panel width for animations
        self.help_panel_width = panel_width

    def toggle_help_panel(self, event=None):
        """Toggle help panel visibility with animation"""
        if not self.help_panel_visible:
            self.show_help_panel()
        else:
            self.hide_help_panel()

    def show_help_panel(self):
        """Show help panel with sliding animation"""
        if not self.help_panel_visible:
            self.help_panel_visible = True
            self.help_panel.lift()
            
            # Animate panel sliding in
            for i in range(31):
                x = -self.help_panel_width + (i * 10)
                self.help_panel.place(x=x, y=0, relheight=1)
                self.update()
                self.after(1)  # Small delay for smooth animation

    def hide_help_panel(self, event=None):
        """Hide help panel with sliding animation"""
        if self.help_panel_visible:
            self.help_panel_visible = False
            
            # Animate panel sliding out
            for i in range(31):
                x = 0 - (i * 10)
                self.help_panel.place(x=x, y=0, relheight=1)
                self.update()
                self.after(1)  # Small delay for smooth animation
    
    def handle_load_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return
            
        threading.Thread(target=self.process_pdf, args=(file_path,), daemon=True).start()
    
    def process_pdf(self, file_path: str):
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Read PDF
            pdf_result = loop.run_until_complete(self.document_service.read_pdf(file_path))
            
            if pdf_result['status'] == 'success':
                self.post_message('chat', sender="System", message=f"PDF loaded: {os.path.basename(file_path)}")
                
                # Analyze content
                analysis = loop.run_until_complete(self.llm_service.analyze_document(pdf_result['content']))
                
                if analysis['status'] == 'success':
                    self.post_message('chat', sender="Assistant", message=analysis['message'])
                else:
                    self.post_message('chat', sender="System", message=f"Error analyzing PDF: {analysis['message']}")
            else:
                self.post_message('error', message=f"Failed to load PDF: {pdf_result['message']}")
                
        except Exception as e:
            self.post_message('error', message=f"Error processing PDF: {str(e)}")
        finally:
            loop.close()
    
    def handle_save_session(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
            
        threading.Thread(target=self.process_save, args=(file_path,), daemon=True).start()
    
    def process_save(self, file_path: str):
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.session_service.save_session(self.session_data, file_path))
            
            if result['status'] == 'success':
                self.post_message('info', message="Session saved successfully!")
            else:
                self.post_message('error', message=f"Failed to save session: {result['message']}")
                
        except Exception as e:
            self.post_message('error', message=f"Error saving session: {str(e)}")
        finally:
            loop.close()
    
    def clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.session_data = []
        
        # Add welcome message again
        self._add_chat_message("Assistant", "Starting a new chat session! How can I help you with your million dollars today?")
    
    def get_chat_history(self) -> str:
        return self.chat_display.get("1.0", "end-1c")
    
    def run(self):
        self.mainloop()
