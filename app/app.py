import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time

# Tentar importar plyer para notificações
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer não instalado. Notificações desabilitadas.")

# --- Cores Modernas (Estilo Notion/Dark Mode) ---
COLORS = {
    'bg_primary': '#191919',
    'bg_secondary': '#202020',
    'bg_tertiary': '#2d2d2d',
    'accent_blue': '#2383e2',
    'accent_green': '#2ea043',
    'accent_yellow': '#e3b341',
    'accent_red': '#f85149',
    'accent_purple': '#a371f7',
    'text_primary': '#ffffff',
    'text_secondary': '#8b949e',
    'text_tertiary': '#6e7681',
    'border': '#30363d',
    'hover': '#252525'
}

# --- Componente de Tarefa Moderno ---
class ModernTask(tk.Frame):
    def __init__(self, master, nome, categoria="geral", importante=False, 
                 funcao_apagar=None, funcao_editar=None, alarme=None, **kwargs):
        super().__init__(master, bg=COLORS['bg_secondary'], **kwargs)
        
        self.nome = nome
        self.categoria = categoria
        self.importante = importante
        self.funcao_apagar = funcao_apagar
        self.funcao_editar = funcao_editar
        self.alarme = alarme
        self.concluida = False
        self.data_criacao = datetime.now()
        
        self.configurar_estilo()
        self.criar_widgets()
        self.bind_events()
        
        if self.alarme and PLYER_AVAILABLE:
            self.iniciar_monitor_alarme()
    
    def configurar_estilo(self):
        self.configure(bg=COLORS['bg_secondary'], relief=tk.FLAT)
        
    def criar_widgets(self):
        # Container principal
        self.container = tk.Frame(self, bg=COLORS['bg_secondary'])
        self.container.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        
        # Checkbox customizado
        self.check_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(
            self.container, variable=self.check_var,
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            selectcolor=COLORS['bg_tertiary'], 
            activebackground=COLORS['bg_secondary'],
            command=self.toggle_conclusao,
            cursor="hand2"
        )
        self.checkbox.pack(side=tk.LEFT, padx=(0, 12))
        
        # Ícone de categoria
        self.icone_categoria = self.get_categoria_icon()
        self.lbl_categoria = tk.Label(
            self.container, text=self.icone_categoria,
            bg=COLORS['bg_secondary'], fg=self.get_categoria_color(),
            font=("Segoe UI", 12), cursor="hand2"
        )
        self.lbl_categoria.pack(side=tk.LEFT, padx=(0, 8))
        
        # Conteúdo principal
        content_frame = tk.Frame(self.container, bg=COLORS['bg_secondary'])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Nome da tarefa
        self.lbl_nome = tk.Label(
            content_frame, text=self.nome,
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            font=("Segoe UI", 11), anchor="w"
        )
        self.lbl_nome.pack(fill=tk.X)
        
        # Meta informações
        self.meta_frame = tk.Frame(content_frame, bg=COLORS['bg_secondary'])
        self.meta_frame.pack(fill=tk.X, pady=(4, 0))
        
        # Badge de importante
        if self.importante:
            self.badge_importante = tk.Label(
                self.meta_frame, text="⭐ Importante",
                bg=COLORS['bg_tertiary'], fg=COLORS['accent_yellow'],
                font=("Segoe UI", 8), padx=8, pady=2
            )
            self.badge_importante.pack(side=tk.LEFT, padx=(0, 6))
        
        # Badge de alarme
        if self.alarme:
            try:
                hora_alarme = datetime.fromisoformat(self.alarme).strftime("%H:%M")
                self.badge_alarme = tk.Label(
                    self.meta_frame, text=f"🔔 {hora_alarme}",
                    bg=COLORS['bg_tertiary'], fg=COLORS['accent_blue'],
                    font=("Segoe UI", 8), padx=8, pady=2
                )
                self.badge_alarme.pack(side=tk.LEFT)
            except:
                pass
        
        # Badge de categoria
        categoria_text = self.categoria.replace('_', ' ').title()
        self.badge_categoria = tk.Label(
            self.meta_frame, text=categoria_text,
            bg=COLORS['bg_tertiary'], fg=COLORS['text_secondary'],
            font=("Segoe UI", 8), padx=8, pady=2
        )
        self.badge_categoria.pack(side=tk.LEFT, padx=(6, 0))
        
        # Botões de ação (aparecem no hover)
        self.actions_frame = tk.Frame(self.container, bg=COLORS['bg_secondary'])
        
        # Botão editar
        self.btn_editar = tk.Label(
            self.actions_frame, text="✎",
            bg=COLORS['bg_secondary'], fg=COLORS['text_tertiary'],
            font=("Segoe UI", 14), cursor="hand2"
        )
        self.btn_editar.pack(side=tk.LEFT, padx=4)
        
        # Botão deletar
        self.btn_deletar = tk.Label(
            self.actions_frame, text="🗑",
            bg=COLORS['bg_secondary'], fg=COLORS['text_tertiary'],
            font=("Segoe UI", 12), cursor="hand2"
        )
        self.btn_deletar.pack(side=tk.LEFT, padx=4)
    
    def bind_events(self):
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.lbl_nome.bind("<Double-Button-1>", lambda e: self.editar())
        self.lbl_categoria.bind("<Button-1>", self.ciclar_categoria)
        self.btn_editar.bind("<Button-1>", lambda e: self.editar())
        self.btn_deletar.bind("<Button-1>", lambda e: self.deletar())
        
        for widget in [self.container, self.lbl_nome, self.meta_frame, self.actions_frame, self.btn_editar, self.btn_deletar]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        self.configure(bg=COLORS['hover'])
        self.container.configure(bg=COLORS['hover'])
        self.lbl_nome.configure(bg=COLORS['hover'])
        self.lbl_categoria.configure(bg=COLORS['hover'])
        self.meta_frame.configure(bg=COLORS['hover'])
        self.actions_frame.configure(bg=COLORS['hover'])
        self.btn_editar.configure(bg=COLORS['hover'])
        self.btn_deletar.configure(bg=COLORS['hover'])
        self.actions_frame.pack(side=tk.RIGHT)
        
    def on_leave(self, e):
        x, y = self.winfo_pointerxy()
        x0 = self.winfo_rootx()
        y0 = self.winfo_rooty()
        x1 = x0 + self.winfo_width()
        y1 = y0 + self.winfo_height()
        
        if x0 <= x <= x1 and y0 <= y <= y1:
            return
        self.configure(bg=COLORS['bg_secondary'])
        self.container.configure(bg=COLORS['bg_secondary'])
        self.lbl_nome.configure(bg=COLORS['bg_secondary'])
        self.lbl_categoria.configure(bg=COLORS['bg_secondary'])
        self.meta_frame.configure(bg=COLORS['bg_secondary'])
        self.actions_frame.configure(bg=COLORS['bg_secondary'])
        self.btn_editar.configure(bg=COLORS['bg_secondary'])
        self.btn_deletar.configure(bg=COLORS['bg_secondary'])
        self.actions_frame.pack_forget()
    
    def get_categoria_icon(self):
        icons = {
            'geral': '📋',
            'trabalho': '💼',
            'pessoal': '🏠',
            'estudos': '📚',
            'saude': '🏃',
            'compras': '🛒'
        }
        return icons.get(self.categoria, '📋')
    
    def get_categoria_color(self):
        colors = {
            'geral': COLORS['accent_blue'],
            'trabalho': COLORS['accent_purple'],
            'pessoal': COLORS['accent_green'],
            'estudos': COLORS['accent_yellow'],
            'saude': COLORS['accent_red'],
            'compras': COLORS['accent_blue']
        }
        return colors.get(self.categoria, COLORS['text_secondary'])
    
    def ciclar_categoria(self, event=None):
        categorias = ['geral', 'trabalho', 'pessoal', 'estudos', 'saude', 'compras']
        current_idx = categorias.index(self.categoria)
        next_idx = (current_idx + 1) % len(categorias)
        self.categoria = categorias[next_idx]
        
        self.lbl_categoria.configure(
            text=self.get_categoria_icon(),
            fg=self.get_categoria_color()
        )
        self.badge_categoria.configure(text=self.categoria.title())
    
    def toggle_conclusao(self):
        self.concluida = self.check_var.get()
        if self.concluida:
            self.lbl_nome.configure(
                fg=COLORS['text_tertiary'],
                font=("Segoe UI", 11, "overstrike")
            )
        else:
            self.lbl_nome.configure(
                fg=COLORS['text_primary'],
                font=("Segoe UI", 11)
            )
        
        # Atualizar estatísticas
        if hasattr(self.master, 'master') and hasattr(self.master.master, 'update_stats'):
            self.master.master.update_stats()
    
    def editar(self):
        if self.funcao_editar:
            self.funcao_editar(self)
    
    def deletar(self):
        if self.funcao_apagar:
            self.funcao_apagar(self)
    
    def iniciar_monitor_alarme(self):
        def verificar_alarme():
            while self.alarme and not self.concluida:
                try:
                    agora = datetime.now()
                    alarme_time = datetime.fromisoformat(self.alarme)
                    
                    if agora >= alarme_time:
                        self.disparar_alarme()
                        break
                except:
                    break
                    
                time.sleep(30)  # Verifica a cada 30 segundos
        
        thread = threading.Thread(target=verificar_alarme, daemon=True)
        thread.start()
    
    def disparar_alarme(self):
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title="⏰ Alarme de Tarefa",
                    message=f"Tarefa: {self.nome}\nCategoria: {self.categoria.title()}",
                    app_name="Organizador Moderno",
                    timeout=10
                )
            except:
                pass

