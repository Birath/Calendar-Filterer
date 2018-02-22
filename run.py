from app import create_app, make_celery
import ssl

app = create_app()

celery = make_celery()
context = ssl.SSLContext()
context.load_cert_chain("secrets/cert.pem", "secrets/key.pem")
app.run(ssl_context=context)