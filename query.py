# -*- coding: utf-8 -*-
"""
Example of querying

Martinez-Gil, J., Buchgeher, G., Gabauer, D., Freudenthaler, B., Filipiak, D., & Fensel, A. (2022). Root cause analysis in the industrial domain using knowledge graphs: A case study on power transformers. Procedia Computer Science, 200, 944-953.

@author: Jorge Martinez-Gil
"""

from owlready2 import get_ontology, default_world

# Load ontology
onto_path = "onto_pw"  # Replace with the actual path to your ontology file
onto = get_ontology(onto_path).load()

# Prepare the SPARQL query
query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://test.org/onto-pw#>

SELECT ?transformer
WHERE {
  ?transformer rdf:type :Transformer .
  ?transformer :relatesToWaterContent ?waterContent .
  ?waterContent :hasWaterLevel ?level .
  FILTER(?level > 100)
}
"""

# Execute the SPARQL query
results = default_world.sparql(query)

# Print the results
for result in results:
    print(result[0])

