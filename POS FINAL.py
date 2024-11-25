import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
from abc import ABC, abstractmethod
from tkinter import simpledialog
import sys
import os

def obtener_ruta_imagen(imagen):
    
    if getattr(sys, 'frozen', False):  
        ruta_carpeta = os.path.dirname(sys.executable)
    else:  
        ruta_carpeta = os.path.dirname(__file__)

    return os.path.join(ruta_carpeta, 'imagenes', imagen)


class Producto(ABC):
    def __init__(self, nombre, precio, cantidad=1):
        self._nombre = nombre
        self._precio = precio
        self._cantidad = cantidad

    @property
    def nombre(self):
        return self._nombre

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if valor < 0:
            raise ValueError("El precio no puede ser negativo")
        self._precio = valor

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if valor < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self._cantidad = valor

    @abstractmethod
    def calcular_precio_final(self, aplicar_descuento=0):
        pass


class ProductoFisico(Producto):
    def __init__(self, nombre, precio, cantidad=1):
        super().__init__(nombre, precio, cantidad)

    def calcular_precio_final(self, aplicar_descuento=0):
        precio_base = self._precio * self._cantidad
        if aplicar_descuento > 0:
            precio_base = precio_base * (1 - aplicar_descuento / 100)
        return precio_base



productos = {
    "Bebidas": [
        ProductoFisico("Agua Horchata", 20),
        ProductoFisico("Agua Jamaica", 15),
        ProductoFisico("Agua Tamarindo", 15),
    ],
    "Comida": [
        ProductoFisico("Sandwich Sencillo", 50),
        ProductoFisico("Pizza Pepperoni", 100),
        ProductoFisico("Lasagna", 150),
    ],
}


root = tk.Tk()
root.title("Proyecto LOAO")
root.geometry("1000x600")
root.configure(bg="white")


frame_categorias = tk.Frame(root, bg="lightgray", width=200)
frame_categorias.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

frame_productos = tk.Frame(root, bg="white")
frame_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_carrito = tk.Frame(root, bg="lightgray", width=300)
frame_carrito.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

title_font = font.Font(family="Helvetica", size=24, weight="bold")
button_font = font.Font(family="Helvetica", size=12)

titulo = tk.Label(root, text="Restaurante L", bg="green", fg="white", font=title_font)
titulo.pack(fill=tk.X)


