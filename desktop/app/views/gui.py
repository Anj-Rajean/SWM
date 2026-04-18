import customtkinter as ctk
from typing import Optional


class LoginView:
    def __init__(self, parent: ctk.CTk, on_login_callback, on_check_new_vault_callback):
        self.parent = parent
        self.on_login = on_login_callback
        self.on_check_new = on_check_new_vault_callback
        self.frame = None
        self.password_entry = None
        self.error_label = None
    
    def show(self):
        self._clear_parent()
        
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color="#D2C4B4")
        self.frame.pack(fill="both", expand=True)
        
        login_frame = ctk.CTkFrame(
            self.frame,
            corner_radius=12,
            fg_color="#AACDDC",
            border_width=2,
            border_color="#81A6C6"
        )
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            login_frame,
            text="ErgoSecure",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1A3263"
        ).pack(pady=(20, 10))
        
        is_new = self.on_check_new()
        if is_new:
            ctk.CTkLabel(
                login_frame,
                text="Créer un mot de passe principal",
                text_color="#1A3263"
            ).pack(pady=5)
        else:
            ctk.CTkLabel(
                login_frame,
                text="Entrer votre mot de passe",
                text_color="#1A3263"
            ).pack(pady=5)
        
        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Mot de passe",
            show="*",
            width=250
        )
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        ctk.CTkButton(
            login_frame,
            text="Valider",
            command=self._handle_login,
            fg_color="#81A6C6",
            hover_color="#6B93B3"
        ).pack(pady=10)
        
        self.error_label = ctk.CTkLabel(login_frame, text="", text_color="red")
        self.error_label.pack(pady=5)
    
    def _handle_login(self):
        password = self.password_entry.get()
        self.on_login(password)
    
    def show_error(self, message: str):
        self.error_label.configure(text=message)
    
    def _clear_parent(self):
        for widget in self.parent.winfo_children():
            widget.destroy()


