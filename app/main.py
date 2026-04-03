from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {'Hello': 'Integrion Test Optimized'}

@app.post('/calculate')
def calculate(a: int, b: int):
    return {'result': a + b}
