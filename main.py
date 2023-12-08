import wave
import sys
import time
import whisper
import threading
import pyaudio
import keyboard
import numpy as np
import uuid

class AudioTranscriber():
    def __init__(self,
                 rate=48000,
                 channels=1,
                 format=pyaudio.paInt24,
                 input=True,
                 model_size="tiny.en",
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
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
                    
        stream.stop_stream()
        stream.close()
        # self.save_audio()
        self.save_waveform()
    
    def set_hotkey(self, hotkey):
        keyboard.add_hotkey(hotkey, self.toggle_recording, suppress=True)
        print("Type ctrl + s to toggle")
        print("Type ctrl+d to cancel recording")
        keyboard.wait('ctrl+d')
        
    def save_audio(self):
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        
        self.transcribe_recording()
    
    def save_waveform(self):
        waveform = np.frombuffer(b''.join(self.frames), dtype=np.uint8)
        waveform = np.pad(waveform, (0, len(waveform) % 4), mode='constant')  # Pad to make it a multiple of 4
        waveform = waveform.reshape(-1, 4)
        waveform = waveform.view(np.int32)

        audio_normalized = waveform / np.iinfo(np.int32).max
        self.transcribe_recording(audio_normalized)
        
    @staticmethod
    def _create_filename() -> str:
        return "output.wav"
    
    @staticmethod
    def _select_model(model: str) -> whisper.Whisper:
        return whisper.load_model(model, in_memory=True)

    def transcribe_recording(self, waveform=None):
        if waveform is None:
            result = self.model.transcribe(self.filename)
        else:
            result = self.model.transcribe(waveform)
        
        print(result["text"])

def main():
    recorder = AudioTranscriber()
    recorder.set_hotkey('ctrl+s')

if __name__ == "__main__":
    main()