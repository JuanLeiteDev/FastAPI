# FastAPI com frontend

## Executar o projeto

Com o ambiente virtual ativo, execute:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Depois aceda a [http://127.0.0.1:8000](http://127.0.0.1:8000). A interface permite criar uma conta, iniciar sessão, configurar e confirmar o 2FA, guardar os códigos de recuperação, consultar os dados da conta e terminar a sessão. Cada código de recuperação pode ser utilizado apenas uma vez.

A documentação interativa da API continua disponível em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
