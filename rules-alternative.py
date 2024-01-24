# -*- coding: utf-8 -*-
"""
Example of classification using SWRL rules. Alternative when SWRL is not accepted in the reasoner

Martinez-Gil, J., Buchgeher, G., Gabauer, D., Freudenthaler, B., Filipiak, D., & Fensel, A. (2022). Root cause analysis in the industrial domain using knowledge graphs: A case study on power transformers. Procedia Computer Science, 200, 944-953.

@author: Jorge Martinez-Gil
"""

from owlready2 import *

# Create a new ontology
onto = get_ontology("http://test.org/onto.owl")

with onto:
    # Define classes
    class Transformer(Thing):
        pass

    class Failure(Transformer):
        pass

    class NonFailure(Transformer):
        pass

    # Define properties
    class hasOxigen(DataProperty, FunctionalProperty):
        domain = [Transformer]
        range = [float]

    class hasNitrogen(DataProperty, FunctionalProperty):
        domain = [Transformer]
        range = [float]

    # Create individuals (example data)
    p1 = Transformer("PW101")
    p1.hasOxigen = 0.4
    p1.hasNitrogen = 1.4
    p2 = Transformer("PW102")
    p2.hasOxigen = 0.6
    p3 = Transformer("PW103")
    p3.hasOxigen = 0.7
    p3.hasNitrogen = 70000  # Nitrogen level

# Implement the logic of the SWRL rules in Python 
# This code is needed when the reasoner cannot operate SWRL rules directly
for transformer in Transformer.instances():
    if transformer.hasOxigen < 0.5:
        transformer.is_a.append(Failure)
    elif transformer.hasOxigen > 0.5:
        transformer.is_a.append(NonFailure)
    if transformer.hasOxigen > 0.5 and transformer.hasNitrogen is not None and transformer.hasNitrogen > 62651:
        transformer.is_a.append(Failure)

# Example: Checking which individuals are instances of Failure
failures = list(Failure.instances())
print("Failures:", [i.name for i in failures])