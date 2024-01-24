# 🌐 Root Cause Analysis in the Industrial Domain using Knowledge Graphs: A Case Study on Power Transformers

[![DOI:10.1016/j.procs.2022.01.304](https://img.shields.io/badge/DOI-10.1016%2Fj.procs.2022.01.304-blue.svg)](https://doi.org/10.1016/j.procs.2022.01.304)

## 📖 Introduction
This material, developed as part of a research presented in "Knowledge Graph-Driven Root Cause Analysis for Industrial Faults" (DOI: [10.1016/j.procs.2022.01.304](https://www.sciencedirect.com/science/article/pii/S1877050922003015)), focuses on identifying, understanding, and correcting faults in industrial settings. The core component is an ontology that facilitates fault analysis through reasoning, classification, and advanced querying capabilities. 🧠

This work is based on the Arias & Mejia-Lara dataset: [Dataset Link](https://data.mendeley.com/datasets/rz75w3fkxy/1)

## 🌍 Overview
In industrial environments, handling faults efficiently is critical due to associated costs. Traditional methods lack the capability to aid human operators in discerning fault causes and solutions. This ontology supports a knowledge graph-driven approach for root cause analysis, which includes:
1. **Reasoning**: Analyzing the current state of power transfromers. 🤖
2. **Classification**: Utilizing rules for failure classification. 🏷️
3. **Querying**: Leveraging graph-query languages for advanced data querying. 📊

## 📚 Ontology
The ontology `onto-pw` was applied in a power transformer case study, demonstrating its effectiveness  in fault analysis.

### Ontology URI
Base URI: `http://test.org/onto-pw`

### Namespaces
- RDF: `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
- XSD: `http://www.w3.org/2001/XMLSchema#`
- RDFS: `http://www.w3.org/2000/01/rdf-schema#`
- OWL: `http://www.w3.org/2002/07/owl#`
- SWRL: `http://www.w3.org/2003/11/swrl#`

### Classes
1. **Transformer**: Represents the primary entity in the ontology.
2. **Gas**: A subclass of Transformer, representing various gases.
3. **Property**: General class for properties.
4. **Estimation**: Represents estimations.
5. **Measurement**: General class for measurements.
6. **DBDS, Power_factor, Interfacial_V, Dielectric_rigidity, Water_content, Health_index, Life_expectation**: Subclasses of Transformer, representing specific properties.
7. **Hydrogen, Oxygen, Nitrogen, Methane, CO, CO2, Ethylene, Ethane, Acetylene**: Subclasses of Gas, representing specific gas types.

### Object Properties
1. **is**: Basic object property.
2. **relatesWaterContentToMeasurement**: Links Water Content to Measurement.
3. (Additional object properties are assumed to follow a similar pattern)

### Datatype Properties
1. **hasWaterLevel**: Represents the water level, with domain as Water Content and range as integer.
2. (Additional object properties are assumed to follow a similar pattern)

### Named Individuals
1. **PW101 and PW102**: Instances of Transformer with associated water levels.

### AllDifferent Declaration
Ensures that specific classes like DBDS, Power_factor, etc., are recognized as distinct.

### Usage
The ontology is structured to represent transformers and their properties, including various gas types and measurements. It allows linking specific transformer instances with their properties, such as water content. This ontology aids operators in the industrial domain, particularly in power transformer fault analysis, by providing a structured framework for reasoning, failure classification, and querying.

### Additional Notes
- The ontology is designed for extensibility and adaptability to various industrial scenarios. 🌟

## 📈 Classification

The file `swrl-rules.py` shows an example of how to perform classification.

### Data Preparation and Analysis
- **Libraries Used**: `pandas`, `owlready2`, `rdflib`. 📚
- **Data**: The script initializes a dataset with various gases and other properties.

### DataFrame Creation
- A `DataFrame` is created using `pandas` to structure the data. This DataFrame includes multiple columns for different gases and properties.

### Ontology Creation
- An ontology is defined using the `owlready2` library.

### Ontology Population
- The script iterates through the DataFrame to create individuals in the ontology, assigning them properties based on the data.
- Each individual is named `Individual` followed by their index in the DataFrame.

### Inference Rules and Reasoning
- Inference rules are established to classify individuals as `Failure` or `NonFailure` based on their `LifeExpectation`, `HealthIndex`, and `PowerFactor`.
- The `Pellet` reasoner is used for reasoning and to infer property values.

### Output
- Finally, the script prints out lists of individuals classified as `Failure` and `NonFailure`.

## 🔍 Querying
The file `query.py` shows an example of how to perform querying.

### Query Overview
- **Purpose**: To select transformers with water content levels above a specific threshold.
- **Namespace Prefixes**:
  - `rdf`: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  - `owl`: <http://www.w3.org/2002/07/owl#>
  - `xsd`: <http://www.w3.org/2001/XMLSchema#>
  - Default (:): <http://test.org/onto-pw#>

### Query Structure
- **SELECT Clause**: Retrieves `?transformer`.
- **WHERE Clause**:
  - Matches any `?transformer` that is of type `:Transformer`.
  - Associates `?transformer` with `?waterContent` using the `:relatesToWaterContent` predicate.
  - Extracts the water level `?level` associated with `?waterContent` using the `:hasWaterLevel` predicate.
  - Uses a `FILTER` to only include transformers where the water level `?level` is greater than 100.

### Query Goal
- The aim is to identify transformers within a given ontology that are potentially at risk due to high water content, as indicated by a water level exceeding 100.

## 📚 Reference

```
@inproceedings{martinez2021root,
  author       = {Jorge Martinez-Gil and
                  Georg Buchgeher and
                  David Gabauer and
                  Bernhard Freudenthaler and
                  Dominik Filipiak and
                  Anna Fensel},
  editor       = {Francesco Longo and
                  Michael Affenzeller and
                  Antonio Padovano},
  title        = {Root Cause Analysis in the Industrial Domain using Knowledge Graphs:
                  {A} Case Study on Power Transformers},
  booktitle    = {Proceedings of the 3rd International Conference on Industry 4.0 and
                  Smart Manufacturing {(ISM} 2022), Virtual Event / Upper Austria University
                  of Applied Sciences - Hagenberg Campus - Linz, Austria, 17-19 November
                  2021},
  series       = {Procedia Computer Science},
  volume       = {200},
  pages        = {944--953},
  publisher    = {Elsevier},
  year         = {2021},
  url          = {https://doi.org/10.1016/j.procs.2022.01.292},
  doi          = {10.1016/J.PROCS.2022.01.292}
}
```

## 📄 License

The material is provided under the MIT License.
