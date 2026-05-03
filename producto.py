from exceptions import ProductoInvalido
class Producto:
   def __init__(self,nombre,precio_unitario,cantidad):
       if nombre != str:
           raise ProductoInvalido("El producto debe ser un nombre, no numeros")
       if nombre == "":
           raise ProductoInvalido("El nombre del producto no puede estar vacío.")
       if precio_unitario < 0:
           raise ProductoInvalido("El precio no puede ser negativo.")
       if cantidad < 0:
           raise ProductoInvalido("La cantidad no puede ser negativa.")
       self.nombre = nombre
       self.precio = precio_unitario
       self.cantidad = cantidad

    @property
   
    def nombre(self):
      return self.nombre
   
    def precio(self):
      return self.precio_unitario 

       