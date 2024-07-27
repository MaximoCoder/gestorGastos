from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

    
class management(models.Model):
    id_presupuesto = models.AutoField(primary_key=True)
    presupuesto = models.DecimalField(max_digits=9, decimal_places=2)  # Hasta 999,999.99
    disponible = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=True)  # Hasta 999,999.99
    gastado = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=True)  # Hasta 999,999.99
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True)  # Puede ser NULL

class tipos_gasto(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    nombre_gasto = models.CharField(max_length=30)

class gastos (models.Model):
    id_gasto = models.AutoField(primary_key=True)
    id_presupuesto = models.ForeignKey(management, on_delete=models.CASCADE)
    id_tipo_gasto = models.ForeignKey(tipos_gasto, on_delete=models.CASCADE)
    nombre_gasto = models.CharField(max_length=30)
    monto_gasto = models.DecimalField(max_digits=9, decimal_places=2)  # Hasta 999,999.99
    fecha_gasto = models.DateField()
