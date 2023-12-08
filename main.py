import wave
import sys
import time
import whisper
import threading
import pyaudio

class AudioTranscriber():
    def __init__(self,
                 rate=48000,
                 channels=1,
                 format=pyaudio.paInt24,
                 input=True,
                 model_size="large",
                 chunk=1024
                 ):
        self.rate = rate
        self.channels = channels
        self.format = format
        self.input = input
        self.model: whisper.Whisper = self._select_model(model_size)
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.filename = self._create_filename()
        self.recording = False
        self.frames = []
    

    
    def toggle_recording(self):
        self.recording = True
        self.recording = False
        threading.Thread(target=self.record).start()
    
    def record(self):
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.chunk,
            input=self.input
        )
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
                    
        stream.stop_stream()
        stream.close()
        self.save_audio()
        
        
    def save_audio(self):
        with wave.open(self.file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        self.transcribe_recording()
        

    def _create_filename() -> str:
        return "output.wav"
    
    def _select_model(model: str) -> whisper.Whisper:
        return whisper.load_model(model)

    def transcribe_recording(self):
        result = self.model.transcribe(self.filename)
        print(result["text"])

def main():
    pass
if __name__ == "__main__":
    main()