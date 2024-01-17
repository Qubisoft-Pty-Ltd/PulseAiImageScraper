import os
from PIL import Image, ImageEnhance, ImageFilter
import os
import azure.ai.vision as sdk
import matplotlib.pyplot as plt

MODEL_DIR_NAME = r'azure_ocr'

SCRAPED_IMG_DIR = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}\\scraped_photos'
OUTPUT_OCR_IMG_DIR = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}\\ocr_img_results'

image_files = [os.path.join(SCRAPED_IMG_DIR, file) for file in os.listdir(SCRAPED_IMG_DIR)]
OUTPUT_FILE = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}\\ocr_results.txt'
OUTPUT_FILE_RESULTS_PATH = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}'



# try with /
# try with adding space 1, 2 etc. like bed 1, bed 2
FLOOR_PLAN_STRS = ['living', 'bedroom', 'kitchen', 'dining', 'bathroom', 'study', 'garage', 
                   'utility', 'laundry', 'alfresco', 'ensuite', 'lounge', "l'dry", 
                   'sunroom', 'bed', 'porch', 'shed', 'carport', 'meals', 'entertainment', 
                   'storage', 'toilet', 'office', 'ens', 'wir', 'wardrobe', 'family', 'master', 
                   'wip', 'bath', 'pwdr', 'double garage', 'main bed', 'courtyard', 'laundry room', 
                   'cellar', 'deck', 'balcony', 'sitting', 'main', 'terrace', 'pantry', 'outdoor entertaining', 
                   'verandah', 'elfresco', 'living/dining', 'rumpus', 'patio', 'enclosed alfresco']

def ocrFloorPlanTextExtraction():

    service_options = sdk.VisionServiceOptions('https://floorplanfeatures.cognitiveservices.azure.com/',
                                            'ba2a46ffa0fc4c52b93e23227b596d36')

    for index, image_file_path in enumerate(image_files):
        img_file_name = image_file_path.split("\\")[-1][:-3]
        vision_source = sdk.VisionSource(
            filename=image_file_path)

        analysis_options = sdk.ImageAnalysisOptions()

        analysis_options.features = (
            # sdk.ImageAnalysisFeature.CAPTION |
            sdk.ImageAnalysisFeature.TEXT
        )

        analysis_options.language = "en"

        analysis_options.gender_neutral_caption = True

        image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)

        result = image_analyzer.analyze()
        if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:

            if result.caption is not None:
                print(" Caption:")
                print("   '{}', Confidence {:.4f}".format(result.caption.content, result.caption.confidence))


            with open(f'{OUTPUT_FILE_RESULTS_PATH}\\{img_file_name}_full_list.txt', 'w', encoding='utf-8') as output_file:
                if result.text is not None:
                    print(" Text:")
                    for line in result.text.lines:
                        points_string = "{" + ", ".join([str(int(point)) for point in line.bounding_polygon]) + "}"
                        formatted_str_line = "   Line: '{}'".format(line.content)
                        print(formatted_str_line)
                        output_file.write(formatted_str_line + "\n")
                        for word in line.words:
                            points_string = "{" + ", ".join([str(int(point)) for point in word.bounding_polygon]) + "}"
                            formatted_str_word = "     Word: '{}'".format(word.content)
                            print(formatted_str_word)
                            output_file.write(formatted_str_word + "\n")

        else:

            error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
            print(" Analysis failed.")
            print("   Error reason: {}".format(error_details.reason))
            print("   Error code: {}".format(error_details.error_code))
            print("   Error message: {}".format(error_details.message))


    # for index, image_file_path in enumerate(images):
    #     # get file name and also remove last three chars
    #     img_file_name = image_file_path.split("\\")[-1][:-3]

    #     with open(f'{OUTPUT_FILE_RESULTS_PATH}\\{img_file_name}_full_list.txt', 'w', encoding='utf-8') as output_file:

    #         for predicted_text in prediction_groups[index]:
    #             extracted_text = predicted_text[0]
    #             output_file.write(extracted_text + "\n")


    #     print("OCR results have been written to ocr_results.txt and text regions have been saved in the 'output' directory.")

if __name__ == '__main__':
    ocrFloorPlanTextExtraction()
    pass