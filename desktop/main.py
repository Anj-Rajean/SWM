import customtkinter as ctk
from app.controllers.vault import VaultController
from app.views.gui import LoginView, DashboardView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ErgoSecure - Gestionnaire de Mots de Passe")
        self.geometry("900x600")
        
        self.controller = None
        self.login_view = None
        self.dashboard_view = None
        
        self.show_login()
    
    def show_login(self):
        self.login_view = LoginView(
            self,
            on_login_callback=self.handle_login,
            on_check_new_vault_callback=self.check_new_vault
        )
        self.login_view.show()
    
    def check_new_vault(self) -> bool:
        return not VaultController.storage_exists()
    
    def handle_login(self, password: str):
        if not password:
            self.login_view.show_error("Veuillez entrer un mot de passe")
            return
        
        controller = VaultController(password)
        
        if controller.is_authenticated:
            self.controller = controller
            self.show_dashboard()
        else:
            self.login_view.show_error("Mot de passe incorrect ou trop court")
    
    def show_dashboard(self):
        self.dashboard_view = DashboardView(self, self.controller)
        self.dashboard_view.show()
    
    def logout(self):
        if self.controller:
            self.controller.logout()
        self.controller = None
        self.show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
