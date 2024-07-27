from django.shortcuts import render, redirect
#CLASE PARA CREAR USUARIOS
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError #FOR ESPECIFIC ERROR
from django.contrib.auth import login, logout, authenticate # FOR SESSION CREATION
from user.models import User
from django.contrib.auth.decorators import login_required #FOR PREVENT UNAUTHORIZED ACCESS
#models 
from .models import management, tipos_gasto, gastos
#Libraries
from decimal import Decimal
from datetime import date
from django.shortcuts import get_object_or_404
from django.contrib import messages

# VIEWS
@login_required
def home(request):
    # Verificar si el usuario ya tiene un presupuesto asignado
    existing_entry = management.objects.filter(id_usuario=request.user, fecha_fin__isnull=True)
    
    if existing_entry:
        # Redirigir o mostrar una vista diferente si el presupuesto ya está asignado
        return redirect('analisis')  # o renderizar una plantilla diferente
    if request.method == 'GET':
        return render(request, 'home.html')
    
@login_required
def analisis(request):
    if request.method == 'GET':
       # Obtener el presupuesto del usuario activo que no tiene fecha de fin
        presupuesto = get_object_or_404(management, id_usuario=request.user, fecha_fin__isnull=True)

        # Obtener todos los gastos relacionados con este presupuesto
        todos_gastos = gastos.objects.filter(id_presupuesto=presupuesto).order_by('id_tipo_gasto')
        #Obtener todos los tipos de gastos y su id
        all_types = tipos_gasto.objects.all()
        # Obtener los nombres de los tipos de gastos relacionados con los gastos actuales
        tipos_gastos = tipos_gasto.objects.filter(id_gasto__in=todos_gastos.values_list('id_tipo_gasto', flat=True))
        
        # Crear un diccionario para mapear id_tipo_gasto a su nombre
        tipos_gastos_dict = {tipo.id_gasto: tipo.nombre_gasto for tipo in tipos_gastos}
        
        # Combinar los datos en una lista de diccionarios
        gastos_con_tipos = []
        for gasto in todos_gastos:
            gastos_con_tipos.append({
                'id_gasto': gasto.id_gasto,
                'nombre_gasto': gasto.nombre_gasto,
                'tipo_gasto': tipos_gastos_dict.get(gasto.id_tipo_gasto.id_gasto, 'N/A'),
                'monto_gasto': gasto.monto_gasto,
                'fecha_gasto': gasto.fecha_gasto,
            })
            #print(gastos_con_tipos)
        # Pasar los datos a la plantilla
        context = {
            'datos': presupuesto, 
            'all_types': all_types,
            'gastos_con_tipos': gastos_con_tipos,
        }
        return render(request, 'analisis.html', context)
    elif request.method == 'POST': 
        # Caso 1: AÑADIR MAS DINERO AL PRESUPUESTO
        if 'submitPresupuesto' in request.POST:
            nuevo_presupuesto = Decimal(request.POST.get('presupuesto'))
            usuario = request.user

            # Recuperar la instancia del modelo existente para el usuario actual
            try:
                entrada_existente = management.objects.get(id_usuario=usuario)
                # Actualizar el presupuesto sumando el nuevo valor al existente, ademas el disponible es el mismo
                entrada_existente.presupuesto = entrada_existente.presupuesto + nuevo_presupuesto
                entrada_existente.save()
                entrada_existente.disponible = entrada_existente.disponible + nuevo_presupuesto
                entrada_existente.save()
                messages.success(request, "Presupuesto actualizado con éxito")
                return redirect('analisis')
            except management.DoesNotExist:
                # Si no existe una entrada, crear una nueva
                new_entry = management(presupuesto=nuevo_presupuesto, id_usuario=usuario)
                new_entry.save()
                messages.success(request, "Presupuesto creado con éxito")
                return redirect('analisis')
            
        # Caso 2: Enviar json con los datos del gasto al campo gastos
        elif 'submitGasto' in request.POST:
            nombre_gasto = request.POST.get('nombre_gasto')
            monto_gasto = Decimal(request.POST.get('monto_gasto'))
            nombre_tipo_gasto = request.POST.get('select_gasto')
            fecha_gasto = request.POST.get('date_gasto')
            
            # Obtener el tipo de gasto por su nombre
            tipo_gasto = get_object_or_404(tipos_gasto, nombre_gasto=nombre_tipo_gasto)
            
            # Obtener el presupuesto del usuario activo que no tiene fecha de fin
            presupuesto = get_object_or_404(management, id_usuario=request.user, fecha_fin__isnull=True)
            
            try:
                # Buscar si ya existe un gasto con el mismo nombre en el presupuesto actual
                gasto_existente = gastos.objects.get(id_presupuesto=presupuesto, nombre_gasto=nombre_gasto)
                
                # Si existe, actualizar el monto del gasto y la fecha
                gasto_existente.monto_gasto += monto_gasto
                gasto_existente.fecha_gasto = fecha_gasto
                gasto_existente.save()
                messages.success(request, "Gasto actualizado con éxito")
                return redirect('analisis')
            except gastos.DoesNotExist:
                # Si no existe un gasto con ese nombre, crear uno nuevo
                new_entry = gastos(
                    id_presupuesto=presupuesto,
                    id_tipo_gasto=tipo_gasto,
                    nombre_gasto=nombre_gasto,
                    monto_gasto=monto_gasto,
                    fecha_gasto=fecha_gasto
                )
                new_entry.save()
                messages.success(request, "Nuevo gasto creado con éxito")
                
            # Actualizar el presupuesto
            try:
                presupuesto.gastado += monto_gasto
                presupuesto.disponible -= monto_gasto
                presupuesto.save()
                #messages.success(request, "Presupuesto actualizado con éxito")

                return redirect('analisis')
                
            except management.DoesNotExist:
                messages.error(request, "Presupuesto no existe")
            
            return redirect('analisis')
        elif 'filtrar' in request.POST:
            nombre_tipo_gasto = request.POST.get('tipo_gasto')
            
            # Obtener el presupuesto del usuario activo que no tiene fecha de fin
            presupuesto = get_object_or_404(management, id_usuario=request.user, fecha_fin__isnull=True)

            # Obtener todos los gastos relacionados con este presupuesto
            if nombre_tipo_gasto:
                todos_gastos = gastos.objects.filter(id_presupuesto=presupuesto, id_tipo_gasto=nombre_tipo_gasto).order_by('id_tipo_gasto')
            else:
                todos_gastos = gastos.objects.filter(id_presupuesto=presupuesto).order_by('id_tipo_gasto')

            #Obtener todos los tipos de gastos y su id
            all_types = tipos_gasto.objects.all()
            
            # Obtener los nombres de los tipos de gastos relacionados con los gastos actuales
            tipos_gastos = tipos_gasto.objects.filter(id_gasto__in=todos_gastos.values_list('id_tipo_gasto', flat=True))
            
            # Crear un diccionario para mapear id_tipo_gasto a su nombre
            tipos_gastos_dict = {tipo.id_gasto: tipo.nombre_gasto for tipo in tipos_gastos}
            
            # Combinar los datos en una lista de diccionarios
            gastos_con_tipos = []
            for gasto in todos_gastos:
                gastos_con_tipos.append({
                    'nombre_gasto': gasto.nombre_gasto,
                    'tipo_gasto': tipos_gastos_dict.get(gasto.id_tipo_gasto.id_gasto, 'N/A'),
                    'monto_gasto': gasto.monto_gasto,
                    'fecha_gasto': gasto.fecha_gasto,
                })
            
            # Pasar los datos a la plantilla
            context = {
                'datos': presupuesto,
                'all_types': all_types,  
                'gastos_con_tipos': gastos_con_tipos,
            }
            
            return render(request, 'analisis.html', context)
        
        elif 'deleteGasto' in request.POST:
            #print("DELETE ")
            id_gasto = request.POST.get('id_gasto')
            gasto = gastos.objects.get(id_gasto=id_gasto)
            try:
                # Obtener el presupuesto antes de eliminar el gasto
                presupuesto = get_object_or_404(management, id_usuario=request.user, fecha_fin__isnull=True)
                monto_gasto = gasto.monto_gasto

                # Eliminar el gasto
                gasto.delete()

                # Actualizar el presupuesto
                presupuesto.gastado -= monto_gasto
                presupuesto.disponible += monto_gasto
                presupuesto.save()

                messages.success(request, "Gasto eliminado y presupuesto actualizado")
                return redirect('analisis')
            except IntegrityError:
                messages.error(request, "Error al eliminar el gasto")
                return redirect('analisis')
        elif 'editGasto' in request.POST:
            id_gasto = request.POST.get('gasto_id')  # Este debería coincidir con el input hidden en el formulario
            nombre_gasto = request.POST.get('nombre_gasto')
            monto_gasto = request.POST.get('monto_gasto')
            fecha_gasto = request.POST.get('date_gasto')
            tipo_gasto = request.POST.get('select_gasto')
            print("EDIT ", id_gasto, nombre_gasto, monto_gasto, fecha_gasto, tipo_gasto)
            
            if None in [id_gasto, nombre_gasto, monto_gasto, fecha_gasto, tipo_gasto]:
                messages.error(request, "Faltan datos en el formulario")
                return redirect('analisis')

            try:
                gasto = gastos.objects.get(id_gasto=id_gasto)
                #obtener el id del tipo gasto con el nombre
                id_tipo_gasto = tipos_gasto.objects.get(nombre_gasto=tipo_gasto)

                # Obtener el presupuesto del usuario activo que no tiene fecha de fin
                presupuesto = get_object_or_404(management, id_usuario=request.user, fecha_fin__isnull=True)
                # Actualizar el gasto
                presupuesto.gastado -= gasto.monto_gasto
                presupuesto.disponible += gasto.monto_gasto

                monto_gasto_decimal = Decimal(monto_gasto)
                gasto.nombre_gasto = nombre_gasto
                gasto.monto_gasto = monto_gasto_decimal
                gasto.fecha_gasto = fecha_gasto
                gasto.id_tipo_gasto = id_tipo_gasto
                gasto.save()
                # Actualizar el presupuesto
                presupuesto.gastado += monto_gasto_decimal
                presupuesto.disponible -= monto_gasto_decimal
                presupuesto.save()

                messages.success(request, "Gasto actualizado")
                return redirect('analisis')
            except gastos.DoesNotExist:
                messages.error(request, "El gasto no existe")
                return redirect('analisis')
            except IntegrityError:
                messages.error(request, "Error al actualizar el gasto")
                return redirect('analisis')
        return render(request, 'analisis.html')



