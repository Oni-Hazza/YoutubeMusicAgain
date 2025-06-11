import yt_dlp

ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'postprocessors':[{
            'key':'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],        
        'noplaylist':True
    }

def getAudioStream(link:str) -> str:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    
    for x in info['formats']:
        if x['format_id'] == '234':
            streamurl = x['url']
            break
    return streamurl