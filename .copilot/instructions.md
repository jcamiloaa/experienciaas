# Instrucciones para GitHub Copilot

- Todas las explicaciones y respuestas deben ser dadas en español.

## Uso de contenedores y comandos principales

- Siempre que se requiera ejecutar comandos relacionados con la aplicación, utiliza los contenedores definidos en Docker Compose.
- Los comandos deben ejecutarse desde la raíz del proyecto.
- Prefiere los siguientes comandos para las tareas habituales:

### Levantar todos los servicios en segundo plano
```sh
docker compose up -d
```

### Reiniciar el contenedor de Django en entorno local
```sh
docker compose -f docker-compose.local.yml restart django
```

### Ejecutar migraciones de Django
```sh
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
```

### Crear nuevas migraciones de Django
```sh
docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations
```

- Si necesitas ejecutar otros comandos de Django, hazlo usando el mismo patrón:
```sh
docker compose -f docker-compose.local.yml run --rm django python manage.py <comando>
```

- No ejecutes comandos de Django directamente en el host, siempre usa el contenedor correspondiente.
- Documenta cualquier comando especial que se agregue en este archivo.

git add .
git commit -m "Example Commit"
git push -u origin main