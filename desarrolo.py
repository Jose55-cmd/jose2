from django.db import models
from decimal import Decimal

# --- CATÁLOGOS ---

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_iso = models.CharField(max_length=3, null=True, blank=True)

    class Meta:
        db_table = 'cat_paises'

class Estado(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, db_column='id_pais')
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'cat_estados'

class Ciudad(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, db_column='id_estado')
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'cat_ciudades'

class EstatusPoliza(models.Model):
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'cat_estatus_poliza'

class EstatusSiniestro(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'cat_estatus_siniestro'

class Moneda(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=5, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'cat_monedas'

class Marca(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'cat_marcas'

class Modelo(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, db_column='id_marca')
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'cat_modelos'

# --- ENTIDADES PRINCIPALES ---

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('NATURAL', 'Natural'),
        ('JURIDICA', 'Jurídica'),
        ('GUBERNAMENTAL', 'Gubernamental'),
    ]
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]

    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CHOICES)
    tipo_documento = models.CharField(max_length=3)
    numero_documento = models.CharField(max_length=20)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, null=True, blank=True)
    telefono_movil = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100)
    direccion = models.TextField(null=True, blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, db_column='id_ciudad')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'clientes'
        unique_together = ('tipo_documento', 'numero_documento')

class CompaniaSeguros(models.Model):
    rif = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(null=True, blank=True)
    telefono_contacto = models.CharField(max_length=20, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'companias_seguros'

class Ramo(models.Model):
    nombre_ramo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'ramos'

class Producto(models.Model):
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, db_column='id_ramo')
    nombre_producto = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'productos'

class Intermediario(models.Model):
    nombre_completo = models.CharField(max_length=150)
    codigo_sudeaseg = models.CharField(max_length=50, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'intermediarios'

class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE, db_column='id_modelo')
    anio = models.IntegerField(db_column='año')
    placa = models.CharField(max_length=20, unique=True)
    serial_motor = models.CharField(max_length=50)
    serial_carroceria = models.CharField(max_length=50)
    color = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'vehiculos'

# --- OPERACIONES ---

class Poliza(models.Model):
    numero_poliza = models.CharField(max_length=50)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, db_column='id_vehiculo')
    compania = models.ForeignKey(CompaniaSeguros, on_delete=models.CASCADE, db_column='id_compania')
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, db_column='id_ramo')
    intermediario = models.ForeignKey(Intermediario, on_delete=models.SET_NULL, null=True, db_column='id_intermediario')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    estatus = models.ForeignKey(EstatusPoliza, on_delete=models.PROTECT, db_column='id_estatus')
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, db_column='id_moneda')
    suma_asegurada = models.DecimalField(max_digits=15, decimal_places=2)
    prima_neta = models.DecimalField(max_digits=15, decimal_places=2)
    vigencia_desde = models.DateField()
    vigencia_hasta = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'polizas'

class ReciboPrima(models.Model):
    ESTATUS_CHOICES = [('Pendiente', 'Pendiente'), ('Pagado', 'Pagado'), ('Anulado', 'Anulado')]
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, db_column='id_poliza')
    monto_cuota = models.DecimalField(max_digits=15, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estatus_cobro = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='Pendiente')

    class Meta:
        db_table = 'recibos_primas'

class Siniestro(models.Model):
    numero_siniestro = models.CharField(max_length=50)
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, db_column='id_poliza')
    estatus = models.ForeignKey(EstatusSiniestro, on_delete=models.PROTECT, db_column='id_estatus')
    fecha_ocurrencia = models.DateTimeField()
    descripcion_evento = models.TextField()
    monto_estimado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        db_table = 'siniestros'