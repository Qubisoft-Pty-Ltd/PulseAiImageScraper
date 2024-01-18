import os
import re
from PIL import Image, ImageEnhance, ImageFilter
import os
import azure.ai.vision as sdk
import matplotlib.pyplot as plt
from PulseAiSqlite import PulseAiSqlite

MODEL_DIR_NAME = r'azure_ocr'

SCRAPED_IMG_DIR = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}\\scraped_photos'
OUTPUT_OCR_IMG_DIR = f'C:\\Users\\marcu\\Work\\Source\\PulseAi\\ImageClassificaiton\\FloorPlanClassifer\\{MODEL_DIR_NAME}\\ocr_img_results'

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


class AzureOcr:


    def __init__(self):
        self.context = PulseAiSqlite('../propertypulseai')
        self.service_options = sdk.VisionServiceOptions('https://floorplanfeatures.cognitiveservices.azure.com/',
                                                'ba2a46ffa0fc4c52b93e23227b596d36')
    

    def InspectorPropertyFloorPlanOCR(self):
        all_properties = self.context.search_all_inspector_properties()
        for property in all_properties:
            if property['FloorPlanImageUrl'] is not None:
                full_path_img = os.path.join(os.getcwd(), property['FloorPlanImageUrl'])
                if os.path.exists(full_path_img):
                    print("The file exists.")
                    results = self.ocrFloorPlanTextExtraction(full_path_img)
                    current_floor_plan_labels = self.context.get_floor_plan_labels(property['Id'])
                    address = property['StreetAddress']
                    for result in results:
                        if current_floor_plan_labels == []:
                            self.context.add_floor_plan_label(property['Id'], result)
                        elif result not in current_floor_plan_labels:
                            self.context.add_floor_plan_label(property['Id'], result)
                        else:
                            print(f'Floor plan label {result} already exists for property {address}')
                else:
                    print("The file does not exist.")
            else:
                print("The file does not exist.")

    def ocrFloorPlanTextExtraction(self, file_path):

        vision_source = sdk.VisionSource(
            filename=file_path)

        analysis_options = sdk.ImageAnalysisOptions()

        analysis_options.features = (
            # sdk.ImageAnalysisFeature.CAPTION |
            sdk.ImageAnalysisFeature.TEXT
        )

        analysis_options.language = "en"

        analysis_options.gender_neutral_caption = True

        image_analyzer = sdk.ImageAnalyzer(self.service_options, vision_source, analysis_options)

        result = image_analyzer.analyze()
        if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
            if result.text is not None:
                print('seomthing')
                return self.Parse_Azure_OCR_Results(result.text.lines)

        else:

            error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
            print(" Analysis failed.")
            print("   Error reason: {}".format(error_details.reason))
            print("   Error code: {}".format(error_details.error_code))
            print("   Error message: {}".format(error_details.message))
            return None


    def Parse_Azure_OCR_Results(self, ocr_results):
        floor_plan_labels = []
        for result in ocr_results:
            label = result.content.lower().strip()


            # try with /
            # try with adding space 1, 2 etc. like bed 1, bed 2

            if label in FLOOR_PLAN_STRS:
                floor_plan_labels.append(label)
            elif label.replace('/', '').strip() in FLOOR_PLAN_STRS:
                floor_plan_labels.append(label.replace('/', '').strip())
            # remove numbers if they are in the string
            elif re.sub(r'\d', '', label).strip() in FLOOR_PLAN_STRS:
                floor_plan_labels.append(label)
        
        return floor_plan_labels




if __name__ == '__main__':
    azureOcr = AzureOcr()
    azureOcr.InspectorPropertyFloorPlanOCR()
    pass