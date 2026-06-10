import tkinter as tk
from tkinter import ttk, messagebox
from .constants import *
from producto import Producto
from venta import Venta
from exceptions import ProductoInvalido, VentaInvalida

class TabRegistro:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  📝 Registro en Vivo  ")

        # Configurar un canvas para hacer scroll si la pantalla es pequeña
        canvas = tk.Canvas(self.frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Fila 1: Nuevo Producto
        frame_prod = tk.LabelFrame(scrollable_frame, text=" 📦 Registrar Nuevo Producto en Catálogo ", font=F_SUBTITLE, bg=CARD, fg=ACCENT1, padx=15, pady=10)
        frame_prod.pack(fill="x", pady=(0, 15), padx=5)

        tk.Label(frame_prod, text="Nombre del Producto:", font=F_BODY, bg=CARD, fg=TXT_SUB).grid(row=0, column=0, sticky="w", pady=6)
        self.txt_prod_nombre = ttk.Entry(frame_prod, width=30)
        self.txt_prod_nombre.grid(row=0, column=1, pady=6, padx=10, sticky="w")

        tk.Label(frame_prod, text="Precio Unitario ($):", font=F_BODY, bg=CARD, fg=TXT_SUB).grid(row=0, column=2, sticky="w", pady=6)
        self.txt_prod_precio = ttk.Entry(frame_prod, width=15)
        self.txt_prod_precio.grid(row=0, column=3, pady=6, padx=10, sticky="w")

        tk.Label(frame_prod, text="Categoría:", font=F_BODY, bg=CARD, fg=TXT_SUB).grid(row=1, column=0, sticky="w", pady=6)
        self.txt_prod_categoria = ttk.Entry(frame_prod, width=30)
        self.txt_prod_categoria.grid(row=1, column=1, pady=6, padx=10, sticky="w")

        tk.Label(frame_prod, text="Talla:", font=F_BODY, bg=CARD, fg=TXT_SUB).grid(row=1, column=2, sticky="w", pady=6)
        self.cb_prod_talla = ttk.Combobox(frame_prod, values=["XS", "S", "M", "L", "XL", "XXL", "N/A"], width=12, state="readonly")
        self.cb_prod_talla.grid(row=1, column=3, pady=6, padx=10, sticky="w")
        self.cb_prod_talla.current(6)

        tk.Label(frame_prod, text="Color:", font=F_BODY, bg=CARD, fg=TXT_SUB).grid(row=2, column=0, sticky="w", pady=6)
        self.txt_prod_color = ttk.Entry(frame_prod, width=30)
        self.txt_prod_color.grid(row=2, column=1, pady=6, padx=10, sticky="w")

        self.var_prod_suscripcion = tk.BooleanVar()
        self.chk_prod_suscripcion = ttk.Checkbutton(frame_prod, text="Ofrece Suscripción", variable=self.var_prod_suscripcion)
        self.chk_prod_suscripcion.grid(row=2, column=3, pady=6, padx=10, sticky="w")

        btn_guardar_prod = tk.Button(
            frame_prod, text="Añadir al Catálogo", command=self.ejecutar_registro_producto,
            font=F_BODY, bg=ACCENT1, fg=BG, activebackground=BG, activeforeground=ACCENT1,
            relief="flat", cursor="hand2", padx=15, pady=6
        )
        btn_guardar_prod.grid(row=3, column=0, columnspan=4, pady=(15, 5))

        # Fila 2: Nueva Transacción de Venta
        pad_venta = tk.LabelFrame(scrollable_frame, text=" 🛒 Registrar Nueva Transacción ", font=F_SUBTITLE, bg=BG, fg=ACCENT2, padx=15, pady=10)
        pad_venta.pack(fill="x", pady=10, padx=5)

        tk.Label(pad_venta, text="Producto del catálogo:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=0, column=0, sticky="w", pady=6)
        self.cb_venta_producto = ttk.Combobox(pad_venta, state="readonly", width=35)
        self.cb_venta_producto.grid(row=0, column=1, columnspan=2, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Cantidad:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=0, column=3, sticky="w", pady=6)
        self.txt_venta_cantidad = ttk.Entry(pad_venta, width=10)
        self.txt_venta_cantidad.grid(row=0, column=4, pady=6, padx=10, sticky="w")
        self.txt_venta_cantidad.insert(0, "1")

        tk.Label(pad_venta, text="Temporada:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=1, column=0, sticky="w", pady=6)
        self.cb_venta_temporada = ttk.Combobox(pad_venta, values=["Spring", "Summer", "Fall", "Winter"], width=26, state="readonly")
        self.cb_venta_temporada.grid(row=1, column=1, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Edad del Cliente:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=1, column=2, sticky="w", pady=6)
        self.txt_venta_edad = ttk.Entry(pad_venta, width=12)
        self.txt_venta_edad.grid(row=1, column=3, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Género:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=2, column=0, sticky="w", pady=6)
        self.cb_venta_genero = ttk.Combobox(pad_venta, values=["Male", "Female", "Other", "N/A"], width=26, state="readonly")
        self.cb_venta_genero.grid(row=2, column=1, pady=6, padx=10, sticky="w")
        self.cb_venta_genero.current(3)

        tk.Label(pad_venta, text="Ubicación (Estado):", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=2, column=2, sticky="w", pady=6)
        self.txt_venta_ubicacion = ttk.Entry(pad_venta, width=28)
        self.txt_venta_ubicacion.grid(row=2, column=3, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Método de Pago:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=3, column=0, sticky="w", pady=6)
        self.cb_venta_pago = ttk.Combobox(pad_venta, values=["Credit Card", "Debit Card", "Cash", "PayPal", "Venmo", "Bank Transfer", "N/A"], width=26, state="readonly")
        self.cb_venta_pago.grid(row=3, column=1, pady=6, padx=10, sticky="w")
        self.cb_venta_pago.current(6)

        tk.Label(pad_venta, text="Tipo de Envío:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=3, column=2, sticky="w", pady=6)
        self.cb_venta_envio = ttk.Combobox(pad_venta, values=["Free Shipping", "Standard", "Express", "Next Day Air", "2-Day Shipping", "Store Pickup", "N/A"], width=15, state="readonly")
        self.cb_venta_envio.grid(row=3, column=3, pady=6, padx=10, sticky="w")
        self.cb_venta_envio.current(6)

        self.var_venta_descuento = tk.BooleanVar()
        self.chk_venta_descuento = ttk.Checkbutton(pad_venta, text="Descuento Aplicado", variable=self.var_venta_descuento)
        self.chk_venta_descuento.grid(row=4, column=1, pady=6, padx=10, sticky="w")

        self.var_venta_promo = tk.BooleanVar()
        self.chk_venta_promo = ttk.Checkbutton(pad_venta, text="Código Promo Usado", variable=self.var_venta_promo)
        self.chk_venta_promo.grid(row=4, column=3, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Calificación (1-5):", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=5, column=0, sticky="w", pady=6)
        self.txt_venta_calif = ttk.Entry(pad_venta, width=28)
        self.txt_venta_calif.grid(row=5, column=1, pady=6, padx=10, sticky="w")

        tk.Label(pad_venta, text="Compras Previas:", font=F_BODY, bg=BG, fg=TXT_SUB).grid(row=5, column=2, sticky="w", pady=6)
        self.txt_venta_previas = ttk.Entry(pad_venta, width=12)
        self.txt_venta_previas.grid(row=5, column=3, pady=6, padx=10, sticky="w")

        btn_guardar_venta = tk.Button(
            pad_venta, text="Registrar Transacción", command=self.ejecutar_registro_venta,
            font=F_BODY, bg=ACCENT2, fg=BG, activebackground=BG, activeforeground=ACCENT2,
            relief="flat", cursor="hand2", padx=15, pady=6
        )
        btn_guardar_venta.grid(row=6, column=0, columnspan=5, pady=(15, 5))

    def actualizar_combo_productos(self):
        nombres = [p.get_nombre() for p in self.app.sistema.obtener_productos()]
        self.cb_venta_producto["values"] = nombres
        if nombres:
            self.cb_venta_producto.current(0)

    def ejecutar_registro_producto(self):
        try:
            nombre = self.txt_prod_nombre.get().strip()
            precio_raw = self.txt_prod_precio.get().strip()
            categoria = self.txt_prod_categoria.get().strip() or "General"
            talla = self.cb_prod_talla.get()
            color = self.txt_prod_color.get().strip()
            suscripcion = self.var_prod_suscripcion.get()

            if not nombre:
                raise ProductoInvalido("El nombre del producto no puede estar vacío.")
            if not precio_raw:
                raise ProductoInvalido("El precio del producto no puede estar vacío.")
            
            try:
                precio = float(precio_raw)
            except ValueError:
                raise ProductoInvalido("El precio debe ser un número válido.")

            nuevo_producto = Producto(
                nombre=nombre, precio_unitario=precio, categoria=categoria,
                color=color, talla=talla, suscripcion=suscripcion
            )

            if self.app.sistema.registrar_producto(nuevo_producto):
                messagebox.showinfo("Registro Exitoso", f"El producto '{nombre}' fue agregado al catálogo.")
                self.actualizar_combo_productos()
                # Limpiar formulario
                self.txt_prod_nombre.delete(0, tk.END)
                self.txt_prod_precio.delete(0, tk.END)
                self.txt_prod_categoria.delete(0, tk.END)
                self.txt_prod_color.delete(0, tk.END)
                self.var_prod_suscripcion.set(False)
                # Actualizar datos
                self.app._sincronizar_datos()
            else:
                messagebox.showwarning("Producto Duplicado", f"El producto '{nombre}' ya existe en el catálogo.")
        except ProductoInvalido as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ejecutar_registro_venta(self):
        try:
            nombre_prod = self.cb_venta_producto.get()
            if not nombre_prod:
                raise VentaInvalida("Debe seleccionar un producto del catálogo.")

            producto_obj = self.app.sistema._buscar_producto(nombre_prod)
            
            cantidad_raw = self.txt_venta_cantidad.get().strip()
            temporada = self.cb_venta_temporada.get() or "General"
            edad_raw = self.txt_venta_edad.get().strip()
            genero = self.cb_venta_genero.get()
            ubicacion = self.txt_venta_ubicacion.get().strip()
            metodo_pago = self.cb_venta_pago.get()
            tipo_envio = self.cb_venta_envio.get()
            descuento = self.var_venta_descuento.get()
            promo = self.var_venta_promo.get()
            calif_raw = self.txt_venta_calif.get().strip()
            previas_raw = self.txt_venta_previas.get().strip()

            try:
                cantidad = float(cantidad_raw) if cantidad_raw else 1.0
            except ValueError:
                raise VentaInvalida("La cantidad debe ser un número válido.")

            try:
                edad = int(edad_raw) if edad_raw else 0
            except ValueError:
                raise VentaInvalida("La edad debe ser un número entero válido.")

            try:
                calificacion = float(calif_raw) if calif_raw else 0.0
            except ValueError:
                raise VentaInvalida("La calificación debe ser un número válido.")

            try:
                compras_previas = int(previas_raw) if previas_raw else 0
            except ValueError:
                raise VentaInvalida("El número de compras previas debe ser un número entero.")

            nueva_venta = Venta(
                producto=producto_obj, cantidad=cantidad, temporada=temporada,
                monto=producto_obj.get_precio_unitario() * cantidad, edad=edad, genero=genero,
                ubicacion=ubicacion, metodo_pago=metodo_pago, tipo_envio=tipo_envio,
                descuento=descuento, codigo_promo=promo, calificacion=calificacion,
                frecuencia_compra="Regular" if compras_previas > 0 else "New", compras_previas=compras_previas
            )

            # Persist and append to CSV immediately
            ruta_actual = self.app.ruta_csv_actual
            self.app.sistema.guardar_venta_csv(nueva_venta, ruta_actual)
            self.app.sistema.registrar_venta(nueva_venta)

            messagebox.showinfo("Registro Exitoso", f"La transacción de venta fue registrada correctamente.\n\nDatos guardados en {ruta_actual}.")
            
            # Sincronización en caliente
            self.app._sincronizar_datos()

            # Limpiar formulario
            self.txt_venta_cantidad.delete(0, tk.END)
            self.txt_venta_cantidad.insert(0, "1")
            self.txt_venta_edad.delete(0, tk.END)
            self.txt_venta_ubicacion.delete(0, tk.END)
            self.txt_venta_calif.delete(0, tk.END)
            self.txt_venta_previas.delete(0, tk.END)
            self.var_venta_descuento.set(False)
            self.var_venta_promo.set(False)
            
        except VentaInvalida as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