def ingreso(request):     
    if request.method == 'POST':
        presupuesto = request.POST.get('presupuesto')
        usuario = request.user # Obtener el id del usuario actual

        # Crear una nueva instancia del modelo y guardar los datos en la base de datos
        new_entry = management(presupuesto=presupuesto, disponible=presupuesto ,fecha_inicio=date.today(), id_usuario=usuario)
        new_entry.save()

        return redirect('analisis')
    
    

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirige a la página principal si ya ha iniciado sesión
    #make diferent actions for POST and GET
    if request.method == 'POST':
        if(request.POST['password1'] == request.POST['password2']):
            #verify if username already exists if not then create the user
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save() # save the user in the database
                login(request, user) #create the session
                return redirect('home')
            except IntegrityError:
                return render(request, 'signup.html',{
                'form': UserCreationForm(),
                'error': 'username already taken'
            })

        else:
            return render(request, 'signup.html',{
                'form': UserCreationForm(),
                'error': 'Passwords do not match'
            })
    else:
        #GET
        return render(request, 'signup.html',{
            'form': UserCreationForm()
        })
    
def signout(request):
    #FOR SESSION DESTROY
    logout(request)
    return redirect('signup')

def init_sesion(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirige a la página principal si ya ha iniciado sesión
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password']) #AUTHENTICATE THE USER
        if user is None:
            return render(request, 'login.html', {
                'form': AuthenticationForm(),
                'error': 'username or password are not correct'
            })
        else:
            login(request, user)
            return redirect('home')
