"""Alternative script for reasoners that do not execute SWRL rules directly."""

from owlready2 import DataProperty, FunctionalProperty, Thing, get_ontology


def main() -> None:
    onto = get_ontology("http://test.org/onto.owl")

    with onto:

        class Transformer(Thing):
            pass

        class Failure(Transformer):
            pass

        class NonFailure(Transformer):
            pass

        class hasOxygen(DataProperty, FunctionalProperty):
            domain = [Transformer]
            range = [float]

        class hasNitrogen(DataProperty, FunctionalProperty):
            domain = [Transformer]
            range = [float]

        transformer_1 = Transformer("PW101")
        transformer_1.hasOxygen = 0.4
        transformer_1.hasNitrogen = 1.4
        transformer_2 = Transformer("PW102")
        transformer_2.hasOxygen = 0.6
        transformer_3 = Transformer("PW103")
        transformer_3.hasOxygen = 0.7
        transformer_3.hasNitrogen = 70000

    for transformer in Transformer.instances():
        if transformer.hasOxygen < 0.5:
            transformer.is_a.append(Failure)
        elif transformer.hasOxygen > 0.5:
            transformer.is_a.append(NonFailure)
        if (
            transformer.hasOxygen > 0.5
            and transformer.hasNitrogen is not None
            and transformer.hasNitrogen > 62651
        ):
            transformer.is_a.append(Failure)

    failures = [instance.name for instance in Failure.instances()]
    print("Failures:", failures)


if __name__ == "__main__":
    main()
