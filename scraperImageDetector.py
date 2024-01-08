import os
import shutil
import tensorflow as tf
import numpy as np
from PIL import Image


MODEL_DIRECTORY = r'C:\Users\marcu\Work\Source\PulseAi\ImageClassificaiton'
PB_FILE=r'model.pb'
LABEL_FILE=r'labels.txt'

class ScraperObjectDetector:
    def __init__(self):
        self.model_dir = MODEL_DIRECTORY
        self.pb_file = PB_FILE
        self.label_file = LABEL_FILE
        self.labels = self.load_labels()
        self.graph = self.load_graph()

    def load_labels(self):
        labels = []

        # Open the label.txt file for reading
        with open(r'./labels.txt', 'r') as file:
            # Read the file line by line
            for line in file:
                # Remove leading and trailing whitespace (e.g., newline characters)
                label = line.strip()
                
                # Append the label to the list
                labels.append(label)
        
        return labels

    def load_graph(self):
        graph = tf.Graph()
        with graph.as_default():
            graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(os.path.join(self.model_dir, self.pb_file), 'rb') as f:
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
        return graph

    def read_tensor_from_image_file(self, file_name, input_height=320, input_width=320, input_mean=117, input_std=1):
        input_image = Image.open(file_name)
        image_resized = input_image.resize((input_width, input_height))
        image_array = np.array(image_resized).astype(np.float32)
        normalized_image = (image_array - input_mean) / input_std
        return np.expand_dims(normalized_image, axis=0)

    def run(self):
        # Load image files
        image_files = [os.path.join(self.model_dir, 'scraped_photos', file) for file in os.listdir(os.path.join(self.model_dir, 'scraped_photos'))]

        # Disable eager execution
        tf.compat.v1.disable_eager_execution()

        with tf.compat.v1.Session(graph=self.graph) as sess:
            input_operation = self.graph.get_operation_by_name('image_tensor')

            result_labels = []

            for file in image_files:
                try:
                    nd = self.read_tensor_from_image_file(file)

                    outputs = sess.run([self.graph.get_operation_by_name('detected_boxes').outputs[0],
                                        self.graph.get_operation_by_name('detected_scores').outputs[0],
                                        self.graph.get_operation_by_name('detected_classes').outputs[0]],
                                    {input_operation.outputs[0]: nd})

                    # Process model outputs (this function needs to be implemented)
                    self.process_model_outputs(outputs, file)
                except Exception as e:
                    print(f"An error occurred while processing {file}: {str(e)}")
                    continue 


            return result_labels

    def process_model_outputs(self, outputs, file):
        detected_boxes, detected_scores, detected_classes = outputs
        # model already aranges scores in order
        top_score_index = np.argmax(detected_scores[0])
        second_top_score_index = 1

        top_score_class = detected_classes[top_score_index]
        top_score_label = self.labels[int(top_score_class)]

        second_top_score_class = detected_classes[second_top_score_index]
        second_top_score_label = self.labels[int(second_top_score_class)]

        label_to_use = top_score_label

        if top_score_label == 'Brickwork' or top_score_label == 'Cabinetry' or top_score_label == 'Window':
            label_to_use = second_top_score_label

        # Create a directory for the label if it doesn't exist
        label_dir = os.path.join(self.model_dir, 'categorised\\' + label_to_use)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)

        # Move the file to the appropriate directory
        shutil.copy(file, os.path.join(label_dir, os.path.basename(file)))




if __name__ == '__main__':
    scraper = ScraperObjectDetector()
    scraper.run()