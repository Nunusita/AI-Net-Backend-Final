# AI Net Backend (Flask)

Backend completo para **AI Net**, con:
- Autenticación JWT (login/registro).
- Integración con Stripe (`/create-checkout-session`, webhooks) para planes: semanal, mensual, anual, vitalicio.
- Procesamiento de video para generar clips tipo Shorts + subtítulos (Whisper).
- Banco de estilos visuales de captions.
- Límites por plan (free: 2 veces por semana, 10 clips por enlace).
- Descarga segura de clips por ID (solo el dueño puede descargar).
- Notificaciones por correo (pago recibido, límite alcanzado).
- Panel de administración básico embebido (con login).
- Multilenguaje en subtítulos.

## Cómo correr

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# configurar .env
cp .env.example .env
flask db upgrade  # si usas migrations

# iniciar
python wsgi.py
```

## Variables de entorno

Ver `.env.example`.

## Estructura

```
app/
  __init__.py
  config.py
  extensions.py
  models.py
  auth/
    routes.py
  payments/
    routes.py
    webhooks.py
  videos/
    routes.py
    processor.py
    subtitles.py
  downloads/
    routes.py
  admin/
    routes.py
    templates/
      login.html
      dashboard.html
  notifications/
    email.py
  styles/
    bank.py
  utils/
    usage.py
wsgi.py
requirements.txt
```

> Nota: Este es un esqueleto funcional con endpoints listos. Ajusta detalles a tu infraestructura (DB, storage, workers).