def mostrar_productos(categoria):
    for widget in frame_productos.winfo_children():
        widget.destroy()

    for producto in productos[categoria]:  
        try:
            image = Image.open(obtener_ruta_imagen(f"{producto.nombre.replace(' ', '')}.jfif"))
        except FileNotFoundError:
            image = Image.open(obtener_ruta_imagen("error.jfif"))  

        image = image.resize((100, 100), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        btn = tk.Button(
            frame_productos,
            image=photo,
            text=f"{producto.nombre}\n${producto.precio}",
            compound=tk.TOP,
            font=button_font,
            command=lambda p=producto: agregar_al_carrito(p),
        )
        btn.image = photo  
        btn.pack(side=tk.TOP, padx=10, pady=5)


carrito = []

def agregar_al_carrito(producto):
    for item in carrito:
        if item.nombre == producto.nombre:
            item.cantidad += 1
            actualizar_carrito() 
            return
    
    carrito.append(producto)
    actualizar_carrito()

def actualizar_carrito():
    listbox_carrito.delete(0, tk.END)
    for producto in carrito:
        listbox_carrito.insert(
            tk.END,
            f"{producto.nombre} - ${producto.precio} (x{producto.cantidad})",
        )


def obtener_subtotal():
    subtotal = 0
    for item in carrito:
        subtotal += item.calcular_precio_final()
    return subtotal


def calcular_total():
    if len(carrito) == 0:
        messagebox.showinfo("Total", "El carrito está vacío.")
        return

    print("Carrito actual:", [(item.nombre, item.precio, item.cantidad) for item in carrito])

    try:
        subtotal = sum(item.precio * item.cantidad for item in carrito)
        iva = subtotal * 0.16
        total = subtotal + iva

        messagebox.showinfo(
            "Total",
            f"Subtotal: ${subtotal:.2f}\nIVA (16%): ${iva:.2f}\nTotal: ${total:.2f}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema al calcular el total: {str(e)}")


carrito_descuento = []

def aplicar_descuento():
    global carrito_descuento  
    try:
        descuento = simpledialog.askfloat("Descuento", "Ingresa el porcentaje de descuento:")
        if descuento is None or descuento < 0 or descuento > 100:
            messagebox.showerror("Error", "Ingresa un valor válido entre 0 y 100.")
            return

        carrito_descuento = []  
        for producto in carrito:
            precio_descuento = producto.precio * producto.cantidad * (1 - descuento / 100)
            carrito_descuento.append((producto.nombre, precio_descuento))

        actualizar_carrito_descuento(carrito_descuento)

        messagebox.showinfo("Éxito", f"Se aplicó un descuento del {descuento:.2f}%.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo aplicar el descuento: {str(e)}")

def buscar_producto():
    termino = tk.simpledialog.askstring("Buscar", "Ingresa el nombre del producto:")
    if termino:
        for widget in frame_productos.winfo_children():
            widget.destroy()
        for categoria in productos.values():
            for producto in categoria:
                if termino.lower() in producto.nombre.lower():
                    try:
                        image = Image.open(obtener_ruta_imagen(f"{producto.nombre.replace(' ', '')}.jfif"))
                    except FileNotFoundError:
                        image = Image.open(obtener_ruta_imagen("error.jfif"))
                    
                    image = image.resize((100, 100), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    btn = tk.Button(
                        frame_productos,
                        image=photo,
                        text=f"{producto.nombre}\n${producto.precio}",
                        compound=tk.TOP,
                        font=button_font,
                        command=lambda p=producto: agregar_al_carrito(p),
                    )
                    btn.image = photo
                    btn.pack(side=tk.TOP, padx=10, pady=5)



def procesar_compra():
    global carrito_descuento 
    
    if len(carrito) == 0:
        messagebox.showinfo("Error", "El carrito está vacío. Agrega productos antes de procesar la compra.")
        return

    if not carrito_descuento:
        carrito_descuento = [(producto.nombre, producto.calcular_precio_final()) for producto in carrito]  

    subtotal = sum(item[1] for item in carrito_descuento)
    iva = subtotal * 0.16
    total = subtotal + iva

    resumen = "\n".join([f"{item[0]}: ${item[1]:.2f}" for item in carrito_descuento])
    ticket = (
        f"---- Ticket de Compra ----\n\n"
        f"{resumen}\n"
        f"Subtotal: ${subtotal:.2f}\n"
        f"IVA (16%): ${iva:.2f}\n"
        f"Total: ${total:.2f}\n"
        f"---------------------------"
    )

    mostrar_ticket(ticket)
    carrito.clear()
    carrito_descuento.clear() 
    listbox_carrito.delete(0, tk.END)

def mostrar_ticket(ticket):
    ticket_window = tk.Toplevel(root)
    ticket_window.title("Ticket de Compra")
    ticket_label = tk.Label(ticket_window, text=ticket, font=button_font, justify=tk.LEFT)
    ticket_label.pack(padx=10, pady=10)


def actualizar_carrito_descuento(carrito_descuento):
    listbox_carrito.delete(0, tk.END)
    for item in carrito_descuento:
        listbox_carrito.insert(tk.END, f"{item[0]} - ${item[1]:.2f}")


# BOTONCITOS
for categoria in productos:
    btn = tk.Button(
        frame_categorias,
        text=categoria,
        bg="white",  
        fg="black",  
        font=button_font,
        command=lambda c=categoria: mostrar_productos(c),
    )
    btn.pack(side=tk.TOP, pady=5, fill=tk.X)

listbox_carrito = tk.Listbox(frame_carrito, font=button_font, bg="white")
listbox_carrito.pack(fill=tk.BOTH, expand=True, pady=10)

btn_total = tk.Button(
    frame_carrito,
    text="Calcular Total",
    font=button_font,
    bg="green",  
    fg="white",  
    command=calcular_total,
)
btn_total.pack(pady=10, fill=tk.X)

btn_descuento = tk.Button(
    frame_carrito,
    text="Aplicar Descuento",
    font=button_font,
    bg="blue",  
    fg="white",  
    command=aplicar_descuento,
)
btn_descuento.pack(pady=10, fill=tk.X)

btn_buscar = tk.Button(
    frame_carrito,
    text="Buscar Producto",
    font=button_font,
    bg="orange",  
    fg="white",  
    command=buscar_producto,
)
btn_buscar.pack(pady=10, fill=tk.X)

btn_procesar_compra = tk.Button(
    frame_carrito, 
    text="Procesar Compra", 
    font=button_font, 
    bg="blue",  
    fg="white",  
    command=procesar_compra
)
btn_procesar_compra.pack(pady=10, fill=tk.X)

root.mainloop()

