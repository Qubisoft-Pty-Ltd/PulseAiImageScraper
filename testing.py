


import os
from PulseAiSqlite import PulseAiSqlite
from PIL import Image
class testing: 

    def __init__(self):
        self.context = PulseAiSqlite('../propertypulseai')

    def checkIfImgPathWorksInDbForFloorPlan(self, address):
        # 20 Merri Parade_Northcote_VIC_3070_floorplan.jpg
        address = address.split('_')
        result = self.context.search_inspector_property(address[0], address[1], address[2], address[3], 'Australia')
        full_path_img = os.path.join(os.getcwd(), result['FloorPlanImageUrl'])

        if os.path.exists(full_path_img):
            print("The file exists.")
            image = Image.open(full_path_img)

            # Display the image using the default image viewer on your system
            image.show()
        else:
            print("The file does not exist.")
        
        print('do something')





if __name__ == '__main__':
    test = testing()
    test.checkIfImgPathWorksInDbForFloorPlan('20 Merri Parade_Northcote_VIC_3070_floorplan.jpg')