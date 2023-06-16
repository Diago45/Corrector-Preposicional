import requests
import json
import spacy
import re
from termcolor import colored

nlp = spacy.load("es_core_news_sm")


def corregir_oracion(oracion):
  # URL del servidor público de LanguageTool
  url = 'https://api.languagetool.org/v2/check'

  # Parámetros de la solicitud
  data = {'text': oracion, 'language': 'es'}
  headers = {'Content-type': 'application/x-www-form-urlencoded'}

  # Enviar la solicitud al servidor público de LanguageTool
  response = requests.post(url, data=data, headers=headers)
  result = json.loads(response.text)

  # Sugerir correcciones para los errores gramaticales
  sugerencias = []
  for match in result['matches']:
    # Obtener el error y la corrección sugerida
    error = match['context']['text'][match['offset']:match['offset'] +
                                     match['length']]
    correccion = match['replacements'][0]['value']
    mensaje = match['message']

    # Reemplazar solo la primera ocurrencia del error con la corrección sugerida en la oración
    oracion = re.sub(r'\b' + error + r'\b', correccion, oracion, 1)

  if len(sugerencias) > 0:
    # Si hay sugerencias de corrección, volver a enviar la oración corregida a LanguageTool
    return corregir_oracion(oracion)
  else:
    # Si no hay sugerencias de corrección, devolver la oración corregida
    return oracion


def corregir_preposiciones(oracion):
  preposiciones_mal_usadas = {
    ("por", "causa", "de"): "a causa de",
    ("en", "base", "a"): "con base en",
    ("de", "acuerdo", "a"): "de acuerdo con",
    ("en", "relación", "a"): "con relación a",
    ("bajo", "la", "base", "de"): "en función de",
    ("vinculado", "a"): "vinculado con",
    ("de", "arriba", "a", "abajo"): "de arriba abajo",
    ("por", "motivo", "a"): "por motivo de"
  }

  preposiciones_sugerencias = {
    ("a", "pesar", "de"): "pese a",
    ("en", "cuanto", "a"): "respecto a",
    ("en", "relación", "con"): "con relación a",
    ("con", "respecto", "de"): "con respecto a",
    ("en", "base", "a"): "con base en",
    ("bajo", "este", "punto", "de", "vista"): "desde este punto de vista"
  }

  oracion_min = oracion.lower()

  for frase, sugerencia in preposiciones_mal_usadas.items():
    if ' '.join(frase) in oracion_min:
      oracion_min = oracion_min.replace(' '.join(frase),
                                        colored(' '.join(frase), 'red'))

  for frase, sugerencia in preposiciones_sugerencias.items():
    if ' '.join(frase) in oracion_min:
      oracion_min = oracion_min.replace(' '.join(frase),
                                        colored(' '.join(frase), 'yellow'))

  palabras = oracion_min.split()
  for i, palabra in enumerate(palabras):
    if palabra.endswith('.'):
      palabras[i + 1] = palabras[i + 1].capitalize()

  # Agregar esta sección para mantener las palabras en mayúscula en la oración corregida
  doc = nlp(oracion)
  for ent in doc.ents:
    if ent.label_ == "PER":
      oracion_min = re.sub(r'\b' + ent.text.lower() + r'\b', ent.text,
                           oracion_min)

  print(f"-- {oracion_min} --")

  for frase, sugerencia in preposiciones_mal_usadas.items():
    if ' '.join(frase) in oracion_min:
      oracion_min = oracion_min.replace(' '.join(frase),
                                        colored(sugerencia, 'green'))

  for frase, sugerencia in preposiciones_sugerencias.items():
    if ' '.join(frase) in oracion_min:
      oracion_min = oracion_min.replace(' '.join(frase),
                                        colored(sugerencia, 'green'))

  palabras = oracion_min.split()
  for i, palabra in enumerate(palabras):
    if palabra.endswith('.'):
      palabras[i + 1] = palabras[i + 1].capitalize()

# Agregar esta sección para mantener las palabras en mayúscula en la oración corregida
  doc = nlp(oracion)
  for ent in doc.ents:
    if ent.label_ == "PER":
      oracion_min = re.sub(r'\b' + ent.text.lower() + r'\b', ent.text,
                           oracion_min)

  print(f"++ {oracion_min} ++")


# Pedir oración
oracion = input(
  "Introduce una oración para verificar los errores gramaticales: ")
oracion_corregida = corregir_oracion(oracion)
print(f"Oración original: {oracion}")
print(f"Oración corregida: {oracion_corregida}")

print("Sugerencias para las preposiciones:")
sugerencias_preposiciones = corregir_preposiciones(oracion_corregida)
