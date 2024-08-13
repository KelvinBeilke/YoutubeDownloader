import webbrowser
import customtkinter as tk
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import threading
from pytube import YouTube, Playlist
import os
import requests
import io


""""
1.Log in to Google Developers Console.              
2.Create a new project.               
3.On the new project dashboard, click Explore & Enable APIs.             
4.In the library, navigate to YouTube Data API v3 under YouTube APIs.              
5.Enable the API.               
6.Create a credential.              
7.A screen will appear with the API key." https://blog.hubspot.com/website/how-to-get-youtube-api-key
"""
# Sua API Key do YouTube Data API v3 (Pesqusiar por Google Cloud Console)
API_KEY = ''

tk.set_appearance_mode('system')

diretorio = None
escolheu_diretorio = False
pausado = False

historico_arquivo = 'historico_downloads.txt'



janela = tk.CTk()
janela.title('Download Musicas')
janela.geometry('1080x720')
janela.iconbitmap('Icone.ico')
janela.resizable(False, False)

main_frame = tk.CTkFrame(janela)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = tk.CTkFrame(main_frame)
left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

right_frame = tk.CTkFrame(main_frame)
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=2)

texto_busca = tk.CTkLabel(left_frame, text='Buscar Vídeo:')
texto_busca.pack(pady=(0, 10))

caixa_busca = tk.CTkEntry(left_frame, width=300)
caixa_busca.pack()

botao_busca = tk.CTkButton(left_frame, text="Buscar",fg_color=("#c30010"),hover_color=("#de0a26"), command=lambda: threading.Thread(target=realizar_busca).start())
botao_busca.pack(pady=(10, 20))

resultados_frame = tk.CTkFrame(left_frame)
resultados_frame.pack(fill="both", expand=True)


texto_link = tk.CTkLabel(right_frame, text='LINK (youtube):')
texto_link.pack()

caixa_link = tk.CTkEntry(right_frame, placeholder_text='youtube.com/', width=350, font=tk.CTkFont(family='arial', size=10))
caixa_link.pack(pady=(0, 10))

lista_opcoes = ['Automatico', 'Video único', 'Playlist']
opcoes = tk.CTkComboBox(right_frame, values=lista_opcoes)
opcoes.set('Automatico')
opcoes.pack(pady=(0, 10))

progresso_texto1 = tk.CTkLabel(right_frame, text='Progresso:')
progresso_texto1.pack()

progresso1 = tk.CTkProgressBar(right_frame, orientation='horizontal', progress_color='#b22222', height=14, width=345)
progresso1.set(value=0)
progresso1.pack(pady=(0, 10))

download = tk.CTkLabel(right_frame, text='Progresso Download:')
download.pack()

porcentagem_downlaod = tk.CTkLabel(right_frame, text='0%')
porcentagem_downlaod.pack()

contador_download = tk.CTkLabel(right_frame, text='0/0')
contador_download.pack()

contador = tk.CTkLabel(right_frame, text='Progresso conversão:')
contador.pack()

porcentagem_conversão = tk.CTkLabel(right_frame, text='0%')
porcentagem_conversão.pack()

contador_label = tk.CTkLabel(right_frame, text='0/0')
contador_label.pack()


def ler_historico():
    if os.path.exists(historico_arquivo):
        with open(historico_arquivo, 'r') as f:
            return f.read().splitlines()
    return []


def escrever_historico(item):
    with open(historico_arquivo, 'a') as f:
        f.write(item + '\n')
    atualizar_historico()

