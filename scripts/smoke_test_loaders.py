import sys
sys.path.append(".")

from src.backend.intelligence.ingestion.pdf_loader import load_pdf
from src.backend.intelligence.ingestion.xml_loader import load_xml
from src.backend.intelligence.ingestion.html_loader import load_html

# Replace with actual paths to your files
test_pdf = "data/corpus/dgca_cars/DGCA_CAR_M.pdf"
test_xml = "data/corpus/faa_ads/FAA_ADS_2017-08831.xml"
test_html = "data/corpus/faa_sdrs/FAA_SDRS_2022-10-03.html"

print("PDF:", len(load_pdf(test_pdf)), "chars")
print("XML:", len(load_xml(test_xml)), "chars")
print("HTML:", len(load_html(test_html)), "chars")