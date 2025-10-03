from django.db import models


class Carrera(models.Model):
    carrera_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.descripcion


class Asignatura(models.Model):
    asignatura_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    carrera = models.ForeignKey(
        "Carrera", on_delete=models.CASCADE, related_name="asignaturas", null=True, blank=True
    )

    def __str__(self):
        return self.descripcion


class Partida(models.Model):
    partida_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200)
    asignatura = models.ForeignKey(
        "Asignatura", on_delete=models.CASCADE, related_name="partidas"
    )

    def __str__(self):
        return self.descripcion


class ProgramaAnalitico(models.Model):
    linea_educativa_id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    contexto = models.TextField()
    asignatura = models.ForeignKey(
        "Asignatura", on_delete=models.CASCADE, related_name="programas_analiticos"
    )

    def __str__(self):
        return self.titulo
    
    def renumerar_preguntas_secuencialmente(self):
        """Renumera todas las preguntas del programa analítico de manera secuencial"""
        unidades = self.unidades.all().order_by('numero_unidad')
        numero_actual = 1
        
        for unidad in unidades:
            preguntas = unidad.preguntas.all().order_by('numero')
            for pregunta in preguntas:
                pregunta.numero = numero_actual
                pregunta.save()
                numero_actual += 1
        
        return numero_actual - 1  # Retorna el total de preguntas renumeradas


class Unidad(models.Model):
    unidad_id = models.AutoField(primary_key=True)
    numero_unidad = models.IntegerField()
    descripcion = models.CharField(max_length=200)
    num_preguntas = models.IntegerField()
    programa_analitico = models.ForeignKey(
        ProgramaAnalitico, on_delete=models.CASCADE, related_name="unidades"
    )

    def __str__(self):
        return f"Unidad {self.numero_unidad}: {self.descripcion}"
    
    def generar_preguntas_automaticamente(self):
        """Genera las preguntas automáticamente con opciones básicas y numeración secuencial"""
        
        # Calcular el número de inicio basándose en las preguntas existentes en el programa analítico
        preguntas_existentes = Pregunta.objects.filter(
            unidad__programa_analitico=self.programa_analitico
        ).exclude(unidad=self)  # Excluir las preguntas de la unidad actual
        
        numero_inicio = 1
        if preguntas_existentes.exists():
            numero_inicio = preguntas_existentes.aggregate(
                max_numero=models.Max('numero')
            )['max_numero'] + 1
        
        # Crear preguntas según num_preguntas con numeración secuencial
        for i in range(self.num_preguntas):
            numero_pregunta = numero_inicio + i
            enunciado = f"Pregunta {numero_pregunta} sobre {self.descripcion}. Explique detalladamente."
            
            pregunta = Pregunta.objects.create(
                enunciado=enunciado,
                numero=numero_pregunta,
                unidad=self
            )
            
            # Crear opciones básicas automáticamente
            opciones_basicas = [
                f"Opción correcta para {self.descripcion}",
                f"Opción parcial para {self.descripcion}",
                f"Opción incorrecta relacionada con {self.descripcion}",
                f"Opción no relacionada con {self.descripcion}"
            ]
            
            for j, opcion_texto in enumerate(opciones_basicas):
                Opcion.objects.create(
                    opcion=opcion_texto,
                    es_correcta=(j == 0),  # Primera opción es correcta por defecto
                    pregunta=pregunta
                )
        
        return True


class Pregunta(models.Model):
    pregunta_id = models.AutoField(primary_key=True)
    enunciado = models.TextField()
    numero = models.IntegerField()
    unidad = models.ForeignKey(
        Unidad, on_delete=models.CASCADE, related_name="preguntas"
    )

    def __str__(self):
        return f"{self.numero}. {self.enunciado[:50]}..."


class Opcion(models.Model):
    opcion_id = models.AutoField(primary_key=True)
    opcion = models.TextField()
    media_url = models.URLField(blank=True, null=True)  # puede ser archivo o imagen si prefieres
    es_correcta = models.BooleanField(default=False)
    pregunta = models.ForeignKey(
        Pregunta, on_delete=models.CASCADE, related_name="opciones"
    )

    def __str__(self):
        return f"Opción: {self.opcion[:30]}{' (Correcta)' if self.es_correcta else ''}"


