from foodbridge.modules.getPantryDetails import PantryContentExtractor
from foodbridge.search.search import getContent, openPage, closeDriver 

def pantryInfo():
    link = "https://www.trcnyc.org/foodpantry/"
    openPage(link)
    content = getContent()
    extractor = PantryContentExtractor(content)
    info = extractor.forward()
    info_dict = info.to_dict()
    print(info_dict)
    closeDriver()
    return info

pantryInfo()