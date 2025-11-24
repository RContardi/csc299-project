"""Tkinter GUI for the Task Manager application.

This module provides a graphical user interface for managing tasks using tkinter.
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Dict, Any
import re
import os
import json
from datetime import datetime, timezone
from PIL import Image, ImageTk

from task_manager import db as db_module
from task_manager.models import Task

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class TaskManagerGUI:
    """Main GUI window for the Task Manager."""

    def __init__(self, root: tk.Tk, db_path: str = "tasks.db"):
        """Initialize the Task Manager GUI.
        
        Args:
            root: The root tkinter window.
            db_path: Path to the SQLite database file.
        """
        self.root = root
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        db_module.initialize(self.conn)
        
        # Configure root window
        self.root.title("Stride - AI Task Manager")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        self.root.configure(bg='#e8f4f8')
        
        # Light blue/white theme styling with enhanced visuals
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#1e88e5', background='#e8f4f8')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12), foreground='#42a5f5', background='#e8f4f8')
        style.configure('TFrame', background='#e8f4f8')
        style.configure('TLabelframe', background='#ffffff', borderwidth=1, relief='solid', bordercolor='#bbdefb')
        style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground='#1e88e5', background='#ffffff')
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), background='#42a5f5', foreground='#ffffff', 
                       borderwidth=0, focuscolor='none', padding=(15, 8))
        style.map('TButton', background=[('active', '#1e88e5'), ('pressed', '#1565c0')])
        style.configure('Treeview', background='#ffffff', foreground='#263238', fieldbackground='#ffffff', 
                       font=('Segoe UI', 9), rowheight=28, borderwidth=0)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#bbdefb', 
                       foreground='#1565c0', borderwidth=1, relief='solid')
        style.map('Treeview.Heading', background=[('active', '#90caf9')])
        style.configure('TEntry', fieldbackground='#ffffff', borderwidth=1, relief='solid')
        
        # OpenAI setup
        self.openai_client = None
        self.use_ai = False
        api_key = os.environ.get("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_ai = True
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
        
        # Create UI components
        self._create_widgets()
        
        # Store task descriptions for popup
        self.task_descriptions_map = {}
        
        # Bind events
        self.task_tree.bind('<Double-Button-1>', self._on_task_double_click)
        self.task_tree.bind('<Button-1>', self._on_single_click)
        
        self._refresh_task_list()
        
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)  # Tasks area gets more space
        main_frame.columnconfigure(1, weight=2)  # Chat area gets less space
        main_frame.rowconfigure(1, weight=1)  # Row 1 contains the task list and chat
        
        # Title and statistics - centered
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 15))
        
        # Tasks title with icon
        tasks_title_container = ttk.Frame(title_frame, style='TFrame')
        tasks_title_container.pack()
        
        # Load and display tasks icon
        try:
            tasks_icon_path = os.path.join(os.path.dirname(__file__), 'tasks_icon.png')
            tasks_icon_image = Image.open(tasks_icon_path)
            
            # Crop to square from center to avoid squishing
            width, height = tasks_icon_image.size
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            tasks_icon_image = tasks_icon_image.crop((left, top, left + size, top + size))
            
            tasks_icon_image = tasks_icon_image.resize((35, 35), Image.Resampling.LANCZOS)
            self.tasks_icon_photo = ImageTk.PhotoImage(tasks_icon_image)
            tasks_icon_label = ttk.Label(tasks_title_container, image=self.tasks_icon_photo, background='#e8f4f8')
            tasks_icon_label.pack(side=tk.LEFT, padx=(0, 8))
        except Exception as e:
            print(f"Could not load tasks icon: {e}")
        
        title_label = ttk.Label(tasks_title_container, text="Tasks", 
                                style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Task statistics below title
        self.stats_label = ttk.Label(title_frame, text="Total: 0 | ✓ 0 | ☐ 0",
                                    font=('Segoe UI', 9), foreground='#64b5f6', background='#e8f4f8')
        self.stats_label.pack()
        
        # Chat title with logo
        chat_title_frame = ttk.Frame(main_frame, style='TFrame')
        chat_title_frame.grid(row=0, column=1, pady=(0, 15), padx=(10, 0))
        
        # Load and display logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'stride_logo.png')
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(chat_title_frame, image=self.logo_photo, background='#e8f4f8')
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        chat_title_label = ttk.Label(chat_title_frame, text="Stride", style='Title.TLabel')
        chat_title_label.pack(side=tk.LEFT)
        
        # Chat area section
        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding="10")
        chat_frame.grid(row=1, column=1, rowspan=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=(10, 0))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display area with enhanced styling
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, 
                                                      font=("Segoe UI", 10),
                                                      state=tk.DISABLED,
                                                      bg="#ffffff",
                                                      relief=tk.SOLID,
                                                      borderwidth=1,
                                                      highlightthickness=0,
                                                      padx=12, pady=12)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure chat tags for light blue/white theme
        self.chat_display.tag_config("user", foreground="#1e88e5", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="#039be5", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("system", foreground="#90a4ae", font=("Segoe UI", 9, "italic"))
        
        # Chat input area
        chat_input_frame = ttk.Frame(chat_frame)
        chat_input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        chat_input_frame.columnconfigure(0, weight=1)
        
        self.chat_entry = ttk.Entry(chat_input_frame, font=("Helvetica", 10))
        self.chat_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        chat_send_button = ttk.Button(chat_input_frame, text="Send", command=self._send_chat_message, width=10)
        chat_send_button.grid(row=0, column=1)
        
        # Bind Enter key for chat
        self.chat_entry.bind('<Return>', lambda e: self._send_chat_message())
        self.chat_entry.bind('<Up>', self._chat_history_up)
        self.chat_entry.bind('<Down>', self._chat_history_down)
        
        # Conversation history for context
        self.chat_history = []
        
        # Chat input history for up/down arrow navigation
        self.chat_input_history = []
        self.chat_history_index = -1
        
        # Add welcome message
        self._add_chat_message("system", "👋 Welcome to Stride! I'm your AI task assistant. Try: 'Add buy milk', 'Complete task 5', 'Edit task 3', or double-click any task to edit it. Use ↑/↓ arrows to recall previous messages.")
        
        # Task list section
        list_frame = ttk.LabelFrame(main_frame, text="Tasks", padding="10")
        list_frame.grid(row=1, column=0, rowspan=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for tasks
        columns = ("ID", "Status", "Title", "Action")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Action", text="")
        
        # Add scrollbar first
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Force GUI to calculate dimensions
        self.root.update_idletasks()
        
        # Now set column widths AFTER grid placement
        # All columns stretch=False to prevent ANY column from moving
        # Title width will be adjusted by resize handler to fill remaining space
        self.task_tree.column("ID", width=50, minwidth=50, anchor=tk.CENTER, stretch=False)
        self.task_tree.column("Status", width=130, minwidth=130, anchor=tk.CENTER, stretch=False)
        self.task_tree.column("Title", width=400, minwidth=200, anchor=tk.W, stretch=False)
        self.task_tree.column("Action", width=110, minwidth=110, anchor=tk.CENTER, stretch=False)
        
        # Store initial column configuration for resize handling
        self.initial_widths = {"ID": 40, "Status": 90, "Title": 270, "Description": 320}
        
        # Disable column resizing by binding to separator clicks and motion
        self.task_tree.bind('<Button-1>', self._prevent_column_resize, add='+')
        self.task_tree.bind('<B1-Motion>', self._prevent_column_resize, add='+')
        self.task_tree.bind('<Motion>', self._prevent_resize_cursor, add='+')
        
        # Bind window resize to adjust columns and rewrap text
        self.root.bind("<Configure>", self._on_window_resize)
        
        # Track last resize time to debounce refresh
        self.last_resize_time = 0
        
        # No status bar needed
    
    def _on_single_click(self, event):
        """Handle single click to detect View More button clicks."""
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.task_tree.identify_column(event.x)
            item = self.task_tree.identify_row(event.y)
            
            # Check if clicked on Action column (View More button)
            if column == "#4" and item:
                values = self.task_tree.item(item, 'values')
                if values and len(values) >= 1:
                    task_id = values[0]
                    self._show_description_popup(task_id)
                    return "break"
    
    def _show_description_popup(self, task_id):
        """Show popup window with full task description."""
        # Convert task_id to int since it comes as string from treeview
        try:
            task_id_int = int(task_id)
        except:
            task_id_int = task_id
        description = self.task_descriptions_map.get(task_id_int, "No Description.")
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Task {task_id} - Description")
        popup.geometry("500x300")
        popup.configure(bg='#ffffff')
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Title label
        title_label = tk.Label(popup, text=f"Task {task_id} Description", 
                               font=('Segoe UI', 12, 'bold'), 
                               bg='#ffffff', fg='#1e88e5')
        title_label.pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # Description text area
        text_frame = tk.Frame(popup, bg='#ffffff')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                font=('Segoe UI', 10),
                                                bg='#f5f5f5', relief=tk.SOLID,
                                                borderwidth=1, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, description)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=(0, 15))
    
    def _on_window_resize(self, event):
        """Adjust column widths proportionally when window is resized."""
        # Only handle resize events from the root window
        if event.widget != self.root:
            return
        
        # Get the current width of the task tree
        try:
            tree_width = self.task_tree.winfo_width()
            if tree_width < 100:  # Skip if tree hasn't been rendered yet
                return
            
            # Calculate available width (scrollbar is handled by tkinter, use full width)
            available_width = tree_width
            
            # Fixed widths for ID, Status, and Action columns
            id_width = 50
            status_width = 130  # Enough for "✓ Complete"
            action_width = 110  # Fixed width for View More button
            
            # Remaining width goes to Title
            remaining = available_width - id_width - status_width - action_width
            title_width = max(200, remaining)
            
            # Apply the new widths
            self.task_tree.column("ID", width=int(id_width))
            self.task_tree.column("Status", width=int(status_width))
            self.task_tree.column("Title", width=int(title_width))
            self.task_tree.column("Action", width=int(action_width))
        except:
            pass  # Ignore errors during initialization
    
    def _prevent_column_resize(self, event):
        """Prevent all column resizing to keep View More locked to the right."""
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "separator":
            return "break"  # Block all separator interactions
        
        # Also prevent resizing by checking if cursor is near column boundaries
        if region == "heading":
            column = self.task_tree.identify_column(event.x)
            bbox = self.task_tree.bbox(self.task_tree.get_children()[0] if self.task_tree.get_children() else "", column)
            if bbox:
                col_right = bbox[0] + bbox[2]
                # If within 5 pixels of right edge, block
                if abs(event.x - col_right) < 5:
                    return "break"
    
    def _prevent_resize_cursor(self, event):
        """Prevent resize cursor from appearing on column boundaries."""
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "separator":
            self.task_tree.config(cursor="arrow")
            return "break"
    
    def _on_column_click(self, event):
        """Prevent resizing the leftmost and rightmost edges."""
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "separator":
            column = self.task_tree.identify_column(event.x)
            # Block if trying to resize left of ID (column #1) or right of Description (column #4)
            if column == "#0" or column == "#4":
                return "break"
        return None
    
    def _on_column_drag(self, event):
        """Prevent dragging the leftmost and rightmost edges."""
        region = self.task_tree.identify_region(event.x, event.y)
        if region == "separator":
            column = self.task_tree.identify_column(event.x)
            if column == "#0" or column == "#4":
                return "break"
        return None
        
    def _chat_history_up(self, event):
        """Navigate up in chat input history."""
        if self.chat_input_history and self.chat_history_index < len(self.chat_input_history) - 1:
            self.chat_history_index += 1
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.insert(0, self.chat_input_history[-(self.chat_history_index + 1)])
    
    def _chat_history_down(self, event):
        """Navigate down in chat input history."""
        if self.chat_history_index > 0:
            self.chat_history_index -= 1
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.insert(0, self.chat_input_history[-(self.chat_history_index + 1)])
        elif self.chat_history_index == 0:
            self.chat_history_index = -1
            self.chat_entry.delete(0, tk.END)
    
    def _on_task_double_click(self, event):
        """Handle double-click on task to edit it."""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        # Get task details
        task_values = self.task_tree.item(selected[0])['values']
        task_id = task_values[0]
        task_title = task_values[2]
        # Get actual description from map instead of "View More"
        try:
            task_id_int = int(task_id)
        except:
            task_id_int = task_id
        task_description = self.task_descriptions_map.get(task_id_int, "")
        if task_description == "No Description.":
            task_description = ""
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Task {task_id}")
        edit_window.geometry("500x250")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Title
        ttk.Label(edit_window, text="Title:", font=('Segoe UI', 10)).pack(pady=(10, 5), padx=10, anchor=tk.W)
        title_entry = ttk.Entry(edit_window, font=('Segoe UI', 10), width=60)
        title_entry.insert(0, task_title)
        title_entry.pack(pady=(0, 10), padx=10)
        
        # Description
        ttk.Label(edit_window, text="Description (optional):", font=('Segoe UI', 10)).pack(pady=(5, 5), padx=10, anchor=tk.W)
        desc_text = tk.Text(edit_window, font=('Segoe UI', 10), height=5, width=60)
        desc_text.insert('1.0', task_description)
        desc_text.pack(pady=(0, 10), padx=10)
        
        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=10)
        
        def save_edit():
            new_title = title_entry.get().strip()
            new_desc = desc_text.get('1.0', tk.END).strip()
            
            if not new_title:
                return
            
            # Update in database
            try:
                cur = self.conn.cursor()
                cur.execute(
                    "UPDATE tasks SET title = ?, description = ? WHERE id = ?",
                    (new_title, new_desc if new_desc else None, task_id)
                )
                self.conn.commit()
                self._refresh_task_list()
                edit_window.destroy()
            except Exception as e:
                pass
        
        ttk.Button(button_frame, text="Save", command=save_edit, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        # Focus title entry
        title_entry.focus()
        title_entry.selection_range(0, tk.END)
    
    def _format_task_title(self, text: str) -> str:
        """Format task title with proper capitalization."""
        # Split into words
        words = text.split()
        
        # Capitalize first letter of each word, but preserve certain lowercase words
        lowercase_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
        
        formatted_words = []
        for i, word in enumerate(words):
            # Always capitalize first word
            if i == 0 or word.lower() not in lowercase_words:
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word.lower())
        
        return ' '.join(formatted_words)
    
    def _add_chat_message(self, role: str, message: str):
        """Add a message to the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        
        if role == "user":
            prefix = "You: "
            tag = "user"
        elif role == "assistant":
            prefix = "AI: "
            tag = "assistant"
        else:
            prefix = ""
            tag = "system"
        
        # Add message with proper formatting
        self.chat_display.insert(tk.END, prefix, tag)
        self.chat_display.insert(tk.END, message + "\n\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _send_chat_message(self):
        """Send a chat message to OpenAI and display the response."""
        message = self.chat_entry.get().strip()
        
        if not message:
            return
        
        # Store the original user request for verification
        self.current_user_request = message
        self.verification_attempts = 0
        self.max_verification_attempts = 10
        
        # Clear completed corrections for new request
        if hasattr(self, 'completed_corrections'):
            self.completed_corrections.clear()
        
        # Add to input history
        self.chat_input_history.append(message)
        self.chat_history_index = -1
        
        # Clear entry
        self.chat_entry.delete(0, tk.END)
        
        # Disable input while processing (after clearing)
        self.chat_entry.config(state=tk.DISABLED)
        
        # Add user message to display
        self._add_chat_message("user", message)
        
        # Show loading indicator
        self._add_chat_message("assistant", "⏳ Thinking...")
        self.root.update_idletasks()
        
        # Capture pre-action state (including completed/pending counts)
        pre_tasks = db_module.list_tasks(self.conn)
        self.pre_action_task_count = len(pre_tasks)
        self.pre_action_completed_count = sum(1 for t in pre_tasks if t.completed)
        self.pre_action_pending_count = self.pre_action_task_count - self.pre_action_completed_count
        
        # Immediate pre-refresh to show current state
        self._refresh_task_list()
        
        # Check if AI is available
        if not self.use_ai or not self.openai_client:
            self._add_chat_message("assistant", "OpenAI is not available. Please set your OPENAI_API_KEY environment variable.")
            return
        
        try:
            # ALWAYS get fresh current tasks for context (don't use cached data)
            self.conn.commit()  # Ensure any pending changes are committed
            tasks = db_module.list_tasks(self.conn)
            
            # Build detailed task summary with descriptions for better AI understanding
            # Reverse order to match task manager display (highest ID first)
            task_lines = []
            for t in reversed(tasks[:20]):  # Show up to 20 tasks, reversed
                status = '✓' if t.completed else '☐'
                desc = f" ({t.description[:30]}...)" if t.description and t.description != "No Description." else ""
                task_lines.append(f"- Task {t.id}: {status} {t.title}{desc}")
            
            tasks_summary = "\n".join(task_lines) if task_lines else "No tasks yet."
            
            # Build conversation with context and function calling
            tasks_list = tasks_summary
            
            # Add deleted tasks context with timestamps
            deleted_tasks = db_module.list_deleted_tasks(self.conn, limit=10)
            deleted_summary = ""
            if deleted_tasks:
                deleted_lines = []
                for dt in deleted_tasks:
                    deleted_id, title, desc, completed, deleted_at = dt
                    status = "✓" if completed else "☐"
                    # Parse ISO timestamp and make it readable
                    try:
                        from datetime import datetime
                        dt_obj = datetime.fromisoformat(deleted_at.replace('Z', '+00:00'))
                        time_str = dt_obj.strftime("%Y-%m-%d %I:%M %p")
                    except:
                        time_str = deleted_at
                    deleted_lines.append(f"- Deleted task #{deleted_id}: {status} {title} (deleted: {time_str})")
                deleted_summary = "\n\nRecently deleted tasks (can be restored):\n" + "\n".join(deleted_lines)
            
            system_message = """You are Stride, an AI assistant for a task manager. The user has these tasks:
""" + tasks_list + deleted_summary + """

CRITICAL RULES:
1. You MUST ALWAYS respond with JSON actions when the user wants to modify tasks
2. NEVER respond with just text like "All tasks have been removed" - you MUST provide the JSON actions
3. For "remove all tasks" you MUST create a delete action for EVERY single task ID shown above
4. For "complete all tasks" you MUST create a complete action for EVERY single task ID shown above
5. When user asks "show me my list" or "what tasks do I have", you MUST include the actual task list in your message, NOT just say "Done!"

REQUIRED FORMAT - When the user wants to manage tasks, you MUST respond with JSON actions:

For SINGLE actions:
{"action": "add or complete or uncomplete or delete or edit or search or list", "task_id": 5, "task_text": "text", "task_title": "title", "task_description": "desc", "search_query": "query", "message": "response"}

For MULTIPLE actions:
{"actions": [{"action": "complete", "task_id": 1}, {"action": "complete", "task_id": 2}], "message": "response"}

For ADDING TASKS - ALWAYS INCLUDE DESCRIPTIONS:
CRITICAL: When adding tasks, you MUST ALWAYS include a task_description that provides relevant details, context, or specifics.
NEVER add tasks without descriptions. Every task needs meaningful description text.

Single task with description:
{"action": "add", "task_text": "buy milk", "task_description": "get 2 percent from store", "message": "Added!"}

Multiple tasks (create separate action for EACH):
{"actions": [
  {"action": "add", "task_text": "attend morning lecture", "task_description": "8:00 AM - 10:00 AM"},
  {"action": "add", "task_text": "complete math homework", "task_description": "Chapter 3 exercises"},
  {"action": "add", "task_text": "study for midterm exam", "task_description": "Focus on chapters 1-5"}
], "message": "Added all tasks!"}

CRITICAL FOR BULK ADD: "add 20 random tasks" - You MUST create EXACTLY 20 separate action objects:
{"actions": [
  {"action": "add", "task_text": "attend morning lecture", "task_description": "Computer Science 101"},
  {"action": "add", "task_text": "complete math homework", "task_description": "Problems 1-20"},
  {"action": "add", "task_text": "study for midterm exam", "task_description": "Review chapters 1-5"},
  {"action": "add", "task_text": "go grocery shopping", "task_description": "Buy milk, eggs, bread"},
  {"action": "add", "task_text": "call dentist", "task_description": "Schedule 6-month checkup"},
  {"action": "add", "task_text": "walk the dog", "task_description": "30 minute walk in park"},
  {"action": "add", "task_text": "pay bills", "task_description": "Electricity and water"},
  {"action": "add", "task_text": "clean kitchen", "task_description": "Dishes and counters"},
  {"action": "add", "task_text": "read chapter 5", "task_description": "History textbook"},
  {"action": "add", "task_text": "practice piano", "task_description": "30 minutes scales"},
  ... (continue for ALL 20 tasks) ...
], "message": "Added 20 tasks!"}

NEVER respond with just "Added 20 tasks!" - you MUST provide all 20 action objects

For EDITING tasks - ALWAYS PERFORM THE ACTION, NEVER tell user to do it themselves:
- "edit task 5" or "change task 5's description" - you MUST create an edit action with appropriate changes: {"action": "edit", "task_id": 5, "task_description": "Updated description based on task", "message": "Task 5 updated!"}
- "change task 3 to buy groceries" gives: {"action": "edit", "task_id": 3, "task_title": "buy groceries", "message": "Updated!"}
- "add description to task 2: urgent" gives: {"action": "edit", "task_id": 2, "task_description": "urgent", "message": "Added description!"}
- "make task 6's description more detailed" gives: {"action": "edit", "task_id": 6, "task_description": "[create detailed description based on task title]", "message": "Task 6 description updated!"}
- "give all tasks descriptions" must edit EVERY task with appropriate descriptions based on the task title
CRITICAL: NEVER respond with "You can double-click" - YOU must perform the edit action yourself

For BULK operations:
- "remove all tasks" needs delete action for EVERY task ID - CRITICAL: ALWAYS check the current task list shown at the top of this message, even if you think tasks were already removed
- "complete all tasks" needs complete action for EVERY task ID  
- "uncomplete 3 tasks" means find 3 COMPLETED tasks and uncomplete them: {"actions": [{"action": "uncomplete", "task_id": X}, {"action": "uncomplete", "task_id": Y}, {"action": "uncomplete", "task_id": Z}], "message": "Uncompleted 3 tasks!"}
- "uncomplete 2 of the completed tasks" means find 2 tasks with ✓ and uncomplete them
- "check off tasks 1-5" gives: {"actions": [{"action": "complete", "task_id": 1}, {"action": "complete", "task_id": 2}, {"action": "complete", "task_id": 3}, {"action": "complete", "task_id": 4}, {"action": "complete", "task_id": 5}], "message": "Done!"}

CRITICAL: NEVER respond with just "Done!" or "All tasks have been removed!" without providing the actual JSON actions. If the current task list shows tasks exist, you MUST generate delete actions for them!

CRITICAL: When user says "uncomplete N tasks" or "uncomplete N of the completed tasks", you MUST:
1. Look at the task list above and identify which tasks have ✓ (completed)
2. Select exactly N completed tasks
3. Create an uncomplete action for EACH of those N tasks
4. Return ALL N actions in the actions array

For PROBABILISTIC operations:
- "give every task a 50% chance to be completed" means randomly select approximately 50% of all uncompleted tasks and complete them
- "give tasks a 30% chance to be deleted" means randomly select about 30% of tasks and delete them
- You CAN and SHOULD perform these operations by selecting the appropriate number of tasks

For DELETED TASKS and RESTORATION:
- When tasks are deleted, they are saved to a deleted_tasks history
- "what tasks were deleted" or "show deleted tasks": {"action": "list_deleted", "message": "Here are recently deleted tasks..."}
- "restore the last deleted task" or "bring back task X": {"action": "restore", "deleted_task_id": X, "message": "Restored!"}
- You can restore recently deleted tasks by their deleted_task_id
- Keep track of deleted tasks in conversation so you can restore them if asked

IMPORTANT: For "all" commands, generate an action for EVERY SINGLE task!

ALWAYS include JSON for task operations. For general chat, respond normally without JSON.

DELETED TASKS TRACKING:
- You have access to recently deleted tasks with their deletion timestamps
- When a user asks "what was deleted" or "what did I remove", refer to the deleted tasks list above
- You can see WHEN each task was deleted (date and time)
- Remember deleted tasks throughout the conversation to answer questions about them

CRITICAL RESPONSE RULES:
- NEVER show JSON, code, or technical formatting in your message to the user
- ALWAYS respond in natural, human-friendly language
- DO NOT include brackets, quotes, or action syntax in your visible message
- Keep responses conversational and friendly
- The "message" field should be what the user sees - make it sound natural!

IMPORTANT: The task list shown above is the CURRENT, UP-TO-DATE list. Always refer to these exact task IDs and titles when responding."""
            
            # Add message to history
            self.chat_history.append({"role": "user", "content": message})
            
            # Keep only last 6 messages for context window (more recent = better accuracy)
            recent_history = self.chat_history[-6:]
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    *recent_history
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            assistant_message = response.choices[0].message.content.strip()
            print(f"DEBUG: AI Response length: {len(assistant_message)} chars")
            print(f"DEBUG: AI Response: {assistant_message[:500]}...")
            
            # Check if response contains task actions (JSON)
            action_performed = False
            display_message = assistant_message
            action_results = []  # Track what actions were performed
            
            try:
                # Try to parse as JSON first
                if assistant_message.strip().startswith('{'):
                    try:
                        action_json = json.loads(assistant_message.strip())
                    except json.JSONDecodeError:
                        # Try to fix truncated JSON by adding closing braces
                        fixed_json = assistant_message.strip()
                        if not fixed_json.endswith('}'):
                            # Count unclosed braces and arrays
                            open_braces = fixed_json.count('{') - fixed_json.count('}')
                            open_brackets = fixed_json.count('[') - fixed_json.count(']')
                            fixed_json += ']' * open_brackets + '}' * open_braces
                        action_json = json.loads(fixed_json)
                    
                    # Handle multiple actions
                    if "actions" in action_json:
                        for action in action_json["actions"]:
                            try:
                                result = self._execute_task_action(action)
                                if result:
                                    action_performed = True
                                    action_results.append(result)
                            except Exception as e:
                                print(f"Action failed: {action}, error: {e}")
                        display_message = action_json.get("message", "Done!")
                    
                    # Handle single action
                    elif "action" in action_json:
                        result = self._execute_task_action(action_json)
                        if result:
                            action_performed = True
                            action_results.append(result)
                        display_message = action_json.get("message", "Done!")
                    
                # If not pure JSON, try to extract JSON from text
                else:
                    import re
                    # Look for JSON object
                    json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', assistant_message, re.DOTALL)
                    if json_match:
                        try:
                            action_json = json.loads(json_match.group())
                            
                            # Handle multiple actions
                            if "actions" in action_json:
                                for action in action_json["actions"]:
                                    try:
                                        result = self._execute_task_action(action)
                                        if result:
                                            action_performed = True
                                            action_results.append(result)
                                    except Exception as e:
                                        print(f"Action failed: {action}, error: {e}")
                                        action_results.append(f"failed: {action.get('task_id', '?')}")
                                display_message = action_json.get("message", assistant_message.replace(json_match.group(), "").strip() or "Done!")
                            
                            # Handle single action (doesn't skip refresh by default)
                            elif "action" in action_json:
                                result = self._execute_task_action(action_json)
                                if result:
                                    action_performed = True
                                    action_results.append(result)
                                display_message = action_json.get("message", assistant_message.replace(json_match.group(), "").strip() or "Done!")
                        except:
                            pass
                    
            except Exception as e:
                print(f"JSON parsing error: {e}")
            
            # Initialize action_counts outside the if block to avoid UnboundLocalError
            action_counts = {}
            
            # Add action summary if actions were performed (human-friendly format)
            if action_results:
                for result in action_results:
                    if result.startswith('failed'):
                        continue
                    action_type = result.split(':')[0]
                    action_counts[action_type] = action_counts.get(action_type, 0) + 1
                
                # Create human-friendly summary
                if action_counts:
                    summary_parts = []
                    for action_type, count in action_counts.items():
                        if action_type == "completed":
                            summary_parts.append(f"{count} task{'s' if count > 1 else ''} completed")
                        elif action_type == "uncompleted":
                            summary_parts.append(f"{count} task{'s' if count > 1 else ''} uncompleted")
                        elif action_type == "added":
                            summary_parts.append(f"{count} task{'s' if count > 1 else ''} added")
                        elif action_type == "edited":
                            summary_parts.append(f"{count} task{'s' if count > 1 else ''} edited")
                        elif action_type == "deleted":
                            summary_parts.append(f"{count} task{'s' if count > 1 else ''} deleted")
                        else:
                            summary_parts.append(f"{count} {action_type}")
                    
                    action_summary = ", ".join(summary_parts)
                    display_message = f"{display_message}\n\n📊 {action_summary.capitalize()}!"
            
            # Remove loading indicator by finding and deleting "Thinking..." message
            self.chat_display.config(state=tk.NORMAL)
            chat_content = self.chat_display.get("1.0", tk.END)
            if "⏳ Thinking..." in chat_content:
                # Find the line with Thinking and delete it
                start_idx = self.chat_display.search("⏳ Thinking...", "1.0", tk.END)
                if start_idx:
                    # Delete from "AI: " to the end of the line including newlines
                    line_start = f"{start_idx} linestart"
                    line_end = f"{start_idx} lineend + 2 chars"  # Include both newlines
                    self.chat_display.delete(line_start, line_end)
            self.chat_display.config(state=tk.DISABLED)
            
            # Strip any remaining JSON from display message
            import re
            clean_message = re.sub(r'\{[^}]*"action"[^}]*\}', '', display_message)
            clean_message = re.sub(r'\{"actions":[^}]*\}', '', clean_message)
            clean_message = clean_message.strip()
            if not clean_message:
                clean_message = "Done!"
            
            # Add to chat history
            self.chat_history.append({"role": "assistant", "content": clean_message})
            
            # Update AI context IMMEDIATELY after actions but before displaying response
            if action_performed:
                try:
                    fresh_tasks = db_module.list_tasks(self.conn)
                    deleted_tasks = db_module.list_deleted_tasks(self.conn, limit=5)
                    
                    context_update = "\n[Current task list after actions]:\n"
                    if not fresh_tasks:
                        context_update += "No tasks in the list.\n"
                    else:
                        # Reverse to match task manager display (highest ID first)
                        for t in reversed(fresh_tasks):
                            status = "✓" if t.completed else "☐"
                            desc_preview = f" - {t.description[:50]}..." if t.description else ""
                            context_update += f"Task {t.id}: {status} {t.title}{desc_preview}\n"
                    
                    if deleted_tasks:
                        context_update += "\n[Recently deleted tasks (can be restored)]:\n"
                        for dt in deleted_tasks:
                            deleted_id, title, desc, completed, deleted_at = dt
                            status = "✓" if completed else "☐"
                            # Parse ISO timestamp and make it readable
                            try:
                                from datetime import datetime
                                dt_obj = datetime.fromisoformat(deleted_at.replace('Z', '+00:00'))
                                time_str = dt_obj.strftime("%Y-%m-%d %I:%M %p")
                            except:
                                time_str = deleted_at
                            context_update += f"Deleted task #{deleted_id}: {status} {title} (deleted: {time_str})\n"
                    
                    # Add to chat history so AI knows current state for NEXT interaction
                    self.chat_history.append({"role": "system", "content": context_update})
                    print(f"DEBUG: AI context updated IMMEDIATELY with {len(fresh_tasks)} tasks, {len(deleted_tasks)} deleted")
                except Exception as e:
                    print(f"Context update error: {e}")
            
            self._add_chat_message("assistant", clean_message)
            
            # Store action results and AI message for verification
            self.last_action_results = action_results
            self.last_action_counts = action_counts if action_results else {}
            self.last_ai_message = clean_message
            
            # Verify AI message matches action results
            message_mismatch = self._detect_message_action_mismatch(clean_message, action_counts)
            if message_mismatch:
                print(f"WARNING: AI message doesn't match action results: {message_mismatch}")
                # Store mismatch for verification to handle
                self.detected_mismatch = message_mismatch
            else:
                self.detected_mismatch = None
            
            # Always refresh after AI response to ensure sync
            print(f"DEBUG: action_performed={action_performed}, action_results={len(action_results)}")
            # Immediate synchronous refresh
            self._refresh_task_list()
            
            # Additional delayed refreshes to catch any timing issues
            self.root.after(50, self._refresh_task_list)
            self.root.after(200, self._refresh_task_list)
            self.root.after(500, self._refresh_task_list)
            self.root.after(800, self._refresh_task_list)
            
            # Check if user's request was an action request (even if no JSON was generated)
            # This handles cases where AI responds with text like "Done!" without actions
            request_lower = message.lower()
            is_action_request = any(phrase in request_lower for phrase in [
                "remove", "delete", "complete", "uncomplete", "add", "edit", "clear"
            ])
            
            # Force verification if it was an action request, even if no actions were performed
            should_verify = action_performed or is_action_request
            
            # Verify and re-enable input after all updates complete
            self.root.after(1200, lambda: self._verify_and_enable_input(should_verify))
            
        except Exception as e:
            error_msg = f"Error communicating with AI: {str(e)}"
            self._add_chat_message("assistant", error_msg)
            # Re-enable input on error
            self.chat_entry.config(state=tk.NORMAL)
    
    def _detect_message_action_mismatch(self, ai_message: str, action_counts: dict) -> str:
        """Detect if AI's message claims don't match actual action results."""
        import re
        
        # Extract numbers from AI message for different action types
        message_lower = ai_message.lower()
        
        # Check for "Added X tasks"
        added_match = re.search(r'(?:added|created)\s+(\d+)\s+task', message_lower)
        if added_match:
            claimed_added = int(added_match.group(1))
            actual_added = action_counts.get('added', 0)
            if claimed_added != actual_added:
                return f"AI claimed {claimed_added} tasks added, but actually added {actual_added}"
        
        # Check for "Removed/Deleted X tasks"
        removed_match = re.search(r'(?:removed|deleted)\s+(\d+)\s+task', message_lower)
        if removed_match:
            claimed_removed = int(removed_match.group(1))
            actual_removed = action_counts.get('deleted', 0)
            if claimed_removed != actual_removed:
                return f"AI claimed {claimed_removed} tasks removed, but actually removed {actual_removed}"
        
        # Check for "Completed X tasks"
        completed_match = re.search(r'(?:completed|done)\s+(\d+)\s+task', message_lower)
        if completed_match:
            claimed_completed = int(completed_match.group(1))
            actual_completed = action_counts.get('completed', 0)
            if claimed_completed != actual_completed:
                return f"AI claimed {claimed_completed} tasks completed, but actually completed {actual_completed}"
        
        # Check for "all tasks" claims
        if re.search(r'all tasks.*(?:removed|deleted)', message_lower):
            actual_removed = action_counts.get('deleted', 0)
            if actual_removed == 0:
                return f"AI claimed all tasks removed, but no deletions occurred"
        
        return ""  # No mismatch detected
    
    def _verify_and_enable_input(self, action_was_performed: bool):
        """Comprehensive verification: user request fulfilled, GUI/AI synced, display updated."""
        try:
            self.verification_attempts += 1
            
            if not action_was_performed:
                # No actions performed, just re-enable
                self.chat_entry.delete(0, tk.END)
                self.chat_entry.config(state=tk.NORMAL)
                return
            
            # RULE 3: Ensure visual updates are complete
            self._refresh_task_list()
            self.root.update_idletasks()
            
            # Get current database state
            current_tasks = db_module.list_tasks(self.conn)
            actual_task_count = len(current_tasks)
            
            # RULE 2: Get what the AI thinks exists from last context update
            expected_task_count = 0
            ai_task_ids = set()
            for msg in reversed(self.chat_history):
                if msg.get("role") == "system" and "[Current task list after actions]" in msg.get("content", ""):
                    content = msg.get("content", "")
                    if "No tasks in the list" in content:
                        expected_task_count = 0
                        ai_task_ids = set()
                    else:
                        # Extract task IDs from context
                        import re
                        task_matches = re.findall(r'Task (\d+):', content)
                        ai_task_ids = set(int(tid) for tid in task_matches)
                        expected_task_count = len(ai_task_ids)
                    break
            
            # Get actual task IDs from database
            actual_task_ids = set(t.id for t in current_tasks)
            
            print(f"DEBUG: Verification attempt {self.verification_attempts}")
            print(f"  Expected count: {expected_task_count}, Actual count: {actual_task_count}")
            print(f"  AI knows: {sorted(ai_task_ids)}, DB has: {sorted(actual_task_ids)}")
            
            # Check for AI message vs action mismatch
            has_mismatch = hasattr(self, 'detected_mismatch') and self.detected_mismatch
            if has_mismatch:
                print(f"  MESSAGE MISMATCH: {self.detected_mismatch}")
            
            # RULE 1: Check if user request was fulfilled
            request_fulfilled = self._check_request_fulfilled(
                self.current_user_request, 
                self.pre_action_task_count,
                actual_task_count,
                current_tasks
            )
            
            # RULE 2: Check if AI and DB match
            lists_match = (expected_task_count == actual_task_count and ai_task_ids == actual_task_ids)
            
            print(f"  Request fulfilled: {request_fulfilled}, Lists match: {lists_match}")
            
            # If verification fails (including message mismatch) and we haven't hit max attempts, try to fix it
            if (not request_fulfilled or not lists_match or has_mismatch) and self.verification_attempts < self.max_verification_attempts:
                print(f"WARNING: Verification failed! Attempting auto-correction...")
                
                # Force a sync by running the action again if needed
                if not lists_match:
                    # Update AI context with correct current state
                    self._force_context_sync()
                
                # If request still not fulfilled, generate corrective actions
                if not request_fulfilled:
                    self._generate_corrective_action()
                    return  # Will re-verify after corrective action
                
                # Schedule another verification
                self.root.after(800, lambda: self._verify_and_enable_input(True))
                return
            
            # If we hit max attempts, log warning but re-enable
            if self.verification_attempts >= self.max_verification_attempts:
                print(f"WARNING: Max verification attempts reached. Force re-enabling input.")
            
            # AFTER request is fulfilled, check if IDs need reordering (only once)
            if request_fulfilled and lists_match and not has_mismatch:
                if len(current_tasks) > 1:
                    task_ids = [t.id for t in current_tasks]
                    sorted_ids = sorted(task_ids)
                    if task_ids != sorted_ids:
                        print(f"DEBUG: IDs out of order {task_ids}, fixing to {sorted_ids}")
                        self._fix_task_id_order()
                        self._refresh_task_list()
                        self._force_context_sync()
            
            # All checks passed or max attempts reached
            # Force final refresh and sync to ensure GUI and AI context are aligned
            self._refresh_task_list()
            self._force_context_sync()
            
            # Clear and re-enable input
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.config(state=tk.NORMAL)
            print("DEBUG: Verification complete, input re-enabled")
            
        except Exception as e:
            print(f"Verification error: {e}")
            import traceback
            traceback.print_exc()
            # On error, re-enable to avoid locking the user out
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.config(state=tk.NORMAL)
    
    def _check_request_fulfilled(self, request: str, pre_count: int, post_count: int, current_tasks: list) -> bool:
        """Check if user's request has been fulfilled based on task state changes."""
        request_lower = request.lower()
        import re
        
        # Store pre-action state for fractional checks
        if not hasattr(self, 'pre_action_completed_count'):
            self.pre_action_completed_count = 0
        if not hasattr(self, 'pre_action_pending_count'):
            self.pre_action_pending_count = 0
        
        # Get action results for detailed verification
        action_results = getattr(self, 'last_action_results', [])
        action_counts = getattr(self, 'last_action_counts', {})
        
        # Check if specific task ID was requested
        task_id_match = re.search(r'(?:remove|delete|complete|uncomplete|edit).*?task\s*(\d+)', request_lower)
        if task_id_match:
            requested_id = int(task_id_match.group(1))
            
            if any(word in request_lower for word in ['remove', 'delete']):
                # If a delete action was performed, check if the TOTAL count decreased
                # Don't check if the specific ID still exists because IDs get renumbered
                if action_counts.get('deleted', 0) > 0:
                    # Action was performed, task was deleted, we're good
                    return True
                
                # No delete action was performed, check if task still exists
                task_still_exists = any(t.id == requested_id for t in current_tasks)
                if task_still_exists:
                    print(f"ERROR: Task {requested_id} still exists after removal request")
                    return False
            elif 'complete' in request_lower and 'uncomplete' not in request_lower:
                # Task should exist and be completed
                task = next((t for t in current_tasks if t.id == requested_id), None)
                if not task or not task.completed:
                    print(f"ERROR: Task {requested_id} not completed as requested")
                    return False
            elif 'uncomplete' in request_lower:
                # Task should exist and be pending
                task = next((t for t in current_tasks if t.id == requested_id), None)
                if not task or task.completed:
                    print(f"ERROR: Task {requested_id} not uncompleted as requested")
                    return False
        
        # Check "remove any X tasks" - verify actual count matches requested count
        # BUT NOT "remove any X completed tasks" or "remove any X pending tasks"
        any_match = re.search(r'(?:remove|delete)\s+any\s+(\d+)(?:\s+tasks?)?$', request_lower)
        # Make sure it's not "remove any X completed" or "remove any X pending"
        if any_match and 'completed' not in request_lower and 'pending' not in request_lower and 'done' not in request_lower:
            requested_count = int(any_match.group(1))
            actual_deleted = action_counts.get('deleted', 0)
            if actual_deleted != requested_count:
                print(f"ERROR: Requested {requested_count} deletions, but only {actual_deleted} were deleted")
                return False
            # Also verify the count change matches
            if pre_count - post_count != requested_count:
                print(f"ERROR: Task count should have decreased by {requested_count}, but decreased by {pre_count - post_count}")
                return False
        
        # Check "remove all" / "delete all" (but NOT "remove all completed")
        if any(phrase in request_lower for phrase in ["remove all", "delete all", "clear all"]):
            # But NOT if it says "remove all completed" - that's handled separately
            if "completed" not in request_lower and "done" not in request_lower:
                if post_count > 0:
                    print(f"ERROR: Still have {post_count} tasks after 'remove all'")
                return post_count == 0
        
        # Check "remove all completed tasks" / "delete all completed"
        if re.search(r'(?:remove|delete)\s+all\s+(?:completed|done)', request_lower):
            # All completed tasks should be removed, but pending tasks should remain
            completed_count = sum(1 for t in current_tasks if t.completed)
            pending_count = sum(1 for t in current_tasks if not t.completed)
            # Should have 0 completed and original pending count
            if completed_count > 0:
                print(f"ERROR: Still have {completed_count} completed tasks after 'remove all completed'")
                return False
            if pending_count != self.pre_action_pending_count:
                print(f"ERROR: Pending count changed from {self.pre_action_pending_count} to {pending_count}, should be unchanged")
                return False
            return True
        
        # Check "remove half of the completed tasks" / "delete half of completed"
        if re.search(r'(?:remove|delete).*half.*(?:completed|done)', request_lower):
            if self.pre_action_completed_count == 0:
                return True  # No completed tasks to remove
            expected_remaining_completed = self.pre_action_completed_count // 2
            actual_completed = sum(1 for t in current_tasks if t.completed)
            # Allow some tolerance (within 1 task)
            return abs(actual_completed - expected_remaining_completed) <= 1
        
        # Check "remove half of the tasks" / "delete 50% of tasks"
        if re.search(r'(?:remove|delete).*(?:half|50%)', request_lower) and 'completed' not in request_lower:
            expected_remaining = pre_count // 2
            # Allow some tolerance
            return abs(post_count - expected_remaining) <= 1
        
        # Check "remove X% of tasks"
        percent_match = re.search(r'(?:remove|delete).*?(\d+)%', request_lower)
        if percent_match:
            percentage = int(percent_match.group(1))
            expected_remove = int(pre_count * percentage / 100)
            expected_remaining = pre_count - expected_remove
            # Allow tolerance of 1 task
            return abs(post_count - expected_remaining) <= 1
        
        # Check "add X tasks" / "add X random tasks"
        add_match = re.search(r'add (\d+)', request_lower)
        if add_match:
            expected_add = int(add_match.group(1))
            return post_count >= pre_count + expected_add
        
        # Check "remove X tasks" / "delete X tasks"
        remove_match = re.search(r'(?:remove|delete) (\d+)', request_lower)
        if remove_match:
            expected_remove = int(remove_match.group(1))
            return post_count <= pre_count - expected_remove
        
        # Check "complete all"
        if "complete all" in request_lower:
            return all(t.completed for t in current_tasks)
        
        # Check "uncomplete all"
        if "uncomplete all" in request_lower or "incomplete all" in request_lower:
            return all(not t.completed for t in current_tasks)
        
        # Check "complete X tasks"
        complete_match = re.search(r'complete (\d+)', request_lower)
        if complete_match:
            expected_complete = int(complete_match.group(1))
            completed_count = sum(1 for t in current_tasks if t.completed)
            return completed_count >= expected_complete
        
        # Check "uncomplete X tasks" / "uncomplete X of the completed"
        uncomplete_match = re.search(r'uncomplete (\d+)', request_lower)
        if uncomplete_match:
            expected_uncomplete = int(uncomplete_match.group(1))
            # Check that at least X tasks were changed from completed to pending
            completed_count = sum(1 for t in current_tasks if t.completed)
            expected_completed = self.pre_action_completed_count - expected_uncomplete
            return abs(completed_count - expected_completed) <= 1
        
        # If we can't determine, assume it's fulfilled (non-modifying request)
        return True
    
    def _fix_task_id_order(self):
        """Fix task IDs to be in sequential order."""
        try:
            cur = self.conn.cursor()
            
            # Get all tasks ordered by ID
            tasks = db_module.list_tasks(self.conn)
            
            # Sort by ID to maintain relative order
            tasks_sorted = sorted(tasks, key=lambda t: t.id)
            
            # Drop temp table if it exists from previous run
            cur.execute("DROP TABLE IF EXISTS tasks_reorder")
            
            # Create a temporary table to hold the reordered tasks
            cur.execute("""
                CREATE TEMPORARY TABLE tasks_reorder (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Copy tasks with new sequential IDs (1, 2, 3, ...)
            for new_id, task in enumerate(tasks_sorted, start=1):
                cur.execute("""
                    INSERT INTO tasks_reorder (id, title, description, completed, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (new_id, task.title, task.description, task.completed, task.created_at))
            
            # Replace original tasks table
            cur.execute("DELETE FROM tasks")
            cur.execute("""
                INSERT INTO tasks (id, title, description, completed, created_at)
                SELECT id, title, description, completed, created_at FROM tasks_reorder
            """)
            cur.execute("DROP TABLE tasks_reorder")
            
            self.conn.commit()
            print(f"DEBUG: Fixed task ID order - reordered {len(tasks)} tasks to IDs 1-{len(tasks)}")
            
        except Exception as e:
            print(f"Error fixing task ID order: {e}")
            import traceback
            traceback.print_exc()
    
    def _force_context_sync(self):
        """Force AI context to sync with actual database state."""
        try:
            fresh_tasks = db_module.list_tasks(self.conn)
            deleted_tasks = db_module.list_deleted_tasks(self.conn, limit=5)
            
            context_update = "\n[FORCED SYNC - Current task list]:\n"
            if not fresh_tasks:
                context_update += "No tasks in the list.\n"
            else:
                for t in reversed(fresh_tasks):
                    status = "✓" if t.completed else "☐"
                    desc_preview = f" - {t.description[:50]}..." if t.description else ""
                    context_update += f"Task {t.id}: {status} {t.title}{desc_preview}\n"
            
            if deleted_tasks:
                context_update += "\n[Recently deleted tasks (can be restored)]:\n"
                for dt in deleted_tasks:
                    deleted_id, title, desc, completed, deleted_at = dt
                    status = "✓" if completed else "☐"
                    # Parse ISO timestamp and make it readable
                    try:
                        from datetime import datetime
                        dt_obj = datetime.fromisoformat(deleted_at.replace('Z', '+00:00'))
                        time_str = dt_obj.strftime("%Y-%m-%d %I:%M %p")
                    except:
                        time_str = deleted_at
                    context_update += f"Deleted task #{deleted_id}: {status} {title} (deleted: {time_str})\n"
            
            # Replace the last system message or add new one
            self.chat_history.append({"role": "system", "content": context_update})
            print(f"DEBUG: Forced context sync - {len(fresh_tasks)} tasks")
        except Exception as e:
            print(f"Force sync error: {e}")
    
    def _generate_corrective_action(self):
        """Generate and execute corrective action to fulfill user request."""
        print(f"DEBUG: Generating corrective action for: '{self.current_user_request}'")
        
        try:
            # Get current state
            current_tasks = db_module.list_tasks(self.conn)
            request_lower = self.current_user_request.lower()
            import re
            
            # Check if there's a detected message/action mismatch to fix
            if hasattr(self, 'detected_mismatch') and self.detected_mismatch:
                mismatch = self.detected_mismatch
                print(f"DEBUG: Fixing message/action mismatch: {mismatch}")
                
                # Extract the shortfall from the mismatch message
                # e.g., "AI claimed 25 tasks added, but actually added 24"
                if "claimed" in mismatch and "but actually" in mismatch:
                    numbers = re.findall(r'\d+', mismatch)
                    if len(numbers) >= 2:
                        claimed = int(numbers[0])
                        actual = int(numbers[1])
                        shortfall = claimed - actual
                        
                        if "added" in mismatch and shortfall > 0:
                            # Need to add more tasks
                            print(f"DEBUG: Adding {shortfall} more task(s) to match AI claim")
                            for i in range(shortfall):
                                db_module.add_task(self.conn, f"Corrective Task {i+1}", "Auto-added to match count")
                            
                            self._refresh_task_list()
                            self._force_context_sync()
                            self._add_chat_message("assistant", f"✓ Corrected: Added {shortfall} more task(s) to match claim of {claimed}")
                            self.root.after(800, lambda: self._verify_and_enable_input(True))
                            return
                        
                        elif "removed" in mismatch or "deleted" in mismatch:
                            if shortfall > 0:
                                # Need to remove more tasks
                                print(f"DEBUG: Removing {shortfall} more task(s) to match AI claim")
                                for i, task in enumerate(current_tasks):
                                    if i >= shortfall:
                                        break
                                    db_module.delete_task(self.conn, task.id)
                                
                                self._refresh_task_list()
                                self._force_context_sync()
                                self._add_chat_message("assistant", f"✓ Corrected: Removed {shortfall} more task(s) to match claim of {claimed}")
                                self.root.after(800, lambda: self._verify_and_enable_input(True))
                                return
            
            # Handle specific task ID requests (e.g., "remove task7")
            # BUT only if no deletion action was already performed AND we haven't done this corrective action before
            task_id_match = re.search(r'(?:remove|delete|complete|uncomplete).*?task\s*(\d+)', request_lower)
            if task_id_match:
                requested_id = int(task_id_match.group(1))
                
                if any(word in request_lower for word in ['remove', 'delete']):
                    # Check if we've already done a corrective deletion for this request
                    corrective_key = f"corrective_delete_{requested_id}_{self.current_user_request}"
                    if hasattr(self, 'completed_corrections') and corrective_key in self.completed_corrections:
                        print(f"DEBUG: Already did corrective deletion for task {requested_id}, stopping")
                        return
                    
                    # Check if a deletion was already performed in the original action
                    action_counts = getattr(self, 'last_action_counts', {})
                    if action_counts.get('deleted', 0) > 0:
                        # Task was already deleted in original action, don't do it again
                        print(f"DEBUG: Task {requested_id} was already deleted in original action, skipping corrective action")
                        return
                    
                    # No deletion performed yet, check if task exists and remove it
                    task_exists = any(t.id == requested_id for t in current_tasks)
                    if task_exists:
                        print(f"DEBUG: Corrective action - deleting task {requested_id}")
                        
                        # Mark this corrective action as done
                        if not hasattr(self, 'completed_corrections'):
                            self.completed_corrections = set()
                        self.completed_corrections.add(corrective_key)
                        
                        db_module.delete_task(self.conn, requested_id)
                        
                        # Refresh and update context
                        self._refresh_task_list()
                        self._force_context_sync()
                        
                        # Add corrective message
                        self._add_chat_message("assistant", f"✓ Corrected: Removed task {requested_id}")
                        
                        # Re-verify ONE more time, then stop
                        self.root.after(800, lambda: self._verify_and_enable_input(True))
                        return
            
            # Handle "remove any X tasks" - if not enough were removed
            # BUT NOT "remove any X completed" or "remove any X pending"
            any_match = re.search(r'(?:remove|delete)\s+any\s+(\d+)(?:\s+tasks?)?$', request_lower)
            if any_match and 'completed' not in request_lower and 'pending' not in request_lower and 'done' not in request_lower:
                requested_count = int(any_match.group(1))
                actual_removed = self.pre_action_task_count - len(current_tasks)
                
                if actual_removed < requested_count:
                    # Need to remove more
                    to_remove = requested_count - actual_removed
                    print(f"DEBUG: Corrective action - removing {to_remove} more tasks")
                    
                    for i, task in enumerate(current_tasks):
                        if i >= to_remove:
                            break
                        db_module.delete_task(self.conn, task.id)
                    
                    # Refresh and update context
                    self._refresh_task_list()
                    self._force_context_sync()
                    
                    # Add corrective message
                    self._add_chat_message("assistant", f"✓ Corrected: Removed {to_remove} more task(s) to reach {requested_count} total")
                    
                    # Re-verify
                    self.root.after(800, lambda: self._verify_and_enable_input(True))
                    return
            
            # Handle "remove all completed" specifically
            if re.search(r'(?:remove|delete)\s+all\s+(?:completed|done)', request_lower):
                # Should only remove completed tasks, restore any pending tasks that were deleted
                completed_tasks = [t for t in current_tasks if t.completed]
                pending_tasks = [t for t in current_tasks if not t.completed]
                
                # If there are completed tasks remaining, remove them
                if len(completed_tasks) > 0:
                    print(f"DEBUG: Corrective action - removing {len(completed_tasks)} completed tasks")
                    for task in completed_tasks:
                        db_module.delete_task(self.conn, task.id)
                
                # If pending count is less than pre-action pending count, restore from deleted_tasks
                if len(pending_tasks) < self.pre_action_pending_count:
                    missing_count = self.pre_action_pending_count - len(pending_tasks)
                    print(f"DEBUG: Corrective action - need to restore {missing_count} pending tasks that were accidentally deleted")
                    
                    # Get recently deleted tasks
                    deleted_tasks = db_module.list_deleted_tasks(self.conn, limit=20)
                    restored = 0
                    
                    # Restore ALL pending tasks that were deleted (not just missing_count)
                    for dt in deleted_tasks:
                        deleted_id, title, desc, completed, deleted_at = dt[0], dt[1], dt[2], dt[3], dt[4]
                        # Only restore if it was pending (not completed)
                        if not completed:
                            db_module.restore_deleted_task(self.conn, deleted_id)
                            restored += 1
                            print(f"DEBUG: Restored task: {title}")
                            if restored >= missing_count:
                                break
                    
                    if restored > 0:
                        self._refresh_task_list()
                        self._force_context_sync()
                        self._add_chat_message("assistant", f"✓ Corrected: Restored {restored} pending task(s) that were accidentally deleted")
                        self.root.after(800, lambda: self._verify_and_enable_input(True))
                        return
                
                # Refresh if we made any changes
                self._refresh_task_list()
                self._force_context_sync()
                if len(completed_tasks) > 0:
                    self._add_chat_message("assistant", f"✓ Corrected: Removed {len(completed_tasks)} completed task(s)")
                self.root.after(800, lambda: self._verify_and_enable_input(True))
                return
            
            # Handle "remove all" specifically (remove everything)
            if any(phrase in request_lower for phrase in ["remove all", "delete all", "clear all"]):
                # But NOT if it says "completed" or "done"
                if "completed" not in request_lower and "done" not in request_lower and len(current_tasks) > 0:
                    print(f"DEBUG: Corrective action - deleting remaining {len(current_tasks)} tasks")
                    for task in current_tasks:
                        db_module.delete_task(self.conn, task.id)
                    
                    # Refresh and update context
                    self._refresh_task_list()
                    self._force_context_sync()
                    
                    # Add corrective message
                    self._add_chat_message("assistant", f"✓ Corrected: Removed remaining {len(current_tasks)} task(s)")
                    
                    # Re-verify
                    self.root.after(800, lambda: self._verify_and_enable_input(True))
                    return
            
            # Handle "remove half of the completed tasks"
            if re.search(r'(?:remove|delete).*half.*(?:completed|done)', request_lower):
                completed_tasks = [t for t in current_tasks if t.completed]
                target_completed = self.pre_action_completed_count // 2
                current_completed = len(completed_tasks)
                
                if current_completed > target_completed:
                    # Need to remove more completed tasks
                    to_remove = current_completed - target_completed
                    print(f"DEBUG: Corrective action - removing {to_remove} more completed tasks")
                    
                    for i, task in enumerate(completed_tasks):
                        if i >= to_remove:
                            break
                        db_module.delete_task(self.conn, task.id)
                    
                    # Refresh and update context
                    self._refresh_task_list()
                    self._force_context_sync()
                    
                    # Add corrective message
                    self._add_chat_message("assistant", f"✓ Corrected: Removed {to_remove} more completed task(s)")
                    
                    # Re-verify
                    self.root.after(800, lambda: self._verify_and_enable_input(True))
                    return
            
            # Handle "remove half of tasks" or percentage-based removals
            if re.search(r'(?:remove|delete).*(?:half|50%|\d+%)', request_lower):
                # Calculate how many should remain
                if 'half' in request_lower or '50%' in request_lower:
                    target_remaining = self.pre_action_task_count // 2
                else:
                    percent_match = re.search(r'(\d+)%', request_lower)
                    if percent_match:
                        percentage = int(percent_match.group(1))
                        to_remove = int(self.pre_action_task_count * percentage / 100)
                        target_remaining = self.pre_action_task_count - to_remove
                    else:
                        target_remaining = len(current_tasks)  # No change
                
                current_count = len(current_tasks)
                if current_count > target_remaining:
                    # Need to remove more tasks
                    to_remove = current_count - target_remaining
                    print(f"DEBUG: Corrective action - removing {to_remove} more tasks")
                    
                    for i, task in enumerate(current_tasks):
                        if i >= to_remove:
                            break
                        db_module.delete_task(self.conn, task.id)
                    
                    # Refresh and update context
                    self._refresh_task_list()
                    self._force_context_sync()
                    
                    # Add corrective message
                    self._add_chat_message("assistant", f"✓ Corrected: Removed {to_remove} more task(s)")
                    
                    # Re-verify
                    self.root.after(800, lambda: self._verify_and_enable_input(True))
                    return
            
            # For other cases, just do another verification
            self.root.after(500, lambda: self._verify_and_enable_input(True))
            
        except Exception as e:
            print(f"Corrective action error: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(500, lambda: self._verify_and_enable_input(True))
    
    def _execute_task_action(self, action: Dict[str, Any]) -> str:
        """Execute a task action from AI and return description of what was done."""
        try:
            action_type = action.get("action")
            
            if action_type == "add":
                task_text = action.get("task_text", "")
                task_desc = action.get("task_description")
                target_id = action.get("task_id")  # Optional: insert at specific ID
                
                if task_text:
                    # Apply title case formatting
                    task_text = self._format_task_title(task_text)
                    
                    if target_id:
                        # Insert at specific ID by shifting existing tasks
                        cur = self.conn.cursor()
                        # Shift all tasks with id >= target_id up by 1
                        cur.execute("UPDATE tasks SET id = id + 1 WHERE id >= ? ORDER BY id DESC", (target_id,))
                        # Insert new task at target_id
                        now = datetime.now(timezone.utc).isoformat()
                        cur.execute("INSERT INTO tasks (id, title, description, completed, created_at) VALUES (?, ?, ?, 0, ?)",
                                  (target_id, task_text, task_desc, now))
                        self.conn.commit()
                        return f"added: '{task_text}' at position {target_id}"
                    else:
                        # Normal append at end
                        task = db_module.add_task(self.conn, task_text, task_desc)
                        return f"added: '{task_text}'"
            
            elif action_type == "edit":
                task_id = action.get("task_id")
                task_title = action.get("task_title")
                task_desc = action.get("task_description")
                
                if task_id:
                    cur = self.conn.cursor()
                    # Handle both title and description updates
                    if task_title and task_desc is not None:
                        task_title = self._format_task_title(task_title)
                        cur.execute("UPDATE tasks SET title = ?, description = ? WHERE id = ?", 
                                  (task_title, task_desc, task_id))
                        print(f"DEBUG: Updated task {task_id} with title='{task_title}' and desc='{task_desc[:50]}...'")
                    elif task_title:
                        task_title = self._format_task_title(task_title)
                        cur.execute("UPDATE tasks SET title = ? WHERE id = ?", (task_title, task_id))
                        print(f"DEBUG: Updated task {task_id} with title='{task_title}'")
                    elif task_desc is not None:
                        cur.execute("UPDATE tasks SET description = ? WHERE id = ?", (task_desc, task_id))
                        print(f"DEBUG: Updated task {task_id} with desc='{task_desc[:50]}...'")
                    else:
                        return "edit failed: no title or description provided"
                    
                    self.conn.commit()
                    return f"edited: task #{task_id}"
            
            elif action_type == "complete":
                task_id = action.get("task_id")
                if task_id:
                    result = db_module.complete_task(self.conn, task_id)
                    if result:
                        return f"completed: task #{task_id}"
            
            elif action_type == "uncomplete":
                task_id = action.get("task_id")
                if task_id:
                    cur = self.conn.cursor()
                    cur.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
                    self.conn.commit()
                    if cur.rowcount > 0:
                        return f"uncompleted: task #{task_id}"
            
            elif action_type == "delete":
                task_id = action.get("task_id")
                if task_id:
                    if db_module.delete_task(self.conn, task_id):
                        return f"deleted: task #{task_id}"
            
            elif action_type == "search":
                search_query = action.get("search_query", "")
                if search_query:
                    self._search_tasks(search_query)
                    return f"searched: '{search_query}'"
            
            elif action_type == "list":
                # Don't just refresh - the AI should include the list in its message
                self._refresh_task_list()
                return ""  # Return empty so AI's message shows through
            
            elif action_type == "list_deleted":
                deleted_tasks = db_module.list_deleted_tasks(self.conn, limit=20)
                return f"listed: {len(deleted_tasks)} deleted tasks"
            
            elif action_type == "restore":
                deleted_task_id = action.get("deleted_task_id")
                if deleted_task_id:
                    if db_module.restore_deleted_task(self.conn, deleted_task_id):
                        return f"restored: deleted task #{deleted_task_id}"
            
            return ""
            
        except Exception as e:
            return ""
    
    def _parse_command_with_ai(self, command_text: str) -> Dict[str, Any]:
        """Use OpenAI to parse the command into structured intent."""
        if not self.use_ai or not self.openai_client:
            return {"action": None, "confidence": 0.0}
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a task manager assistant. Parse user commands into JSON.
Response format:
{
  "action": "add|complete|uncomplete|delete|search|list",
  "task_id": number (for complete/uncomplete/delete),
  "task_text": "text" (for add),
  "search_query": "text" (for search),
  "confidence": 0.0-1.0
}

Examples:
"buy milk" -> {"action": "add", "task_text": "buy milk", "confidence": 0.95}
"mark task 5 done" -> {"action": "complete", "task_id": 5, "confidence": 0.9}
"show me all tasks" -> {"action": "list", "confidence": 0.95}
"remove task 3" -> {"action": "delete", "task_id": 3, "confidence": 0.9}
"find homework" -> {"action": "search", "search_query": "homework", "confidence": 0.9}
"uncheck task 2" -> {"action": "uncomplete", "task_id": 2, "confidence": 0.85}"""},
                    {"role": "user", "content": command_text}
                ],
                temperature=0.0,
                max_tokens=150
            )
            
            result_text = response.choices[0].message.content.strip()
            # Try to extract JSON from the response
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            parsed = json.loads(result_text)
            return parsed
            
        except Exception as e:
            print(f"AI parsing error: {e}")
            return {"action": None, "confidence": 0.0}
    
    def _history_up(self, event):
        """Navigate up in command history."""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[-(self.history_index + 1)])
    
    def _history_down(self, event):
        """Navigate down in command history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.command_entry.delete(0, tk.END)
    
    def _process_command(self):
        """Process natural language command from the input field."""
        command_text = self.command_entry.get().strip()
        
        if not command_text:
            return
        
        # Add to history
        self.command_history.append(command_text)
        self.history_index = -1
        
        # Clear entry
        self.command_entry.delete(0, tk.END)
        
        # Parse and execute command
        try:
            # Try AI parsing first if available
            if self.use_ai:
                ai_result = self._parse_command_with_ai(command_text)
                if ai_result.get("confidence", 0) > 0.5:
                    action = ai_result.get("action")
                    
                    if action == "list":
                        self._refresh_task_list()
                        self.status_label.config(text="🤖 Showing all tasks")
                        return
                    
                    elif action == "search":
                        keyword = ai_result.get("search_query", "")
                        if keyword:
                            self._search_tasks(keyword)
                            return
                    
                    elif action == "complete":
                        task_id = ai_result.get("task_id")
                        if task_id:
                            self._complete_task_by_id(task_id)
                            return
                    
                    elif action == "uncomplete":
                        task_id = ai_result.get("task_id")
                        if task_id:
                            self._uncomplete_task_by_id(task_id)
                            return
                    
                    elif action == "delete":
                        task_id = ai_result.get("task_id")
                        if task_id:
                            self._delete_task_by_id(task_id)
                            return
                    
                    elif action == "add":
                        task_text = ai_result.get("task_text", command_text)
                        task = db_module.add_task(self.conn, task_text, None)
                        self.status_label.config(text=f"🤖 Added task {task.id}: {task.title}")
                        self._refresh_task_list()
                        return
            
            # Fall back to regex parsing
            cmd_lower = command_text.lower()
            
            # List/show all
            if cmd_lower in ["list", "show all", "all", "show tasks"]:
                self._refresh_task_list()
                self.status_label.config(text="Showing all tasks")
                return
            
            # Search
            search_match = re.match(r'^(?:search|find)\s+(.+)$', cmd_lower)
            if search_match:
                keyword = search_match.group(1)
                self._search_tasks(keyword)
                return
            
            # Complete task
            complete_match = re.match(r'^(?:complete|check|done|finish|mark)\s+(?:task\s+)?(\d+)(?:\s+(?:done|complete|as\s+done|as\s+complete))?$', cmd_lower)
            if complete_match:
                task_id = int(complete_match.group(1))
                self._complete_task_by_id(task_id)
                return
            
            # Uncomplete task
            uncomplete_match = re.match(r'^(?:uncomplete|uncheck|undo|unfinish)\s+(?:task\s+)?(\d+)$', cmd_lower)
            if uncomplete_match:
                task_id = int(uncomplete_match.group(1))
                self._uncomplete_task_by_id(task_id)
                return
            
            # Delete task
            delete_match = re.match(r'^(?:delete|remove|get\s+rid\s+of)\s+(?:task\s+)?(\d+)$', cmd_lower)
            if delete_match:
                task_id = int(delete_match.group(1))
                self._delete_task_by_id(task_id)
                return
            
            # Add task (default if no other pattern matches)
            # Remove common command prefixes if present
            add_match = re.match(r'^(?:add|create|new|i\s+need\s+to|remind\s+me\s+to)\s+(.+)$', command_text, re.IGNORECASE)
            if add_match:
                task_text = add_match.group(1)
            else:
                task_text = command_text
            
            # Add the task
            task = db_module.add_task(self.conn, task_text, None)
            self.status_label.config(text=f"✓ Added task {task.id}: {task.title}")
            self._refresh_task_list()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to process command: {e}")
    

            
    def _reorder_all_task_ids(self):
        """Reorder all task IDs to be sequential starting from 1."""
        try:
            cur = self.conn.cursor()
            
            # Get all tasks in order
            cur.execute("SELECT id, title, description, completed, created_at FROM tasks ORDER BY created_at ASC")
            tasks = cur.fetchall()
            
            if not tasks:
                return
            
            # Create temp table
            cur.execute("""CREATE TEMPORARY TABLE IF NOT EXISTS tasks_backup AS 
                          SELECT * FROM tasks WHERE 0""")
            cur.execute("DELETE FROM tasks_backup")
            cur.execute("INSERT INTO tasks_backup SELECT * FROM tasks")
            
            # Clear and reinsert with sequential IDs
            cur.execute("DELETE FROM tasks")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
            
            for old_task in tasks:
                _, title, description, completed, created_at = old_task
                cur.execute(
                    "INSERT INTO tasks (title, description, completed, created_at) VALUES (?, ?, ?, ?)",
                    (title, description, completed, created_at)
                )
            
            cur.execute("DROP TABLE tasks_backup")
            self.conn.commit()
        except Exception as e:
            print(f"Reorder error: {e}")
    
    def _refresh_task_list(self):
        """Refresh the task list display."""
        # Clear current items and descriptions map
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Clear the descriptions map to ensure fresh data
        self.task_descriptions_map.clear()
        
        try:
            tasks = db_module.list_tasks(self.conn)
            
            # Calculate statistics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.completed)
            pending_tasks = total_tasks - completed_tasks
            
            # Update statistics display
            self.stats_label.config(text=f"Total: {total_tasks} | ✓ {completed_tasks} | ☐ {pending_tasks}")
            
            # Reverse the order so newest (highest ID) appears first
            for task in reversed(tasks):
                status = "✓ Complete" if task.completed else "☐ Pending"
                # Store description for popup
                description = task.description if (task.description and task.description.strip()) else "No Description."
                self.task_descriptions_map[task.id] = description
                
                # Format View More with icon
                values = (task.id, status, task.title, "📄 View More")
                
                # Add task to tree with tags
                if task.completed:
                    item_id = self.task_tree.insert("", tk.END, values=values, tags=("completed",))
                else:
                    item_id = self.task_tree.insert("", tk.END, values=values, tags=("normal",))
            
            # Configure tag colors
            self.task_tree.tag_configure("completed", foreground="gray")
            self.task_tree.tag_configure("normal", foreground="#263238")
            
            # Force update of the display
            self.task_tree.update_idletasks()
            
        except Exception as e:
            pass  # Silently handle errors
            
    def _search_tasks(self, keyword: str):
        """Search for tasks by keyword."""
        # Clear current items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        try:
            tasks = db_module.search_tasks(self.conn, keyword)
            
            for task in tasks:
                status = "✓ Complete" if task.completed else "☐ Pending"
                description = task.description if task.description else "No Description."
                self.task_descriptions_map[task.id] = description
                # Format View More with icon
                values = (task.id, status, task.title, "📄 View More")
                
                if task.completed:
                    item_id = self.task_tree.insert("", tk.END, values=values, tags=("completed",))
                else:
                    item_id = self.task_tree.insert("", tk.END, values=values, tags=("normal",))
            
            self.task_tree.tag_configure("completed", foreground="gray")
            self.task_tree.tag_configure("normal", foreground="#263238")
            
            self.status_label.config(text=f"Found {len(tasks)} task(s) matching '{keyword}'")
        except Exception as e:
            self.status_label.config(text=f"Search error: {str(e)}")
            
    def _complete_task_by_id(self, task_id: int):
        """Mark a task as complete by ID."""
        try:
            if db_module.complete_task(self.conn, task_id):
                self.status_label.config(text=f"✓ Task {task_id} marked as complete")
                self._refresh_task_list()
            else:
                self.status_label.config(text=f"Task {task_id} not found")
        except Exception as e:
            self.status_label.config(text=f"Error completing task: {str(e)}")
    
    def _uncomplete_task_by_id(self, task_id: int):
        """Mark a task as incomplete by ID."""
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
            self.conn.commit()
            
            if cur.rowcount > 0:
                self.status_label.config(text=f"☐ Task {task_id} marked as incomplete")
                self._refresh_task_list()
            else:
                self.status_label.config(text=f"Task {task_id} not found")
        except Exception as e:
            self.status_label.config(text=f"Error uncompleting task: {str(e)}")
            
    def _delete_task_by_id(self, task_id: int):
        """Delete a task by ID."""
        try:
            if db_module.delete_task(self.conn, task_id):
                self.status_label.config(text=f"✗ Task {task_id} deleted")
                self._refresh_task_list()
            else:
                self.status_label.config(text=f"Task {task_id} not found")
        except Exception as e:
            self.status_label.config(text=f"Error deleting task: {str(e)}")
            
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = TaskManagerGUI(root)
    
    # Handle window close event
    def on_closing():
        app.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
