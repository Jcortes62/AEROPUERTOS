import customtkinter as ctk

# Configurar el tema y apariencia
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("green")  # "blue", "dark-blue", "green"

# Crear ventana principal
app = ctk.CTk()
app.geometry("800x600")
app.title("App con Colores Personalizados")

# Personalizar el fondo de la ventana
app.configure(bg="#1e1e2e")  # Fondo oscuro personalizado

# Etiqueta con color personalizado
label = ctk.CTkLabel(app, text="¡Bienvenido!", font=("Arial", 24), text_color="#ffffff")
label.pack(pady=40)

# Botón con colores personalizados
boton = ctk.CTkButton(app, text="Presióname", fg_color="#4CAF50", hover_color="#45a049")
boton.pack(pady=20)

# Campo de entrada con bordes y color de texto
entry = ctk.CTkEntry(app, placeholder_text="Escribe aquí", fg_color="#2a2d3e", text_color="#ffffff", border_color="#4CAF50")
entry.pack(pady=20)

# Iniciar la aplicación
app.mainloop()
