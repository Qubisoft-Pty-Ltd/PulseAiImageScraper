import os
import shutil
import tensorflow as tf
import numpy as np
from PIL import Image


class ScraperFloorplanClassifier:
    def __init__(self):
        self.model_dir = os.getcwd()
        self.model_file = os.path.join(os.getcwd(), 'FloorPlanClassifier\model.pb')
        self.label_file = os.path.join(os.getcwd(), 'FloorPlanClassifier\labels.txt')
        self.scraped_images_path = os.path.join(os.getcwd(), 'scraped_photos\property_photos')
        self.floor_plan_path = os.path.join(os.getcwd(), 'scraped_photos\\floorplan')
        self.labels = self.load_labels()
        self.graph = self.load_graph()

    def load_labels(self):
        labels = []

        # Open the label.txt file for reading
        with open(self.label_file, 'r') as file:
            # Read the file line by line
            for line in file:
                # Remove leading and trailing whitespace (e.g., newline characters)
                label = line.strip()
                
                # Append the label to the list
                labels.append(label)
        
        return labels

    def load_graph(self):
        model_path = self.model_file
        graph = tf.Graph()
        with graph.as_default():
            graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(model_path, 'rb') as f:
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
    
        for op in graph.get_operations():
            print(op.name)
        return graph

    def read_tensor_from_image_file(self, file_name, input_height=300, input_width=300):
        input_image = Image.open(file_name)
        image_resized = input_image.resize((input_width, input_height))
        return np.expand_dims(image_resized, axis=0)

    def classify_and_organise_scraped_images(self):
        # Load image files
        image_files = [os.path.join(self.scraped_images_path, file) for file in os.listdir(self.scraped_images_path)]

        # Disable eager execution
        tf.compat.v1.disable_eager_execution()

        with tf.compat.v1.Session(graph=self.graph) as sess:
            input_operation = self.graph.get_operation_by_name('data')  # Adjusted input operation name

            result_labels = []

            for file in image_files:
                try:
                    nd = self.read_tensor_from_image_file(file)

                    outputs = sess.run(self.graph.get_operation_by_name('model_output').outputs[0],  # Adjusted output operation name
                                    {input_operation.outputs[0]: nd})

                    # Assuming your model outputs a binary classification in 'outputs'
                    # You might need to process 'outputs' to get the final label, e.g., through argmax if it's a softmax output
                    predicted_label = np.argmax(outputs)
                    predicted_label_str = self.labels[predicted_label]
                    if predicted_label_str == 'Floorplan':
                        self.move_image_if_floor_plan(file)
                    result_labels.append(predicted_label)

                except Exception as e:
                    print(f"An error occurred while processing {file}: {str(e)}")
                    continue 

        return result_labels

    def move_image_if_floor_plan(self, file):
        # Process the prediction and categorize
        if not os.path.exists(self.floor_plan_path):
            os.makedirs(self.floor_plan_path)
        new_file_name = f'{os.path.basename(file).split("_")[0]}_floorplan.jpg'
        shutil.copy(file, os.path.join(self.floor_plan_path, new_file_name))


if __name__ == '__main__':
    scraper = ScraperFloorplanClassifier()
    scraper.classify_and_organise_scraped_images()