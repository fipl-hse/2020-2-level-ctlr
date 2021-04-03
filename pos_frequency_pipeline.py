"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import collections
from pathlib import Path
import re
from pipeline import TextProcessingPipeline
from constants import ASSETS_PATH
from visualizer import visualize

class POSFrequencyPipeline:
    def run(self):
        # we guess that all files are already preprocessed in a dir
        pattern = re.compile("\(\w+")
        path = Path(ASSETS_PATH)
        files = list(path.glob('**/*.txt'))
        if not files:
            print("no info to plot")
        speech_parts = collections.Counter()
        for file in files:
            with open(file) as f:
                data = f.read()
                strings = [i[1:] for i in re.findall(pattern, data)]
                speech_parts.update(strings)
        visualize(speech_parts, "picture.png")

def main():
    pipeline = POSFrequencyPipeline()
    pipeline.run()

if __name__ == '__main__':
    main()
