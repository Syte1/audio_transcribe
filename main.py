import wave
import sys
import time
import whisper
import threading
import pyaudio
import keyboard
import uuid
import tempfile
from pathlib import Path

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
        self.filename = Path("output.wav")
        self.recording = False
        self.frames = []
        print("Object created")

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            print("Recording")
            self.frames = [] # clear frames
            threading.Thread(target=self.record).start()
    
    @staticmethod
    def print_something():
        print("Something")
        
    def record(self):
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.chunk,
            input=self.input
        )
        last_check = time.time()
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
            
            # Check if 0.5 seconds have passed
            if time.time() - last_check >= 2:
                last_check = time.time()

                # Save, transcribe, and clear frames
                self.save_audio_temp()
        
        stream.stop_stream()
        stream.close()
        self.save_audio(self.filename)
    
    def save_audio_temp(self):
        temp_filename = self._create_random_filename()
        self.save_audio(temp_filename)
        # Optionally delete the temp file after transcription
        Path(temp_filename).unlink()

    
    def set_hotkey(self, hotkey):
        keyboard.add_hotkey(hotkey, self.toggle_recording, suppress=True)
        print("Type ctrl + s to toggle")
        print("Type ctrl+d to cancel recording")
        keyboard.wait('ctrl+d')
        
    def save_audio(self, filename: Path=Path("output.wav")):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        self.transcribe_recording(filename)
        
    @staticmethod
    def _create_random_filename() -> str:
        return str(Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.wav")
    
    @staticmethod
    def _select_model(model: str) -> whisper.Whisper:
        return whisper.load_model(model, in_memory=True)

    def transcribe_recording(self, filename: str):
        result = self.model.transcribe(filename)
        transcription = result["text"]
        if transcription:
            print(transcription)

def main():
    recorder = AudioTranscriber()
    recorder.set_hotkey('ctrl+s')

if __name__ == "__main__":
    main()