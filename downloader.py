
import os
import re
import requests
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, APIC, error
from googleapiclient.discovery import build

CARPETA_SALIDA="musica"
YOUTUBE_API_KEY = "ADD YOUR API KEY HERE"


if not os.path.exists(CARPETA_SALIDA):
	os.makedirs(CARPETA_SALIDA)
def get_info(url):
	opciones = {
		"quiet": True,
		"extract_flat": True,
		"ignoreerrors": True,
		"playlistend": 99999,
	}

	with yt_dlp.YoutubeDL(opciones) as ydl:
		info = ydl.extract_info(url, download=False)

	if info is None:
		return None
	
	titulo = info.get("title", "Sin titulo")
	artista = info.get("artist") or info.get("uploader", "Desconocido")
	miniatura = info.get("thumbnail", "")

	return titulo, artista, miniatura
	
def get_playlist(playlist_id):
	youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

	info_playlist = youtube.playlists().list(
		part="snippet",
		id=playlist_id
	).execute()
	titulo_playlist = info_playlist["items"][0]["snippet"]["title"]

	ids = []
	page_token = None

	while True:
		respuesta = youtube.playlistItems().list(
			part="contentDetails",
			playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token
        ).execute()
		for item in respuesta["items"]:
			ids.append(item["contentDetails"]["videoId"])

		page_token = respuesta.get("nextPageToken")
		if not page_token:
			break

	return ids, titulo_playlist


def descargar(url, titulo, artista, miniatura):
	nombre_archivo = titulo.replace("/", "-")
	ruta_mp3 = os.path.join(CARPETA_SALIDA, f"{nombre_archivo}.mp3")

	opciones = {
		"format": "bestaudio",
		"outtmpl": os.path.join(CARPETA_SALIDA, f"{nombre_archivo}.%(ext)s"),
		"nooverwrites": True,
		"postprocessors": [{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "mp3",
			"preferredquality": "0",
		}],
		"quiet": True,
	}
	
	with yt_dlp.YoutubeDL(opciones) as ydl:
		ydl.download([url])

	agregar_metadatos(ruta_mp3, titulo, artista, miniatura)


def agregar_metadatos(ruta_mp3, titulo, artista, miniatura):
	audio= ID3(ruta_mp3)

	audio[TIT2] = TIT2(encoding=3, text=titulo)
	audio[TPE1] = TPE1(encoding=3, text=artista)

	if miniatura:
		respuesta = requests.get(miniatura)
		audio[APIC] = APIC(
			encoding=3,
			mime="image/jpeg",
			type=3,
			desc="Cover",
			data=respuesta.content
		)
	audio.save()

def extraer_playlist_id(url):
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

def main():
	print("\nDescargador mp3 youtube\n")
	url = input("Url:  ").strip()

	print("\n\nObteniendo informacion...\n")
	playlist_id = extraer_playlist_id(url)

	if playlist_id:
		ids, titulo_playlist = get_playlist(playlist_id)
		global CARPETA_SALIDA
		CARPETA_SALIDA = os.path.join("musica", titulo_playlist.replace("/", "-"))
		if not os.path.exists(CARPETA_SALIDA):
			os.makedirs(CARPETA_SALIDA)
		print(f"\nPlaylist: {titulo_playlist}")
		print(f"Total de canciones: {len(ids)}")
		confirmar = input("\nDescargar playlist? (s/n): ").strip().lower()
		if confirmar == "s":
			for i, video_id, in enumerate(ids, 1):
				url_cancion = f"https://www.youtube.com/watch?v={video_id}"
				info = get_info(url_cancion)
				if info is None:
					print("\nVideo no disponible, saltando... ")
					continue
				titulo, artista, miniatura = info
				print(f"\n[{i}/{len(ids)}] {titulo}")
				descargar(url_cancion, titulo, artista, miniatura)
				print(f"\nPlaylist guardada en '{CARPETA_SALIDA}'")
		else:
			print("\nCancelado.")
	else:
		info = get_info(url)
		if info is None:
			print("\n Video no disponible")
			return
		titulo, artista, miniatura = info
		print(f"\nTitulo: {titulo}")
		print(f"\nArtista: {artista}")
		confirmar = input("Descargar? (s/n): ").strip().lower()
		if confirmar == "s":
			print("\nDescargando...")
			descargar(url, titulo, artista, miniatura)
			print(f"Guardado en '{CARPETA_SALIDA}'")
		else:
			print("\nCancelado.")


if __name__ == "__main__":
	main()