class DashboardView:
    def __init__(self, parent: ctk.CTk, controller):
        self.parent = parent
        self.controller = controller
        self.header = None
        self.controls = None
        self.entries_frame = None
        self.search_entry = None
    
    def show(self):
        self._clear_parent()
        
        self._create_header()
        self._create_controls()
        self._create_entries_frame()
        self.load_entries()
    
    def _create_header(self):
        self.header = ctk.CTkFrame(self.parent, fg_color="#AACDDC", height=50)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        ctk.CTkLabel(
            self.header,
            text="ErgoSecure",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1A3263"
        ).pack(side="left", padx=20)
        
        ctk.CTkButton(
            self.header,
            text="Déconnexion",
            command=self.controller.logout,
            fg_color="#81A6C6",
            hover_color="#6B93B3",
            width=100
        ).pack(side="right", padx=20)
    
    def _create_controls(self):
        self.controls = ctk.CTkFrame(self.parent, fg_color="#D2C4B4")
        self.controls.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            self.controls,
            placeholder_text="Rechercher...",
            width=300
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search())
        
        ctk.CTkButton(
            self.controls,
            text="Rechercher",
            command=self.search,
            fg_color="#81A6C6"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.controls,
            text="+ Ajouter",
            command=self.show_add_modal,
            fg_color="#81A6C6",
            hover_color="#6B93B3"
        ).pack(side="right", padx=5)
    
    def _create_entries_frame(self):
        self.entries_frame = ctk.CTkScrollableFrame(self.parent, fg_color="#D2C4B4")
        self.entries_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def load_entries(self, entries=None):
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        
        if entries is None:
            entries = self.controller.get_all_entries()
        
        if not entries:
            ctk.CTkLabel(
                self.entries_frame,
                text="Aucun mot de passe. Ajoutez votre premier!",
                text_color="#81A6C6"
            ).pack(pady=20)
            return
        
        for entry in entries:
            self._create_entry_card(entry)
    
    def _create_entry_card(self, entry):
        card = ctk.CTkFrame(
            self.entries_frame,
            fg_color="#AACDDC",
            corner_radius=8
        )
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            card,
            text=entry.title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1A3263"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            card,
            text=f"Username: {entry.username}",
            text_color="#1A3263"
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            card,
            text=f"Password: ••••••••",
            text_color="#1A3263"
        ).pack(anchor="w", padx=10)
        
        if entry.url:
            ctk.CTkLabel(
                card,
                text=f"URL: {entry.url}",
                text_color="#1A3263"
            ).pack(anchor="w", padx=10)
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(anchor="e", padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Copy User",
            command=lambda: self._copy_to_clipboard(entry.username),
            width=80,
            fg_color="#81A6C6"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Copy Pass",
            command=lambda: self._copy_to_clipboard(entry.password),
            width=80,
            fg_color="#81A6C6"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Edit",
            command=lambda: self.show_edit_modal(entry),
            width=60,
            fg_color="#81A6C6"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda: self._delete_entry(entry.id),
            width=60,
            fg_color="#ff6b6b"
        ).pack(side="left", padx=2)
    
    def search(self):
        query = self.search_entry.get()
        if query:
            results = self.controller.search(query)
            self.load_entries(results)
        else:
            self.load_entries()
    
    def show_add_modal(self):
        self._show_entry_modal(None)
    
    def show_edit_modal(self, entry):
        self._show_entry_modal(entry)
    
    def _show_entry_modal(self, entry):
        modal = ctk.CTkToplevel(self.parent)
        modal.title("Ajouter un mot de passe" if not entry else "Modifier le mot de passe")
        modal.geometry("400x450")
        modal.transient(self.parent)
        
        is_edit = entry is not None
        
        ctk.CTkLabel(modal, text="Titre", text_color="#1A3263").pack(pady=(10, 0))
        title_entry = ctk.CTkEntry(modal, width=300)
        title_entry.pack(pady=5)
        if entry:
            title_entry.insert(0, entry.title)
        
        ctk.CTkLabel(modal, text="Username", text_color="#1A3263").pack(pady=(10, 0))
        user_entry = ctk.CTkEntry(modal, width=300)
        user_entry.pack(pady=5)
        if entry:
            user_entry.insert(0, entry.username)
        
        ctk.CTkLabel(modal, text="Mot de passe", text_color="#1A3263").pack(pady=(10, 0))
        pass_frame = ctk.CTkFrame(modal, fg_color="transparent")
        pass_frame.pack(pady=5)
        
        pass_entry = ctk.CTkEntry(pass_frame, show="*", width=220)
        pass_entry.pack(side="left")
        if entry:
            pass_entry.insert(0, entry.password)
        
        def generate():
            import secrets
            import string
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            pass_entry.delete(0, "end")
            pass_entry.insert(0, password)
        
        ctk.CTkButton(pass_frame, text="Générer", command=generate, width=70).pack(side="left", padx=5)
        
        ctk.CTkLabel(modal, text="URL (optionnel)", text_color="#1A3263").pack(pady=(10, 0))
        url_entry = ctk.CTkEntry(modal, width=300)
        url_entry.pack(pady=5)
        if entry:
            url_entry.insert(0, entry.url or "")
        
        ctk.CTkLabel(modal, text="Notes (optionnel)", text_color="#1A3263").pack(pady=(10, 0))
        notes_entry = ctk.CTkTextbox(modal, width=300, height=60)
        notes_entry.pack(pady=5)
        if entry:
            notes_entry.insert("1.0", entry.notes or "")
        
        def save():
            title = title_entry.get()
            username = user_entry.get()
            password = pass_entry.get()
            url = url_entry.get() or None
            notes = notes_entry.get("1.0", "end").strip() or None
            
            if not title or not username or not password:
                return
            
            if is_edit:
                self.controller.update_entry(entry.id, title, username, password, url, notes)
            else:
                self.controller.add_entry(title, username, password, url, notes)
            
            modal.destroy()
            self.load_entries()
        
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="Annuler", command=modal.destroy, fg_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Sauvegarder", command=save, fg_color="#81A6C6", hover_color="#6B93B3").pack(side="left", padx=5)
    
    def _delete_entry(self, entry_id):
        self.controller.delete_entry(entry_id)
        self.load_entries()
    
    def _copy_to_clipboard(self, text):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
    
    def _clear_parent(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
