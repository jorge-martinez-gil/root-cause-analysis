# -*- coding: utf-8 -*-
"""
Example of classification using SWRL rules

Martinez-Gil, J., Buchgeher, G., Gabauer, D., Freudenthaler, B., Filipiak, D., & Fensel, A. (2022). Root cause analysis in the industrial domain using knowledge graphs: A case study on power transformers. Procedia Computer Science, 200, 944-953.

@author: Jorge Martinez-Gil
"""

import pandas as pd
from owlready2 import *
from rdflib import URIRef

# Load the data (this should be loaded from external file)
data = {
    'Hydrogen': [2845, 12886, 2820, 1099, 3210, 13500, 10200],
    'Oxigen': [5860, 61, 16400, 70, 3570, 343, 11900],
    'Nitrogen': [27842, 25041, 56300, 37520, 47900, 36500, 33700],
    'Methane': [7406, 877, 144, 545, 160, 3150, 573],
    'CO': [32, 83, 257, 184, 360, 113, 87],
    'CO2': [1344, 864, 1080, 1402, 2130, 984, 611],
    'Ethylene': [16684, 4, 206, 6, 4, 5, 0],
    'Ethane': [5467, 305, 11, 230, 43, 1230, 162],
    'Acethylene': [7, 0, 2190, 0, 4, 1, 0],
    'DBDS': [19, 45, 1, 87, 1, 1, 1],
    'Power factor': [1, 1, 1, 4.58, 0.77, 4.93, 3.53],
    'Interfacial V': [45, 45, 39, 33, 44, 37, 45],
    'Dielectric rigidity': [55, 55, 52, 49, 55, 52, 55],
    'Water content': [0, 0, 11, 5, 3, 6, 5],
    'Health index': [95.2, 85.5, 85.3, 85.3, 85.2, 75.6, 75.6],
    'Life expectation': [19, 19, 19, 6, 6, 6, 6]
}

df = pd.DataFrame(data)

# Create a new ontology
onto = get_ontology("http://test.org/onto.owl")

with onto:
    class HealthIndex(DataProperty, FunctionalProperty):
        domain = [Thing]
        range = [float]

    class PowerFactor(DataProperty, FunctionalProperty):
        domain = [Thing]
        range = [float]

    class LifeExpectation(DataProperty, FunctionalProperty):
        domain = [Thing]
        range = [str]

    class Failure(Thing):
        pass

    class NonFailure(Thing):
        pass


    # Add the individuals and their properties to the ontology
    for index, row in df.iterrows():
        individual = Thing(f"Individual{index}", namespace=onto)
        individual.HealthIndex = float(row['Health index'])
        individual.PowerFactor = float(row['Power factor'])
        individual.LifeExpectation = str(row['Life expectation']) 
        print(f"Individual{index} added to the ontology")


    Imp().set_as_rule('LifeExpectation(?p, ?val) ^ lessThan(?val, 22) -> Failure(?p)')
    Imp().set_as_rule('HealthIndex(?p, ?val) ^ lessThan(?val, 85) -> NonFailure(?p)')
    Imp().set_as_rule('PowerFactor(?p, ?val) ^ lessThan(?val, 1) -> NonFailure(?p)')

sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)
print(list(onto.search(is_a = Failure)))
print(list(onto.search(is_a = NonFailure)))