def buscar_videos(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&q={query}&type=video&key={API_KEY}"
    response = requests.get(url)
    results = response.json().get('items', [])
    return results

def exibir_opcoes(resultados):
    for widget in resultados_frame.winfo_children():
        widget.destroy()

    for video in resultados:
        titulo = video['snippet']['title']
        video_id = video['id']['videoId']
        thumbnail_url = video['snippet']['thumbnails']['high']['url']


        img_data = requests.get(thumbnail_url).content
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((60, 45))
        photo = ImageTk.PhotoImage(img)


        frame = tk.CTkFrame(resultados_frame)
        frame.pack(fill="x", pady=5)


        label_img = tk.CTkLabel(frame, image=photo)
        label_img.image = photo  # Manter referência da imagem
        label_img.pack(side="left")

        label_titulo = tk.CTkLabel(frame, text=titulo)
        label_titulo.pack(side="left", padx=10)


        botao_selecionar = tk.CTkButton(frame, text="Selecionar",fg_color=("#c30010"),hover_color=("#de0a26"), command=lambda id=video_id: selecionar_video(id))
        botao_selecionar.pack(side="right")

def selecionar_video(video_id):
    link = f"https://www.youtube.com/watch?v={video_id}"
    caixa_link.delete(0, tk.END)
    caixa_link.insert(0, link)

def realizar_busca():
    query = caixa_busca.get()
    if query:
        resultados = buscar_videos(query)
        exibir_opcoes(resultados)
    else:
        messagebox.showwarning("Busca", "Digite um termo de busca.")

def mudar_diretorio():
    global diretorio, escolheu_diretorio
    diretorio = askdirectory(title='Selecione a pasta de download:')
    escolheu_diretorio = True

def download_unico():
    global diretorio, pausado
    link = caixa_link.get()

    try:
        yt = YouTube(link)
        filename = yt.streams.filter(file_extension='mp4').first().default_filename
        if os.path.isfile(os.path.join(diretorio, filename)):
            print("O arquivo já existe no diretório. Não é necessário fazer o download.")
            return

        pausado = False
        yt.streams.filter(file_extension='mp4').first().download(diretorio)
        progresso1.set(value=1)
        contador_download.configure(text='1/1')
        porcentagem_downlaod.configure(text='100%')
        escrever_historico(filename)
        converter_mp3()


        messagebox.showinfo("Download Concluído", f"Download do vídeo '{filename}' concluído.")
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")

def download_playlist():
    global diretorio, pausado
    link = caixa_link.get()

    try:
        playlist = Playlist(link)
        incremento = 100 / len(playlist.videos)

        for i, video in enumerate(playlist.videos):
            mp3_filename = video.title + '.mp3'
            if os.path.isfile(os.path.join(diretorio, mp3_filename)):
                print(f"O arquivo {mp3_filename} já existe no diretório. Não é necessário fazer o download.")
                progresso1.set(value=(incremento * (i + 1)) / 100)
                contador_download.configure(text=f'{i + 1}/{len(playlist.videos)}')
                porcentagem = (i + 1) / len(playlist.videos)
                porcentagem_downlaod.configure(text=f'{porcentagem * 100:.2f}%')
                continue

            while pausado:
                janela.update()

            video.streams.filter(file_extension='mp4').first().download(diretorio)
            progresso1.set(value=(incremento * (i + 1)) / 100)
            contador_download.configure(text=f'{i + 1}/{len(playlist.videos)}')
            porcentagem = (i + 1) / len(playlist.videos)
            porcentagem_downlaod.configure(text=f'{porcentagem * 100:.2f}%')
            escrever_historico(video.title + '.mp4')




        contador_download.configure(text=f'{len(playlist.videos)}/{len(playlist.videos)}')
        porcentagem_downlaod.configure(text='100%')
        progresso1.set(1)
        messagebox.showinfo("Download Concluído", "Download da playlist concluído.")
    except Exception as e:
        print(f"Erro ao baixar a playlist: {e}")

def converter_mp3():
    global diretorio
    if not escolheu_diretorio:
        mudar_diretorio()

    pasta_converter = diretorio

    def converter():
        try:
            files = [f for f in os.listdir(pasta_converter) if
                     os.path.isfile(os.path.join(pasta_converter, f)) and f.endswith('.mp4')]
            arquivos_convertidos = 0
            for i, arquivo in enumerate(files):
                diretorio = os.path.join(pasta_converter, arquivo)
                mp4 = VideoFileClip(diretorio)
                mp3 = diretorio[:-4] + '.mp3'
                mp4.audio.write_audiofile(mp3)
                mp4.close()
                arquivos_convertidos += 1
                contador_label.configure(text=f'{arquivos_convertidos}/{len(files)}')
                porcentagem_conversão.configure(text=f'{(arquivos_convertidos / len(files)) * 100:.2f}%')
                progresso1.set(value=arquivos_convertidos / len(files))
                os.remove(diretorio)
                escrever_historico(arquivo + ' convertido para MP3')

            messagebox.showinfo("Conversão Concluída", "Conversão dos vídeos concluída.")


        except Exception as e:
            print(f"Erro ao converter o vídeo: {e}")

    t = threading.Thread(target=converter)
    t.start()

def comando():
    global diretorio, escolheu_diretorio

    if not escolheu_diretorio:
        mudar_diretorio()

    try:
        if opcoes.get().lower() == 'automatico':
            if 'start_radio' in caixa_link.get() or 'list' in caixa_link.get():
                download_playlist()
                converter_mp3()
            else:
                download_unico()
        elif opcoes.get().lower() == 'video único':
            download_unico()
        elif opcoes.get().lower() == 'playlist':
            download_playlist()
            converter_mp3()

    except Exception as e:
        print(f"Erro ao executar o comando: {e}")
    finally:
        caixa_link.delete(0, tk.END)
def pausar():
    global pausado
    pausado = not pausado
    if pausado:
        botao_pausar.configure(text='Retomar')
    else:
        botao_pausar.configure(text='Pausar')

def abrir_historico():
    historico = ler_historico()
    if historico:
        webbrowser.open(historico_arquivo)
    else:
        messagebox.showinfo("Histórico", "Nenhum download foi realizado ainda.")

def limpar_historico():
    if os.path.exists(historico_arquivo):
        os.remove(historico_arquivo)
    atualizar_historico()
    messagebox.showinfo("Histórico", "Histórico limpo com sucesso.")

def atualizar_historico():
    historico = ler_historico()
    historico_label.configure(text="\n".join(historico[-10:]))



botao_iniciar = tk.CTkButton(right_frame, text='Iniciar Download',fg_color=("#c30010"),hover_color=("#de0a26"), command=comando)
botao_iniciar.pack(pady=(10, 10))

botao_pausar = tk.CTkButton(right_frame, text='Pausar',fg_color=("#c30010"),hover_color=("#de0a26"), command=pausar)
botao_pausar.pack(pady=(0, 10))

botao_diretorio = tk.CTkButton(right_frame, text='Selecionar Diretório',fg_color=("#c30010"),hover_color=("#de0a26"), command=mudar_diretorio)
botao_diretorio.pack(pady=(0, 10))

botao_historico = tk.CTkButton(right_frame, text='Abrir Histórico',fg_color=("#c30010"),hover_color=("#de0a26"), command=abrir_historico)
botao_historico.pack(pady=(0, 10))

botao_limpar_historico = tk.CTkButton(right_frame, text='Limpar Histórico',fg_color=("#c30010"), hover_color=("#de0a26"), command=limpar_historico)
botao_limpar_historico.pack(pady=(0, 10))

historico_label = tk.CTkLabel(right_frame, text="", font=tk.CTkFont(size=10), wraplength=480, justify="left")
historico_label.pack(pady=(10, 10))

atualizar_historico()

janela.mainloop()
