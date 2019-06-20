"""Copyright 2019 Google, Modified by REV 2019

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
import pyaudio
import sys
import json

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def get_results(data_gen):
    """Function to print out the responses from data_gen. Prints partial transcripts and
        edits them as new responses change. Finalizes and makes a new line when recieving a
        final transcript.
    """
    char_diff = 0
    prev_message_length = 0

    #
    for data in data_gen:
        data = json.loads(data)

        if data['type'] == 'partial':
            message = data['transcript']

            if len(message) < prev_message_length:
                char_diff = prev_message_length - len(message)
            else:
                prev_message_length = len(message)

            sys.stdout.write(message+ " " * char_diff + "\r")
            sys.stdout.flush()
        elif data['type'] == 'final':
            message = data['transcript']

            if len(message) < prev_message_length:
                char_diff = prev_message_length - len(message)
            else:
                prev_message_length = len(message)

            print(message + " " * char_diff)
            prev_message_length = 0
            char_diff = 0

rate = 44100
chunk = 1024

access_token = '02Jn8jDGSOpHC5ca5gvNl-7Tbw_cktAr1sdMVMZ-MjFOP1pRfwccKadqXim_lqGcw84c2VELmmt6jL6yzB48ugGkAR3oY'

example_mc = MediaConfig('audio/x-raw', 'interleaved', rate, 'S16LE', 1)

streamclient = RevAiStreamingClient(access_token, example_mc)

with MicrophoneStream(rate, chunk) as stream:
    try:
        response_gen = streamclient.start(stream.generator())
        get_results(response_gen)
        streamclient.end()
    except Exception as e:
        print(e)
        streamclient.end()