# --- Modal de Edição Moderno ---
class ModernEditModal:
    def __init__(self, parent, task, callback):
        self.parent = parent
        self.task = task
        self.callback = callback
        
        self.top = tk.Toplevel(parent)
        self.top.title("Editar Tarefa")
        self.top.geometry("450x400")
        self.top.configure(bg=COLORS['bg_primary'])
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        self.criar_widgets()
        self.centralizar()
    
    def centralizar(self):
        self.top.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 450) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 400) // 2
        self.top.geometry(f"+{x}+{y}")
    
    def criar_widgets(self):
        # Header
        header = tk.Frame(self.top, bg=COLORS['bg_primary'], height=60)
        header.pack(fill=tk.X, padx=24, pady=(24, 16))
        header.pack_propagate(False)
        
        tk.Label(
            header, text="Editar Tarefa",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        # Conteúdo
        content = tk.Frame(self.top, bg=COLORS['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=24)
        
        # Nome
        tk.Label(
            content, text="Nome da Tarefa",
            font=("Segoe UI", 10),
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 6))
        
        self.entry_nome = tk.Entry(
            content, font=("Segoe UI", 12),
            bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT, bd=1
        )
        self.entry_nome.insert(0, self.task.nome)
        self.entry_nome.pack(fill=tk.X, ipady=10, pady=(0, 16))
        self.entry_nome.focus()
        
        # Categoria
        tk.Label(
            content, text="Categoria",
            font=("Segoe UI", 10),
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 6))
        
        self.categoria_var = tk.StringVar(value=self.task.categoria)
        categorias = ['geral', 'trabalho', 'pessoal', 'estudos', 'saude', 'compras']
        
        categoria_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        categoria_frame.pack(fill=tk.X, pady=(0, 16))
        
        for i, cat in enumerate(categorias):
            rb = tk.Radiobutton(
                categoria_frame, text=cat.title(), variable=self.categoria_var,
                value=cat, bg=COLORS['bg_primary'], fg=COLORS['text_primary'],
                selectcolor=COLORS['bg_tertiary'], 
                activebackground=COLORS['bg_primary'],
                font=("Segoe UI", 10), cursor="hand2"
            )
            rb.pack(side=tk.LEFT, padx=(0, 16))
        
        # Importante
        self.importante_var = tk.BooleanVar(value=self.task.importante)
        tk.Checkbutton(
            content, text="⭐ Marcar como importante",
            variable=self.importante_var,
            bg=COLORS['bg_primary'], fg=COLORS['accent_yellow'],
            selectcolor=COLORS['bg_tertiary'],
            activebackground=COLORS['bg_primary'],
            font=("Segoe UI", 10), cursor="hand2"
        ).pack(anchor="w", pady=(0, 16))
        
        # Alarme
        tk.Label(
            content, text="🔔 Alarme (opcional)",
            font=("Segoe UI", 10),
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 6))
        
        alarme_frame = tk.Frame(content, bg=COLORS['bg_primary'])
        alarme_frame.pack(fill=tk.X, pady=(0, 24))
        
        self.alarme_entry = tk.Entry(
            alarme_frame, font=("Segoe UI", 11),
            bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT, width=5
        )
        if self.task.alarme:
            try:
                hora = datetime.fromisoformat(self.task.alarme).strftime("%H:%M")
                self.alarme_entry.insert(0, hora)
            except:
                pass
        self.alarme_entry.pack(side=tk.LEFT, ipady=8)
        
        tk.Label(
            alarme_frame, text="Formato: HH:MM",
            bg=COLORS['bg_primary'], fg=COLORS['text_tertiary'],
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=10)
        
        # Botões
        button_frame = tk.Frame(self.top, bg=COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, padx=24, pady=(0, 24))
        
        tk.Button(
            button_frame, text="Cancelar",
            bg=COLORS['bg_tertiary'], fg=COLORS['text_primary'],
            font=("Segoe UI", 11), bd=0, padx=20, pady=10,
            command=self.top.destroy, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=(8, 0))
        
        tk.Button(
            button_frame, text="Salvar",
            bg=COLORS['accent_blue'], fg="white",
            font=("Segoe UI", 11, "bold"), bd=0, padx=24, pady=10,
            command=self.salvar, cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        self.entry_nome.bind("<Return>", lambda e: self.salvar())
    
    def salvar(self):
        novo_nome = self.entry_nome.get().strip()
        if not novo_nome:
            messagebox.showwarning("Aviso", "O nome da tarefa é obrigatório!")
            return
        
        self.task.nome = novo_nome
        self.task.categoria = self.categoria_var.get()
        self.task.importante = self.importante_var.get()
        
        # Processar alarme
        alarme_text = self.alarme_entry.get().strip()
        if alarme_text:
            try:
                hora, minuto = map(int, alarme_text.split(':'))
                agora = datetime.now()
                alarme_time = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                if alarme_time < agora:
                    alarme_time += timedelta(days=1)
                self.task.alarme = alarme_time.isoformat()
            except:
                messagebox.showwarning("Aviso", "Formato de hora inválido! Use HH:MM")
                return
        else:
            self.task.alarme = None
        
        self.callback()
        self.top.destroy()

# --- App Principal Moderno ---
class ModernTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador Moderno")
        self.root.geometry("550x750")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.minsize(450, 600)
        
        self.tasks = []
        self.filtered_tasks = []
        self.current_filter = "todas"
        self.data_file = "modern_tasks.json"
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Header moderno
        header = tk.Frame(self.root, bg=COLORS['bg_primary'], height=80)
        header.pack(fill=tk.X, padx=24, pady=(20, 0))
        header.pack_propagate(False)
        
        # Título com data
        title_frame = tk.Frame(header, bg=COLORS['bg_primary'])
        title_frame.pack(side=tk.LEFT)
        
        data_atual = datetime.now().strftime("%d %b, %Y")
        tk.Label(
            title_frame, text=data_atual,
            font=("Segoe UI", 11),
            bg=COLORS['bg_primary'], fg=COLORS['accent_blue']
        ).pack(anchor="w")
        
        tk.Label(
            title_frame, text="Minhas Tarefas",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS['bg_primary'], fg=COLORS['text_primary']
        ).pack(anchor="w")
        
        # Botão menu
        menu_btn = tk.Label(
            header, text="☰",
            font=("Segoe UI", 20),
            bg=COLORS['bg_primary'], fg=COLORS['text_secondary'],
            cursor="hand2"
        )
        menu_btn.pack(side=tk.RIGHT)
        menu_btn.bind("<Button-1>", self.show_menu)
        
        # Input moderno
        input_frame = tk.Frame(self.root, bg=COLORS['bg_secondary'])
        input_frame.pack(fill=tk.X, padx=24, pady=20)
        
        self.task_input = tk.Entry(
            input_frame, font=("Segoe UI", 12),
            bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief=tk.FLAT
        )
        self.task_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(16, 8))
        self.task_input.bind("<Return>", lambda e: self.add_task())
        self.task_input.insert(0, "Adicionar nova tarefa...")
        self.task_input.bind("<FocusIn>", self.on_input_focus_in)
        self.task_input.bind("<FocusOut>", self.on_input_focus_out)
        self.task_input.configure(fg=COLORS['text_tertiary'])
        
        add_btn = tk.Label(
            input_frame, text="+",
            font=("Segoe UI", 20),
            bg=COLORS['bg_secondary'], fg=COLORS['accent_blue'],
            cursor="hand2"
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 16))
        add_btn.bind("<Button-1>", lambda e: self.add_task())
        
        # Filtros modernos
        filter_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        filter_frame.pack(fill=tk.X, padx=24, pady=(0, 16))
        
        filters = [
            ("Todas", "todas"),
            ("Importantes", "importantes"),
            ("Hoje", "hoje"),
            ("Alarmes", "alarme")
        ]
        
        self.filter_buttons = {}
        for text, value in filters:
            btn = tk.Label(
                filter_frame, text=text,
                font=("Segoe UI", 10),
                bg=COLORS['bg_primary'], fg=COLORS['text_tertiary'],
                cursor="hand2", padx=12, pady=6
            )
            btn.pack(side=tk.LEFT)
            btn.bind("<Button-1>", lambda e, v=value: self.apply_filter(v))
            self.filter_buttons[value] = btn
        
        # Separador
        separator = tk.Frame(self.root, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X, padx=24)
        
        # Container de tarefas com scroll
        self.canvas = tk.Canvas(self.root, bg=COLORS['bg_primary'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, bg=COLORS['bg_primary'])
        self.tasks_container = tk.Frame(self.canvas, bg=COLORS['bg_primary'])
        
        self.tasks_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Salvamos o ID da janela do canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.tasks_container, anchor="nw")
        
        # Forçamos o container interno a ter exatamente a mesma largura do canvas
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(24, 0), pady=16)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 24), pady=16)
        
        # Bind scroll
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Estatísticas modernas
        self.stats_label = tk.Label(
            self.root, text="",
            font=("Segoe UI", 10),
            bg=COLORS['bg_primary'], fg=COLORS['text_tertiary']
        )
        self.stats_label.pack(pady=16)
        
        # Aplicar filtro inicial
        self.apply_filter("todas")
        
    def on_input_focus_in(self, e):
        if self.task_input.get() == "Adicionar nova tarefa...":
            self.task_input.delete(0, tk.END)
            self.task_input.configure(fg=COLORS['text_primary'])
    
    def on_input_focus_out(self, e):
        if not self.task_input.get().strip():
            self.task_input.insert(0, "Adicionar nova tarefa...")
            self.task_input.configure(fg=COLORS['text_tertiary'])
    
    def add_task(self):
        nome = self.task_input.get().strip()
        if not nome or nome == "Adicionar nova tarefa...":
            return
        
        task = ModernTask(
            self.tasks_container, nome,
            categoria="geral",
            funcao_apagar=self.delete_task,
            funcao_editar=self.edit_task
        )
        
        self.tasks.append(task)
        self.task_input.delete(0, tk.END)
        self.task_input.configure(fg=COLORS['text_primary'])
        self.apply_filter(self.current_filter)
        self.save_data()
    
    def edit_task(self, task):
        def callback():
            task.lbl_nome.configure(text=task.nome)
            task.lbl_categoria.configure(
                text=task.get_categoria_icon(),
                fg=task.get_categoria_color()
            )
            task.badge_categoria.configure(text=task.categoria.title())
            
            # Limpar meta frame
            for widget in task.meta_frame.winfo_children():
                widget.destroy()
            
            # Recriar badges
            if task.importante:
                badge = tk.Label(
                    task.meta_frame, text="⭐ Importante",
                    bg=COLORS['bg_tertiary'], fg=COLORS['accent_yellow'],
                    font=("Segoe UI", 8), padx=8, pady=2
                )
                badge.pack(side=tk.LEFT, padx=(0, 6))
            
            if task.alarme:
                try:
                    hora_alarme = datetime.fromisoformat(task.alarme).strftime("%H:%M")
                    badge_alarme = tk.Label(
                        task.meta_frame, text=f"🔔 {hora_alarme}",
                        bg=COLORS['bg_tertiary'], fg=COLORS['accent_blue'],
                        font=("Segoe UI", 8), padx=8, pady=2
                    )
                    badge_alarme.pack(side=tk.LEFT)
                except:
                    pass
            
            categoria_text = task.categoria.replace('_', ' ').title()
            badge_categoria = tk.Label(
                task.meta_frame, text=categoria_text,
                bg=COLORS['bg_tertiary'], fg=COLORS['text_secondary'],
                font=("Segoe UI", 8), padx=8, pady=2
            )
            badge_categoria.pack(side=tk.LEFT, padx=(6, 0))
            
            self.apply_filter(self.current_filter)
            self.save_data()
        
        ModernEditModal(self.root, task, callback)
    
    def delete_task(self, task):
        if messagebox.askyesno("Confirmar", "Excluir esta tarefa?"):
            task.destroy()
            if task in self.tasks:
                self.tasks.remove(task)
            self.apply_filter(self.current_filter)
            self.save_data()
    
    def apply_filter(self, filter_type):
        self.current_filter = filter_type
        
        # Reset button styles
        for btn in self.filter_buttons.values():
            btn.configure(fg=COLORS['text_tertiary'])
        
        # Highlight active filter
        if filter_type in self.filter_buttons:
            self.filter_buttons[filter_type].configure(fg=COLORS['accent_blue'])
        
        # Hide all tasks
        for task in self.tasks:
            task.pack_forget()
        
        # Filter and show tasks
        self.filtered_tasks = []
        hoje = datetime.now().date()
        
        for task in self.tasks:
            show = False
            if filter_type == "todas":
                show = True
            elif filter_type == "importantes":
                show = task.importante
            elif filter_type == "hoje":
                show = task.data_criacao.date() == hoje
            elif filter_type == "alarme":
                show = task.alarme is not None
            
            if show:
                task.pack(fill=tk.X, pady=4)
                self.filtered_tasks.append(task)
        
        self.update_stats()
    
    def update_stats(self):
        if not hasattr(self, 'stats_label'):
            return
            
        total = len(self.filtered_tasks)
        concluidas = len([t for t in self.filtered_tasks if t.concluida])
        stats_text = f"{total} tarefas • {concluidas} concluídas"
        
        if total > 0:
            progress = (concluidas / total) * 100
            stats_text += f" • {progress:.0f}% completo"
        
        self.stats_label.configure(text=stats_text)
    
    def show_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
        menu.add_command(label="💾 Salvar", command=self.save_data)
        menu.add_command(label="🧹 Limpar Concluídas", command=self.clear_completed)
        menu.add_separator()
        menu.add_command(label="ℹ️ Sobre", command=self.show_about)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def clear_completed(self):
        for task in self.tasks[:]:
            if task.concluida:
                task.destroy()
                self.tasks.remove(task)
        self.apply_filter(self.current_filter)
        self.save_data()
    
    def show_about(self):
        messagebox.showinfo(
            "Sobre",
            "Organizador Moderno v2.0\n\n"
            "Um app de tarefas minimalista e elegante\n"
            "com alarmes e categorias inteligentes.\n\n"
            "Desenvolvido com ❤️ usando Python"
        )
    
    def save_data(self):
        data = []
        for task in self.tasks:
            data.append({
                'nome': task.nome,
                'categoria': task.categoria,
                'importante': task.importante,
                'concluida': task.concluida,
                'alarme': task.alarme,
                'data_criacao': task.data_criacao.isoformat()
            })
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar: {e}")
    
    def load_data(self):
        if not os.path.exists(self.data_file):
            # Adicionar algumas tarefas de exemplo
            exemplos = [
                ("✨ Bem-vindo ao Organizador Moderno!", "geral", True, None),
                ("📱 Clique no ícone para mudar categoria", "trabalho", False, None),
                ("⏰ Tarefa com alarme de exemplo", "pessoal", False, 
                 (datetime.now() + timedelta(minutes=5)).isoformat())
            ]
            
            for nome, cat, imp, alarme in exemplos:
                task = ModernTask(
                    self.tasks_container, nome,
                    categoria=cat, importante=imp, alarme=alarme,
                    funcao_apagar=self.delete_task,
                    funcao_editar=self.edit_task
                )
                self.tasks.append(task)
        else:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    task = ModernTask(
                        self.tasks_container, item['nome'],
                        categoria=item.get('categoria', 'geral'),
                        importante=item.get('importante', False),
                        alarme=item.get('alarme'),
                        funcao_apagar=self.delete_task,
                        funcao_editar=self.edit_task
                    )
                    if item.get('concluida'):
                        task.check_var.set(True)
                        task.toggle_conclusao()
                    self.tasks.append(task)
            except Exception as e:
                print(f"Erro ao carregar: {e}")
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# --- Execução ---
if __name__ == "__main__":
    root = tk.Tk()
    
    # Instalar plyer se necessário
    if not PLYER_AVAILABLE:
        print("\n⚠️  Plyer não está instalado. Para habilitar notificações, execute:")
        print("   pip install plyer\n")
    
    app = ModernTodoApp(root)
    
    # Centralizar janela
    root.update_idletasks()
    width = 550
    height = 750
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()