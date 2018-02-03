from app import create_app
import ssl

app = create_app()
context = ssl.SSLContext()
context.load_cert_chain("secrets/cert.pem", "secrets/key.pem")
app.run(ssl_context=context)