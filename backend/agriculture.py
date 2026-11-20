import json

with open("data/crops.json", "r") as file:
    crop_data = json.load(file)


def get_agriculture_advice(crop, soil):
    crop = crop.lower().strip()
    soil = soil.lower().strip()

    if crop not in crop_data:
        return "Crop not found in our database. Please enter a supported crop."

    if soil not in crop_data[crop]:
        return "Soil type not available for this crop. Please try another soil type."

    return crop_data[crop][soil]