import wave
import sys
# import time

import pyaudio

    
def main():
    
    
    
    CHUNK = 1024
    print("args: ",sys.argv)

    if len(sys.argv) < 2:
        print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
        sys.exit(-1)
    with wave.open(sys.argv[1], 'rb') as wf:
        
        # def callback(in_data, frame_count, time_info, status):
        #     data = wf.readframes(frame_count)
            
            
        #     return (data, pyaudio.paContinue)
        p = pyaudio.PyAudio()
        
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        while len(data := wf.readframes(CHUNK)):
            stream.write(data)

        # while stream.is_active():
        #     time.sleep(.1)
        
        stream.close()
        
        p.terminate()
    
if __name__ == "__main__":
    main()