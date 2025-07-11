# Mejoras del Modelo de Usuario - Experienciaas

## Resumen de Cambios

Se ha mejorado significativamente el modelo de usuario para una plataforma de eventos, añadiendo campos esenciales para la gestión de perfiles de usuarios y participantes en eventos.

## Nuevos Campos Añadidos

### Información Personal
- **name**: Nombre completo del usuario (mejorado con mejor traducción)
- **birth_date**: Fecha de nacimiento con validación de edad (mínimo 13 años)
- **gender**: Género con opciones (Masculino, Femenino, Otro, Prefiero no decir)
- **bio**: Biografía personal (máximo 500 caracteres)
- **avatar**: Foto de perfil del usuario

### Información de Contacto
- **country_code**: Código de país para teléfono (con lista predefinida)
- **phone_number**: Número de teléfono con validación
- **country**: País de residencia
- **city**: Ciudad de residencia
- **address**: Dirección completa (opcional)
- **postal_code**: Código postal

### Información Profesional
- **occupation**: Ocupación o profesión
- **company**: Empresa donde trabaja
- **website**: Sitio web personal o profesional

### Redes Sociales
- **linkedin_url**: Perfil de LinkedIn
- **twitter_url**: Perfil de Twitter/X
- **instagram_url**: Perfil de Instagram
- **facebook_url**: Perfil de Facebook

### Intereses y Hobbies
- **interests**: Lista de intereses (JSON field) con opciones predefinidas:
  - Música, Tecnología, Deportes, Arte, Gastronomía
  - Viajes, Negocios, Educación, Salud y Bienestar
  - Videojuegos, Fotografía, Moda, Libros y Literatura
  - Cine, Actividades al Aire Libre, Ciencia, Cultura, Networking
- **hobbies**: Descripción libre de hobbies (máximo 300 caracteres)

### Configuración de Privacidad
- **profile_visible**: Si el perfil es público (por defecto: True)
- **show_email**: Si mostrar el email a otros usuarios (por defecto: False)
- **show_phone**: Si mostrar el teléfono a otros usuarios (por defecto: False)

### Preferencias de Notificación
- **email_notifications**: Notificaciones por email (por defecto: True)
- **sms_notifications**: Notificaciones por SMS (por defecto: False)
- **marketing_emails**: Emails promocionales (por defecto: False)

## Propiedades Calculadas

### Nuevas propiedades añadidas:
- **full_phone**: Teléfono completo con código de país
- **age**: Edad calculada desde la fecha de nacimiento
- **location**: Ubicación formateada (Ciudad, País)
- **get_interests_display()**: Lista de intereses en formato legible

## Formularios Mejorados

### UserUpdateForm
- Formulario completo con todos los nuevos campos
- **Email no editable**: Protege el email como identificador único
- Organizado en secciones lógicas
- Validación personalizada para intereses
- Widgets Bootstrap con estilos personalizados

### UserSignupForm y UserSocialSignupForm
- Añadido campo de nombre obligatorio en el registro

## Templates Actualizados

### user_form.html
- Diseño completamente reorganizado en secciones:
  - Información Personal
  - Información de Contacto
  - Información Profesional
  - Redes Sociales
  - Intereses y Hobbies
  - Configuración de Privacidad
  - Preferencias de Notificación
- Estilos mejorados con grid para intereses
- Validación visual de errores
- Soporte para carga de imágenes

### user_detail.html
- Muestra avatar del usuario
- Información adicional (edad, ubicación, ocupación)
- Respeta configuración de privacidad
- Enlaces a redes sociales
- Muestra intereses y hobbies
- Información profesional

## Panel de Administración

### UserAdmin mejorado:
- Fieldsets organizados por categorías
- Nuevos filtros (género, país, configuración de privacidad)
- Búsqueda mejorada (ciudad, ocupación, empresa)
- Columnas adicionales en la lista (edad, ubicación, ocupación)

## Validaciones Implementadas

1. **Fecha de nacimiento**: Mínimo 13 años, máximo 120 años
2. **Teléfono**: Entre 7 y 15 dígitos numéricos
3. **Intereses**: Selección múltiple de opciones predefinidas
4. **URLs**: Validación automática para redes sociales y website

## Consideraciones de Seguridad

- **Email no editable**: Una vez registrado, el email no se puede cambiar desde el formulario de perfil
- Configuración de privacidad para proteger datos sensibles
- Validación de edad para cumplir regulaciones
- Campos opcionales para no forzar información personal
- Control granular de notificaciones
- Protección del email como identificador único de login

## Compatibilidad

- Mantiene compatibilidad con el modelo existente
- Migración automática aplicada
- Todos los campos nuevos son opcionales
- No afecta funcionalidad existente

## Uso Recomendado

1. Los usuarios pueden completar su perfil gradualmente
2. Usar los intereses para recomendaciones de eventos
3. Respetar configuración de privacidad en todas las vistas
4. Aprovechar la información de ubicación para eventos locales
5. Usar datos profesionales para eventos de networking
